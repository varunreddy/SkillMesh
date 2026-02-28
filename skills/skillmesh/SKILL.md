---
name: skillmesh
description: Retrieve the most relevant SkillMesh cards from a registry and inject a Codex-ready context block before coding. Use when a task spans many domains and you want top-K routing instead of loading the full skill catalog.
---

## How to use
- Ask: `Route this request with SkillMesh: <your task>`
- Run the router script to emit routed context.
- Continue the task using only the returned top-K cards.

## Command
Use `scripts/route.sh` (or `scripts/route.py`) to emit context:

```bash
scripts/route.sh --provider codex --registry <path> --query "<query>" --top-k 5
```

## Parameters
- `--registry`: Registry file path (`tools.yaml`, `tools.json`, or `roles.registry.yaml`).
- `--provider`: `codex` (default) or `claude`.
- `--top-k`: Number of cards to retrieve (default `5`).
- `--backend`: `auto`, `memory`, or `chroma` (default `auto`).
- `--dense`: Enable optional dense reranking.
- `--instruction-chars`: Max instruction chars per expert (default `700`).
- `--query`: User request text.

## Notes
- If `--registry` is omitted, the router uses `SKILLMESH_REGISTRY`.
- If `skillmesh` is not on `PATH`, the router falls back to `python -m skill_registry_rag`.
