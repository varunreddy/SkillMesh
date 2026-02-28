"""Thin facade that delegates to a retrieval backend."""

from __future__ import annotations

from .backends.memory import InMemoryBackend
from .models import ExpertCard, RetrievalHit


class SkillRetriever:
    def __init__(self, cards: list[ExpertCard], *, use_dense: bool = False, backend: str = "auto"):
        if backend == "chroma":
            from .backends.chroma import ChromaBackend
            self._backend = ChromaBackend()
        elif backend == "memory" or (backend == "auto" and len(cards) < 100):
            self._backend = InMemoryBackend(use_dense=use_dense)
        else:
            try:
                from .backends.chroma import ChromaBackend
                self._backend = ChromaBackend()
            except ImportError:
                self._backend = InMemoryBackend(use_dense=use_dense)
        self._backend.index(cards)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievalHit]:
        return self._backend.query(query, top_k=top_k)
