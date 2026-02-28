from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout

from skill_registry_rag.cli import main


def test_cli_retrieve_emits_enriched_fields():
    root = Path(__file__).resolve().parents[1]
    registry = root / "examples" / "registry" / "tools.json"

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "retrieve",
                "--registry",
                str(registry),
                "--query",
                "opencv contour detection",
                "--top-k",
                "1",
            ]
        )

    assert code == 0
    payload = json.loads(buf.getvalue())
    hit = payload["hits"][0]
    assert hit["id"] == "cv.opencv-image-processing"
    assert "dependencies" in hit
    assert "risk_level" in hit
    assert "metadata" in hit


def test_cli_index_creates_collection():
    root = Path(__file__).resolve().parents[1]
    registry = root / "examples" / "registry" / "tools.json"

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "index",
                "--registry",
                str(registry),
                "--ephemeral",
            ]
        )

    assert code == 0
    output = buf.getvalue()
    assert "Indexed" in output


def test_cli_retrieve_with_backend_flag():
    root = Path(__file__).resolve().parents[1]
    registry = root / "examples" / "registry" / "tools.json"

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "retrieve",
                "--registry",
                str(registry),
                "--query",
                "opencv contour detection",
                "--top-k",
                "1",
                "--backend",
                "memory",
            ]
        )

    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["hits"][0]["id"] == "cv.opencv-image-processing"


def test_cli_retrieve_security_expert():
    root = Path(__file__).resolve().parents[1]
    registry = root / "examples" / "registry" / "tools.json"

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "retrieve",
                "--registry",
                str(registry),
                "--query",
                "owasp xss csrf sql injection mitigation",
                "--top-k",
                "1",
                "--backend",
                "memory",
            ]
        )

    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["hits"][0]["id"] == "sec.owasp-web"
