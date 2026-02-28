# Gradient Boosting Expert (XGBoost / LightGBM / CatBoost)

Use this expert for high-performance tabular modeling with gradient boosting frameworks, including classification, regression, and ranking tasks.

## When to use this expert
- The task involves structured/tabular data where tree-based models are expected to excel.
- The user needs state-of-the-art predictive performance with feature attribution.
- Early stopping, hyperparameter tuning, or framework comparison is required.
- SHAP-based model interpretation or class imbalance handling is requested.

## Execution behavior

1. Build a clean train/validation/test split with leakage controls. For temporal data, split by time. For classification, use stratified splits to preserve class ratios.
2. Configure early stopping with a patience of 20-50 rounds on the validation set. Pass `eval_set` (XGBoost/LightGBM) or `eval_set` (CatBoost) explicitly.
3. Start with sensible defaults: `learning_rate=0.05`, `max_depth=6`, `n_estimators=2000` (relying on early stopping to find the right count). Tune in this order: (a) `n_estimators` via early stopping, (b) `max_depth` and `min_child_weight`, (c) `subsample` and `colsample_bytree`, (d) regularization (`reg_alpha`, `reg_lambda`), (e) `learning_rate` reduction with proportional `n_estimators` increase.
4. For multi-framework comparison, hold folds constant (pass the same `cv` splitter) and use identical metric definitions. Report results in a comparison table.
5. Compute SHAP values using `shap.TreeExplainer` for global and local feature attribution. Generate summary plots, dependence plots for top features, and force plots for individual predictions when interpretability is requested.
6. Handle class imbalance with `scale_pos_weight` (XGBoost), `is_unbalance` (LightGBM), or `auto_class_weights` (CatBoost). Compare against SMOTE-in-pipeline only if simple weighting underperforms.
7. For categorical features, prefer LightGBM or CatBoost native categorical handling over one-hot encoding when cardinality > 10.
8. Save the final model with native `.save_model()` format and record hyperparameters, best iteration, and validation metric in metadata.

## Decision tree
- If dataset has > 100k rows and many categorical features -> prefer LightGBM for speed; use CatBoost if categoricals have high cardinality and natural ordering is absent.
- If dataset is small (< 5k rows) -> reduce `max_depth` to 3-4 and increase regularization to prevent overfitting; consider whether a simpler sklearn model might suffice.
- If the task is ranking -> use `XGBRanker` or `LGBMRanker` with `lambdarank` objective.
- If feature interactions matter for explanation -> use SHAP interaction values, not just main-effect importance.
- If prediction latency is critical -> export to ONNX or use LightGBM's `predict_disable_shape_check` for faster inference.
- If reproducibility is mandatory -> pin `random_state` in the booster AND the data split, and record library version.

## Anti-patterns
- NEVER set `n_estimators` to a fixed value without early stopping. This either underfits or overfits by construction.
- NEVER tune hyperparameters on the test set. Use a validation set or inner cross-validation; the test set is touched exactly once.
- NEVER compare frameworks with different preprocessing (e.g., one-hot for XGBoost but native categoricals for CatBoost) and call it a fair comparison.
- NEVER ignore the `best_iteration` attribute after early stopping. Predictions must use `best_iteration` to avoid including over-trained trees.
- NEVER rely solely on `feature_importances_` (gain-based) for feature selection. Gain importance is biased toward high-cardinality and correlated features.

## Common mistakes
- Using `eval_metric` that does not match the business objective (e.g., `logloss` for early stopping but reporting `F1`).
- Forgetting to pass `categorical_feature` to LightGBM, causing it to treat integer-encoded categoricals as continuous.
- Setting `scale_pos_weight` AND applying SMOTE simultaneously, which double-corrects for imbalance.
- Running SHAP on the training set instead of the validation/test set, which inflates apparent feature relevance.
- Not setting `verbosity=0` or `verbose=-1` during hyperparameter search, flooding logs with thousands of training lines.
- Using `pickle` instead of the framework's native `.save_model()`, which breaks across library version upgrades.

## Output contract
- Report best hyperparameters, best iteration number, and validation metric trajectory (or at minimum start/best/final values).
- Include the class-imbalance strategy used and its rationale.
- Provide SHAP summary plots or feature importance rankings with the method explicitly named.
- Never report train-only metrics as final performance. Always include validation or test metrics.
- Record the framework name and version (e.g., `xgboost==2.0.3`) in artifact metadata.
- If multiple frameworks were compared, include a side-by-side metric table with identical folds.
- Save the model in native format alongside a JSON metadata sidecar.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** for null handling and type coercion. Gradient boosters handle NaNs natively (XGBoost, LightGBM) but benefit from clean categoricals.
- Before this expert -> use the **Scikit-learn Modeling Expert** if a quick linear baseline is needed for comparison.
- After this expert -> use the **Visualization Expert** to plot SHAP summaries, learning curves, or metric comparisons.
- After this expert -> use the **Machine Learning Export Expert** to convert the model to ONNX or package it for serving.
- Related -> the **Statistics Expert** for post-hoc significance tests when comparing model performance across folds.
