# SkillMesh v2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Scale SkillMesh from 15 in-memory experts to thousands via ChromaDB-backed hybrid retrieval, and ship ~60 rich domain experts with deep instruction files.

**Architecture:** Extract current BM25+dense logic into an `InMemoryBackend` behind a `RetrievalBackend` Protocol. Add a `ChromaBackend` using ChromaDB for persistent vector storage with BM25 re-ranking. Auto-select backend based on card count. Expand all instruction files from ~18 lines to 60-100 lines with anti-patterns, decision trees, and composability hints. Add ~45 new expert domains.

**Tech Stack:** Python 3.10+, ChromaDB, rank-bm25, numpy, sentence-transformers (optional), pytest

---

## Phase 1: Backend Abstraction

### Task 1: Create RetrievalBackend Protocol and backends package

**Files:**
- Create: `src/skill_registry_rag/backends/__init__.py`
- Create: `src/skill_registry_rag/backends/memory.py`
- Test: `tests/test_backends.py`

**Step 1: Create the backends package with Protocol**

Create `src/skill_registry_rag/backends/__init__.py`:

```python
"""Retrieval backend abstraction."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import ExpertCard, RetrievalHit


@runtime_checkable
class RetrievalBackend(Protocol):
    """Interface for retrieval backends."""

    def index(self, cards: list[ExpertCard]) -> None:
        """Index a list of expert cards for retrieval."""
        ...

    def query(self, text: str, top_k: int = 3) -> list[RetrievalHit]:
        """Retrieve top-k expert cards matching the query text."""
        ...


__all__ = ["RetrievalBackend"]
```

**Step 2: Extract InMemoryBackend from retriever.py**

Create `src/skill_registry_rag/backends/memory.py`. Move ALL retrieval logic from `retriever.py` (the `_tokenize`, `_rrf` functions, and the BM25/dense scoring) into this file as the `InMemoryBackend` class:

```python
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
    """BM25 + optional dense retrieval, held entirely in memory."""

    def __init__(self, *, use_dense: bool = False):
        self._use_dense = use_dense
        self._cards: list[ExpertCard] = []
        self._doc_texts: list[str] = []
        self._tokens: list[list[str]] = []
        self._bm25: Optional[BM25Okapi] = None
        self._dense_model = None
        self._dense_embeddings: Optional[np.ndarray] = None

    def index(self, cards: list[ExpertCard]) -> None:
        self._cards = cards
        self._doc_texts = [self._compose_doc(c) for c in cards]
        self._tokens = [_tokenize(d) for d in self._doc_texts]
        self._bm25 = BM25Okapi(self._tokens) if self._tokens else None
        self._dense_model = None
        self._dense_embeddings = None
        if self._use_dense:
            self._init_dense()

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
```

**Step 3: Write failing tests for InMemoryBackend**

Create `tests/test_backends.py`:

```python
from __future__ import annotations

from pathlib import Path

from skill_registry_rag.backends import RetrievalBackend
from skill_registry_rag.backends.memory import InMemoryBackend
from skill_registry_rag.registry import load_registry


def _load_cards():
    root = Path(__file__).resolve().parents[1]
    return load_registry(root / "examples" / "registry" / "experts.yaml")


def test_in_memory_backend_implements_protocol():
    backend = InMemoryBackend()
    assert isinstance(backend, RetrievalBackend)


def test_in_memory_backend_index_and_query():
    cards = _load_cards()
    backend = InMemoryBackend()
    backend.index(cards)
    hits = backend.query("build matplotlib seaborn heatmap", top_k=2)
    assert len(hits) == 2
    assert hits[0].card.id == "viz.matplotlib-seaborn"


def test_in_memory_backend_empty_cards():
    backend = InMemoryBackend()
    backend.index([])
    hits = backend.query("anything", top_k=3)
    assert hits == []


def test_in_memory_backend_sklearn_query():
    cards = _load_cards()
    backend = InMemoryBackend()
    backend.index(cards)
    hits = backend.query("sklearn pipeline cross validation leakage safe", top_k=1)
    assert hits[0].card.id == "ml.sklearn-modeling"
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_backends.py -v`
Expected: 4 PASS

