from __future__ import annotations

from pathlib import Path

import pytest

from skill_registry_rag.registry import RegistryError, load_registry


def test_load_registry_examples():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "experts.yaml"
    cards = load_registry(registry_path)

    assert len(cards) == 53
    ids = {c.id for c in cards}
    assert "viz.matplotlib-seaborn" in ids
    assert "ml.model-export" in ids
    assert "ml.sklearn-modeling" in ids
    assert "ml.gradient-boosting" in ids
    assert "dl.pytorch-training" in ids
    assert "stats.scipy-statsmodels" in ids
    assert "scipy.optimization-signal" in ids
    assert "chemistry.rdkit-cheminformatics" in ids
    assert "graph.networkx-analytics" in ids
    assert "cv.opencv-image-processing" in ids
    assert "geo.geopandas-spatial" in ids
    assert "nlp.spacy-transformers" in ids
    assert "docs.pdf-generation" in ids
    assert "docs.slides-pptx" in ids
    assert "cloud.aws-s3" in ids
    assert "web.fastapi" in ids
    assert "fe.react" in ids
    assert "sys.rust" in ids
    assert "sec.owasp-web" in ids
    assert "sec.secrets-management" in ids
    assert "sec.container-security" in ids
    assert "sec.dependency-scanning" in ids
    assert "sec.iam-policies" in ids
    assert "sec.penetration-testing" in ids


def test_registry_has_entry_for_each_instruction_file():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "experts.yaml"
    cards = load_registry(registry_path)

    card_files = {Path(c.instruction_file).name for c in cards}
    instruction_files = {
        p.name for p in (root / "examples" / "registry" / "instructions").glob("*.md")
    }
    assert card_files == instruction_files


def test_load_enriched_json_registry_fields():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "tools.enriched.json"
    cards = load_registry(registry_path)

    assert len(cards) == 53
    by_id = {c.id: c for c in cards}
    cv = by_id["cv.opencv-image-processing"]
    assert "opencv-python" in cv.dependencies
    assert cv.input_contract.get("required")
    assert "processed_images" in cv.output_artifacts
    assert cv.risk_level == "medium"
    assert cv.metadata.get("install_extra") == "cv"


def test_schema_validation_rejects_invalid_registry(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"experts":[{"id":"x"}]}', encoding="utf-8")

    with pytest.raises(RegistryError):
        load_registry(bad, schema_path=Path(__file__).resolve().parents[1] / "examples" / "registry" / "schema.json")
