# SkillMesh Initial Smoke Benchmark (2026-03-01)

Scope: 3-task quick benchmark comparing full-catalog routing vs role-installed routing.

## Setup

- SkillMesh version: 0.3.0
- Provider format: codex
- Retrieval backend: memory
- Full registry: `examples/registry/tools.json`
- Installed registry: `/tmp/skillmesh-benchmark.registry.yaml`
- Installed roles: `Analytics-Engineer`, `Machine-Learning-Engineer`, `DevOps-Engineer`

## Raw Results

| Task ID | Domain | Config | Prompt Tokens (proxy) | Latency (s) | Expected Role Match | Quality Proxy (1-5) |
|---|---|---|---:|---:|---|---:|
| T01 | BI | Routed (full catalog) | 1746.8 | 0.782 | yes | 5 |
| T01 | BI | Role+Routed (installed roles) | 1701.5 | 0.176 | yes | 5 |
| T02 | ML | Routed (full catalog) | 1699.2 | 0.783 | yes | 5 |
| T02 | ML | Role+Routed (installed roles) | 1654.0 | 0.171 | yes | 5 |
| T03 | DevOps | Routed (full catalog) | 1567.8 | 0.769 | yes | 5 |
| T03 | DevOps | Role+Routed (installed roles) | 1557.8 | 0.176 | yes | 5 |

## Aggregate

| Config | Avg Prompt Tokens (proxy) | Median Latency (s) | Avg Quality Proxy | Role Match Rate |
|---|---:|---:|---:|---|
| Routed (full catalog) | 1671.3 | 0.782 | 5.0 | 3/3 |
| Role+Routed (installed roles) | 1637.8 | 0.176 | 5.0 | 3/3 |

## Notes

- Token metric is an offline proxy: `len(output_chars)/4`.
- Quality score is a proxy based on expected-role presence in top-K output, not human judgment.
- Next step: run 10-20 tasks with human-rated quality and publish deltas vs baseline all-tools prompting.
