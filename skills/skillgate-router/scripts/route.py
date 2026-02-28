#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def _find_repo_root() -> Path | None:
    markers = ("src/skill_registry_rag/__main__.py", "examples/registry/tools.enriched.json")
    starts = [Path.cwd(), Path(__file__).resolve()]
    for start in starts:
        for candidate in [start, *start.parents]:
            if all((candidate / marker).exists() for marker in markers):
                return candidate
    return None


def _existing_path(value: str) -> str:
    p = Path(value).expanduser()
    return str(p.resolve()) if p.exists() else ""


def _default_registry() -> str:
    for env_key in ("SKILLGATE_REGISTRY", "SKILLMESH_REGISTRY"):
        env = os.getenv(env_key, "").strip()
        if env:
            return env

    repo_root = _find_repo_root()
    if repo_root is not None:
        return str((repo_root / "examples" / "registry" / "tools.enriched.json").resolve())

    # Best-effort fallback for users invoking from another checkout.
    cwd_candidate = _existing_path("examples/registry/tools.enriched.json")
    if cwd_candidate:
        return cwd_candidate
    return ""


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skillgate-route",
        description="Emit top-k SkillGate context for Codex/Claude.",
    )
    p.add_argument("--provider", default="codex", choices=["codex", "claude"])
    p.add_argument("--registry", default=_default_registry())
    p.add_argument("--top-k", default="5")
    p.add_argument("--backend", default="auto", choices=["auto", "memory", "chroma"])
    p.add_argument("--dense", action="store_true")
    p.add_argument("--instruction-chars", default="700")
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
    registry_path = Path(registry).expanduser()
    if not registry_path.exists():
        print(f"Error: Registry not found: {registry_path}", file=sys.stderr)
        return 2

    cmd = [
        "skill-rag",
        "emit",
        "--provider",
        args.provider,
        "--registry",
        str(registry_path.resolve()),
        "--query",
        query,
        "--top-k",
        str(args.top_k),
        "--backend",
        args.backend,
        "--instruction-chars",
        str(args.instruction_chars),
    ]
    if args.dense:
        cmd.append("--dense")

    # Fallback to module invocation when CLI script is not on PATH.
    env = os.environ.copy()
    if shutil.which("skill-rag") is None:
        repo_root = _find_repo_root()
        if repo_root is not None:
            src_path = repo_root / "src"
            env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")
        cmd = [
            sys.executable,
            "-m",
            "skill_registry_rag",
            "emit",
            "--provider",
            args.provider,
            "--registry",
            str(registry_path.resolve()),
            "--query",
            query,
            "--top-k",
            str(args.top_k),
            "--backend",
            args.backend,
            "--instruction-chars",
            str(args.instruction_chars),
        ]
        if args.dense:
            cmd.append("--dense")

    try:
        proc = subprocess.run(cmd, check=False, env=env)
        return int(proc.returncode)
    except FileNotFoundError:
        pretty = " ".join(shlex.quote(c) for c in cmd)
        print(
            "Error: SkillGate CLI is not installed.\n"
            "Install with `pip install -e .` from the SkillGate repo,\n"
            "or run from a checkout with:\n"
            f"  {pretty}",
            file=sys.stderr,
        )
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