**Step 5: Commit**

```bash
git add src/skill_registry_rag/backends/ tests/test_backends.py
git commit -m "feat: extract InMemoryBackend behind RetrievalBackend protocol"
```

---

### Task 2: Refactor SkillRetriever to delegate to backends

**Files:**
- Modify: `src/skill_registry_rag/retriever.py` (full rewrite — replace with delegation)
- Modify: `src/skill_registry_rag/__init__.py` (add backend exports)

**Step 1: Rewrite retriever.py as a thin facade**

Replace entire contents of `src/skill_registry_rag/retriever.py`:

```python
from __future__ import annotations

from .backends.memory import InMemoryBackend
from .models import ExpertCard, RetrievalHit


class SkillRetriever:
    """Top-k expert retrieval.

    Delegates to a RetrievalBackend. Defaults to InMemoryBackend
    for backward compatibility.
    """

    def __init__(
        self,
        cards: list[ExpertCard],
        *,
        use_dense: bool = False,
        backend: str = "auto",
    ):
        if backend == "chroma":
            from .backends.chroma import ChromaBackend
            self._backend = ChromaBackend()
        elif backend == "memory" or (backend == "auto" and len(cards) < 100):
            self._backend = InMemoryBackend(use_dense=use_dense)
        else:
            # auto with >= 100 cards: try chroma, fall back to memory
            try:
                from .backends.chroma import ChromaBackend
                self._backend = ChromaBackend()
            except ImportError:
                self._backend = InMemoryBackend(use_dense=use_dense)

        self._backend.index(cards)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievalHit]:
        return self._backend.query(query, top_k=top_k)
```

**Step 2: Update __init__.py exports**

Add backend exports to `src/skill_registry_rag/__init__.py`:

```python
"""skill-registry-rag package."""

from .backends import RetrievalBackend
from .backends.memory import InMemoryBackend
from .models import ExpertCard, RetrievalHit
from .registry import load_registry
from .retriever import SkillRetriever

__all__ = [
    "ExpertCard",
    "InMemoryBackend",
    "RetrievalBackend",
    "RetrievalHit",
    "SkillRetriever",
    "load_registry",
]
```

**Step 3: Run ALL existing tests to verify nothing breaks**

Run: `pytest -v`
Expected: All 18 existing tests PASS + 4 new backend tests PASS (22 total)

**Step 4: Commit**

```bash
git add src/skill_registry_rag/retriever.py src/skill_registry_rag/__init__.py
git commit -m "refactor: SkillRetriever delegates to RetrievalBackend"
```

---

## Phase 2: ChromaDB Backend

### Task 3: Add chromadb dependency

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add chromadb to dependencies**

In `pyproject.toml`, change the dependencies array to:

```toml
dependencies = [
  "numpy>=1.24",
  "PyYAML>=6.0",
  "rank-bm25>=0.2.2",
  "jsonschema>=4.0",
  "chromadb>=0.5.0",
]
```

**Step 2: Install updated package**

Run: `pip install -e ".[dev]"`
Expected: chromadb installed successfully

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add chromadb for persistent vector backend"
```

---

### Task 4: Implement ChromaBackend

**Files:**
- Create: `src/skill_registry_rag/backends/chroma.py`
- Modify: `tests/test_backends.py` (add ChromaDB tests)

**Step 1: Write failing tests for ChromaBackend**

Append to `tests/test_backends.py`:

```python
import pytest
from skill_registry_rag.backends.chroma import ChromaBackend


def test_chroma_backend_implements_protocol():
    backend = ChromaBackend()
    assert isinstance(backend, RetrievalBackend)


def test_chroma_backend_index_and_query():
    cards = _load_cards()
    backend = ChromaBackend()
    backend.index(cards)
    hits = backend.query("build matplotlib seaborn heatmap", top_k=2)
    assert len(hits) == 2
    # ChromaDB uses dense embeddings; top-1 should still be viz expert
    assert hits[0].card.id == "viz.matplotlib-seaborn"


def test_chroma_backend_empty_cards():
    backend = ChromaBackend()
    backend.index([])
    hits = backend.query("anything", top_k=3)
    assert hits == []


