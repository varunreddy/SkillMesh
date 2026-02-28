---
name: skillgate-router
description: Retrieve the most relevant SkillGate expert cards from a registry and inject a Codex-ready context block before coding. Use when a task spans many domains and you want top-K routing instead of loading the full skill catalog.
---

## How to use
- Ask: `Route this request with SkillGate: <your task>`
- Run the router script to emit routed context.
- Continue the task using only the returned top-K cards.

## Command
Use `scripts/route.sh` (or `scripts/route.py`) to emit context:

```bash
scripts/route.sh --provider codex --registry <path> --query "<query>" --top-k 5
```

## Parameters
- `--registry`: Registry file path (`experts.yaml` or `tools.enriched.json`).
- `--provider`: `codex` (default) or `claude`.
- `--top-k`: Number of experts to retrieve (default `5`).
- `--backend`: `auto`, `memory`, or `chroma` (default `auto`).
- `--dense`: Enable optional dense reranking.
- `--instruction-chars`: Max instruction chars per expert (default `700`).
- `--query`: User request text.

## Notes
- If `--registry` is omitted, the router uses `SKILLGATE_REGISTRY` (or `SKILLMESH_REGISTRY`).
- If `skill-rag` is not on `PATH`, the router falls back to `python -m skill_registry_rag`.
