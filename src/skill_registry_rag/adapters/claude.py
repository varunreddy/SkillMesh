from __future__ import annotations

from ..models import RetrievalHit


def _trim(text: str, n: int) -> str:
    txt = str(text or "").strip()
    if len(txt) <= n:
        return txt
    return txt[:n].rstrip() + " ..."


def render_claude_context(query: str, hits: list[RetrievalHit], *, instruction_chars: int = 700) -> str:
    lines: list[str] = []
    lines.append("<retrieved_cards>")
    lines.append(f"  <query>{query}</query>")
    for hit in hits:
        c = hit.card
        lines.append("  <card>")
        lines.append(f"    <id>{c.id}</id>")
        lines.append(f"    <title>{c.title}</title>")
        lines.append(f"    <domain>{c.domain}</domain>")
        lines.append(f"    <score>{hit.score:.4f}</score>")
        lines.append(f"    <description>{_trim(c.description, 260)}</description>")
        if c.tags:
            lines.append(f"    <tags>{', '.join(c.tags[:12])}</tags>")
        if c.tool_hints:
            lines.append(f"    <tool_hints>{', '.join(c.tool_hints[:8])}</tool_hints>")
        if c.dependencies:
            lines.append(f"    <dependencies>{', '.join(c.dependencies[:8])}</dependencies>")
        if c.risk_level:
            lines.append(f"    <risk_level>{c.risk_level}</risk_level>")
        if c.output_artifacts:
            lines.append(f"    <output_artifacts>{', '.join(c.output_artifacts[:6])}</output_artifacts>")
        lines.append("    <instructions>")
        lines.append(_trim(c.instruction_text, instruction_chars))
        lines.append("    </instructions>")
        lines.append("  </card>")
    lines.append("</retrieved_cards>")
    return "\n".join(lines) + "\n"
