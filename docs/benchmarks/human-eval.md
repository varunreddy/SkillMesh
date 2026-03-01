# SkillMesh Human Evaluation Workflow

Use this when you want publishable quality claims (human judgment), not only automated proxies.

## Scope

This workflow scores retrieval quality for each benchmark variant (A/B/C) using blind ratings.

Quality rubric (1-5):
- `1`: mostly irrelevant cards
- `2`: some relevance but misses core role/task
- `3`: partially useful set with noticeable gaps
- `4`: mostly relevant set with minor gaps
- `5`: highly relevant set, expected role and key cards included

## 1) Prepare Blind Rating Sheet

```bash
python scripts/benchmark_human_eval.py prepare \
  --input-csv docs/benchmarks/2026-03-01-real-10task.csv \
  --output-template docs/benchmarks/2026-03-01-real-10task.human-eval.template.csv \
  --output-key docs/benchmarks/2026-03-01-real-10task.human-eval.key.csv \
  --seed 42
```

Outputs:
- `*.human-eval.template.csv`: share with each rater
- `*.human-eval.key.csv`: keep private until rating is complete

## 2) Collect Rater Files

Create one copy of the template per rater and fill `quality_score` + optional `notes`.

Example files:
- `docs/benchmarks/ratings/rater-varun.csv`
- `docs/benchmarks/ratings/rater-teammate.csv`

Required columns in each rating file:
- `item_id`
- `quality_score` (1-5)
- `rater_id` (optional, inferred from filename if blank)

## 3) Aggregate Results

```bash
python scripts/benchmark_human_eval.py aggregate \
  --key-csv docs/benchmarks/2026-03-01-real-10task.human-eval.key.csv \
  --ratings-csv docs/benchmarks/ratings/rater-varun.csv docs/benchmarks/ratings/rater-teammate.csv \
  --output-combined docs/benchmarks/2026-03-01-real-10task.human-eval.combined.csv \
  --output-summary-csv docs/benchmarks/2026-03-01-real-10task.human-eval.summary.csv \
  --output-summary-md docs/benchmarks/2026-03-01-real-10task.human-eval.summary.md
```

Generated artifacts:
- Combined row-level ratings CSV
- Config-level summary CSV
- Markdown report with per-config scores and inter-rater agreement

## 4) Reporting Recommendation

For external sharing, report both:
- automated metrics (tokens, latency, routing matches)
- human quality metrics (mean/median by config + agreement stats)

This prevents over-claiming from proxy-only evaluation.
