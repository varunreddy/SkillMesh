# Scikit-learn Tree and Forest Models Expert

Use this expert for decision trees and bagging-style tree ensembles in sklearn, including feature importance diagnostics and overfitting control.

## When to use this expert
- The task benefits from non-linear tabular modeling with moderate interpretability.
- You need `DecisionTree`, `RandomForest`, or `ExtraTrees` baselines.
- You want robust performance without external boosting frameworks.

## Execution behavior
1. Build a consistent preprocessing pipeline (tree-safe encoding, missing-value handling).
2. Train a simple `DecisionTree` baseline first.
3. Expand to `RandomForest`/`ExtraTrees` for variance reduction.
4. Tune depth and node controls (`max_depth`, `min_samples_leaf`, `min_samples_split`).
5. Evaluate with cross-validation and holdout metrics.
6. Use permutation importance as default importance signal.
7. Check calibration and subgroup error behavior before release.

## Decision tree
- If dataset is small and noisy -> constrain depth aggressively.
- If variance is high -> increase trees and use `RandomForest`.
- If speed is priority -> use `ExtraTrees` with controlled depth.
- If interpretability is strict -> keep a shallow single-tree surrogate for explanation.

## Anti-patterns
- NEVER trust training-set impurity importance alone.
- NEVER leave depth unconstrained on small datasets.
- NEVER ship a tree model without stability checks across seeds/folds.

## Common mistakes
- Setting too few trees for forest models and reading unstable metrics.
- Ignoring class imbalance in classification tasks.
- Reporting AUC without threshold-dependent metrics when threshold matters.

## Output contract
- Provide model family and tuned hyperparameters.
- Report CV + holdout metrics and calibration status.
- Include permutation importance and key error cohorts.
- Document operational limits and retraining triggers.

## Composability hints
- Before this expert -> use **Feature Engineering for ML** for clean tabular inputs.
- After this expert -> use **Scikit-learn Pipeline Ops** for packaging and threshold policy.
- Related -> **Gradient Boosting with XGBoost and LightGBM** for higher-capacity alternatives.
