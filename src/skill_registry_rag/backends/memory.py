"""In-memory retrieval backend using BM25 + optional dense embeddings."""

from __future__ import annotations

import re
from typing import Optional

import numpy as np
from rank_bm25 import BM25Okapi

from ..models import ExpertCard, RetrievalHit


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_\.]+", str(text or "").lower())


def _rrf(ranks: list[np.ndarray], n_docs: int, k: int = 60) -> np.ndarray:
    scores = np.zeros(n_docs, dtype=np.float32)
    for order in ranks:
        for rank, idx in enumerate(order, start=1):
            scores[int(idx)] += 1.0 / (k + rank)
    return scores


class InMemoryBackend:
    """BM25 + optional dense retrieval, fully in-process."""

    def __init__(self, *, use_dense: bool = False) -> None:
        self.use_dense = use_dense
        self._cards: list[ExpertCard] = []
        self._doc_texts: list[str] = []
        self._tokens: list[list[str]] = []
        self._bm25: Optional[BM25Okapi] = None
        self._dense_model = None
        self._dense_embeddings: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # RetrievalBackend interface
    # ------------------------------------------------------------------

    def index(self, cards: list[ExpertCard]) -> None:
        self._cards = cards
        self._doc_texts = [self._compose_doc(c) for c in cards]
        self._tokens = [_tokenize(d) for d in self._doc_texts]
        self._bm25 = BM25Okapi(self._tokens) if self._tokens else None
        self._dense_model = None
        self._dense_embeddings = None
        if self.use_dense:
            self._init_dense()

    def query(self, text: str, top_k: int = 3) -> list[RetrievalHit]:
        if not self._cards:
            return []
        top_k = max(1, min(int(top_k), min(20, len(self._cards))))

        sparse = self._sparse_scores(text)
        dense = self._dense_scores(text)

        sparse_rank = np.argsort(-sparse)
        if dense is None:
            hybrid = sparse
        else:
            dense_rank = np.argsort(-dense)
            hybrid = _rrf([sparse_rank, dense_rank], n_docs=len(self._cards))

        idx = np.argsort(-hybrid)[:top_k]
        hits: list[RetrievalHit] = []
        for i in idx:
            dense_score = None if dense is None else float(dense[int(i)])
            hits.append(
                RetrievalHit(
                    card=self._cards[int(i)],
                    score=float(hybrid[int(i)]),
                    sparse_score=float(sparse[int(i)]),
                    dense_score=dense_score,
                )
            )
        return hits

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compose_doc(card: ExpertCard) -> str:
        input_contract_text = ", ".join(
            f"{k}:{v}" for k, v in card.input_contract.items()
        )
        metadata_text = ", ".join(f"{k}:{v}" for k, v in card.metadata.items())
        return "\n".join(
            [
                card.id,
                card.title,
                card.domain,
                card.description,
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
            ]
        )

    def _init_dense(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("BAAI/bge-small-en-v1.5")
            embs = model.encode(self._doc_texts, normalize_embeddings=True)
            self._dense_model = model
            self._dense_embeddings = np.asarray(embs, dtype=np.float32)
        except Exception:
            self._dense_model = None
            self._dense_embeddings = None

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

        q_set = set(q_tokens)
        overlaps = []
        for toks in self._tokens:
            d_set = set(toks)
            inter = len(q_set & d_set)
            union = len(q_set | d_set)
            overlaps.append((inter / union) if union else 0.0)
        return np.asarray(overlaps, dtype=np.float32)

    def _dense_scores(self, query: str) -> Optional[np.ndarray]:
        if self._dense_model is None or self._dense_embeddings is None:
            return None
        try:
            q = self._dense_model.encode([query], normalize_embeddings=True)
            q_vec = np.asarray(q[0], dtype=np.float32)
            scores = self._dense_embeddings @ q_vec
            mn = float(np.min(scores))
            mx = float(np.max(scores))
            if mx - mn < 1e-9:
                return np.zeros_like(scores, dtype=np.float32)
            return ((scores - mn) / (mx - mn)).astype(np.float32)
        except Exception:
            return None
