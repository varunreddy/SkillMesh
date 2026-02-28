# Claude Desktop Integration

Claude Desktop integration is MCP-based. SkillGate can be used today in two ways:

## Option A: Manual (works immediately)

1. Run SkillGate router in Claude format:

```bash
skill-rag emit \
  --provider claude \
  --registry /absolute/path/to/tools.enriched.json \
  --query "your request" \
  --top-k 5
```

2. Paste the emitted block into Claude Desktop.
3. Continue prompting with: "Use only the above top-5 capabilities."

## Option B: MCP wrapper (recommended for full tooling)

Build a thin MCP server that wraps:

```bash
skill-rag emit --provider claude --registry <path> --query <query> --top-k 5
```

Expose one MCP tool, e.g. `route_with_skillgate(query, top_k=5)`.

Then add that MCP server to Claude Desktop config and call it from chat.

## Notes

- Keep registry paths absolute in desktop environments.
- Use `tools.enriched.json` for best routing quality.
- Version-control your registry so routing stays deterministic.
