from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional

import numpy as np
from rank_bm25 import BM25Okapi

from ..models import ExpertCard, RetrievalHit
from .memory import _tokenize, _rrf


def _default_data_dir() -> Path:
    return Path(os.environ.get("SKILLMESH_DATA_DIR", Path.home() / ".skillmesh" / "chroma"))


def _card_hash(card: ExpertCard) -> str:
    content = f"{card.id}|{card.title}|{card.description}|{','.join(card.tags)}|{card.instruction_text[:500]}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _compose_doc(card: ExpertCard) -> str:
    input_contract_text = ", ".join(f"{k}:{v}" for k, v in card.input_contract.items())
    metadata_text = ", ".join(f"{k}:{v}" for k, v in card.metadata.items())
    return "\n".join([
        card.id, card.title, card.domain, card.description,
        "tags: " + ", ".join(card.tags),
        "tool_hints: " + ", ".join(card.tool_hints),
        "examples: " + " | ".join(card.examples),
        "aliases: " + ", ".join(card.aliases),
        "dependencies: " + ", ".join(card.dependencies),
        "output_artifacts: " + ", ".join(card.output_artifacts),
        "quality_checks: " + ", ".join(card.quality_checks),
        "constraints: " + ", ".join(card.constraints),
        "input_contract: " + input_contract_text,
        "risk_level: " + card.risk_level,
        "maturity: " + card.maturity,
        "metadata: " + metadata_text,
        card.instruction_text[:2000],
    ])


class ChromaBackend:
    def __init__(self, *, collection_name: str = "skillmesh_experts", data_dir: str | Path | None = None, ephemeral: bool = False):
        import chromadb

        self._collection_name = collection_name
        self._ephemeral = ephemeral

        if ephemeral:
            self._client = chromadb.Client()
        else:
            persist_dir = str(Path(data_dir) if data_dir else _default_data_dir())
            self._client = chromadb.PersistentClient(path=persist_dir)

        self._cards: list[ExpertCard] = []
        self._card_map: dict[str, ExpertCard] = {}
        self._bm25: Optional[BM25Okapi] = None
        self._tokens: list[list[str]] = []
        self._collection = None

    def index(self, cards: list[ExpertCard]) -> None:
        if not cards:
            self._cards = []
            self._card_map = {}
            self._bm25 = None
            self._tokens = []
            self._collection = None
            return

        self._cards = cards
        self._card_map = {c.id: c for c in cards}

        doc_texts = [_compose_doc(c) for c in cards]
        self._tokens = [_tokenize(d) for d in doc_texts]
        self._bm25 = BM25Okapi(self._tokens) if self._tokens else None

        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass

        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        ids = [c.id for c in cards]
        documents = doc_texts
        metadatas = [
            {
                "domain": c.domain,
                "risk_level": c.risk_level or "",
                "maturity": c.maturity or "",
                "tags": ",".join(c.tags[:20]),
                "content_hash": _card_hash(c),
            }
            for c in cards
        ]

        batch_size = 500
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            self._collection.upsert(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end],
            )

    def _sparse_scores(self, query: str) -> np.ndarray:
        n = len(self._cards)
        if n == 0:
            return np.array([], dtype=np.float32)
        q_tokens = _tokenize(query)
        if not q_tokens:
            return np.zeros(n, dtype=np.float32)
        if self._bm25 is not None:
            scores = np.asarray(self._bm25.get_scores(q_tokens), dtype=np.float32)
            mx = float(np.max(scores)) if len(scores) else 0.0
            return scores / mx if mx > 0 else scores
        return np.zeros(n, dtype=np.float32)

    def query(self, text: str, top_k: int = 3) -> list[RetrievalHit]:
        if not self._cards or self._collection is None:
            return []
        top_k = max(1, min(int(top_k), min(20, len(self._cards))))

        n_candidates = min(len(self._cards), max(top_k * 3, 20))
        results = self._collection.query(query_texts=[text], n_results=n_candidates)

        n = len(self._cards)
        dense_scores = np.zeros(n, dtype=np.float32)
        id_to_idx = {c.id: i for i, c in enumerate(self._cards)}

        if results and results["ids"] and results["ids"][0]:
            chroma_ids = results["ids"][0]
            chroma_dists = results["distances"][0] if results.get("distances") else None
            for rank, cid in enumerate(chroma_ids):
                if cid in id_to_idx:
                    idx = id_to_idx[cid]
                    if chroma_dists is not None:
                        dense_scores[idx] = 1.0 - chroma_dists[rank]
                    else:
                        dense_scores[idx] = 1.0 / (rank + 1)

        mx = float(np.max(dense_scores)) if np.any(dense_scores) else 0.0
        mn = float(np.min(dense_scores[dense_scores > 0])) if np.any(dense_scores > 0) else 0.0
        if mx - mn > 1e-9:
            mask = dense_scores > 0
            dense_scores[mask] = (dense_scores[mask] - mn) / (mx - mn)

        sparse = self._sparse_scores(text)

        sparse_rank = np.argsort(-sparse)
        dense_rank = np.argsort(-dense_scores)
        hybrid = _rrf([sparse_rank, dense_rank], n_docs=n)

        idx = np.argsort(-hybrid)[:top_k]
        hits: list[RetrievalHit] = []
        for i in idx:
            hits.append(
                RetrievalHit(
                    card=self._cards[int(i)],
                    score=float(hybrid[int(i)]),
                    sparse_score=float(sparse[int(i)]),
                    dense_score=float(dense_scores[int(i)]),
                )
            )
        return hits
