from __future__ import annotations

from pathlib import Path

from skill_registry_rag.adapters import render_claude_context, render_codex_context
from skill_registry_rag.registry import load_registry
from skill_registry_rag.retriever import SkillRetriever


def _get_hits():
    root = Path(__file__).resolve().parents[1]
    cards = load_registry(root / "examples" / "registry" / "tools.yaml")
    retriever = SkillRetriever(cards)
    return retriever.retrieve("create matplotlib seaborn charts", top_k=2)


def _get_json_hits():
    root = Path(__file__).resolve().parents[1]
    cards = load_registry(root / "examples" / "registry" / "tools.json")
    retriever = SkillRetriever(cards)
    return retriever.retrieve("opencv contour detection", top_k=1)


def test_codex_adapter_contains_markdown_sections():
    out = render_codex_context("create matplotlib seaborn charts", _get_hits(), instruction_chars=200)
    assert "# Retrieved SkillMesh Cards" in out
    assert "```md" in out
    assert "viz.matplotlib-seaborn" in out


def test_claude_adapter_contains_xml_tags():
    out = render_claude_context("create matplotlib seaborn charts", _get_hits(), instruction_chars=200)
    assert "<retrieved_cards>" in out
    assert "<card>" in out
    assert "viz.matplotlib-seaborn" in out


def test_adapters_render_enriched_metadata():
    hits = _get_json_hits()
    codex_out = render_codex_context("opencv contour detection", hits, instruction_chars=150)
    claude_out = render_claude_context("opencv contour detection", hits, instruction_chars=150)

    assert "Dependencies:" in codex_out
    assert "Risk level:" in codex_out
    assert "<dependencies>" in claude_out
    assert "<risk_level>" in claude_out
