# Feature Engineering Expert

Use this expert when tasks require transforming raw columns into informative features for machine learning, including encoding strategies, interaction terms, feature selection, and feature store patterns.

## When to use this expert
- The task involves encoding categorical variables, creating interaction or polynomial features, or deriving temporal features from raw data.
- Feature selection is needed to reduce dimensionality before model training.
- The user needs a reproducible, pipeline-safe feature engineering workflow that avoids train/test leakage.
- A feature store or reusable feature registry is being designed for production ML.

## Execution behavior

1. Profile every column: inspect cardinality, missing-value rates, data types, and distribution skew. Separate columns into categorical (low-cardinality, high-cardinality), numeric, datetime, and free-text buckets.
2. For low-cardinality categoricals (< 15 unique values), apply one-hot encoding via `OneHotEncoder(handle_unknown="ignore")` inside a `ColumnTransformer`. For ordinal categoricals with a natural order, use `OrdinalEncoder` with an explicit `categories` list.
3. For high-cardinality categoricals (>= 15 unique values), use target encoding with smoothing (`category_encoders.TargetEncoder` with `smoothing` parameter) or learned embeddings. Always fit the encoder inside cross-validation folds to prevent leakage.
4. Generate interaction and polynomial features where domain knowledge suggests non-linear relationships. Use `PolynomialFeatures(degree=2, interaction_only=True)` for pairwise interactions; manually create ratio or difference features for known domain formulas.
5. For datetime columns, extract calendar features (day-of-week, month, is_holiday), lag features, and rolling-window statistics (mean, std over configurable windows). Ensure lag/window calculations respect temporal ordering and avoid future leakage.
6. Perform feature selection inside the cross-validation loop. Start with variance thresholding, then apply an embedded method (L1 penalty coefficients or tree-based `feature_importances_`) or `SelectFromModel`. Use `RFECV` only when the feature count is manageable (< 200).
7. Wrap every transformation into a scikit-learn `Pipeline` or `ColumnTransformer` so the full feature engineering graph is serialized with the model and can be applied identically at inference time.
8. Document every engineered feature with its derivation logic, expected range, and any upstream dependencies so it can be registered in a feature store or catalog.

## Decision tree
- If categorical + low cardinality (< 15 unique) -> one-hot encode with `handle_unknown="ignore"`.
- If categorical + high cardinality (>= 15 unique) -> target encoding with smoothing, or entity embeddings when a neural model is downstream.
- If numeric pair has known domain interaction -> create multiplication, ratio, or difference feature explicitly.
- If numeric relationships may be non-linear -> add `PolynomialFeatures(degree=2, interaction_only=True)` and let downstream regularization prune.
- If feature count exceeds 2x sample count -> use embedded selection (L1, tree importance) inside cross-validation to avoid overfitting.
- If temporal data -> generate lag features and rolling statistics; never use future values in window calculations.

## Anti-patterns
- NEVER fit a target encoder on the full dataset before splitting. This leaks target information into validation and test sets, inflating metrics.
- NEVER one-hot encode high-cardinality columns (hundreds of unique values) without considering dimensionality. The resulting sparse matrix degrades tree models and inflates memory.
- NEVER engineer features in a standalone script that is separate from the training pipeline. The same transformations must apply at inference time without code duplication.
- NEVER perform feature selection on the full dataset and then evaluate on a subset. Selection must happen inside each cross-validation fold.
- NEVER drop features based solely on low correlation with the target. Non-linear models can exploit features that appear linearly uncorrelated.

## Common mistakes
- Using `LabelEncoder` on input features instead of `OrdinalEncoder`. `LabelEncoder` assigns arbitrary integers with no unknown-handling and is designed for the target only.
- Applying target encoding without a smoothing parameter, which overfits to rare categories and produces extreme encoded values.
- Creating rolling-window features without shifting by one period, causing the current observation's value to leak into its own feature.
- Generating thousands of polynomial features without subsequent selection, leading to a curse-of-dimensionality slowdown and overfitting.
- Computing feature importance on training data only. Use `permutation_importance` on the validation set for an unbiased estimate.
- Forgetting to persist the fitted encoder alongside the model, making it impossible to transform new data at serving time.

## Output contract
- Deliver a fitted `Pipeline` or `ColumnTransformer` that encapsulates every feature transformation and can be serialized with `joblib.dump`.
- Provide a feature manifest listing each engineered feature name, derivation method, source column(s), and expected value range.
- Report the feature count before and after selection, along with the selection method and threshold used.
- Include leakage-prevention evidence: confirm that target encoding and feature selection were fitted inside CV folds.
- If a feature store is used, register features with versioned metadata (creation date, owner, upstream table).
- Record the `category_encoders` or `sklearn` version for reproducibility.
- Supply a short exploratory summary (top-10 features by importance, cardinality stats) to aid downstream model interpretation.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle nulls, deduplication, and type coercion before feature creation.
- After this expert -> use the **Scikit-learn Modeling Expert** or **Gradient Boosting Expert** to train models on the engineered feature set.
- After this expert -> use the **Hyperparameter Tuning Expert** to jointly optimize feature selection thresholds and model hyperparameters.
- Related -> the **Time Series Expert** for advanced temporal feature patterns (seasonality decomposition, Fourier features).
- Related -> the **Statistics Expert** for statistical tests that inform feature interactions (e.g., chi-squared, mutual information).
