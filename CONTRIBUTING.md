# Contributing to SkillMesh

Thanks for your interest in contributing! SkillMesh grows by adding expert cards, registries, and roles that make LLM routing smarter across more domains.

## How to Add a New Expert Card

Expert cards are instruction files that tell an LLM how to behave as a domain specialist.

### 1. Create the instruction file

Add a Markdown file to `examples/registry/instructions/`. Use `docker.md` as a reference template.

**Required sections:**

```markdown
# {Expert Name} Expert

One-line description of the specialist.

## When to use this expert
- Bullet list of retrieval triggers

## Execution behavior
1. Numbered step-by-step workflow (6-8 steps)

## Decision tree
- If {condition} -> {action}

## Anti-patterns
- NEVER {prohibited behavior}

## Common mistakes
- {Mistake description and why it's wrong}

## Output contract
- {What the expert must produce}

## Composability hints
- Upstream: {expert} for {reason}
- Downstream: {expert} for {reason}
```

### 2. Add the card to a registry

Add an entry to the relevant `*.registry.yaml` file and to `tools.json` / `tools.yaml`.

**Registry YAML entry:**

```yaml
- id: {domain}.{function-name}
  title: {Human Readable Title}
  domain: {domain_category}
  instruction_file: instructions/{filename}.md
  tags:
  - tag1
  - tag2
```

**tools.json entry** (includes full metadata):

```json
{
  "id": "{domain}.{function-name}",
  "title": "{Human Readable Title}",
  "domain": "{domain_category}",
  "instruction_file": "instructions/{filename}.md",
  "description": "One-line retrieval description.",
  "tags": ["tag1", "tag2"],
  "tool_hints": ["library1", "library2"],
  "examples": ["Example query 1", "Example query 2"],
  "aliases": ["alt-name"],
  "dependencies": ["library1"],
  "input_contract": {
    "required": "what's needed",
    "optional": "what's optional"
  },
  "output_artifacts": ["artifact1"],
  "quality_checks": ["check1"],
  "constraints": ["constraint1"],
  "risk_level": "low",
  "maturity": "stable",
  "metadata": {
    "provider_support": ["codex", "claude"],
    "owner": "community"
  }
}
```

### 3. Test retrieval

```bash
skillmesh retrieve \
  --registry examples/registry/tools.json \
  --query "your expected query" \
  --top-k 3
```

Verify your new card appears in the results for relevant queries.

## How to Create a New Registry

Registries are domain-scoped subsets of the full catalog. Use `ml-engineering.registry.yaml` as a reference.

1. Create `examples/registry/{domain}.registry.yaml`
2. Add a `registry_name`, `version`, and `updated_at` header
3. List the tools (referencing existing instruction files)
4. Test with `skillmesh retrieve --registry examples/registry/{domain}.registry.yaml --query "..."  --top-k 3`

## How to Add a New Role

Roles are orchestrators that combine multiple expert cards. Use `roles/data-engineer.md` as a reference.

1. Create `examples/registry/roles/{role-name}.md`
2. Include sections: allowed expert dependencies, execution behavior, output contract, guardrails
3. Add the role to `roles.registry.yaml` with id format `role.{role-name}`
4. Add the role to `tools.json` and `tools.yaml`

## Code Style

- **Linting:** `ruff check src tests`
- **Testing:** `pytest`
- **Python:** 3.10+
- **Formatting:** Follow existing patterns in `src/`

## PR Process

1. Fork the repository
2. Create a feature branch: `git checkout -b add-{expert-name}-card`
3. Make your changes
4. Run `ruff check src tests && pytest`
5. Open a PR with a clear description of what you added

## Testing Changes

```bash
# Lint
ruff check src tests

# Unit tests
pytest

# Manual retrieval test
skillmesh retrieve \
  --registry examples/registry/tools.json \
  --query "your test query" \
  --top-k 5
```

For instruction files, verify that:
- All 8 sections are present
- Anti-patterns use NEVER prefix
- Composability hints reference real expert IDs
- The file is under 80 lines
