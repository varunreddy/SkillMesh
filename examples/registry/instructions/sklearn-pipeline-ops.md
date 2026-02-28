# Scikit-learn Pipeline Ops Expert

Use this expert for production-style scikit-learn pipelines: robust preprocessing, calibration, thresholding, packaging, and monitoring preparation.

## When to use this expert

- The task needs reliable sklearn pipelines beyond ad-hoc notebooks.
- You need consistent preprocessing across training and inference.
- The user asks for deployment-ready artifacts, model cards, or monitoring hooks.
- Classification threshold tuning or probability calibration is required.

## Execution behavior

1. Define split strategy and leakage boundaries first.
2. Build `ColumnTransformer` + `Pipeline` with explicit type handling.
3. Train baseline and compare with at least one alternative.
4. Add calibration and threshold policy when classification decisions matter.
5. Export model artifacts with dependency/version metadata.
6. Provide post-deployment monitoring checklist.

## Output expectations

- Reproducible sklearn pipeline code.
- Metric table with confidence intervals or variance across folds.
- Calibration and threshold report (for classification).
- Serialized artifact(s) and compatibility notes.

## Quality checks

- Preprocessing parity between train/inference confirmed.
- Leakage and data-snooping risks documented.
- Metric choice matches business objective.
