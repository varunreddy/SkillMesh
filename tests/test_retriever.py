from __future__ import annotations

from pathlib import Path

from skill_registry_rag.registry import load_registry
from skill_registry_rag.retriever import SkillRetriever


def _load_cards():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "experts.yaml"
    return load_registry(registry_path)


def _load_json_cards():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "examples" / "registry" / "tools.enriched.json"
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
