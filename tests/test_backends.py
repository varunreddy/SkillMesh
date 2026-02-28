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


from skill_registry_rag.backends.chroma import ChromaBackend


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
