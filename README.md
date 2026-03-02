# SkillMesh

[![CI](https://github.com/varunreddy/SkillMesh/actions/workflows/ci.yml/badge.svg)](https://github.com/varunreddy/SkillMesh/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**Stop stuffing hundreds of tools into your LLM prompt. Route to the right ones.**

SkillMesh is a retrieval router for agent tool catalogs. Instead of loading every skill/tool into every prompt, it selects the best few cards for the query and injects only those.

## Why Teams Adopt SkillMesh

- Keeps prompts small as your catalog grows (top-K instead of full dump)
- Improves tool selection quality on multi-domain tasks
- Cuts token cost per call by avoiding irrelevant tool context
- Works with Claude (MCP), Codex (skill bundle), and local CLI workflows
- Standardized OpenAI-style function schemas for tool expansion

## The Problem

LLM agents break when you load every tool into the prompt. Token counts explode, accuracy drops, and cost scales linearly with your catalog size. Teams with 50+ skills end up with bloated system prompts that confuse the model and burn budget.

SkillMesh solves this with retrieval-based routing: given a user query, it selects only the top-K most relevant expert cards and injects them into the prompt — keeping context small, accurate, and cheap.

## High-Value Use Cases

- Internal AI assistants with large tool/skill catalogs (50+ cards)
- Multi-step workflows crossing domains (data -> ML -> infra -> reporting)
- Teams using MCP where tool overload hurts selection quality
- Role-based execution flows (`Data-Analyst`, `Financial-Analyst`, `AWS-Engineer`)

## SkillMesh vs Static Skill Docs

| | Static `SKILL.md` only | SkillMesh routing |
|---|---|---|
| Prompt strategy | Load broad instructions every turn | Inject only relevant top-K cards |
| Scale behavior | Gets noisy as catalog grows | Remains focused with retrieval |
| Multi-domain tasks | Manual tool prompting | Query-driven cross-domain routing |
| Expansion | Add docs and hope model picks right one | Add cards + retrieval handles selection |

## Before vs After

| | Without SkillMesh | With SkillMesh |
|---|---|---|
| **Prompt tokens** | ~50,000+ (all tools loaded) | ~3,000 (top-K only) |
| **Tool selection** | Model guesses from a huge list | BM25+Dense retrieval picks the best match |
| **Cost per call** | High (full catalog every time) | Low (only relevant cards) |
| **Accuracy** | Degrades as catalog grows | Stays consistent |
| **Multi-domain tasks** | Confusing for the model | Routed precisely (clean + train + deploy) |

## How It Works

```
User Query
    │
    ▼
┌─────────────────────┐
│  BM25 + Dense Index  │  ← Scores every card in your registry
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   RRF Fusion Rank    │  ← Merges sparse + dense rankings
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Top-K Card Select  │  ← Returns the K best expert cards
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Agent acts as expert │  ← Full instructions injected into prompt
└─────────────────────┘
```

Each card contains: execution behavior, decision trees, anti-patterns, output contracts, and composability hints — everything the agent needs to act as a domain expert.

## One-line MCP install (Claude Desktop / Claude Code)

Add this to your Claude Desktop config (`claude_desktop_config.json`) or Claude Code MCP settings:

```json
{
  "mcpServers": {
    "skillmesh": {
      "command": "uvx",
      "args": ["--from", "skillmesh[mcp]", "skillmesh-mcp"]
    }
  }
}
```

No env vars. No file paths. No cloning. The bundled registry is included in the package.

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) to be installed.

## 60-Second Demo

```bash
git clone https://github.com/varunreddy/SkillMesh.git
cd SkillMesh
pip install -e .
skillmesh emit \
  --provider claude \
  --registry examples/registry/tools.json \
  --query "clean messy sales data, train a baseline model, and generate charts" \
  --top-k 5
```

Output (truncated):

```
<context>
  <card id="data.data-cleaning" title="Data Cleaning and Validation Expert">
    # Data Cleaning and Validation Expert
    Specialist in detecting and correcting data quality issues...
  </card>
  <card id="ml.sklearn-modeling" title="Scikit-learn Modeling and Evaluation">
    ...
  </card>
  <card id="viz.matplotlib-seaborn" title="Visualization with Matplotlib and Seaborn">
    ...
  </card>
</context>
```

Only the relevant experts are injected — the rest of the 100+ card catalog stays out of the prompt.

## Integrations

| Platform | Method | Status | Docs |
|---|---|---|---|
| **Claude Code** | MCP server | Supported | [Setup guide](docs/integrations/claude-code.md) |
| **Claude Desktop** | MCP server | Supported | [Setup guide](docs/integrations/claude-desktop.md) |
| **Codex** | Skill bundle | Supported | [Setup guide](docs/integrations/codex.md) |

### Claude MCP Server

The easiest way to run it is via `uvx` (see "One-line MCP install" above). For local development:

```bash
pip install -e .[mcp]
skillmesh-mcp
```

The server auto-discovers the registry: env var `SKILLMESH_REGISTRY` → repo root → bundled registry.

Exposes five tools via MCP:
- `route_with_skillmesh(query, top_k)` — provider-formatted context block
- `retrieve_skillmesh_cards(query, top_k)` — structured JSON payload
- `list_skillmesh_roles(catalog?, registry?)` — full role list with installed status
- `list_installed_skillmesh_roles(catalog?, registry?)` — installed roles only
- `install_skillmesh_role(role, catalog?, registry?, dry_run?)` — install by id or friendly name (for example `Data-Analyst`)

Copy-ready config templates in `examples/mcp/`.

### Codex Skill Bundle

```bash
$skill-installer install https://github.com/varunreddy/SkillMesh/tree/main/skills/skillmesh
```

Direct role commands in SkillMesh:

```bash
skillmesh roles
skillmesh roles list
skillmesh Data-Analyst install
skillmesh roles install Data-Analyst
```

Or via installed bundle wrapper:

```bash
~/.codex/skills/skillmesh/scripts/roles.sh
~/.codex/skills/skillmesh/scripts/roles.sh list
~/.codex/skills/skillmesh/scripts/roles.sh install --role-id role.data-engineer
```

## Quickstart

### Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

Optional extras:

```bash
pip install -e .[dense]   # Dense reranking with sentence-transformers
pip install -e .[mcp]     # Claude MCP server
```

### Retrieve top-K cards

```bash
skillmesh retrieve \
  --registry examples/registry/tools.json \
  --query "set up nginx reverse proxy with SSL" \
  --top-k 3
```

### Emit provider-ready context

```bash
skillmesh emit \
  --provider claude \
  --registry examples/registry/tools.json \
  --query "deploy container to GCP Cloud Run" \
  --top-k 5
```

## Curated Registries

Use domain-specific registries for tighter routing:

| Registry | Domain | Cards |
|---|---|---|
| `tools.json` / `tools.yaml` | Full catalog | 103 |
| `ml-engineering.registry.yaml` | ML training & evaluation | 15 |
| `data-engineering.registry.yaml` | Pipelines & data platforms | 10 |
| `bi-analytics.registry.yaml` | BI & dashboards | 12 |
| `devops.registry.yaml` | DevOps & infrastructure | 8 |
| `web-apis.registry.yaml` | API design & patterns | 7 |
| `cloud-gcp.registry.yaml` | Google Cloud Platform | 7 |
| `cloud-bi.registry.yaml` | Cloud BI | 17 |
| `roles.registry.yaml` | Role orchestrators | 11 |

```bash
skillmesh emit \
  --provider claude \
  --registry examples/registry/devops.registry.yaml \
  --query "configure prometheus alerting and grafana dashboards" \
  --top-k 3
```

## Benchmarking

Use the reproducible benchmark template:
- [Benchmark template](docs/benchmarks/benchmark-template.md)
- [Human eval workflow](docs/benchmarks/human-eval.md)

## CLI Commands

| Command | Description |
|---|---|
| `skillmesh retrieve` | Top-K retrieval payload (JSON) |
| `skillmesh fetch` | Alias for `retrieve` (supports free-text query shorthand) |
| `skillmesh emit` | Provider-formatted context block |
| `skillmesh index` | Index registry into Chroma for persistent retrieval |
| `skillmesh roles wizard` | Interactive role picker and installer |
| `skillmesh roles list` | List available role cards from a catalog |
| `skillmesh roles install` | Install role card + missing dependency cards into target registry |
| `skillmesh role` | Alias for `roles` |
| `skillmesh-mcp` | Stdio MCP server for Claude |

`skillmesh retrieve`/MCP payloads include `invocation` in OpenAI function-tool format for every card.

```bash
skillmesh --help
```

## Repository Layout

```
src/skill_registry_rag/
├── models.py          # Tool/role card models
├── registry.py        # Registry loading + validation
├── retriever.py       # BM25 + optional dense retrieval
├── adapters/          # Provider formatters (codex, claude)
└── cli.py             # skillmesh CLI

examples/registry/
├── tools.json         # Full tool catalog
├── tools.yaml         # YAML version of full catalog
├── instructions/      # Expert instruction files (90+)
├── roles/             # Role orchestrator files
└── *.registry.yaml    # Domain-specific registries

skills/skillmesh/      # Codex-installable skill
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add expert cards, create registries, and submit PRs.

## Troubleshooting

### `skillmesh: command not found`

```bash
pip install -e .
```

### Missing registry path

The CLI and MCP server auto-discover the registry. If auto-discovery fails, pass `--registry` or set:

```bash
export SKILLMESH_REGISTRY=/path/to/tools.json
# or pass --registry on every command
```

### `skillmesh-mcp` fails to start

```bash
pip install -e .[mcp]
```

### Codex does not detect new skill

Restart Codex after running `$skill-installer`.

## Development

```bash
ruff check src tests
pytest
```

## License

MIT — see [LICENSE](LICENSE).

---

If SkillMesh helps your team, please **star the repo** — it directly improves discoverability and helps others find the project.
