from __future__ import annotations

from pathlib import Path

import skill_registry_rag.backends.chroma as chroma_backend
from skill_registry_rag.registry import load_registry
from skill_registry_rag.retriever import SkillRetriever


def _load_cards():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "tools.yaml"
    return load_registry(registry_path)


def _load_json_cards():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "tools.json"
    return load_registry(registry_path)


def test_retriever_visualization_query_returns_viz_first():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("build matplotlib seaborn heatmap and trend chart", top_k=2)

    assert hits
    assert hits[0].card.id == "viz.matplotlib-seaborn"


def test_retriever_model_export_query_returns_ml_export_first():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("export sklearn pipeline as onnx and joblib model artifact", top_k=2)

    assert hits
    assert hits[0].card.id == "ml.model-export"


def test_retriever_slides_query_returns_slides_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("create pptx slides with executive summary and charts", top_k=2)

    assert hits
    assert hits[0].card.id == "docs.slides-pptx"


def test_retriever_statistics_query_returns_stats_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("run anova and ols diagnostics with scipy and statsmodels", top_k=2)

    assert hits
    assert hits[0].card.id == "stats.scipy-statsmodels"


def test_retriever_chemistry_query_returns_rdkit_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("compute smiles fingerprints and substructure similarity with rdkit", top_k=2)

    assert hits
    assert hits[0].card.id == "chemistry.rdkit-cheminformatics"


def test_retriever_opencv_query_returns_cv_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("opencv cv2 contour detection and edge threshold pipeline", top_k=2)

    assert hits
    assert hits[0].card.id == "cv.opencv-image-processing"


def test_retriever_geospatial_query_returns_geo_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("geopandas shapely spatial join and crs reprojection", top_k=2)

    assert hits
    assert hits[0].card.id == "geo.geopandas-spatial"


def test_retriever_nlp_query_returns_nlp_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("spacy transformers named entity recognition and text classification", top_k=2)

    assert hits
    assert hits[0].card.id == "nlp.spacy-transformers"


def test_retriever_pytorch_query_returns_dl_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("pytorch training loop with cuda amp checkpoint", top_k=2)

    assert hits
    assert hits[0].card.id == "dl.pytorch-training"


def test_retriever_xgboost_query_returns_boosting_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("xgboost lightgbm shap feature importance and early stopping", top_k=2)

    assert hits
    assert hits[0].card.id == "ml.gradient-boosting"


def test_retriever_json_registry_cv_query_returns_cv_expert():
    cards = _load_json_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve("opencv contour edge threshold cv2", top_k=2)

    assert hits
    assert hits[0].card.id == "cv.opencv-image-processing"


def test_retriever_owasp_query_returns_security_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve(
        "owasp top 10 xss csrf sql injection security headers", top_k=2
    )

    assert hits
    assert hits[0].card.id == "sec.owasp-web"


def test_retriever_secrets_query_returns_security_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve(
        "rotate api keys with vault kms and secret scanning in ci", top_k=2
    )

    assert hits
    assert hits[0].card.id == "sec.secrets-management"


def test_retriever_cloud_s3_query_returns_s3_expert():
    cards = _load_cards()
    retriever = SkillRetriever(cards, use_dense=False)
    hits = retriever.retrieve(
        "create s3 bucket lifecycle policy and presigned upload url", top_k=2
    )

    assert hits
    assert hits[0].card.id == "cloud.aws-s3"


def test_retriever_auto_backend_falls_back_to_memory_when_chroma_fails(monkeypatch):
    class FailingChromaBackend:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("chroma init failed")

    monkeypatch.setattr(chroma_backend, "ChromaBackend", FailingChromaBackend)

    cards = _load_json_cards()
    retriever = SkillRetriever(cards, use_dense=False, backend="auto")
    hits = retriever.retrieve("opencv contour edge threshold cv2", top_k=2)

    assert hits
    assert hits[0].card.id == "cv.opencv-image-processing"


def test_retriever_passes_dense_and_hybrid_defaults_to_chroma(monkeypatch):
    captured: dict[str, object] = {}

    class StubChromaBackend:
        def __init__(self, *args, **kwargs):
            captured.update(kwargs)

        def index(self, cards):
            return None

        def query(self, text, top_k=3):
            return []

    monkeypatch.setattr(chroma_backend, "ChromaBackend", StubChromaBackend)

    cards = _load_json_cards()
    retriever = SkillRetriever(cards, use_dense=True, backend="chroma")
    retriever.retrieve("any query", top_k=1)

    assert captured["use_dense"] is True
    assert captured["sparse_weight"] == 0.8
    assert captured["dense_weight"] == 0.2
    assert captured["min_dense_candidates"] == 100
    assert captured["dense_candidates_multiplier"] == 10

def test_retriever_dense_mode_e2e():
    """Test dense mode retrieval end-to-end to ensure inference and schema alignment works."""
    cards = _load_json_cards()
    # We slice to a small number of cards so the dense embedding test runs quickly.
    small_catalog = cards[:10]
    
    # Force use dense mode with chroma.
    # Note: this requires sentence-transformers and chromadb to be installed.
    retriever = SkillRetriever(small_catalog, use_dense=True, backend="chroma")
    hits = retriever.retrieve("matplotlib charting and visualization", top_k=2)
    
    # We should get back results; we just care that the dense pipeline doesn't crash 
    # and returns formatted hits.
    assert len(hits) > 0
    assert hasattr(hits[0], "score")
    assert hasattr(hits[0], "dense_score")
