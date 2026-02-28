# Codex Integration

Install SkillGate as a native Codex skill and route large task requests to top-K experts.

## 1) Install the stable skill bundle

```bash
$skill-installer install https://github.com/varunreddy/SkillGate/tree/main/skills/skillgate-router
```

Restart Codex after install.

## 2) Configure a registry path (recommended)

```bash
export SKILLGATE_REGISTRY=/absolute/path/to/tools.enriched.json
```

## 3) Route requests with SkillGate

```bash
~/.codex/skills/skillgate-router/scripts/route.sh \
  --provider codex \
  --backend auto \
  --query "build a secure FastAPI service with JWT auth and SQLAlchemy" \
  --top-k 5
```

## 4) Continue with routed context only

- Keep the emitted context block in the conversation.
- Ask Codex to proceed using only the returned expert cards.

## Optional flags

- `--registry <path>`: Override `SKILLGATE_REGISTRY`.
- `--backend auto|memory|chroma`: Choose retrieval backend.
- `--dense`: Enable optional dense reranking.
- `--instruction-chars <n>`: Cap instruction snippet length per expert.
