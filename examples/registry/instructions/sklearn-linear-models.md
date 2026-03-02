# Scikit-learn Linear Models Expert

Use this expert for supervised tabular modeling with linear decision functions, including linear regression and linear classification baselines.

## When to use this expert
- You need an interpretable baseline for regression or classification.
- The task favors fast training, stable coefficients, and explainability.
- You want a leakage-safe pipeline using sklearn preprocessors plus a linear estimator.

## Execution behavior
1. Split data first (`train/validation/test`) before fitting preprocessors.
2. Build a `Pipeline` with scaling and encoding where needed.
3. Choose estimator family by task:
   - regression: `LinearRegression`, `HuberRegressor`, `QuantileRegressor`
   - classification: `LogisticRegression`, `SGDClassifier`, `LinearSVC`
4. Tune solver and optimization settings (`max_iter`, tolerance, class weights).
5. Report both aggregate metrics and slice-level metrics.
6. Inspect coefficient stability across folds before drawing conclusions.
7. Persist pipeline + metadata (`sklearn` version, feature names, seed).

## Decision tree
- If regression residuals are heavy-tailed -> try `HuberRegressor` or quantile regression.
- If classes are imbalanced -> use `class_weight="balanced"` and threshold tuning.
- If feature count is high -> use sparse-friendly linear models and strict regularization.
- If interpretability is the top priority -> prefer linear models before tree ensembles.

## Anti-patterns
- NEVER fit scalers or encoders on full data before split.
- NEVER compare models using only train scores.
- NEVER interpret coefficients without checking feature scaling and collinearity.

## Common mistakes
- Forgetting to standardize numerical features for linear classifiers.
- Using accuracy alone on imbalanced classification tasks.
- Ignoring convergence warnings from `LogisticRegression`/`SGDClassifier`.

## Output contract
- Provide pipeline definition and estimator settings.
- Report train/validation/test metrics with confidence intervals or fold variance.
- Include coefficient table (or top coefficients) with sign and magnitude interpretation.
- Document model limits and fallback candidate models.

## Composability hints
- Before this expert -> use **Feature Engineering for ML** for stable transforms.
- After this expert -> use **Statistical Model Diagnostics** for residual and calibration checks.
- Related -> **Scikit-learn Pipeline Ops** for production packaging and monitoring handoff.
