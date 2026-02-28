# SkillGate

A retrieval-gated skill architecture for LLM agents that scales to hundreds of tools by exposing only the top-K relevant capabilities per request.

SkillGate separates behavior from routing:

- `SKILL.md` and expert instruction files define behavior.
- A registry (`tools.enriched.json` or `experts.yaml`) defines retrieval metadata.
- A retriever selects only the best-matching expert cards per request.
- Provider adapters emit agent-ready context for Codex or Claude.

## Why SkillGate

Traditional "all skills in one prompt" setups do not scale. SkillGate keeps prompts small and precise by retrieving only what is relevant at runtime.

This gives you:

- Lower context usage
- Better tool selection consistency
- Cleaner domain isolation for large skill catalogs

## Repository Layout

- `src/skill_registry_rag/models.py`: expert card models
- `src/skill_registry_rag/registry.py`: registry loading and schema validation
- `src/skill_registry_rag/retriever.py`: BM25 + optional dense retrieval
- `src/skill_registry_rag/adapters/`: provider formatters (`codex`, `claude`)
- `src/skill_registry_rag/cli.py`: `skill-rag` CLI
- `skills/skillgate-router/`: Codex-installable skill bundle (stable)
- `skills/.experimental/skillgate-router/`: Legacy compatibility path

## Install

```bash
git clone https://github.com/varunreddy/SkillGate.git
cd SkillGate
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Optional dense retrieval:

```bash
pip install -e .[dense]
```

## Quick CLI Usage

Retrieve top experts:

```bash
skill-rag retrieve \
  --registry examples/registry/tools.enriched.json \
  --query "create seaborn charts for trend and distribution" \
  --top-k 5
```

Emit Codex context:

```bash
skill-rag emit \
  --provider codex \
  --registry examples/registry/tools.enriched.json \
  --query "export sklearn model to onnx and joblib" \
  --top-k 5
```

Emit Claude context:

```bash
skill-rag emit \
  --provider claude \
  --registry examples/registry/tools.enriched.json \
  --query "build opencv contour detection pipeline" \
  --top-k 5
```

## Codex-Native Skill Bundle

SkillGate ships a Codex-installable skill at:

- `skills/skillgate-router`

Install via GitHub directory URL:

```bash
$skill-installer install https://github.com/varunreddy/SkillGate/tree/main/skills/skillgate-router
```

Restart Codex after installation.

Legacy install URL (still supported):

```bash
$skill-installer install https://github.com/varunreddy/SkillGate/tree/main/skills/.experimental/skillgate-router
```

## Use in Codex

### 1. Configure registry path (recommended)

```bash
export SKILLGATE_REGISTRY=/absolute/path/to/tools.enriched.json
```

### 2. Route a task through SkillGate

```bash
~/.codex/skills/skillgate-router/scripts/route.sh \
  --provider codex \
  --backend auto \
  --query "design a geospatial join workflow" \
  --top-k 5
```

You can also pass `--registry` directly if `SKILLGATE_REGISTRY` is not set.

### 3. Continue with top-K only

Paste/keep the returned context block in Codex and proceed using only the surfaced capabilities.

More details: `docs/integrations/codex.md`

Direct CLI alternative:

```bash
skill-rag emit --provider codex --registry "$SKILLGATE_REGISTRY" --query "<task>" --top-k 5
```

## Use in Claude Code

### 1. Emit Claude-formatted routed context

```bash
~/.codex/skills/skillgate-router/scripts/route.sh \
  --provider claude \
  --backend auto \
  --registry /absolute/path/to/tools.enriched.json \
  --query "train a pytorch model with mixed precision and checkpoints" \
  --top-k 5
```

### 2. Paste into Claude Code

Paste the emitted XML block into Claude Code.

### 3. Constrain execution

Prompt Claude to proceed using only those top-K tools/experts.

More details: `docs/integrations/claude-code.md`

## Use in Claude Desktop

Claude Desktop is MCP-first. SkillGate supports both immediate manual usage and MCP integration.

### Option A: Manual routing

```bash
skill-rag emit \
  --provider claude \
  --registry /absolute/path/to/tools.enriched.json \
  --query "your request" \
  --top-k 5
```

Paste output into Claude Desktop and continue with top-K constrained prompting.

### Option B: MCP wrapper (recommended)

Wrap this command in an MCP tool:

```bash
skill-rag emit --provider claude --registry <path> --query <query> --top-k 5
```

Expose a tool such as `route_with_skillgate(query, top_k=5)` and register it in Claude Desktop MCP config.

More details: `docs/integrations/claude-desktop.md`

## Registry and Schema

Recommended starting files:

- Enriched registry: `examples/registry/tools.enriched.json`
- JSON schema: `examples/registry/schema.json`

Expert cards can carry:

- Core identity (`id`, `title`, `domain`, `instruction_file`, `description`)
- Retrieval metadata (`tags`, `aliases`, `tool_hints`, `examples`)
- Governance metadata (`constraints`, `quality_checks`, `risk_level`, `maturity`, `metadata`)

## Troubleshooting

### `skill-rag: command not found`

Install into the active environment:

```bash
pip install -e .
```

### Missing registry path

Set env var or pass `--registry`:

```bash
export SKILLGATE_REGISTRY=/absolute/path/to/tools.enriched.json
```

### Codex does not detect new skill

Restart Codex after running `$skill-installer`.

### Push denied for workflow changes

Ensure your GitHub token has `workflow` scope.

## Development

```bash
ruff check src tests
pytest
```

## License

MIT
