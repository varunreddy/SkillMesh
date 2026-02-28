# Codex Integration

Install SkillMesh as a native Codex skill and route large task requests to top-K cards.

## 1) Install the stable skill bundle

```bash
$skill-installer install https://github.com/varunreddy/SkillMesh/tree/main/skills/skillmesh
```

Restart Codex after install.

## 2) Configure a registry path (recommended)

```bash
export SKILLMESH_REGISTRY=/absolute/path/to/tools.json
```

## 3) Route requests with SkillMesh

```bash
~/.codex/skills/skillmesh/scripts/route.sh \
  --provider codex \
  --backend auto \
  --query "build a secure FastAPI service with JWT auth and SQLAlchemy" \
  --top-k 5
```

## 4) Continue with routed context only

- Keep the emitted context block in the conversation.
- Ask Codex to proceed using only the returned cards.

## Optional flags

- `--registry <path>`: Override `SKILLMESH_REGISTRY`.
- `--backend auto|memory|chroma`: Choose retrieval backend.
- `--dense`: Enable optional dense reranking.
- `--instruction-chars <n>`: Cap instruction snippet length per card.
