# Claude Code Integration

SkillGate can be used in Claude Code by calling the router script and asking Claude to follow only returned top-K capabilities.

## 1) Install the skill bundle in Codex-style layout

```bash
$skill-installer install https://github.com/varunreddy/SkillGate/tree/main/skills/skillgate-router
```

Restart Codex after install.

## 2) Route for Claude output format

```bash
~/.codex/skills/skillgate-router/scripts/route.sh \
  --provider claude \
  --backend auto \
  --registry /absolute/path/to/tools.enriched.json \
  --query "build an opencv contour pipeline" \
  --top-k 5
```

## 3) Use in Claude Code workflow

- Run the command above.
- Paste the returned XML block into Claude Code.
- Ask Claude to proceed using only those top-5 experts/tools.

## Optional helper alias

```bash
alias skillgate-claude='~/.codex/skills/skillgate-router/scripts/route.sh --provider claude --top-k 5'
```

Then run:

```bash
skillgate-claude --registry /path/to/tools.enriched.json --query "your task"
```
