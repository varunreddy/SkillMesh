# Claude Desktop Integration

SkillMesh ships a native MCP server (`skillmesh-mcp`) for Claude Desktop.

## Option A: Zero-config install with uvx (recommended)

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

### 1) Add SkillMesh MCP server to Claude Desktop

Edit your Claude Desktop MCP config and add:

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

No env vars or file paths needed — the bundled registry is included in the package.

### 2) Restart Claude Desktop

After restart, Claude can call these MCP tools:

- `route_with_skillmesh(query, top_k=5, provider="claude")`
- `retrieve_skillmesh_cards(query, top_k=5)`

## Option B: Manual install from source

### 1) Install MCP support

```bash
pip install -e .[mcp]
```

### 2) Add SkillMesh MCP server to Claude Desktop

Edit Claude Desktop MCP config (platform path may vary) and add:

```json
{
  "mcpServers": {
    "skillmesh": {
      "command": "/absolute/path/to/.venv/bin/skillmesh-mcp",
      "args": [],
      "env": {
        "SKILLMESH_REGISTRY": "/absolute/path/to/tools.json"
      }
    }
  }
}
```

Alternative command if you prefer module execution:

```json
{
  "command": "/absolute/path/to/.venv/bin/python",
  "args": ["-m", "skill_registry_rag.mcp_server"]
}
```

### 3) Restart Claude Desktop

Typical config locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Example prompt in Claude Desktop

`Use route_with_skillmesh for: clean noisy sales data, train a baseline model, and create charts.`

## Notes

- Registry can be set per tool call (`registry=...`) or globally via `SKILLMESH_REGISTRY`.
- When neither is set, the bundled registry is used automatically.
- For local/testing only, set `SKILLMESH_MCP_TRANSPORT` if you need a transport other than `stdio`.
