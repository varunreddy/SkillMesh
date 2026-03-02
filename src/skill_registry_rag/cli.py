from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ._resolve import resolve_registry_path
from .adapters import render_claude_context, render_codex_context
from .roles import (
    RoleCatalogError,
    friendly_role_name,
    install_role_bundle,
    list_role_offers,
    resolve_role_selector,
)
from .registry import RegistryError, load_registry
from .retriever import SkillRetriever

_TOP_LEVEL_COMMANDS = {"index", "retrieve", "emit", "roles"}


def _default_catalog_path() -> str:
    env_catalog = os.getenv("SKILLMESH_CATALOG", "").strip()
    if env_catalog:
        return env_catalog
    try:
        return str(resolve_registry_path(None))
    except ValueError:
        return ""


def _default_role_registry_path() -> str:
    role_registry = os.getenv("SKILLMESH_ROLE_REGISTRY", "").strip()
    if role_registry:
        return role_registry

    explicit_registry = os.getenv("SKILLMESH_REGISTRY", "").strip()
    if explicit_registry:
        return explicit_registry

    return str((Path.home() / ".codex" / "skills" / "skillmesh" / "installed.registry.yaml"))


def _print_role_offers(offers: list[dict[str, object]], *, catalog: str, registry: str = "") -> None:
    print(f"Catalog: {catalog}")
    if registry:
        print(f"Installed registry: {registry}")
    print(f"Roles available: {len(offers)}")
    print("")
    print("ROLE | DEPENDENCIES | INSTALLED | TITLE")
    for offer in offers:
        role_id = str(offer["id"])
        installed = "yes" if bool(offer["installed"]) else "no"
        print(
            f"{friendly_role_name(role_id)} | {offer['dependency_count']} | "
            f"{installed} | {offer['title']}"
        )


def _print_installed_roles(offers: list[dict[str, object]], *, registry: str) -> None:
    installed = [offer for offer in offers if bool(offer["installed"])]
    print(f"Installed registry: {registry}")
    print(f"Installed roles: {len(installed)}")
    if not installed:
        print("No roles installed. Run `skillmesh roles wizard` or `skillmesh <Role-Name> install`.")
        return
    print("")
    print("ROLE | DEPENDENCIES | TITLE")
    for offer in installed:
        role_id = str(offer["id"])
        print(f"{friendly_role_name(role_id)} | {offer['dependency_count']} | {offer['title']}")


def _print_install_result(result: dict[str, object], *, dry_run: bool) -> None:
    action = "Dry run for" if dry_run else "Installed"
    role_id = str(result["role_id"])
    print(f"{action} role bundle: {friendly_role_name(role_id)}")
    print(f"Catalog: {result['catalog_registry']}")
    print(f"Target registry: {result['target_registry']}")
    print(
        f"Added cards: {len(result['added_ids'])} "
        f"({', '.join(result['added_ids']) if result['added_ids'] else 'none'})"
    )
    print(
        f"Already present: {len(result['already_present_ids'])} "
        "("
        f"{', '.join(result['already_present_ids']) if result['already_present_ids'] else 'none'}"
        ")"
    )
    if result["copied_instruction_files"]:
        print(
            f"Instruction files {'to copy' if dry_run else 'copied'}: "
            f"{len(result['copied_instruction_files'])}"
        )
    if result["unresolved_dependencies"]:
        print(
            "Unresolved dependencies: "
            + ", ".join(result["unresolved_dependencies"])
        )


def _run_roles_wizard(*, catalog: str, registry: str, dry_run: bool) -> int:
    offers = list_role_offers(catalog_registry=catalog, installed_registry=(registry or None))
    if not offers:
        print("No roles found in catalog.")
        return 2

    print("SkillMesh Role Wizard")
    print(f"Catalog: {catalog}")
    print(f"Target registry: {registry}")
    print("")
    for idx, offer in enumerate(offers, start=1):
        role_id = str(offer["id"])
        installed = "installed" if bool(offer["installed"]) else "new"
        print(
            f"{idx}. {friendly_role_name(role_id)} ({offer['dependency_count']} deps, {installed})"
            f" - {offer['title']}"
        )

    selected_role_id = ""
    while not selected_role_id:
        choice = input("Select role by number or id (q to cancel): ").strip()
        if choice.lower() in {"q", "quit", "exit"}:
            print("Cancelled.")
            return 0
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(offers):
                selected_role_id = str(offers[n - 1]["id"])
                break
        else:
            try:
                selected_role_id = resolve_role_selector(choice, offers)
                break
            except RoleCatalogError:
                selected_role_id = ""
        print("Invalid selection. Enter a number, role id, or q.")

    confirmation = input(
        f"Install {selected_role_id} into {registry}? [Y/n]: "
    ).strip().lower()
    if confirmation not in {"", "y", "yes"}:
        print("Cancelled.")
        return 0

    result = install_role_bundle(
        catalog_registry=catalog,
        target_registry=registry,
        role_id=selected_role_id,
        dry_run=bool(dry_run),
    )
    _print_install_result(result, dry_run=bool(dry_run))
    return 0


