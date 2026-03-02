# Scikit-learn Dimensionality Reduction Expert

Use this expert for dimensionality reduction and latent-feature extraction in sklearn, including PCA and related decomposition methods.

## When to use this expert
- Feature space is high-dimensional and noisy.
- You need compact latent features for modeling, clustering, or visualization.
- You want reproducible reduction pipelines with explained-variance controls.

## Execution behavior
1. Fit reducers only on training folds to prevent leakage.
2. Start with `PCA` baseline and explained-variance targets.
3. Compare alternatives when needed:
   - sparse/high-dimensional text-like data: `TruncatedSVD`
   - independent source separation: `FastICA`
   - supervised projection: `PLSRegression` (when target-aware reduction is needed)
4. Select component count by validation performance plus variance curves.
5. Evaluate downstream impact on primary task metrics.
6. Inspect component loadings for sanity and dominant feature drivers.
7. Persist reducer + preprocessing pipeline.

## Decision tree
- If preserving most variance is the objective -> use `PCA`.
- If matrix is sparse -> use `TruncatedSVD` instead of dense PCA.
- If independent latent factors are expected -> try `FastICA`.
- If reduction hurts core metric materially -> reduce less or keep full feature set.

## Anti-patterns
- NEVER fit decomposition on full dataset before split.
- NEVER pick component count from visual preference alone.
- NEVER use transformed features without tracking inverse mapping limits.

## Common mistakes
- Over-reducing dimensionality and discarding predictive signal.
- Ignoring whether components are stable across folds/seeds.
- Mixing scaled and unscaled features before decomposition.

## Output contract
- Provide chosen reducer and component-count rationale.
- Report explained variance (or equivalent) and downstream metric impact.
- Include top loading patterns or component interpretation summary.
- Document reproducibility metadata and pipeline serialization steps.

## Composability hints
- Before this expert -> use **Feature Engineering for ML** for robust input preprocessing.
- After this expert -> use **Scikit-learn Modeling and Evaluation** for downstream supervised performance checks.
- Related -> **Scikit-learn Clustering and GMM Expert** for clustering in latent space.
