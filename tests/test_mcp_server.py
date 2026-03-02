from __future__ import annotations

from pathlib import Path

import pytest

from skill_registry_rag.mcp_server import (
    build_routed_context,
    install_role_payload,
    list_roles_payload,
    retrieve_cards_payload,
)


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
    assert "invocation" in payload["hits"][0]


def test_retrieve_cards_payload_includes_invocation_details():
    payload = retrieve_cards_payload(
        query="sklearn cross validation pipeline",
        registry=str(_example_registry()),
        top_k=1,
        backend="memory",
    )

    assert payload["hits"]
    hit = payload["hits"][0]
    assert hit["id"] == "ml.sklearn-modeling"
    assert hit["invocation"]["type"] == "function"
    assert hit["invocation"]["function"]["name"] == "sklearn_model_selection_cross_validate"


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


def test_list_roles_payload_returns_friendly_names():
    payload = list_roles_payload(catalog=str(_example_registry()))
    assert payload["roles"]
    first = payload["roles"][0]
    assert "name" in first


def test_install_role_payload_accepts_friendly_name(tmp_path):
    target = tmp_path / "mcp-installed.registry.yaml"
    payload = install_role_payload(
        role="Data-Analyst",
        catalog=str(_example_registry()),
        registry=str(target),
    )
    assert payload["role_id"] == "role.data-analyst"
    assert "role.data-analyst" in payload["added_ids"]


def test_list_roles_payload_installed_only(tmp_path):
    target = tmp_path / "mcp-installed-only.registry.yaml"
    install_role_payload(
        role="DevOps-Engineer",
        catalog=str(_example_registry()),
        registry=str(target),
    )
    payload = list_roles_payload(
        catalog=str(_example_registry()),
        registry=str(target),
        installed_only=True,
    )
    ids = {role["id"] for role in payload["roles"]}
    assert ids == {"role.devops-engineer"}
