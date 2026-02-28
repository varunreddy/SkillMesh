# Claude Code Integration

SkillMesh can be used in Claude Code by calling the router script and asking Claude to follow only returned top-K capabilities.

## 1) Install the skill bundle in Codex-style layout

```bash
$skill-installer install https://github.com/varunreddy/SkillMesh/tree/main/skills/skillmesh
```

Restart Codex after install.

## 2) Route for Claude output format

```bash
~/.codex/skills/skillmesh/scripts/route.sh \
  --provider claude \
  --backend auto \
  --registry /absolute/path/to/tools.json \
  --query "build an opencv contour pipeline" \
  --top-k 5
```

## 3) Use in Claude Code workflow

- Run the command above.
- Paste the returned XML block into Claude Code.
- Ask Claude to proceed using only those top-5 cards/tools.

## Optional helper alias

```bash
alias skillmesh-claude='~/.codex/skills/skillmesh/scripts/route.sh --provider claude --top-k 5'
```

Then run:

```bash
skillmesh-claude --registry /path/to/tools.json --query "your task"
```
