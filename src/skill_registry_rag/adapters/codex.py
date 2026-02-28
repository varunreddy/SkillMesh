from __future__ import annotations

from ..models import RetrievalHit


def _trim(text: str, n: int) -> str:
    txt = str(text or "").strip()
    if len(txt) <= n:
        return txt
    return txt[:n].rstrip() + " ..."


def render_codex_context(query: str, hits: list[RetrievalHit], *, instruction_chars: int = 700) -> str:
    lines: list[str] = []
    lines.append("# Retrieved SkillMesh Cards")
    lines.append(f"Query: {query}")
    lines.append("")
    for idx, hit in enumerate(hits, start=1):
        c = hit.card
        lines.append(f"## {idx}. {c.title} (`{c.id}`)")
        lines.append(f"Domain: {c.domain}")
        if c.description:
            lines.append(f"Purpose: {_trim(c.description, 260)}")
        if c.tags:
            lines.append(f"Tags: {', '.join(c.tags[:12])}")
        if c.tool_hints:
            lines.append(f"Tool hints: {', '.join(c.tool_hints[:8])}")
        if c.dependencies:
            lines.append(f"Dependencies: {', '.join(c.dependencies[:8])}")
        if c.risk_level:
            lines.append(f"Risk level: {c.risk_level}")
        if c.output_artifacts:
            lines.append(f"Output artifacts: {', '.join(c.output_artifacts[:6])}")
        lines.append(f"Score: {hit.score:.4f}")
        lines.append("Instructions:")
        lines.append("```md")
        lines.append(_trim(c.instruction_text, instruction_chars))
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
