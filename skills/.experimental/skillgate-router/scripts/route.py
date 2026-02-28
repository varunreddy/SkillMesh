#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def _default_registry() -> str:
    env = os.getenv("SKILLGATE_REGISTRY", "").strip()
    if env:
        return env

    # Best-effort local default for repository usage.
    repo_root = Path(__file__).resolve().parents[4]
    candidate = repo_root / "examples" / "registry" / "tools.enriched.json"
    if candidate.exists():
        return str(candidate)
    return ""


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skillgate-route",
        description="Emit top-k SkillGate context for Codex/Claude.",
    )
    p.add_argument("--provider", default="codex", choices=["codex", "claude"])
    p.add_argument("--registry", default=_default_registry())
    p.add_argument("--top-k", default="5")
    p.add_argument("--query", default="")
    p.add_argument("query_positional", nargs="*")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    query = (args.query or " ".join(args.query_positional)).strip()
    if not query:
        print("Error: Provide a query via --query or positional text.", file=sys.stderr)
        return 2

    registry = str(args.registry or "").strip()
    if not registry:
        print(
            "Error: Missing registry path. Pass --registry or set SKILLGATE_REGISTRY.",
            file=sys.stderr,
        )
        return 2

    cmd = [
        "skill-rag",
        "emit",
        "--provider",
        args.provider,
        "--registry",
        registry,
        "--query",
        query,
        "--top-k",
        str(args.top_k),
    ]

    # Fallback to module invocation when CLI script is not on PATH.
    env = os.environ.copy()
    if shutil.which("skill-rag") is None:
        repo_root = Path(__file__).resolve().parents[4]
        src_path = repo_root / "src"
        if src_path.exists():
            env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")
        cmd = [
            sys.executable,
            "-m",
            "skill_registry_rag",
            "emit",
            "--provider",
            args.provider,
            "--registry",
            registry,
            "--query",
            query,
            "--top-k",
            str(args.top_k),
        ]

    try:
        proc = subprocess.run(cmd, check=False, env=env)
        return int(proc.returncode)
    except FileNotFoundError:
        pretty = " ".join(shlex.quote(c) for c in cmd)
        print(
            "Error: SkillGate CLI is not installed. Install with `pip install skillgate` \\n"
            "or run from repo with:\n"
            f"  {pretty}",
            file=sys.stderr,
        )
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
