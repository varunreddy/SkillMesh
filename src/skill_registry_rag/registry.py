from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from .models import ToolCard


class RegistryError(ValueError):
    """Raised when the tool/role registry is invalid."""


def _validate_schema(raw: Any, registry_path: Path, schema_path: Path | None) -> None:
    path = schema_path
    if path is None:
        candidate = registry_path.parent / "schema.json"
        path = candidate if candidate.exists() else None
    if path is None:
        return
    if not path.exists():
        raise RegistryError(f"Schema file not found: {path}")

    try:
        from jsonschema import Draft202012Validator
    except Exception as exc:
        raise RegistryError(
            "jsonschema package is required for schema validation. "
            "Install dependencies from pyproject."
        ) from exc

    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RegistryError(f"Failed to parse schema JSON: {path}") from exc

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(raw), key=lambda e: list(e.absolute_path))
    if not errors:
        return

    first = errors[0]
    where = ".".join(str(x) for x in first.absolute_path) or "<root>"
    raise RegistryError(f"Schema validation failed at {where}: {first.message}")


def _read_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    raise RegistryError(f"Unsupported registry extension: {suffix}")


def _normalize_entries(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        entries = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get("tools"), list):
            entries = raw["tools"]
        elif isinstance(raw.get("roles"), list):
            entries = raw["roles"]
        else:
            raise RegistryError(
                "Registry object must contain one of: 'tools' or 'roles'."
            )
    else:
        raise RegistryError(
            "Registry must be a list or an object with 'tools'/'roles'."
        )

    out: list[dict[str, Any]] = []
    for i, row in enumerate(entries):
        if not isinstance(row, dict):
            raise RegistryError(f"Entry at index {i} is not an object.")
        out.append(row)
    return out


