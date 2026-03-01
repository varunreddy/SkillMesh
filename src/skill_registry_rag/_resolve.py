"""Shared registry-path resolution used by both CLI and MCP server."""

from __future__ import annotations

import os
from pathlib import Path


def _find_repo_root() -> Path | None:
    here = Path(__file__).resolve()
    markers = ("src/skill_registry_rag/__main__.py", "examples/registry/tools.json")
    for candidate in [here.parent, *here.parents]:
        if all((candidate / marker).exists() for marker in markers):
            return candidate
    return None


def _default_registry_path() -> Path | None:
    # 1. Env var
    env_path = os.getenv("SKILLMESH_REGISTRY", "").strip()
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        if not candidate.exists():
            raise ValueError(
                f"SKILLMESH_REGISTRY points to a missing file: {candidate}"
            )
        return candidate

    # 2. Repo root
    repo_root = _find_repo_root()
    if repo_root is not None:
        candidate = (repo_root / "examples" / "registry" / "tools.json").resolve()
        if candidate.exists():
            return candidate

    # 3. Bundled compiled registry
    from .data import bundled_registry_path

    bundled = bundled_registry_path()
    return bundled if bundled.exists() else None


def resolve_registry_path(registry: str | None = None) -> Path:
    """Resolve a registry path from explicit argument, env var, repo root, or bundled fallback."""
    if registry and registry.strip():
        candidate = Path(registry).expanduser().resolve()
        if not candidate.exists():
            raise ValueError(f"Registry not found: {candidate}")
        return candidate

    default = _default_registry_path()
    if default is None:
        raise ValueError(
            "Missing registry path. Provide --registry, set SKILLMESH_REGISTRY, "
            "or install skillmesh[mcp] for the bundled registry."
        )
    return default
