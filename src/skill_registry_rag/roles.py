from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml


_SUPPORTED_SUFFIXES = {".json", ".yaml", ".yml"}
_ROLE_DEPENDENCY_ID_RE = re.compile(r"`([A-Za-z0-9._-]+)`")


class RoleCatalogError(ValueError):
    """Raised when role catalog operations fail."""


def friendly_role_name(role_id: str) -> str:
    suffix = str(role_id).strip().split(".", 1)[-1]
    chunks = [part for part in suffix.replace("_", "-").split("-") if part]
    expanded: list[str] = []
    for chunk in chunks:
        low = chunk.lower()
        if low == "ml":
            expanded.extend(["Machine", "Learning"])
        elif low == "bi":
            expanded.extend(["Business", "Intelligence"])
        elif low == "api":
            expanded.append("API")
        elif low == "aws":
            expanded.append("AWS")
        elif low == "gcp":
            expanded.append("GCP")
        elif low == "devops":
            expanded.append("DevOps")
        else:
            expanded.append(chunk.capitalize())
    return "-".join(expanded) if expanded else str(role_id).strip()


def _role_selector_key(value: str) -> str:
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def resolve_role_selector(selector: str, offers: list[dict[str, Any]]) -> str:
    selected = str(selector or "").strip()
    if not selected:
        raise RoleCatalogError("Missing role selector.")

    key = _role_selector_key(selected)
    matches: list[str] = []
    for offer in offers:
        role_id = str(offer["id"])
        suffix = role_id.split(".", 1)[-1]
        title = str(offer.get("title", ""))
        title_short = title.replace(" Role Orchestrator", "").strip()
        variants = {
            role_id,
            suffix,
            friendly_role_name(role_id),
            friendly_role_name(role_id).replace("-", " "),
            title,
            title_short,
        }
        if key in {_role_selector_key(v) for v in variants}:
            matches.append(role_id)

    unique_matches = sorted(set(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if not unique_matches:
        raise RoleCatalogError(
            f"Unknown role selector: '{selected}'. Run `skillmesh roles list`."
        )

    pretty = ", ".join(friendly_role_name(role_id) for role_id in unique_matches)
    raise RoleCatalogError(f"Ambiguous role selector '{selected}'. Matches: {pretty}")


def _read_registry_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    raise RoleCatalogError(f"Unsupported registry extension: {suffix}")


def _write_registry_document(path: Path, payload: Any) -> None:
    suffix = path.suffix.lower()
    if suffix not in _SUPPORTED_SUFFIXES:
        raise RoleCatalogError(f"Unsupported registry extension: {suffix}")

    if suffix == ".json":
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return

    dumped = yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)
    path.write_text(dumped, encoding="utf-8")


def _normalize_entries(payload: Any, *, path: Path) -> tuple[dict[str, Any], str]:
    if payload is None:
        return {"tools": []}, "tools"
    if isinstance(payload, list):
        return {"tools": payload}, "tools"
    if not isinstance(payload, dict):
        raise RoleCatalogError(f"Registry must be list/object: {path}")

    if isinstance(payload.get("tools"), list):
        return payload, "tools"
    if isinstance(payload.get("roles"), list):
        return payload, "roles"
    if payload == {}:
        payload["tools"] = []
        return payload, "tools"

    raise RoleCatalogError(
        f"Registry object must include one of 'tools' or 'roles': {path}"
    )


def _entry_id(entry: dict[str, Any]) -> str:
    return str(entry.get("id", "")).strip()


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def _is_role_entry(entry: dict[str, Any]) -> bool:
    card_id = _entry_id(entry)
    if card_id.startswith("role."):
        return True
    if str(entry.get("domain", "")).strip().lower() == "role_orchestrator":
        return True

    tags = entry.get("tags")
    if isinstance(tags, list):
        tag_set = {str(x).strip().lower() for x in tags if str(x).strip()}
        if "role" in tag_set:
            return True

    return False


def _parse_role_dependencies_from_instruction(instruction_path: Path) -> list[str]:
    if not instruction_path.exists():
        return []

    text = instruction_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("## allowed expert dependencies"):
            start_idx = idx + 1
            break

    if start_idx is None:
        return []

    dependency_ids: list[str] = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        for match in _ROLE_DEPENDENCY_ID_RE.findall(stripped):
            dependency_ids.append(match.strip())
    return _unique(dependency_ids)


def _resolve_role_dependencies(
    role_entry: dict[str, Any],
    *,
    catalog_root: Path,
    known_ids: set[str],
) -> list[str]:
    dependencies = role_entry.get("dependencies")
    dep_ids = _unique(dependencies if isinstance(dependencies, list) else [])

    if not dep_ids:
        instruction_file = str(role_entry.get("instruction_file", "")).strip()
        if instruction_file:
            dep_ids = _parse_role_dependencies_from_instruction(
                (catalog_root / instruction_file).resolve()
            )

    if not dep_ids:
        tool_hints = role_entry.get("tool_hints")
        if isinstance(tool_hints, list):
            dep_ids = _unique(
                [str(x).strip() for x in tool_hints if str(x).strip() in known_ids]
            )

    return dep_ids


def _load_catalog(path: str | Path) -> tuple[Path, dict[str, Any], str, list[dict[str, Any]]]:
    catalog_path = Path(path).expanduser().resolve()
    if not catalog_path.exists():
        raise RoleCatalogError(f"Catalog registry not found: {catalog_path}")

    payload = _read_registry_document(catalog_path)
    normalized, key = _normalize_entries(payload, path=catalog_path)
    entries = normalized[key]
    if not isinstance(entries, list):
        raise RoleCatalogError(f"Registry entries must be a list: {catalog_path}")

    return catalog_path, normalized, key, entries


def _load_target_registry(path: str | Path) -> tuple[Path, dict[str, Any], str, list[dict[str, Any]]]:
    target_path = Path(path).expanduser().resolve()
    if target_path.exists():
        payload = _read_registry_document(target_path)
        normalized, key = _normalize_entries(payload, path=target_path)
        entries = normalized[key]
        if not isinstance(entries, list):
            raise RoleCatalogError(f"Registry entries must be a list: {target_path}")
        return target_path, normalized, key, entries

    suffix = target_path.suffix.lower()
    if suffix not in _SUPPORTED_SUFFIXES:
        raise RoleCatalogError(f"Unsupported registry extension: {suffix}")
    return target_path, {"tools": []}, "tools", []


def list_role_offers(
    *,
    catalog_registry: str | Path,
    installed_registry: str | Path | None = None,
) -> list[dict[str, Any]]:
    catalog_path, _, _, catalog_entries = _load_catalog(catalog_registry)
    catalog_root = catalog_path.parent
    by_id = {
        _entry_id(entry): entry
        for entry in catalog_entries
        if isinstance(entry, dict) and _entry_id(entry)
    }
    known_ids = set(by_id)

    installed_ids: set[str] = set()
    if installed_registry:
        _, _, _, installed_entries = _load_target_registry(installed_registry)
        installed_ids = {
            _entry_id(entry)
            for entry in installed_entries
            if isinstance(entry, dict) and _entry_id(entry)
        }

    offers: list[dict[str, Any]] = []
    for entry in catalog_entries:
        if not isinstance(entry, dict) or not _is_role_entry(entry):
            continue
        role_id = _entry_id(entry)
        deps = _resolve_role_dependencies(
            entry,
            catalog_root=catalog_root,
            known_ids=known_ids,
        )
        unresolved = [dep for dep in deps if dep not in known_ids]
        missing_for_install = [dep for dep in deps if dep not in installed_ids]
        offers.append(
            {
                "id": role_id,
                "title": str(entry.get("title", "")).strip(),
                "description": str(entry.get("description", "")).strip(),
                "dependency_ids": deps,
                "dependency_count": len(deps),
                "unresolved_dependencies": unresolved,
                "installed": role_id in installed_ids,
                "missing_dependency_count": len(missing_for_install),
            }
        )

    offers.sort(key=lambda x: x["id"])
    return offers


def install_role_bundle(
    *,
    catalog_registry: str | Path,
    target_registry: str | Path,
    role_id: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    normalized_role_id = str(role_id).strip()
    if not normalized_role_id:
        raise RoleCatalogError("`role_id` must be non-empty.")

    catalog_path, _, _, catalog_entries = _load_catalog(catalog_registry)
    catalog_root = catalog_path.parent

    catalog_by_id = {
        _entry_id(entry): entry
        for entry in catalog_entries
        if isinstance(entry, dict) and _entry_id(entry)
    }
    known_ids = set(catalog_by_id)

    role_entry = catalog_by_id.get(normalized_role_id)
    if role_entry is None:
        raise RoleCatalogError(f"Role not found in catalog: {normalized_role_id}")
    if not _is_role_entry(role_entry):
        raise RoleCatalogError(f"Card is not a role: {normalized_role_id}")

    dependency_ids = _resolve_role_dependencies(
        role_entry,
        catalog_root=catalog_root,
        known_ids=known_ids,
    )
    requested_ids = _unique([normalized_role_id, *dependency_ids])

    target_path, target_payload, target_key, target_entries = _load_target_registry(
        target_registry
    )
    existing_ids = {
        _entry_id(entry)
        for entry in target_entries
        if isinstance(entry, dict) and _entry_id(entry)
    }

    added_ids: list[str] = []
    already_present: list[str] = []
    unresolved_dependencies: list[str] = []
    copied_instruction_files: list[str] = []
    for card_id in requested_ids:
        if card_id in existing_ids:
            already_present.append(card_id)
            continue

        entry = catalog_by_id.get(card_id)
        if entry is None:
            unresolved_dependencies.append(card_id)
            continue

        entry_copy = copy.deepcopy(entry)
        instruction_file = str(entry_copy.get("instruction_file", "")).strip()
        if instruction_file:
            source_instruction = (catalog_root / instruction_file).resolve()
            target_instruction = (target_path.parent / instruction_file).resolve()
            inline_instruction = str(entry_copy.get("instruction_text", "")).strip()
            if source_instruction.exists():
                if dry_run and not target_instruction.exists():
                    copied_instruction_files.append(str(target_instruction))
                elif not dry_run and not target_instruction.exists():
                    target_instruction.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_instruction, target_instruction)
                    copied_instruction_files.append(str(target_instruction))
            elif inline_instruction:
                if dry_run and not target_instruction.exists():
                    copied_instruction_files.append(str(target_instruction))
                elif not dry_run and not target_instruction.exists():
                    target_instruction.parent.mkdir(parents=True, exist_ok=True)
                    target_instruction.write_text(inline_instruction + "\n", encoding="utf-8")
                    copied_instruction_files.append(str(target_instruction))
            else:
                unresolved_dependencies.append(card_id)
                continue

        target_entries.append(entry_copy)
        existing_ids.add(card_id)
        added_ids.append(card_id)

    target_payload[target_key] = target_entries

    if not dry_run:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        _write_registry_document(target_path, target_payload)

    return {
        "role_id": normalized_role_id,
        "catalog_registry": str(catalog_path),
        "target_registry": str(target_path),
        "requested_ids": requested_ids,
        "dependency_ids": dependency_ids,
        "added_ids": added_ids,
        "already_present_ids": already_present,
        "unresolved_dependencies": unresolved_dependencies,
        "copied_instruction_files": copied_instruction_files,
        "dry_run": bool(dry_run),
    }
