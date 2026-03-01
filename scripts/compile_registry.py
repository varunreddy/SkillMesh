#!/usr/bin/env python3
"""Compile examples/registry/tools.json into a self-contained JSON with inlined instruction_text.

Output: src/skill_registry_rag/data/tools.compiled.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "examples" / "registry" / "tools.json"
DEST = REPO_ROOT / "src" / "skill_registry_rag" / "data" / "tools.compiled.json"


def compile_registry() -> None:
    if not SOURCE.exists():
        print(f"Source registry not found: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    tools = raw.get("tools", [])
    root = SOURCE.parent

    for entry in tools:
        instruction_file = entry.get("instruction_file", "")
        if not instruction_file:
            continue
        instruction_path = (root / instruction_file).resolve()
        if not instruction_path.exists():
            print(
                f"WARNING: instruction file missing for '{entry.get('id')}': {instruction_path}",
                file=sys.stderr,
            )
            entry["instruction_text"] = ""
            continue
        entry["instruction_text"] = instruction_path.read_text(encoding="utf-8").strip()

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Compiled {len(tools)} tools -> {DEST}")


if __name__ == "__main__":
    compile_registry()
