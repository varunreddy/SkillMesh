# Scikit-learn Modeling Expert

Use this expert when tasks require robust model training and evaluation in scikit-learn, including classification, regression, clustering, and dimensionality reduction on tabular data.

## When to use this expert
- The task involves training or comparing classical ML models on structured/tabular data.
- Feature engineering, preprocessing pipelines, or model selection is explicitly needed.
- Cross-validated performance estimates with proper leakage controls are required.
- The user needs reproducible sklearn Pipeline artifacts for downstream serving or reporting.

## Execution behavior

1. Inspect the target variable distribution and decide split strategy: use `StratifiedKFold` for classification with class imbalance, `TimeSeriesSplit` for temporal data, or `train_test_split` with a fixed `random_state` for simple cases.
2. Build a single `Pipeline` (or `ColumnTransformer` + `Pipeline`) that chains every preprocessing step (imputation, scaling, encoding, feature selection) with the estimator. Never fit transformers outside the pipeline.
3. Perform model comparison using `cross_val_score` or `cross_validate` with at least 5 folds before committing to a single algorithm.
4. For hyperparameter search, prefer `RandomizedSearchCV` for wide exploration and `GridSearchCV` only when the search space is already narrow. Always pass `scoring` explicitly.
5. If nested cross-validation is needed (e.g., research papers, unbiased estimates), wrap the search inside an outer `cross_val_score` loop.
6. After selecting the best model, refit on the full training set and evaluate once on the held-out test set.
7. Track metrics aligned to the objective: F1-macro or ROC-AUC for imbalanced classification, MAE/RMSE for regression, silhouette score for clustering.
8. Persist the trained pipeline with `joblib.dump` alongside a metadata dict recording feature names, target name, sklearn version, and metric scores.

## Decision tree
- If classes are imbalanced (minority < 15%) -> use `class_weight='balanced'` or SMOTE inside the pipeline, and report precision-recall AUC instead of accuracy.
- If features mix numeric and categorical -> use `ColumnTransformer` with separate sub-pipelines, not ad-hoc encoding before the pipeline.
- If dataset has < 1000 rows -> prefer simpler models (LogisticRegression, Ridge) and use repeated stratified k-fold to reduce variance in estimates.
- If the user asks for "feature importance" -> use `permutation_importance` on the test set, not `.feature_importances_` from tree models alone, to avoid bias toward high-cardinality features.
- If temporal ordering matters -> never shuffle; use `TimeSeriesSplit` and make this explicit in the output.

## Anti-patterns
- NEVER fit a scaler or encoder on the full dataset before splitting. This leaks information from test into train and inflates metrics.
- NEVER report accuracy alone on imbalanced datasets. It hides poor minority-class performance.
- NEVER use `cross_val_predict` to report performance metrics directly; it is designed for generating out-of-fold predictions, not for computing scores.
- NEVER hard-code column indices in a ColumnTransformer. Use column name lists so the pipeline survives column reordering.
- NEVER call `.predict()` on training data and present it as model performance.

## Common mistakes
- Forgetting to set `random_state` in both the splitter and the estimator, making results non-reproducible across runs.
- Using `LabelEncoder` on input features instead of `OrdinalEncoder` or `OneHotEncoder`. `LabelEncoder` is designed for the target variable only.
- Applying SMOTE or oversampling before the train/test split, which leaks synthetic samples into the test set.
- Selecting features based on correlation with the target computed on the full dataset, then evaluating on a "held-out" set that influenced feature selection.
- Using `r2_score` on very small test sets where a single outlier can flip R-squared negative, without noting the instability.
- Ignoring convergence warnings from `LogisticRegression` or `SVM`. Increase `max_iter` or scale features.

## Output contract
- Include selected features, preprocessing steps, and estimator hyperparameters in artifact metadata.
- Report confidence intervals or fold-wise variance for key metrics (e.g., "F1-macro: 0.82 +/- 0.03").
- Provide a confusion matrix for classification or residual diagnostics for regression.
- Never claim performance from train-only evaluation.
- Save the fitted pipeline as a single serialized file that can be loaded for inference without re-fitting.
- Record the sklearn version used (`sklearn.__version__`) in the metadata for reproducibility.
- If feature importance is computed, include the method used and any caveats.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle nulls, type coercion, and deduplication.
- After this expert -> use the **Machine Learning Export Expert** to package the pipeline for serving or ONNX conversion.
- After this expert -> use the **Visualization Expert** to plot confusion matrices, ROC curves, or residual distributions.
- Related -> the **Gradient Boosting Expert** for tree-based alternatives that often outperform sklearn defaults on tabular data.
- Related -> the **Statistics Expert** for hypothesis testing on model coefficients or residual diagnostics.
