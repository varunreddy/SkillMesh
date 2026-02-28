---
name: skillgate-router
description: Retrieve top-5 relevant expert cards/tools from a registry and inject a Codex-ready context block.
---

## How to use
- Ask: `Route this request with SkillGate: <your task>`
- I will run the SkillGate retriever against the configured registry and return a context block.
- Then I will proceed using only the returned top-5 tools/cards.

## Command
Use `scripts/route.sh` (or `scripts/route.py`) to emit context:

```bash
skill-rag emit --provider codex --registry <path> --query "<query>" --top-k 5
```

## Parameters
- `--registry`: Path to your SkillGate registry (`experts.yaml` or `tools.enriched.json`).
- `--provider`: `codex` (default) or `claude`.
- `--top-k`: Number of cards to retrieve (default `5`).
- `--query`: User request to route.

## Notes
- If `--registry` is omitted, the router uses `SKILLGATE_REGISTRY` env var.
- For Claude integrations, run with `--provider claude`.