def test_chroma_backend_sklearn_query():
    cards = _load_cards()
    backend = ChromaBackend()
    backend.index(cards)
    hits = backend.query("sklearn pipeline cross validation metrics", top_k=1)
    assert hits[0].card.id == "ml.sklearn-modeling"


def test_chroma_backend_pytorch_query():
    cards = _load_cards()
    backend = ChromaBackend()
    backend.index(cards)
    hits = backend.query("pytorch training loop cuda mixed precision checkpoint", top_k=1)
    assert hits[0].card.id == "dl.pytorch-training"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_backends.py -v -k chroma`
Expected: FAIL (ImportError — chroma module doesn't exist yet)

**Step 3: Implement ChromaBackend**

Create `src/skill_registry_rag/backends/chroma.py`:

```python
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import numpy as np
from rank_bm25 import BM25Okapi

from ..models import ExpertCard, RetrievalHit

# Re-use tokenizer from memory backend
from .memory import _tokenize, _rrf


def _default_data_dir() -> Path:
    import os
    return Path(os.environ.get("SKILLMESH_DATA_DIR", Path.home() / ".skillmesh" / "chroma"))


def _card_hash(card: ExpertCard) -> str:
    """Deterministic hash of card content for change detection."""
    content = f"{card.id}|{card.title}|{card.description}|{','.join(card.tags)}|{card.instruction_text[:500]}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _compose_doc(card: ExpertCard) -> str:
    """Compose searchable text from card fields."""
    input_contract_text = ", ".join(f"{k}:{v}" for k, v in card.input_contract.items())
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


class ChromaBackend:
    """ChromaDB-backed retrieval with BM25 re-ranking via RRF.

    Dense retrieval via ChromaDB's built-in embedding function.
    Sparse retrieval via BM25 on card text. Combined with RRF.
    """

    def __init__(
        self,
        *,
        collection_name: str = "skillmesh_experts",
        data_dir: str | Path | None = None,
        ephemeral: bool = False,
    ):
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

        # Build BM25 index for sparse scoring
        doc_texts = [_compose_doc(c) for c in cards]
        self._tokens = [_tokenize(d) for d in doc_texts]
        self._bm25 = BM25Okapi(self._tokens) if self._tokens else None

        # Upsert into ChromaDB collection
        # Delete and recreate to ensure clean state
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

        # ChromaDB has batch size limits; upsert in chunks
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

        # Dense retrieval from ChromaDB
        # Fetch more candidates than top_k for better RRF fusion
        n_candidates = min(len(self._cards), max(top_k * 3, 20))
        results = self._collection.query(
            query_texts=[text],
            n_results=n_candidates,
        )

        # Build dense score array over all cards
        n = len(self._cards)
        dense_scores = np.zeros(n, dtype=np.float32)
        id_to_idx = {c.id: i for i, c in enumerate(self._cards)}

        if results and results["ids"] and results["ids"][0]:
            chroma_ids = results["ids"][0]
            # ChromaDB returns distances; for cosine, distance = 1 - similarity
            chroma_dists = results["distances"][0] if results.get("distances") else None
            for rank, cid in enumerate(chroma_ids):
                if cid in id_to_idx:
                    idx = id_to_idx[cid]
                    if chroma_dists is not None:
                        dense_scores[idx] = 1.0 - chroma_dists[rank]
                    else:
                        dense_scores[idx] = 1.0 / (rank + 1)

        # Normalize dense scores
        mx = float(np.max(dense_scores)) if np.any(dense_scores) else 0.0
        mn = float(np.min(dense_scores[dense_scores > 0])) if np.any(dense_scores > 0) else 0.0
        if mx - mn > 1e-9:
            mask = dense_scores > 0
            dense_scores[mask] = (dense_scores[mask] - mn) / (mx - mn)

        # BM25 sparse scores
        sparse = self._sparse_scores(text)

        # RRF fusion
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
```

**Step 4: Run ChromaDB tests**

Run: `pytest tests/test_backends.py -v`
Expected: All 9 tests PASS (4 in-memory + 5 chroma)

**Step 5: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/skill_registry_rag/backends/chroma.py tests/test_backends.py
git commit -m "feat: add ChromaDB backend with BM25+dense RRF hybrid retrieval"
```

