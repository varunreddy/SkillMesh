"""Thin facade that delegates to a retrieval backend."""

from __future__ import annotations

from .backends.memory import InMemoryBackend
from .models import ExpertCard, RetrievalHit


class SkillRetriever:
    def __init__(self, cards: list[ExpertCard], *, use_dense: bool = False, backend: str = "chroma"):
        if backend == "memory" or (backend == "auto" and len(cards) < (100 if use_dense else 1000)):
            self._backend = InMemoryBackend(use_dense=use_dense)
        else:
            try:
                from .backends.chroma import ChromaBackend
                self._backend = ChromaBackend(
                    use_dense=bool(use_dense),
                    sparse_weight=0.8,
                    dense_weight=0.2,
                    min_dense_candidates=100,
                    dense_candidates_multiplier=10,
                )
            except Exception:
                self._backend = InMemoryBackend(use_dense=use_dense)
        self._backend.index(cards)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievalHit]:
        return self._backend.query(query, top_k=top_k)