def _normalize_cli_argv(argv: list[str] | None) -> list[str]:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        return args

    # Friendly alias: `skillmesh fetch ...` -> `skillmesh retrieve ...`
    if args[0].strip().lower() == "fetch":
        if len(args) == 1:
            return ["retrieve"]
        remaining = args[1:]
        if any(token == "--query" or token.startswith("--query=") for token in remaining):
            return ["retrieve", *remaining]
        if remaining[0].startswith("-"):
            return ["retrieve", *remaining]

        query_parts: list[str] = []
        idx = 0
        while idx < len(remaining):
            token = remaining[idx]
            if token.startswith("-"):
                break
            query_parts.append(token)
            idx += 1
        if not query_parts:
            return ["retrieve", *remaining]
        return ["retrieve", "--query", " ".join(query_parts), *remaining[idx:]]

    # Support singular alias: `skillmesh role` -> `skillmesh roles`
    if args[0].strip().lower() == "role":
        args[0] = "roles"

    # `skillmesh roles` -> show installed roles
    if args[0].strip().lower() == "roles":
        # Friendly shorthand: `skillmesh roles install Data-Analyst`
        if len(args) >= 3 and args[1].strip().lower() == "install":
            role_id_flag_present = any(
                token == "--role-id" or token.startswith("--role-id=")
                for token in args[2:]
            )
            if not role_id_flag_present:
                rest = args[2:]
                selector_index = -1
                i = 0
                while i < len(rest):
                    token = rest[i]
                    if token in {"--catalog", "--registry"}:
                        if i + 1 >= len(rest):
                            return args
                        i += 2
                        continue
                    if token.startswith("--catalog=") or token.startswith("--registry="):
                        i += 1
                        continue
                    if token in {"--dry-run", "--json"}:
                        i += 1
                        continue
                    if token.startswith("-"):
                        return args
                    selector_index = i
                    break

                if selector_index >= 0:
                    selector = rest[selector_index]
                    args = [
                        "roles",
                        "install",
                        *rest[:selector_index],
                        "--role-id",
                        selector,
                        *rest[selector_index + 1:],
                    ]

        if len(args) == 1:
            return ["roles", "installed", *args[1:]]
        if args[1].startswith("-") and args[1] not in {"-h", "--help"}:
            return ["roles", "installed", *args[1:]]
        return args

    # Friendly shorthand: `skillmesh Data-Analyst install`
    if (
        len(args) >= 2
        and args[1].strip().lower() == "install"
        and args[0].strip().lower() not in _TOP_LEVEL_COMMANDS
        and not args[0].startswith("-")
    ):
        return ["roles", "install", "--role-id", args[0], *args[2:]]

    return args


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillmesh",
        description="Top-k SkillMesh tool/role card retrieval for Codex/Claude style runtimes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # index command
    index_cmd = sub.add_parser("index", help="Index registry into ChromaDB for persistent retrieval")
    index_cmd.add_argument("--registry", default=None, help="Path to tools/roles YAML/JSON")
    index_cmd.add_argument("--collection", default="skillmesh_experts", help="ChromaDB collection name")
    index_cmd.add_argument("--data-dir", default=None, help="ChromaDB persistence directory")
    index_cmd.add_argument("--ephemeral", action="store_true", help="Use ephemeral (in-memory) ChromaDB for testing")

    retrieve = sub.add_parser("retrieve", help="Retrieve top-k cards for query")
    retrieve.add_argument("--registry", default=None, help="Path to tools/roles YAML/JSON")
    retrieve.add_argument("--query", required=True, help="User query")
    retrieve.add_argument("--top-k", type=int, default=3, help="Top-k hits")
    retrieve.add_argument("--dense", action="store_true", help="Enable optional dense scoring")
    retrieve.add_argument("--backend", choices=["auto", "memory", "chroma"], default="auto", help="Retrieval backend")

    emit = sub.add_parser("emit", help="Emit provider-specific context block")
    emit.add_argument("--provider", required=True, choices=["codex", "claude"], help="Target provider")
    emit.add_argument("--registry", default=None, help="Path to tools/roles YAML/JSON")
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

    roles = sub.add_parser("roles", help="Role commands")
    roles_sub = roles.add_subparsers(dest="roles_command", required=False)

    roles_list = roles_sub.add_parser("list", help="List available role cards from catalog")
    roles_list.add_argument(
        "--catalog",
        default=_default_catalog_path(),
        help="Path to source tools/roles catalog YAML/JSON",
    )
    roles_list.add_argument(
        "--registry",
        default=_default_role_registry_path(),
        help="Optional installed registry path for showing installed/missing status",
    )
    roles_list.add_argument("--json", action="store_true", help="Emit JSON output")

    roles_install = roles_sub.add_parser(
        "install",
        help="Install selected role card and missing dependency cards into registry",
    )
    roles_install.add_argument(
        "--catalog",
        default=_default_catalog_path(),
        help="Path to source tools/roles catalog YAML/JSON",
    )
    roles_install.add_argument(
        "--registry",
        default=_default_role_registry_path(),
        help="Target registry YAML/JSON to write role/dependency cards into",
    )
    roles_install.add_argument(
        "--role-id",
        required=True,
        help="Role card id to install (example: role.data-engineer)",
    )
    roles_install.add_argument("--dry-run", action="store_true", help="Show changes only")
    roles_install.add_argument("--json", action="store_true", help="Emit JSON output")

    roles_wizard = roles_sub.add_parser(
        "wizard",
        help="Interactive role picker that installs into a target registry",
    )
    roles_wizard.add_argument(
        "--catalog",
        default=_default_catalog_path(),
        help="Path to source tools/roles catalog YAML/JSON",
    )
    roles_wizard.add_argument(
        "--registry",
        default=_default_role_registry_path(),
        help="Target registry YAML/JSON to write role/dependency cards into",
    )
    roles_wizard.add_argument("--dry-run", action="store_true", help="Show changes only")

    roles_installed = roles_sub.add_parser(
        "installed",
        help="Show only installed roles",
    )
    roles_installed.add_argument(
        "--catalog",
        default=_default_catalog_path(),
        help="Path to source tools/roles catalog YAML/JSON",
    )
    roles_installed.add_argument(
        "--registry",
        default=_default_role_registry_path(),
        help="Installed registry YAML/JSON path",
    )
    roles_installed.add_argument("--json", action="store_true", help="Emit JSON output")

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
                "invocation": hit.card.invocation,
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
    normalized_argv = _normalize_cli_argv(argv)
    parser = _build_parser()
    args = parser.parse_args(normalized_argv)

    if args.command == "roles":
        catalog = str(getattr(args, "catalog", "") or "").strip()
        if not catalog:
            print(
                "Error: missing --catalog. Provide a catalog path or set SKILLMESH_CATALOG.",
                file=sys.stderr,
            )
            return 2

        registry = str(getattr(args, "registry", "") or "").strip()
        try:
            if args.roles_command in {None, "installed", "list"}:
                offers = list_role_offers(
                    catalog_registry=catalog,
                    installed_registry=(registry or None),
                )
                if args.roles_command in {None, "installed"}:
                    installed = [offer for offer in offers if bool(offer["installed"])]
                    if getattr(args, "json", False):
                        print(json.dumps({"roles": installed}, indent=2))
                        return 0
                    _print_installed_roles(offers, registry=registry)
                    return 0

                if getattr(args, "json", False):
                    print(json.dumps({"roles": offers}, indent=2))
                    return 0

                _print_role_offers(offers, catalog=catalog, registry=registry)
                return 0

            if args.roles_command == "wizard":
                try:
                    return _run_roles_wizard(
                        catalog=catalog,
                        registry=registry,
                        dry_run=bool(args.dry_run),
                    )
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
                    return 130

            role_offers = list_role_offers(catalog_registry=catalog)
            resolved_role_id = resolve_role_selector(args.role_id, role_offers)
            result = install_role_bundle(
                catalog_registry=catalog,
                target_registry=registry,
                role_id=resolved_role_id,
                dry_run=bool(args.dry_run),
            )
            if args.json:
                print(json.dumps(result, indent=2))
                return 0

            _print_install_result(result, dry_run=bool(args.dry_run))
            return 0
        except RoleCatalogError as exc:
            print(f"RoleCatalogError: {exc}", file=sys.stderr)
            return 2

    try:
        registry_path = resolve_registry_path(args.registry)
        cards = load_registry(registry_path)
    except (RegistryError, ValueError) as exc:
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
        print(f"Indexed {len(cards)} cards into collection '{args.collection}'")
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