def _to_list(value: Any, field: str, card_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise RegistryError(f"'{field}' must be a list in card '{card_id}'.")
    return [str(x).strip() for x in value if str(x).strip()]


def _to_map(value: Any, field: str, card_id: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise RegistryError(f"'{field}' must be an object in card '{card_id}'.")
    out: dict[str, str] = {}
    for k, v in value.items():
        key = str(k).strip()
        val = str(v).strip()
        if key and val:
            out[key] = val
    return out


def _to_any_map(value: Any, field: str, card_id: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise RegistryError(f"'{field}' must be an object in card '{card_id}'.")
    return dict(value)


def _sanitize_function_name(raw: str) -> str:
    # OpenAI function names: alnum, underscore, dash, max length 64.
    # Anthropic function names: alnum, underscore, max length 64.
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", raw.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "tool"
    return cleaned[:64]


def _default_parameters(
    *, card_title: str, card_description: str, input_contract: dict[str, str]
) -> dict[str, Any]:
    task_desc = input_contract.get("required") or card_description or card_title
    context_desc = input_contract.get("optional") or (
        "Optional structured inputs for this tool."
    )
    return {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": task_desc},
            "context": {"type": "object", "description": context_desc},
        },
        "required": ["task"],
        "additionalProperties": True,
    }


def _normalize_parameters(
    raw: Any, *, card_title: str, card_description: str, input_contract: dict[str, str]
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return _default_parameters(
            card_title=card_title,
            card_description=card_description,
            input_contract=input_contract,
        )

    out = dict(raw)
    if str(out.get("type", "")).strip() != "object":
        out["type"] = "object"
    props = out.get("properties")
    if not isinstance(props, dict):
        out["properties"] = {}
    if "additionalProperties" not in out:
        out["additionalProperties"] = True
    return out


def _normalize_invocation(
    raw: dict[str, Any],
    *,
    card_id: str,
    card_title: str,
    card_description: str,
    input_contract: dict[str, str],
) -> dict[str, Any]:
    default_fn_name = _sanitize_function_name(card_id.replace(".", "_"))
    default_desc = card_description or f"Execute {card_title}"

    if not raw:
        return {
            "type": "function",
            "function": {
                "name": default_fn_name,
                "description": default_desc,
                "parameters": _default_parameters(
                    card_title=card_title,
                    card_description=card_description,
                    input_contract=input_contract,
                ),
                "strict": False,
            },
        }

    if raw.get("type") != "function" or not isinstance(raw.get("function"), dict):
        raise RegistryError(
            f"'invocation' must follow OpenAI function tool schema in card '{card_id}'."
        )

    fn = dict(raw["function"])
    return {
        "type": "function",
        "function": {
            "name": _sanitize_function_name(str(fn.get("name", default_fn_name))),
            "description": str(fn.get("description", default_desc)).strip(),
            "parameters": _normalize_parameters(
                fn.get("parameters"),
                card_title=card_title,
                card_description=card_description,
                input_contract=input_contract,
            ),
            "strict": bool(fn.get("strict", False)),
        },
    }


def _validate_required(row: dict[str, Any], required: list[str], idx: int) -> None:
    for key in required:
        val = str(row.get(key, "")).strip()
        if not val:
            raise RegistryError(f"Missing required field '{key}' at entry index {idx}.")


def load_registry(
    registry_path: str | Path,
    *,
    validate_schema: bool = True,
    schema_path: str | Path | None = None,
) -> list[ToolCard]:
    path = Path(registry_path).expanduser().resolve()
    if not path.exists():
        raise RegistryError(f"Registry not found: {path}")

    raw = _read_structured(path)
    if validate_schema:
        _validate_schema(
            raw,
            path,
            Path(schema_path).expanduser().resolve() if schema_path is not None else None,
        )
    entries = _normalize_entries(raw)

    cards: list[ToolCard] = []
    seen_ids: set[str] = set()
    root = path.parent

    for idx, row in enumerate(entries):
        _validate_required(row, ["id", "title", "domain", "instruction_file"], idx)

        card_id = str(row["id"]).strip()
        if card_id in seen_ids:
            raise RegistryError(f"Duplicate card id: '{card_id}'")
        seen_ids.add(card_id)

        title = str(row["title"]).strip()
        description = str(row.get("description", "")).strip()
        instruction_file = str(row["instruction_file"]).strip()
        input_contract = _to_map(row.get("input_contract"), "input_contract", card_id)
        invocation_raw = _to_any_map(row.get("invocation"), "invocation", card_id)

        # Use inlined instruction_text if present (compiled registry), else read from file
        instruction_text = str(row.get("instruction_text", "")).strip()
        if not instruction_text:
            instruction_path = (root / instruction_file).resolve()
            if not instruction_path.is_relative_to(root.resolve()):
                raise RegistryError(f"Path traversal detected: {instruction_path} is outside of {root.resolve()}")
            if not instruction_path.exists():
                raise RegistryError(
                    f"Instruction file missing for '{card_id}': {instruction_path}"
                )
            instruction_text = instruction_path.read_text(encoding="utf-8").strip()

        card = ToolCard(
            id=card_id,
            title=title,
            domain=str(row["domain"]).strip(),
            instruction_file=instruction_file,
            description=description,
            tags=_to_list(row.get("tags"), "tags", card_id),
            tool_hints=_to_list(row.get("tool_hints"), "tool_hints", card_id),
            examples=_to_list(row.get("examples"), "examples", card_id),
            aliases=_to_list(row.get("aliases"), "aliases", card_id),
            dependencies=_to_list(row.get("dependencies"), "dependencies", card_id),
            output_artifacts=_to_list(
                row.get("output_artifacts"), "output_artifacts", card_id
            ),
            quality_checks=_to_list(
                row.get("quality_checks"), "quality_checks", card_id
            ),
            constraints=_to_list(row.get("constraints"), "constraints", card_id),
            input_contract=input_contract,
            invocation=_normalize_invocation(
                invocation_raw,
                card_id=card_id,
                card_title=title,
                card_description=description,
                input_contract=input_contract,
            ),
            risk_level=str(row.get("risk_level", "")).strip(),
            maturity=str(row.get("maturity", "")).strip(),
            metadata=_to_any_map(row.get("metadata"), "metadata", card_id),
            instruction_text=instruction_text,
        )
        cards.append(card)

    return cards
