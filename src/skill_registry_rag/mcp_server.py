from __future__ import annotations

import os
import sys
from typing import Any

from ._resolve import resolve_registry_path
from .adapters import render_claude_context, render_codex_context
from .registry import RegistryError, load_registry
from .retriever import SkillRetriever

_VALID_PROVIDERS = {"claude", "codex"}
_VALID_BACKENDS = {"auto", "memory", "chroma"}


def _normalize_query(query: str) -> str:
    normalized = str(query or "").strip()
    if not normalized:
        raise ValueError("`query` must be a non-empty string.")
    return normalized


def _normalize_top_k(top_k: int) -> int:
    if int(top_k) < 1:
        raise ValueError("`top_k` must be >= 1.")
    return int(top_k)


def _normalize_provider(provider: str) -> str:
    normalized = str(provider or "").strip().lower()
    if normalized not in _VALID_PROVIDERS:
        raise ValueError("`provider` must be one of: claude, codex.")
    return normalized


def _normalize_backend(backend: str) -> str:
    normalized = str(backend or "auto").strip().lower()
    if normalized not in _VALID_BACKENDS:
        raise ValueError("`backend` must be one of: auto, memory, chroma.")
    return normalized


def _retrieve_hits(
    *,
    query: str,
    registry: str | None,
    top_k: int,
    backend: str,
    dense: bool,
):
    resolved_query = _normalize_query(query)
    resolved_top_k = _normalize_top_k(top_k)
    resolved_backend = _normalize_backend(backend)
    registry_path = resolve_registry_path(registry)

    try:
        cards = load_registry(registry_path)
    except RegistryError as exc:
        raise ValueError(f"Invalid registry: {exc}") from exc

    retriever = SkillRetriever(
        cards,
        use_dense=bool(dense),
        backend=resolved_backend,
    )
    hits = retriever.retrieve(resolved_query, top_k=resolved_top_k)
    return resolved_query, registry_path, hits


def retrieve_cards_payload(
    *,
    query: str,
    registry: str | None = None,
    top_k: int = 5,
    backend: str = "auto",
    dense: bool = False,
) -> dict[str, Any]:
    resolved_query, registry_path, hits = _retrieve_hits(
        query=query,
        registry=registry,
        top_k=top_k,
        backend=backend,
        dense=dense,
    )
    payload_hits: list[dict[str, Any]] = []
    for hit in hits:
        payload_hits.append(
            {
                "id": hit.card.id,
                "title": hit.card.title,
                "domain": hit.card.domain,
                "description": hit.card.description,
                "tags": hit.card.tags,
                "tool_hints": hit.card.tool_hints,
                "aliases": hit.card.aliases,
                "dependencies": hit.card.dependencies,
                "input_contract": hit.card.input_contract,
                "output_artifacts": hit.card.output_artifacts,
                "quality_checks": hit.card.quality_checks,
                "constraints": hit.card.constraints,
                "risk_level": hit.card.risk_level,
                "maturity": hit.card.maturity,
                "metadata": hit.card.metadata,
                "score": hit.score,
                "sparse_score": hit.sparse_score,
                "dense_score": hit.dense_score,
            }
        )

    return {
        "query": resolved_query,
        "registry": str(registry_path),
        "hits": payload_hits,
    }


def build_routed_context(
    *,
    query: str,
    registry: str | None = None,
    top_k: int = 5,
    backend: str = "auto",
    dense: bool = False,
    provider: str = "claude",
    instruction_chars: int = 700,
) -> str:
    resolved_provider = _normalize_provider(provider)
    resolved_instruction_chars = int(instruction_chars)
    if resolved_instruction_chars < 100:
        raise ValueError("`instruction_chars` must be >= 100.")

    resolved_query, _, hits = _retrieve_hits(
        query=query,
        registry=registry,
        top_k=top_k,
        backend=backend,
        dense=dense,
    )

    if resolved_provider == "codex":
        return render_codex_context(
            resolved_query,
            hits,
            instruction_chars=resolved_instruction_chars,
        )
    return render_claude_context(
        resolved_query,
        hits,
        instruction_chars=resolved_instruction_chars,
    )


def create_mcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("skillmesh")

    @mcp.tool()
    def route_with_skillmesh(
        query: str,
        top_k: int = 5,
        registry: str | None = None,
        backend: str = "auto",
        dense: bool = False,
        provider: str = "claude",
        instruction_chars: int = 700,
    ) -> str:
        """Return a routed context block for Claude/Codex from top-K SkillMesh cards."""
        return build_routed_context(
            query=query,
            registry=registry,
            top_k=top_k,
            backend=backend,
            dense=dense,
            provider=provider,
            instruction_chars=instruction_chars,
        )

    @mcp.tool()
    def retrieve_skillmesh_cards(
        query: str,
        top_k: int = 5,
        registry: str | None = None,
        backend: str = "auto",
        dense: bool = False,
    ) -> dict[str, Any]:
        """Return top-K SkillMesh cards as structured JSON payload."""
        return retrieve_cards_payload(
            query=query,
            registry=registry,
            top_k=top_k,
            backend=backend,
            dense=dense,
        )

    return mcp


def main() -> int:
    try:
        server = create_mcp_server()
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith("mcp"):
            print(
                "Missing MCP dependency. Install with: pip install -e .[mcp]",
                file=sys.stderr,
            )
            return 2
        raise

    transport = os.getenv("SKILLMESH_MCP_TRANSPORT", "stdio").strip() or "stdio"
    server.run(transport=transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
