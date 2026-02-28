from __future__ import annotations

import argparse
import json
import sys

from .adapters import render_claude_context, render_codex_context
from .registry import RegistryError, load_registry
from .retriever import SkillRetriever


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-rag",
        description="Top-k skill expert retrieval for Codex/Claude style runtimes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # index command
    index_cmd = sub.add_parser("index", help="Index registry into ChromaDB for persistent retrieval")
    index_cmd.add_argument("--registry", required=True, help="Path to experts YAML/JSON")
    index_cmd.add_argument("--collection", default="skillmesh_experts", help="ChromaDB collection name")
    index_cmd.add_argument("--data-dir", default=None, help="ChromaDB persistence directory")
    index_cmd.add_argument("--ephemeral", action="store_true", help="Use ephemeral (in-memory) ChromaDB for testing")

    retrieve = sub.add_parser("retrieve", help="Retrieve top-k experts for query")
    retrieve.add_argument("--registry", required=True, help="Path to experts YAML/JSON")
    retrieve.add_argument("--query", required=True, help="User query")
    retrieve.add_argument("--top-k", type=int, default=3, help="Top-k hits")
    retrieve.add_argument("--dense", action="store_true", help="Enable optional dense scoring")
    retrieve.add_argument("--backend", choices=["auto", "memory", "chroma"], default="auto", help="Retrieval backend")

    emit = sub.add_parser("emit", help="Emit provider-specific context block")
    emit.add_argument("--provider", required=True, choices=["codex", "claude"], help="Target provider")
    emit.add_argument("--registry", required=True, help="Path to experts YAML/JSON")
    emit.add_argument("--query", required=True, help="User query")
    emit.add_argument("--top-k", type=int, default=3, help="Top-k hits")
    emit.add_argument("--dense", action="store_true", help="Enable optional dense scoring")
    emit.add_argument("--backend", choices=["auto", "memory", "chroma"], default="auto", help="Retrieval backend")
    emit.add_argument(
        "--instruction-chars",
        type=int,
        default=700,
        help="Max instruction text per retrieved expert",
    )

    return parser


def _hits_payload(hits):
    payload = []
    for hit in hits:
        payload.append(
            {
                "id": hit.card.id,
                "title": hit.card.title,
                "domain": hit.card.domain,
                "description": hit.card.description,
                "tags": hit.card.tags,
                "tool_hints": hit.card.tool_hints,
                "aliases": hit.card.aliases,
                "dependencies": hit.card.dependencies,
                "input_contract": hit.card.input_contract,
                "output_artifacts": hit.card.output_artifacts,
                "quality_checks": hit.card.quality_checks,
                "constraints": hit.card.constraints,
                "risk_level": hit.card.risk_level,
                "maturity": hit.card.maturity,
                "metadata": hit.card.metadata,
                "score": hit.score,
                "sparse_score": hit.sparse_score,
                "dense_score": hit.dense_score,
            }
        )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        cards = load_registry(args.registry)
    except RegistryError as exc:
        print(f"RegistryError: {exc}", file=sys.stderr)
        return 2

    if args.command == "index":
        from .backends.chroma import ChromaBackend

        backend = ChromaBackend(
            collection_name=args.collection,
            data_dir=args.data_dir,
            ephemeral=args.ephemeral,
        )
        backend.index(cards)
        print(f"Indexed {len(cards)} experts into collection '{args.collection}'")
        return 0

    backend_choice = getattr(args, "backend", "auto")
    retriever = SkillRetriever(
        cards,
        use_dense=bool(getattr(args, "dense", False)),
        backend=backend_choice,
    )
    hits = retriever.retrieve(args.query, top_k=args.top_k)

    if args.command == "retrieve":
        print(json.dumps({"query": args.query, "hits": _hits_payload(hits)}, indent=2))
        return 0

    if args.provider == "codex":
        out = render_codex_context(args.query, hits, instruction_chars=args.instruction_chars)
    else:
        out = render_claude_context(args.query, hits, instruction_chars=args.instruction_chars)

    print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
