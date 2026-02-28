"""Retrieval backend abstraction."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import ExpertCard, RetrievalHit


@runtime_checkable
class RetrievalBackend(Protocol):
    def index(self, cards: list[ExpertCard]) -> None: ...
    def query(self, text: str, top_k: int = 3) -> list[RetrievalHit]: ...

__all__ = ["RetrievalBackend"]
