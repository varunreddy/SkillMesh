from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from ._resolve import resolve_registry_path
from .adapters import render_claude_context, render_codex_context
from .roles import (
    RoleCatalogError,
    friendly_role_name,
    install_role_bundle,
    list_role_offers,
    resolve_role_selector,
)
from .registry import RegistryError, load_registry
from .retriever import SkillRetriever

_VALID_PROVIDERS = {"claude", "codex"}
_VALID_BACKENDS = {"auto", "memory", "chroma"}


def _default_role_catalog_path() -> Path:
    env_catalog = os.getenv("SKILLMESH_CATALOG", "").strip()
    if env_catalog:
        candidate = Path(env_catalog).expanduser().resolve()
        if not candidate.exists():
            raise ValueError(f"SKILLMESH_CATALOG points to a missing file: {candidate}")
        return candidate
    return resolve_registry_path(None)


def _default_role_registry_path() -> Path:
    role_registry = os.getenv("SKILLMESH_ROLE_REGISTRY", "").strip()
    if role_registry:
        return Path(role_registry).expanduser().resolve()
    env_registry = os.getenv("SKILLMESH_REGISTRY", "").strip()
    if env_registry:
        return Path(env_registry).expanduser().resolve()
    return (Path.home() / ".codex" / "skills" / "skillmesh" / "installed.registry.yaml").resolve()


def _resolve_role_catalog_path(catalog: str | None) -> Path:
    if catalog and catalog.strip():
        candidate = Path(catalog).expanduser().resolve()
        if not candidate.exists():
            raise ValueError(f"Catalog not found: {candidate}")
        return candidate
    return _default_role_catalog_path()


def _resolve_role_registry_path(registry: str | None) -> Path:
    if registry and registry.strip():
        return Path(registry).expanduser().resolve()
    return _default_role_registry_path()


def _role_offer_payload(offer: dict[str, Any]) -> dict[str, Any]:
    role_id = str(offer["id"])
    out = dict(offer)
    out["name"] = friendly_role_name(role_id)
    return out


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
    normalized = str(backend or "chroma").strip().lower()
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
    backend: str = "chroma",
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
                "invocation": hit.card.invocation,
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
    backend: str = "chroma",
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


def list_roles_payload(
    *,
    catalog: str | None = None,
    registry: str | None = None,
    installed_only: bool = False,
) -> dict[str, Any]:
    catalog_path = _resolve_role_catalog_path(catalog)
    registry_path = _resolve_role_registry_path(registry)
    try:
        offers = list_role_offers(
            catalog_registry=str(catalog_path),
            installed_registry=str(registry_path),
        )
    except RoleCatalogError as exc:
        raise ValueError(str(exc)) from exc
    if installed_only:
        offers = [offer for offer in offers if bool(offer["installed"])]

    return {
        "catalog": str(catalog_path),
        "registry": str(registry_path),
        "installed_only": bool(installed_only),
        "roles": [_role_offer_payload(offer) for offer in offers],
    }


def install_role_payload(
    *,
    role: str,
    catalog: str | None = None,
    registry: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    catalog_path = _resolve_role_catalog_path(catalog)
    registry_path = _resolve_role_registry_path(registry)
    try:
        offers = list_role_offers(catalog_registry=str(catalog_path))
        resolved_role_id = resolve_role_selector(role, offers)
        result = install_role_bundle(
            catalog_registry=str(catalog_path),
            target_registry=str(registry_path),
            role_id=resolved_role_id,
            dry_run=bool(dry_run),
        )
    except RoleCatalogError as exc:
        raise ValueError(str(exc)) from exc
    result["role_name"] = friendly_role_name(resolved_role_id)
    return result


def create_mcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("skillmesh")

    @mcp.tool()
    def route_with_skillmesh(
        query: str,
        top_k: int = 5,
        registry: str | None = None,
        backend: str = "chroma",
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
        backend: str = "chroma",
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

    @mcp.tool()
    def list_skillmesh_roles(
        catalog: str | None = None,
        registry: str | None = None,
    ) -> dict[str, Any]:
        """Return all available SkillMesh roles with installed status."""
        return list_roles_payload(
            catalog=catalog,
            registry=registry,
            installed_only=False,
        )

    @mcp.tool()
    def list_installed_skillmesh_roles(
        catalog: str | None = None,
        registry: str | None = None,
    ) -> dict[str, Any]:
        """Return only installed SkillMesh roles."""
        return list_roles_payload(
            catalog=catalog,
            registry=registry,
            installed_only=True,
        )

    @mcp.tool()
    def install_skillmesh_role(
        role: str,
        catalog: str | None = None,
        registry: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Install a SkillMesh role bundle by id or friendly name."""
        return install_role_payload(
            role=role,
            catalog=catalog,
            registry=registry,
            dry_run=dry_run,
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
