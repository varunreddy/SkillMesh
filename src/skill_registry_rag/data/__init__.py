from __future__ import annotations

from pathlib import Path


def bundled_registry_path() -> Path:
    """Return the path to the compiled registry bundled with this package."""
    return Path(__file__).parent / "tools.compiled.json"