---

## Phase 3: CLI `index` Command

### Task 5: Add `index` subcommand and `--backend` flag to CLI

**Files:**
- Modify: `src/skill_registry_rag/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing test for `index` command**

Append to `tests/test_cli.py`:

```python
def test_cli_index_creates_collection():
    root = Path(__file__).resolve().parents[1]
    registry = root / "examples" / "registry" / "tools.enriched.json"

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "index",
                "--registry",
                str(registry),
                "--ephemeral",
            ]
        )

    assert code == 0
    output = buf.getvalue()
    assert "Indexed" in output


def test_cli_retrieve_with_backend_flag():
    root = Path(__file__).resolve().parents[1]
    registry = root / "examples" / "registry" / "tools.enriched.json"

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "retrieve",
                "--registry",
                str(registry),
                "--query",
                "opencv contour detection",
                "--top-k",
                "1",
                "--backend",
                "memory",
            ]
        )

    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["hits"][0]["id"] == "cv.opencv-image-processing"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -v`
Expected: 2 new tests FAIL

**Step 3: Update cli.py**

Add `index` subcommand and `--backend` flag to existing subcommands in `src/skill_registry_rag/cli.py`. Updated `_build_parser`:

```python
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-rag",
        description="Top-k skill expert retrieval for Codex/Claude style runtimes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # index command
    index_cmd = sub.add_parser("index", help="Index registry into ChromaDB for persistent retrieval")
    index_cmd.add_argument("--registry", required=True, help="Path to experts YAML/JSON")
    index_cmd.add_argument("--collection", default="skillmesh_experts", help="ChromaDB collection name")
    index_cmd.add_argument("--data-dir", default=None, help="ChromaDB persistence directory")
    index_cmd.add_argument("--ephemeral", action="store_true", help="Use ephemeral (in-memory) ChromaDB for testing")

    # retrieve command
    retrieve = sub.add_parser("retrieve", help="Retrieve top-k experts for query")
    retrieve.add_argument("--registry", required=True, help="Path to experts YAML/JSON")
    retrieve.add_argument("--query", required=True, help="User query")
    retrieve.add_argument("--top-k", type=int, default=3, help="Top-k hits")
    retrieve.add_argument("--dense", action="store_true", help="Enable optional dense scoring")
    retrieve.add_argument("--backend", choices=["auto", "memory", "chroma"], default="auto", help="Retrieval backend")

    # emit command
    emit = sub.add_parser("emit", help="Emit provider-specific context block")
    emit.add_argument("--provider", required=True, choices=["codex", "claude"], help="Target provider")
    emit.add_argument("--registry", required=True, help="Path to experts YAML/JSON")
    emit.add_argument("--query", required=True, help="User query")
    emit.add_argument("--top-k", type=int, default=3, help="Top-k hits")
    emit.add_argument("--dense", action="store_true", help="Enable optional dense scoring")
    emit.add_argument("--backend", choices=["auto", "memory", "chroma"], default="auto", help="Retrieval backend")
    emit.add_argument(
        "--instruction-chars",
        type=int,
        default=700,
        help="Max instruction text per retrieved expert",
    )

    return parser
```

Updated `main()`:

```python
def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "index":
        try:
            cards = load_registry(args.registry)
        except RegistryError as exc:
            print(f"RegistryError: {exc}", file=sys.stderr)
            return 2

        from .backends.chroma import ChromaBackend

        backend = ChromaBackend(
            collection_name=args.collection,
            data_dir=args.data_dir,
            ephemeral=args.ephemeral,
        )
        backend.index(cards)
        print(f"Indexed {len(cards)} experts into collection '{args.collection}'")
        return 0

    try:
        cards = load_registry(args.registry)
    except RegistryError as exc:
        print(f"RegistryError: {exc}", file=sys.stderr)
        return 2

    backend_choice = getattr(args, "backend", "auto")
    retriever = SkillRetriever(
        cards,
        use_dense=bool(getattr(args, "dense", False)),
        backend=backend_choice,
    )
    hits = retriever.retrieve(args.query, top_k=args.top_k)

    if args.command == "retrieve":
        print(json.dumps({"query": args.query, "hits": _hits_payload(hits)}, indent=2))
        return 0

    if args.provider == "codex":
        out = render_codex_context(args.query, hits, instruction_chars=args.instruction_chars)
    else:
        out = render_claude_context(args.query, hits, instruction_chars=args.instruction_chars)

    print(out, end="")
    return 0
