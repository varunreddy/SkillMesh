# expert-registry-rag

`expert-registry-rag` is an instruction-first skills runtime:

- `*.md` files hold behavior and guidance for the agent.
- A structured registry holds domain expert metadata and tool hints.
- A retriever returns top-k expert cards for a query.
- Provider adapters format the retrieved cards for Codex or Claude prompts.

This project is designed for teams that want reusable domain expertise without hardcoding giant prompt menus.

## Why this pattern

Traditional skill systems often overload markdown files with both:

1. Behavioral instructions
2. Discovery/index metadata

This project splits concerns:

1. Instruction files (`instructions/*.md`) only define behavior
2. Registry (`experts.yaml` or enriched JSON) defines retrieval metadata and pointers
3. Retriever picks relevant experts at runtime via BM25 + optional dense scoring

## Architecture

- `src/skill_registry_rag/models.py`: Expert card models
- `src/skill_registry_rag/registry.py`: Registry loading and validation
- `src/skill_registry_rag/retriever.py`: Top-k retrieval engine
- `src/skill_registry_rag/adapters/`: Prompt context rendering for providers
- `src/skill_registry_rag/cli.py`: CLI for retrieval and context emission

## Registry schema

Each expert card supports:

- `id`: stable identifier
- `title`: display name
- `domain`: domain label
- `instruction_file`: relative path to markdown instructions
- `description`: short purpose summary
- `tags`: retrieval and routing tags
- `tool_hints`: optional concrete imports/tool names
- `examples`: optional example intents
- `dependencies`: package/runtime dependencies
- `input_contract`: expected inputs and constraints
- `output_artifacts`: canonical outputs produced by the expert
- `quality_checks`: validation checklist
- `constraints`: guardrails and failure boundaries
- `risk_level`, `maturity`, `metadata`: operational governance fields

Recommended enriched sample registry:

- `examples/registry/tools.enriched.json`
- `examples/registry/schema.json` (validated by loader and tests)

Current sample catalog includes:

- Visualization (`matplotlib`, `seaborn`)
- ML export (`joblib`, `pickle`, `ONNX`)
- Scikit-learn modeling/evaluation
- Gradient boosting (`xgboost`, `lightgbm`, `catboost`, `shap`)
- Deep learning (`pytorch`)
- Statistical inference (`scipy`, `statsmodels`)
- Scientific computing (`scipy.optimize`, `scipy.signal`)
- Cheminformatics (`rdkit`)
- Graph analytics (`networkx`)
- Computer vision (`opencv`)
- Geospatial analysis (`geopandas`, `shapely`)
- NLP (`spacy`, `transformers`)
- PDF generation
- Slide deck generation (`python-pptx`)
- Data cleaning/schema normalization

## Quickstart

```bash
cd expert-registry-rag
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Retrieve top experts:

```bash
skill-rag retrieve \
  --registry examples/registry/tools.enriched.json \
  --query "create seaborn charts for trend and distribution analysis" \
  --top-k 3
```

Emit Codex context block:

```bash
skill-rag emit \
  --provider codex \
  --registry examples/registry/tools.enriched.json \
  --query "export sklearn model to onnx and joblib with metadata" \
  --top-k 2
```

Emit Claude context block:

```bash
skill-rag emit \
  --provider claude \
  --registry examples/registry/tools.enriched.json \
  --query "generate a powerpoint deck from analysis findings" \
  --top-k 2
```

## Dense retrieval (optional)

Install with dense extras:

```bash
pip install -e .[dense]
```

Then pass `--dense` to CLI commands.

## Running tests

```bash
pytest
```

## OSS roadmap

1. Add pluggable vector backends (FAISS, Qdrant, pgvector)
2. Add telemetry hooks (hit@k, precision@k, override rate)
3. Add policy filters (allowed tools per environment)
4. Add hosted registry API mode

## License

MIT
