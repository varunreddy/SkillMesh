# Scikit-learn Regularized Regression Expert (L1/L2/ElasticNet)

Use this expert when regression tasks require coefficient shrinkage, sparse feature selection, or multicollinearity control.

## When to use this expert
- You need L1/L2 regularization for robust generalization.
- Features are correlated and ordinary least squares is unstable.
- You want sparse coefficients (`Lasso`) or blended penalties (`ElasticNet`).

## Execution behavior
1. Build a leakage-safe `Pipeline` with numeric scaling and categorical encoding.
2. Start with `Ridge`, `Lasso`, and `ElasticNet` baselines.
3. Select regularization strength with cross-validation:
   - `RidgeCV`
   - `LassoCV`
   - `ElasticNetCV`
4. Tune `alpha` on log scale and `l1_ratio` for ElasticNet.
5. Compare models on MAE/RMSE and coefficient stability.
6. Validate residual diagnostics and error by important cohorts.
7. Persist the best pipeline and selected hyperparameters.

## Decision tree
- If many weak but useful correlated features -> prefer `Ridge`.
- If feature selection is required -> prefer `Lasso` or `ElasticNet`.
- If `Lasso` is unstable across folds -> move to `ElasticNet` with moderate `l1_ratio`.
- If outliers dominate error -> combine with robust preprocessing and compare against `HuberRegressor`.

## Anti-patterns
- NEVER choose alpha from test-set performance.
- NEVER interpret zeroed coefficients as causal evidence.
- NEVER skip feature scaling for penalized linear models.

## Common mistakes
- Searching only one or two alpha values.
- Reporting only one metric when business impact depends on tails.
- Ignoring coefficient sign flips across CV folds.

## Output contract
- Provide chosen model (`Ridge`/`Lasso`/`ElasticNet`) and tuned hyperparameters.
- Report MAE, RMSE, and fold variance.
- Include coefficient summary with retained/dropped feature counts.
- Document tradeoffs between sparsity and predictive error.

## Composability hints
- Before this expert -> use **Feature Engineering for ML** for robust transforms.
- After this expert -> use **Statistical Model Diagnostics** for heteroskedasticity and residual checks.
- Related -> **Scikit-learn Modeling and Evaluation** for broader model comparisons.