```

**Step 4: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/skill_registry_rag/cli.py tests/test_cli.py
git commit -m "feat: add 'index' CLI command and --backend flag for ChromaDB"
```

---

## Phase 4: Enrich Existing Instruction Files

### Task 6: Enrich all 15 existing instruction files

**Files:**
- Modify: all 15 files in `examples/registry/instructions/`

Each file expands from ~18 lines to 60-100 lines using the v2 structure: when to use, execution behavior (expanded), decision tree, anti-patterns, common mistakes, output contract (expanded), composability hints.

**Step 1: Enrich sklearn-modeling.md**

Replace `examples/registry/instructions/sklearn-modeling.md` with:

```markdown
# Scikit-learn Modeling Expert

Use this expert when tasks require robust model training and evaluation in scikit-learn.

## When to use this expert

- Building classification or regression models on tabular data
- Comparing multiple model families with fair evaluation
- Setting up reproducible ML pipelines with preprocessing
- Evaluating model performance with proper validation

## Execution behavior

1. Profile the target variable: class balance for classification, distribution for regression.
2. Choose split strategy: stratified k-fold for classification, standard k-fold for regression, TimeSeriesSplit for temporal data. Never use random shuffle on time-ordered data.
3. Build a unified `Pipeline` with `ColumnTransformer` for heterogeneous preprocessing and the estimator as the final step.
4. Run cross-validation for model comparison before committing to a final fit.
5. Select metrics aligned to objective: F1/PR-AUC for imbalanced classification, RMSE/MAE for regression, ROC-AUC for balanced binary.
6. Refit the best model on the full training set. Evaluate once on the held-out test set.
7. Persist the trained pipeline and metadata for reproducibility.

## Decision tree

- If classification + imbalanced classes → use `class_weight='balanced'` or SMOTE, report F1/PR-AUC not accuracy.
- If regression + outliers → prefer MAE over MSE, consider robust scalers.
- If < 1000 samples → prefer simpler models (LogisticRegression, Ridge) before tree ensembles.
- If > 50 features → apply feature selection inside the pipeline (SelectKBest or model-based).
- If temporal data → use `TimeSeriesSplit`, never `StratifiedKFold`.
- If multi-class → use `classification_report`, check per-class F1, not just macro.

## Anti-patterns

- NEVER fit a scaler or encoder on the full dataset before splitting. This leaks test information into training. Always fit preprocessing inside the Pipeline.
- NEVER report train-set metrics as model performance.
- NEVER use `accuracy` as the primary metric for imbalanced datasets.
- NEVER tune hyperparameters on the test set. Use a separate validation fold or nested CV.
- NEVER ignore cross-validation variance. A model with 0.92 +/- 0.15 is unreliable.

## Common mistakes

- Fitting `StandardScaler` outside the Pipeline, causing data leakage.
- Using `train_test_split` with `shuffle=True` on time series data.
- Forgetting to set `random_state` on both the splitter and the estimator.
- Comparing models with different CV fold assignments.
- Not checking for NaN in the target variable before fitting.
- Using `GridSearchCV` with too many combinations (prefer `RandomizedSearchCV` or Optuna).

## Output contract

- Include selected features and preprocessing steps in artifact metadata.
- Report confidence intervals or fold variance for key metrics.
- Provide confusion matrix for classification or residual plot for regression.
- Log library version (`sklearn.__version__`) in the output metadata.
- Never claim performance from train-only evaluation.

## Composability hints

- Before this expert → `data.schema-normalization` for clean input data.
- After this expert → `ml.model-export` for persistence and deployment.
- Related → `ml.hyperparameter-tuning` for advanced search strategies.
- Related → `ml.feature-engineering` for feature creation before modeling.
```

