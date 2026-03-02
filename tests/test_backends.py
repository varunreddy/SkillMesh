from __future__ import annotations

from pathlib import Path

import numpy as np

from skill_registry_rag.backends import RetrievalBackend
from skill_registry_rag.backends.chroma import ChromaBackend
from skill_registry_rag.backends.memory import InMemoryBackend
from skill_registry_rag.models import ToolCard
from skill_registry_rag.registry import load_registry


def _load_cards():
    root = Path(__file__).resolve().parents[1]
    return load_registry(root / "examples" / "registry" / "tools.yaml")


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


def test_chroma_backend_implements_protocol():
    backend = ChromaBackend(ephemeral=True)
    assert isinstance(backend, RetrievalBackend)


def test_chroma_backend_index_and_query():
    cards = _load_cards()
    backend = ChromaBackend(ephemeral=True)
    backend.index(cards)
    hits = backend.query("build matplotlib seaborn heatmap", top_k=2)
    assert len(hits) == 2
    assert hits[0].card.id == "viz.matplotlib-seaborn"


def test_chroma_backend_empty_cards():
    backend = ChromaBackend(ephemeral=True)
    backend.index([])
    hits = backend.query("anything", top_k=3)
    assert hits == []


def test_chroma_backend_sklearn_query():
    cards = _load_cards()
    backend = ChromaBackend(ephemeral=True)
    backend.index(cards)
    hits = backend.query("sklearn pipeline cross validation metrics", top_k=1)
    assert hits[0].card.id == "ml.sklearn-modeling"


def test_chroma_backend_pytorch_query():
    cards = _load_cards()
    backend = ChromaBackend(ephemeral=True)
    backend.index(cards)
    hits = backend.query("pytorch training loop cuda mixed precision checkpoint", top_k=1)
    assert hits[0].card.id == "dl.pytorch-training"


def test_chroma_backend_dense_false_is_sparse_only():
    cards = _load_cards()
    backend = ChromaBackend(use_dense=False)
    backend.index(cards)

    # Dense mode is disabled, so Chroma collection is never built.
    assert backend._collection is None
    hits = backend.query("build matplotlib seaborn heatmap", top_k=2)
    assert len(hits) == 2
    assert all(hit.dense_score is None for hit in hits)


def test_chroma_backend_weighted_hybrid_affects_rank_order(monkeypatch):
    cards = [
        ToolCard(
            id="card.sparse",
            title="Sparse Winner",
            domain="test",
            instruction_file="n/a",
        ),
        ToolCard(
            id="card.dense",
            title="Dense Winner",
            domain="test",
            instruction_file="n/a",
        ),
    ]

    class StubCollection:
        def query(self, query_texts, n_results):  # noqa: ANN001
            return {
                "ids": [["card.dense", "card.sparse"]],
                "distances": [[0.0, 0.2]],  # dense: card.dense > card.sparse
            }

    sparse_scores = np.asarray([1.0, 0.0], dtype=np.float32)  # sparse: card.sparse > card.dense

    sparse_heavy = ChromaBackend(use_dense=False, sparse_weight=0.8, dense_weight=0.2)
    sparse_heavy._cards = cards
    sparse_heavy._use_dense = True
    sparse_heavy._collection = StubCollection()
    monkeypatch.setattr(sparse_heavy, "_sparse_scores", lambda _: sparse_scores)
    sparse_hits = sparse_heavy.query("any", top_k=1)
    assert sparse_hits[0].card.id == "card.sparse"

    dense_heavy = ChromaBackend(use_dense=False, sparse_weight=0.3, dense_weight=0.7)
    dense_heavy._cards = cards
    dense_heavy._use_dense = True
    dense_heavy._collection = StubCollection()
    monkeypatch.setattr(dense_heavy, "_sparse_scores", lambda _: sparse_scores)
    dense_hits = dense_heavy.query("any", top_k=1)
    assert dense_hits[0].card.id == "card.dense"
