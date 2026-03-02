# SkillMesh Real Benchmark (10 Tasks, top-k=5/3/1, Chroma+RRF Weighted)

Date: 2026-03-02

## Setup

- SkillMesh version: 0.4.0
- Provider format: codex
- Retrieval backend: chroma (dense + BM25 weighted hybrid, sparse=0.8 dense=0.2)
- Full registry cards: 154
- Installed role registry cards: 62
- Installed roles: Analytics-Engineer, Machine-Learning-Engineer, DevOps-Engineer
- Token metric: exact `cl100k_base` tokens on emitted codex context text

## Aggregate Results

| Config ID | Config | Avg Prompt Tokens | Median Latency (s) | Avg Quality Proxy (1-5) | Top-1 Role Match | Top-5 Role Match | Delta Tokens vs A | Delta Latency vs A |
|---|---|---:|---:|---:|---|---|---:|---:|
| A | All-cards baseline (full catalog, top-k=all, chroma+RRF weighted) | 5719.9 | 0.130 | 4.9 | 9/10 | 10/10 | 0.0% | 0.0% |
| B5 | Routed (full catalog, top-k=5, chroma+RRF weighted) | 1533.0 | 0.126 | 4.9 | 9/10 | 10/10 | -73.2% | -2.7% |
| B3 | Routed (full catalog, top-k=3, chroma+RRF weighted) | 964.7 | 0.126 | 4.9 | 9/10 | 10/10 | -83.1% | -2.7% |
| B1 | Routed (full catalog, top-k=1, chroma+RRF weighted) | 412.7 | 0.126 | 4.7 | 9/10 | 9/10 | -92.8% | -2.7% |
| C5 | Role+Routed (installed roles, top-k=5, chroma+RRF weighted) | 1474.9 | 0.126 | 5.0 | 10/10 | 10/10 | -74.2% | -3.1% |
| C3 | Role+Routed (installed roles, top-k=3, chroma+RRF weighted) | 914.8 | 0.126 | 5.0 | 10/10 | 10/10 | -84.0% | -2.7% |
| C1 | Role+Routed (installed roles, top-k=1, chroma+RRF weighted) | 395.1 | 0.126 | 5.0 | 10/10 | 10/10 | -93.1% | -3.1% |

## Human Eval Summary (Completed Sheets)

| Config ID | Config | N Ratings | Avg Quality (1-5) | Median | Top-Box (>=4) |
|---|---|---:|---:|---:|---:|
| A | All-cards baseline (full catalog, top-k=all, chroma+RRF weighted) | 20 | 4.9 | 5.0 | 100.0% |
| B5 | Routed (full catalog, top-k=5, chroma+RRF weighted) | 20 | 4.9 | 5.0 | 100.0% |
| B3 | Routed (full catalog, top-k=3, chroma+RRF weighted) | 20 | 4.9 | 5.0 | 100.0% |
| B1 | Routed (full catalog, top-k=1, chroma+RRF weighted) | 20 | 4.7 | 5.0 | 90.0% |
| C5 | Role+Routed (installed roles, top-k=5, chroma+RRF weighted) | 20 | 5.0 | 5.0 | 100.0% |
| C3 | Role+Routed (installed roles, top-k=3, chroma+RRF weighted) | 20 | 5.0 | 5.0 | 100.0% |
| C1 | Role+Routed (installed roles, top-k=1, chroma+RRF weighted) | 20 | 5.0 | 5.0 | 100.0% |

## Notes

- Quality proxy: 5=expected role at rank1, 4=expected role in top5, 2=missing.
- Latency is measured in-process per task+config: load registry + build retriever + retrieve + render context.
- Chroma backend now honors `use_dense`; this run uses weighted hybrid with broader dense candidate pool.
- Current rater sheets were seeded from `quality_proxy` (`notes=seeded from quality_proxy`) to validate the human-eval pipeline end-to-end.

## Artifacts

- Raw CSV: `/home/varun/my_workspace/researchers/SkillMesh/docs/benchmarks/2026-03-02-topk-531-10task-chroma-rrf.csv`
- Human eval template: `/home/varun/my_workspace/researchers/SkillMesh/docs/benchmarks/2026-03-02-topk-531-10task-chroma-rrf.human-eval.template.csv`
- Human eval key: `/home/varun/my_workspace/researchers/SkillMesh/docs/benchmarks/2026-03-02-topk-531-10task-chroma-rrf.human-eval.key.csv`
- Human eval combined ratings: `/home/varun/my_workspace/researchers/SkillMesh/docs/benchmarks/2026-03-02-topk-531-10task-chroma-rrf.human-eval.combined.csv`
- Human eval summary CSV: `/home/varun/my_workspace/researchers/SkillMesh/docs/benchmarks/2026-03-02-topk-531-10task-chroma-rrf.human-eval.summary.csv`
- Human eval summary MD: `/home/varun/my_workspace/researchers/SkillMesh/docs/benchmarks/2026-03-02-topk-531-10task-chroma-rrf.human-eval.summary.md`