**Step 2: Enrich visualization-matplotlib-seaborn.md**

Replace with expanded version (same pattern — when to use, decision tree, anti-patterns, common mistakes, composability hints). Target: 60-80 lines.

**Step 3: Repeat for all remaining 13 instruction files**

Each file follows the same expansion pattern. Files to enrich:
- `gradient-boosting-xgb-lgbm.md`
- `pytorch-training.md`
- `statistics-scipy-statsmodels.md`
- `scipy-optimization-signal.md`
- `chemistry-rdkit.md`
- `graph-networkx.md`
- `opencv-image-processing.md`
- `geospatial-geopandas.md`
- `nlp-spacy-transformers.md`
- `pdf-creation.md`
- `slide-creation.md`
- `data-cleaning.md`
- `machine-learning-export.md`

**Step 4: Run all tests to ensure nothing breaks**

Run: `pytest -v`
Expected: All tests PASS (instruction content changes don't break retrieval accuracy)

**Step 5: Commit**

```bash
git add examples/registry/instructions/
git commit -m "content: enrich all 15 instruction files with anti-patterns, decision trees, and composability hints"
```

---

## Phase 5: Add New Expert Domains

This phase adds ~45 new expert cards with instruction files. Split into batches by domain group to keep commits focused.

### Task 7: Add Cloud + Infrastructure experts (7 experts)

**Files:**
- Create: 7 new instruction files in `examples/registry/instructions/`
- Modify: `examples/registry/experts.yaml` (append 7 entries)
- Modify: `examples/registry/tools.enriched.json` (append 7 entries)
- Modify: `tests/test_registry.py` (update count assertions)
- Modify: `tests/test_retriever.py` (add retrieval accuracy tests)

**Step 1: Create instruction files**

Create the following 7 files in `examples/registry/instructions/`:

- `aws-s3.md` (~70 lines) — bucket ops, lifecycle policies, presigned URLs, versioning, encryption, cross-region replication. Anti-patterns: public buckets, no lifecycle rules, hardcoded credentials.
- `aws-lambda.md` (~70 lines) — handler patterns, cold start optimization, layers, environment variables, timeouts, memory tuning, VPC considerations. Anti-patterns: monolithic handlers, no dead letter queue, storing state in /tmp.
- `aws-vpc.md` (~70 lines) — subnet design, security groups, NACLs, NAT gateways, VPC peering, flow logs. Anti-patterns: 0.0.0.0/0 ingress, single AZ, no flow logs.
- `terraform.md` (~70 lines) — state management, module structure, plan-before-apply, drift detection, workspaces. Anti-patterns: local state in production, no locking, wildcard providers.
- `docker.md` (~70 lines) — multi-stage builds, layer caching, non-root users, .dockerignore, health checks, image scanning. Anti-patterns: latest tag, root user, secrets in build args.
- `kubernetes.md` (~70 lines) — deployments, services, RBAC, resource limits, liveness/readiness probes, HPA, namespaces. Anti-patterns: no resource limits, privileged containers, default namespace.
- `github-actions.md` (~70 lines) — workflow triggers, job matrices, caching, secrets, artifact upload, reusable workflows. Anti-patterns: unpinned actions, secrets in logs, no caching.

**Step 2: Add entries to experts.yaml**

Append 7 entries following the existing format. Example for one:

```yaml
  - id: cloud.aws-s3
    title: AWS S3 Bucket Operations
    domain: cloud_infrastructure
    instruction_file: instructions/aws-s3.md
    description: Retrieve this expert for S3 bucket creation, lifecycle policies, presigned URLs, and secure object storage patterns.
    tags:
      - aws
      - s3
      - bucket
      - storage
      - lifecycle
      - presigned-url
      - encryption
    tool_hints:
      - aws s3
      - aws s3api
      - boto3.client('s3')
    examples:
      - Create versioned S3 bucket with lifecycle rules and encryption
      - Generate presigned URL for secure temporary file access
```

**Step 3: Add entries to tools.enriched.json**

Add corresponding entries with full enriched metadata (dependencies, input_contract, output_artifacts, quality_checks, constraints, risk_level, maturity, metadata).

**Step 4: Update test_registry.py count assertion**

Change `assert len(cards) == 15` to `assert len(cards) == 22` (15 + 7).

**Step 5: Add retrieval accuracy tests**

Add to `tests/test_retriever.py`:

```python
def test_retriever_aws_s3_query():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("create s3 bucket with lifecycle and presigned urls", top_k=2)
    assert hits[0].card.id == "cloud.aws-s3"


def test_retriever_kubernetes_query():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("kubernetes deployment with rbac and resource limits", top_k=2)
    assert hits[0].card.id == "cloud.kubernetes"


def test_retriever_terraform_query():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("terraform state management modules and drift detection", top_k=2)
    assert hits[0].card.id == "cloud.terraform"
```

**Step 6: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add examples/registry/ tests/
git commit -m "feat: add 7 cloud + infrastructure expert domains"
```

---

### Task 8: Add APIs + Web experts (6 experts)

**Files:** Same pattern as Task 7.

New experts:
- `web.fastapi` — async endpoints, dependency injection, Pydantic models, middleware, CORS, background tasks
- `web.flask` — blueprints, app factory, extensions, context locals, error handlers
- `web.auth-jwt` — JWT issuance/validation, refresh tokens, RBAC claims, token revocation
- `web.auth-oauth` — OAuth2 authorization code, PKCE, token exchange, scope management
- `web.sqlalchemy` — session lifecycle, relationship loading, migrations (Alembic), connection pooling
- `web.rest-design` — resource naming, HTTP methods, pagination, filtering, error responses, versioning

New instruction files: 6 files, 60-80 lines each.
Update experts.yaml count to 28, add 6 retriever tests.

**Commit:** `feat: add 6 API + web expert domains`

---

### Task 9: Add Data + Finance experts (7 experts)

New experts:
- `data.pandas-advanced` — groupby, merge/join strategies, memory optimization, categorical dtype, vectorized ops
- `data.sql-queries` — joins, CTEs, window functions, query planning, index usage, EXPLAIN
- `data.time-series` — stationarity testing, decomposition, ARIMA, Prophet, cross-validation for time series
- `finance.quantitative` — portfolio optimization, VaR, Sharpe ratio, backtesting, risk attribution
- `finance.financial-modeling` — DCF, comparable multiples, scenario analysis, sensitivity tables
- `data.spark` — partitioning, broadcast joins, UDFs, caching, Spark SQL, memory tuning
- `data.dbt` — model layering (staging/intermediate/marts), tests, incremental models, macros

Update experts.yaml count to 35, add retriever tests.

**Commit:** `feat: add 7 data + finance expert domains`

---

### Task 10: Add Security + DevSecOps experts (6 experts)

New experts:
- `sec.owasp-web` — XSS prevention, CSRF tokens, SQLi parameterization, SSRF, broken auth
- `sec.secrets-management` — Vault, environment variables, rotation policies, never-hardcode
- `sec.container-security` — image scanning, rootless containers, distroless, seccomp, network policies
- `sec.dependency-scanning` — SCA tools, CVE triage, lockfile auditing, supply chain security
- `sec.iam-policies` — least privilege, policy boundaries, condition keys, audit logging
- `sec.penetration-testing` — methodology (recon/scan/exploit/report), scope definition, authorized context only

Update experts.yaml count to 41, add retriever tests.

**Commit:** `feat: add 6 security + DevSecOps expert domains`

---

### Task 11: Add Frontend + Mobile experts (6 experts)

New experts:
- `fe.react` — hooks patterns, component composition, memo/callback, suspense, error boundaries
- `fe.nextjs` — app router, server components, data fetching, middleware, ISR, metadata
- `fe.react-native` — navigation (React Navigation), native modules, platform-specific code, Expo
- `fe.css-architecture` — Tailwind utility patterns, CSS modules, design tokens, responsive breakpoints
- `fe.accessibility` — WCAG 2.1 AA, ARIA roles, keyboard navigation, screen reader testing, focus management
- `fe.state-management` — Redux Toolkit vs Zustand vs Context, server state (TanStack Query), state shape

Update experts.yaml count to 47, add retriever tests.

**Commit:** `feat: add 6 frontend + mobile expert domains`

---

### Task 12: Add Systems + Low-level experts (6 experts)

New experts:
- `sys.rust` — ownership, lifetimes, borrowing, error handling (Result/Option), async with tokio
- `sys.go` — goroutines, channels, select, error wrapping, interfaces, context propagation
- `sys.cpp-modern` — smart pointers, RAII, move semantics, templates, constexpr, ranges
- `sys.concurrency` — mutexes, lock-free structures, async patterns, deadlock prevention, thread pools
- `sys.systems-design` — load balancing, caching layers, sharding, CAP theorem, consistency models
- `sys.memory-management` — profiling (valgrind, heaptrack), leak detection, allocation strategies, arena allocators

Update experts.yaml count to 53, add retriever tests.

**Commit:** `feat: add 6 systems + low-level expert domains`

---

### Task 13: Add additional ML/DL experts (4 experts)

New experts:
- `ml.feature-engineering` — encoding strategies, interaction features, target encoding, feature stores
- `ml.hyperparameter-tuning` — Optuna, Bayesian optimization, cross-validation strategy, early pruning
- `dl.transformers-finetuning` — HuggingFace Trainer, LoRA/QLoRA, dataset preparation, evaluation
- `dl.langchain-agents` — chains, agents, memory types, tool use, RAG patterns

Update experts.yaml count to 57, add retriever tests.

**Commit:** `feat: add 4 additional ML/DL expert domains`

---

## Phase 6: Update Registry and Final Tests

### Task 14: Update schema.json and tools.enriched.json for all new experts

**Files:**
- Modify: `examples/registry/schema.json` (no changes needed if schema is already flexible)
- Modify: `examples/registry/tools.enriched.json` (add all ~42 new enriched entries)

**Step 1: Verify schema accommodates new domains**

Read `schema.json` — it uses `additionalProperties: true`, so new domain values are fine. No schema changes needed.

**Step 2: Add all new experts to tools.enriched.json**

Each new expert gets the full enriched format with: id, title, domain, instruction_file, description, tags, tool_hints, examples, aliases, dependencies, input_contract, output_artifacts, quality_checks, constraints, risk_level, maturity, metadata.

**Step 3: Update version**

Change `"version": "0.3.0"` to `"version": "2.0.0"` in tools.enriched.json.

**Step 4: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add examples/registry/tools.enriched.json
git commit -m "feat: complete v2 enriched JSON registry with all 57 experts"
```

---

### Task 15: Update README.md and pyproject.toml version

**Files:**
- Modify: `README.md` (update for v2 features: ChromaDB backend, index command, expert count)
- Modify: `pyproject.toml` (bump version to 2.0.0, update description)

**Step 1: Update pyproject.toml**

Change `version = "0.1.0"` to `version = "2.0.0"`.
Update description to mention ChromaDB and scale.

**Step 2: Update README.md**

- Update project description to mention ChromaDB-backed retrieval
- Add `skill-rag index` documentation
- Add `--backend` flag documentation
- Update expert count from 15 to ~57
- Update install instructions to mention chromadb dependency
- Complete branding references migration to SkillMesh

**Step 3: Final full test run**

Run: `pytest -v`
Expected: All tests PASS

Run: `ruff check src tests`
Expected: No lint errors

**Step 4: Commit**

```bash
git add README.md pyproject.toml
git commit -m "docs: update README and version for v2 release"
```

---

## Summary

| Phase | Tasks | New Files | Experts |
|-------|-------|-----------|---------|
| 1: Backend abstraction | 1-2 | 3 | 0 |
| 2: ChromaDB backend | 3-4 | 1 | 0 |
| 3: CLI updates | 5 | 0 | 0 |
| 4: Enrich existing | 6 | 0 | 0 (15 enriched) |
| 5: New domains | 7-13 | ~42 .md files | +42 new |
| 6: Registry + docs | 14-15 | 0 | 0 |
| **Total** | **15 tasks** | **~46 new files** | **~57 experts** |
