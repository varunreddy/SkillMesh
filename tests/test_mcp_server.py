from __future__ import annotations

from pathlib import Path

import pytest

from skill_registry_rag.mcp_server import build_routed_context, retrieve_cards_payload


def _example_registry() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "registry" / "tools.json"


def test_retrieve_cards_payload_for_known_query():
    payload = retrieve_cards_payload(
        query="opencv contour detection",
        registry=str(_example_registry()),
        top_k=1,
        backend="memory",
    )

    assert payload["hits"]
    assert payload["hits"][0]["id"] == "cv.opencv-image-processing"


def test_build_routed_context_claude_format():
    context = build_routed_context(
        query="opencv contour detection",
        registry=str(_example_registry()),
        top_k=1,
        backend="memory",
        provider="claude",
    )

    assert "<retrieved_cards>" in context
    assert "<id>cv.opencv-image-processing</id>" in context


def test_retrieve_uses_registry_env_when_not_passed(monkeypatch):
    registry = _example_registry().resolve()
    monkeypatch.setenv("SKILLMESH_REGISTRY", str(registry))

    payload = retrieve_cards_payload(
        query="opencv contour detection",
        top_k=1,
        backend="memory",
    )

    assert payload["registry"] == str(registry)


def test_build_routed_context_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        build_routed_context(
            query="opencv contour detection",
            registry=str(_example_registry()),
            top_k=0,
            backend="memory",
            provider="claude",
        )
