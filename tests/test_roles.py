from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from skill_registry_rag.cli import main
from skill_registry_rag.roles import install_role_bundle, list_role_offers
from skill_registry_rag.registry import load_registry


def _catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "registry" / "tools.json"


def test_list_role_offers_includes_roles_and_dependency_counts():
    offers = list_role_offers(catalog_registry=str(_catalog_path()))
    by_id = {offer["id"]: offer for offer in offers}

    assert "role.data-engineer" in by_id
    assert by_id["role.data-engineer"]["dependency_count"] >= 8

    # This role has empty dependency list in tools.json and should fall back to role markdown.
    assert "role.devops-engineer" in by_id
    assert by_id["role.devops-engineer"]["dependency_count"] >= 8
    assert "role.aws-engineer" in by_id
    assert by_id["role.aws-engineer"]["dependency_count"] >= 18


def test_install_role_bundle_creates_registry_with_role_and_dependencies(tmp_path):
    target = tmp_path / "installed.registry.yaml"
    result = install_role_bundle(
        catalog_registry=str(_catalog_path()),
        target_registry=str(target),
        role_id="role.data-engineer",
    )

    assert target.exists()
    assert "role.data-engineer" in result["added_ids"]
    cards = load_registry(target)
    ids = {card.id for card in cards}
    assert "role.data-engineer" in ids
    assert "data.spark" in ids
    assert "cloud.terraform" in ids


def test_install_aws_role_bundle_creates_registry_with_aws_dependencies(tmp_path):
    target = tmp_path / "aws-installed.registry.yaml"
    result = install_role_bundle(
        catalog_registry=str(_catalog_path()),
        target_registry=str(target),
        role_id="role.aws-engineer",
    )

    assert target.exists()
    assert "role.aws-engineer" in result["added_ids"]
    cards = load_registry(target)
    ids = {card.id for card in cards}
    assert "role.aws-engineer" in ids
    assert "cloud.aws-ec2" in ids
    assert "cloud.aws-eks" in ids
    assert "cloud.aws-s3" in ids
    assert "cloud.aws-lambda" in ids
    assert "cloud.aws-vpc" in ids
    assert "cloud.aws-rds" in ids
    assert "cloud.aws-dynamodb" in ids
    assert "cloud.aws-api-gateway" in ids
    assert "cloud.aws-cloudfront" in ids
    assert "cloud.aws-sqs-sns-eventbridge" in ids
    assert "cloud.aws-cloudwatch-observability" in ids
    assert "cloud.aws-iam-identity-center" in ids
    assert "cloud.aws-kms" in ids


def test_install_role_bundle_skips_existing_cards(tmp_path):
    catalog = json.loads(_catalog_path().read_text(encoding="utf-8"))
    tools = catalog["tools"]
    spark = [entry for entry in tools if entry.get("id") == "data.spark"][0]
    target = tmp_path / "existing.registry.json"
    target.write_text(json.dumps({"tools": [spark]}, indent=2), encoding="utf-8")

    result = install_role_bundle(
        catalog_registry=str(_catalog_path()),
        target_registry=str(target),
        role_id="role.data-engineer",
    )

    assert "data.spark" in result["already_present_ids"]
    reloaded = json.loads(target.read_text(encoding="utf-8"))
    ids = [entry["id"] for entry in reloaded["tools"]]
    assert ids.count("data.spark") == 1


def test_cli_roles_list_and_install_json(tmp_path):
    buf = StringIO()
    with redirect_stdout(buf):
        code = main(["roles", "list", "--catalog", str(_catalog_path()), "--json"])
    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["roles"]

    target = tmp_path / "roles.registry.json"
    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "roles",
                "install",
                "--catalog",
                str(_catalog_path()),
                "--registry",
                str(target),
                "--role-id",
                "role.devops-engineer",
                "--json",
            ]
        )

    assert code == 0
    install_payload = json.loads(buf.getvalue())
    assert "role.devops-engineer" in install_payload["added_ids"]
    # Dependency parsing falls back to role markdown when dependencies are absent.
    assert "devops.nginx" in install_payload["added_ids"]


def test_cli_roles_list_uses_default_catalog():
    buf = StringIO()
    with redirect_stdout(buf):
        code = main(["roles", "list", "--json"])
    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["roles"]


def test_cli_roles_wizard_interactive_install(tmp_path, monkeypatch):
    target = tmp_path / "wizard.registry.yaml"
    answers = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "roles",
                "wizard",
                "--catalog",
                str(_catalog_path()),
                "--registry",
                str(target),
            ]
        )

    assert code == 0
    assert target.exists()
    output = buf.getvalue()
    assert "SkillMesh Role Wizard" in output
    assert "Installed role bundle:" in output


def test_cli_roles_list_uses_friendly_role_display():
    buf = StringIO()
    with redirect_stdout(buf):
        code = main(["roles", "list", "--catalog", str(_catalog_path())])
    assert code == 0
    output = buf.getvalue()
    assert "AWS-Engineer" in output
    assert "Machine-Learning-Researcher" in output
    assert "role.ml-researcher" not in output


def test_cli_roles_no_subcommand_shows_installed_only(tmp_path):
    target = tmp_path / "installed-only.registry.yaml"
    install_role_bundle(
        catalog_registry=str(_catalog_path()),
        target_registry=str(target),
        role_id="role.data-analyst",
    )

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "roles",
                "--catalog",
                str(_catalog_path()),
                "--registry",
                str(target),
            ]
        )
    assert code == 0
    output = buf.getvalue()
    assert "Installed roles: 1" in output
    assert "Data-Analyst" in output
    assert "Machine-Learning-Researcher" not in output


def test_cli_friendly_shorthand_install_command(tmp_path):
    target = tmp_path / "shorthand.registry.yaml"
    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "Data-Analyst",
                "install",
                "--catalog",
                str(_catalog_path()),
                "--registry",
                str(target),
            ]
        )
    assert code == 0
    output = buf.getvalue()
    assert "Installed role bundle: Data-Analyst" in output
    cards = load_registry(target)
    ids = {card.id for card in cards}
    assert "role.data-analyst" in ids


def test_cli_roles_install_accepts_positional_selector(tmp_path):
    target = tmp_path / "roles-install-positional.registry.yaml"
    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "roles",
                "install",
                "Financial-Analyst",
                "--catalog",
                str(_catalog_path()),
                "--registry",
                str(target),
            ]
        )
    assert code == 0
    output = buf.getvalue()
    assert "Installed role bundle: Financial-Analyst" in output
    cards = load_registry(target)
    ids = {card.id for card in cards}
    assert "role.financial-analyst" in ids


def test_cli_role_singular_alias_maps_to_roles_installed(tmp_path):
    target = tmp_path / "role-alias.registry.yaml"
    install_role_bundle(
        catalog_registry=str(_catalog_path()),
        target_registry=str(target),
        role_id="role.data-analyst",
    )

    buf = StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "role",
                "--catalog",
                str(_catalog_path()),
                "--registry",
                str(target),
            ]
        )
    assert code == 0
    output = buf.getvalue()
    assert "Installed roles: 1" in output
    assert "Data-Analyst" in output


def test_cli_roles_help_shows_subcommands():
    buf = StringIO()
    with pytest.raises(SystemExit) as exc:
        with redirect_stdout(buf):
            main(["roles", "--help"])

    assert exc.value.code == 0
    output = buf.getvalue()
    assert "list" in output
    assert "install" in output
