# SkillMesh Benchmark Template

Use this template to report reproducible, apples-to-apples comparisons between:
- baseline: load many/all tools directly
- SkillMesh routed: top-K cards only
- SkillMesh role-installed + routed: installed role bundle, then top-K within that registry

---

## 1) Benchmark Metadata

- Date:
- Maintainer:
- SkillMesh version:
- Commit SHA:
- Model/runtime:
- Registry source:
- Number of cards in full catalog:
- Number of cards in installed role registry (if used):

## 2) Claims Being Tested

- C1: SkillMesh reduces prompt tokens.
- C2: SkillMesh improves or preserves task quality.
- C3: SkillMesh keeps latency comparable or better.

## 3) Environment

- OS:
- Python:
- CPU:
- RAM:
- Retrieval backend (`memory|chroma|auto`):
- Dense reranking enabled (`true|false`):

## 4) Task Set

Use 10-20 realistic tasks across domains. Keep wording fixed across all runs.

| Task ID | Domain | Prompt |
|---|---|---|
| T01 | BI | Build an executive KPI dashboard with governance and refresh policy |
| T02 | ML | Train baseline classifier and produce diagnostics |
| T03 | DevOps | Set up CI/CD, monitoring, and rollback strategy |
| ... | ... | ... |

## 5) Configurations Compared

### A) Baseline (all cards/tools exposed)
- Method:
- Effective cards in prompt:

### B) SkillMesh routed (full catalog -> top-K)
- Command pattern:
```bash
skillmesh emit --provider codex --registry <full-registry> --query "<task>" --top-k <k>
```
- K:

### C) SkillMesh role-installed + routed
- Install pattern:
```bash
skillmesh <Role-Name> install --registry <installed-registry>
```
- Route pattern:
```bash
skillmesh emit --provider codex --registry <installed-registry> --query "<task>" --top-k <k>
```
- K:

## 6) Measurement Method

- Token count method:
- Latency method:
- Human eval workflow reference: `docs/benchmarks/human-eval.md`
- Quality rubric:
  - 1: wrong/incomplete
  - 3: mostly correct with gaps
  - 5: production-ready structure + key checks included
- Number of raters:
- Tie-break process:

## 7) Raw Results Table

One row per task per configuration.

| Task ID | Config | Prompt Tokens | Completion Tokens | Total Tokens | Latency (s) | Quality (1-5) | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| T01 | A |  |  |  |  |  |  |
| T01 | B |  |  |  |  |  |  |
| T01 | C |  |  |  |  |  |  |

## 8) Aggregated Summary

| Metric | Baseline (A) | Routed (B) | Role+Routed (C) | Delta B vs A | Delta C vs A |
|---|---:|---:|---:|---:|---:|
| Avg prompt tokens |  |  |  |  |  |
| Avg total tokens |  |  |  |  |  |
| Median latency (s) |  |  |  |  |  |
| Avg quality score |  |  |  |  |  |
| Win rate vs A | - |  |  | - | - |

## 9) Retrieval Accuracy Notes

Track whether top returned cards were actually appropriate.

| Task ID | Expected Role/Card(s) | Returned Top-K | Match? | Miss Diagnosis |
|---|---|---|---|---|
| T01 |  |  |  |  |

## 10) Key Findings (Copy-Paste for Launch Posts)

- Token reduction:
- Quality impact:
- Latency impact:
- Best-fit scenario for SkillMesh:
- Failure modes observed:

## 11) Repro Steps

```bash
# 1) Install
pip install -e .[dev]

# 2) (Optional) prepare role-installed registry
skillmesh Data-Analyst install --registry /tmp/skillmesh-installed.registry.yaml

# 3) Run retrieval/routing for each task and capture metrics
skillmesh emit --provider codex --registry examples/registry/tools.json --query "<task>" --top-k 5
```

## 12) Artifact Checklist

- [ ] Raw CSV or JSON attached
- [ ] Commands used attached
- [ ] Environment details attached
- [ ] At least 10 tasks
- [ ] Mean + median reported
- [ ] Outliers explained
- [ ] One screenshot/clip for external sharing

---

## Appendix A: CSV Header Template

```csv
task_id,config,prompt_tokens,completion_tokens,total_tokens,latency_seconds,quality_score,notes
```
