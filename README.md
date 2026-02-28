# SkillMesh

Route LLM agents to the right tools at runtime instead of loading your full skill catalog into every prompt.

SkillMesh is built for teams running many skills or functions (data cleaning, modeling, cloud, infra, visualization) and needing predictable top-K routing.

## Why teams adopt SkillMesh

- Prompt size stays small as your catalog grows.
- Tool selection gets more consistent across similar requests.
- Multi-domain tasks become easier to route (`clean + predict + visualize + deploy`).
- You can enforce governance metadata per tool/role card.

If this project helps you, please star the repo. It directly improves discoverability.

## 60-second local demo

```bash
git clone https://github.com/varunreddy/SkillMesh.git
cd SkillMesh
pip install -e .
skillmesh emit --provider codex --registry examples/registry/tools.json --query "clean messy sales data, train a baseline model, and generate charts" --top-k 5
```

You should see a routed context block with the top cards and their instructions.

## Quickstart

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Optional dense reranking:

```bash
pip install -e .[dense]
```

Optional Claude MCP server:

```bash
pip install -e .[mcp]
```

### 2) Retrieve tool/role cards

```bash
skillmesh retrieve \
  --registry examples/registry/tools.json \
  --query "create seaborn charts for trend and distribution" \
  --top-k 5
```

### 3) Emit provider-ready context

```bash
skillmesh emit \
  --provider codex \
  --registry examples/registry/tools.json \
  --query "export sklearn model to onnx and joblib" \
  --top-k 5
```

## Codex skill bundle

SkillMesh ships a Codex-installable skill at `skills/skillmesh`.

Install:

```bash
$skill-installer install https://github.com/varunreddy/SkillMesh/tree/main/skills/skillmesh
```

Then route tasks:

```bash
~/.codex/skills/skillmesh/scripts/route.sh \
  --provider codex \
  --registry /absolute/path/to/tools.json \
  --query "design a geospatial join workflow" \
  --top-k 5
```

You can set a default registry with:

```bash
export SKILLMESH_REGISTRY=/absolute/path/to/tools.json
```

## Integrations

- Codex: `docs/integrations/codex.md`
- Claude Code: `docs/integrations/claude-code.md`
- Claude Desktop: `docs/integrations/claude-desktop.md`

## Claude MCP server

SkillMesh includes a native MCP server command: `skillmesh-mcp`.

```bash
export SKILLMESH_REGISTRY=/absolute/path/to/tools.json
skillmesh-mcp
```

Claude can call these tools through MCP:

- `route_with_skillmesh(...)`: provider-formatted routed context (`claude` or `codex`)
- `retrieve_skillmesh_cards(...)`: structured top-K payload

Full Claude Desktop setup is in `docs/integrations/claude-desktop.md`.
Copy-ready MCP config templates:

- `examples/mcp/claude-desktop.macos.json`
- `examples/mcp/claude-desktop.linux.json`
- `examples/mcp/claude-desktop.windows.json`

## Core concepts

- Behavior lives in `SKILL.md` and instruction files.
- Routing metadata lives in `examples/registry/tools.json` or `tools.yaml`.
- Retrieval layer selects only the most relevant cards.
- Adapters format output for Codex or Claude.

## CLI commands

- `skillmesh retrieve`: top-K retrieval payload (JSON)
- `skillmesh emit`: provider-formatted context block
- `skillmesh index`: index registry into Chroma for persistent retrieval
- `skillmesh-mcp`: stdio MCP server exposing `route_with_skillmesh` and `retrieve_skillmesh_cards`

Run help:

```bash
skillmesh --help
```

## Repository layout

- `src/skill_registry_rag/models.py`: tool/role card models
- `src/skill_registry_rag/registry.py`: registry loading + validation
- `src/skill_registry_rag/retriever.py`: BM25 + optional dense retrieval
- `src/skill_registry_rag/adapters/`: provider formatters (`codex`, `claude`)
- `src/skill_registry_rag/cli.py`: `skillmesh` CLI
- `skills/skillmesh/`: Codex-installable skill

## Real examples to try

- Query: `clean noisy tabular data and detect outliers`
- Query: `train pytorch model with checkpoints and mixed precision`
- Query: `connect Azure data source, build features, and publish dashboard`

Use the sample registry in `examples/registry/`.

## Curated registries

Use smaller registries when you want tighter routing for a specific workflow:

- `examples/registry/roles.registry.yaml`
- `examples/registry/ml-engineering.registry.yaml`
- `examples/registry/data-engineering.registry.yaml`
- `examples/registry/bi-analytics.registry.yaml`
- `examples/registry/cloud-bi.registry.yaml`

Example:

```bash
skillmesh emit \
  --provider codex \
  --registry examples/registry/ml-engineering.registry.yaml \
  --query "act as an ML engineer and build a reproducible sklearn pipeline with diagnostics" \
  --top-k 5
```

## Trust and contribution signals

- CI workflow: `.github/workflows/ci.yml`
- Tests: `tests/`
- Schema: `examples/registry/schema.json`
- Growth plan: `docs/plans/2026-02-28-growth-plan.md`

## Troubleshooting

### `skillmesh: command not found`

```bash
pip install -e .
```

### Missing registry path

Pass `--registry` or set:

```bash
export SKILLMESH_REGISTRY=/absolute/path/to/tools.json
```

### Codex does not detect new skill

Restart Codex after `$skill-installer`.

### `skillmesh-mcp` fails to start

```bash
pip install -e .[mcp]
```

## Development

```bash
ruff check src tests
pytest
```

## License

MIT
