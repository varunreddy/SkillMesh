from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class ToolCard:
    id: str
    title: str
    domain: str
    instruction_file: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    tool_hints: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    output_artifacts: list[str] = field(default_factory=list)
    quality_checks: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    input_contract: dict[str, str] = field(default_factory=dict)
    risk_level: str = ""
    maturity: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    instruction_text: str = ""


@dataclass(slots=True)
class RetrievalHit:
    card: ToolCard
    score: float
    sparse_score: float
    dense_score: Optional[float] = None


# Backward-compatible alias for older imports.
ExpertCard = ToolCard
