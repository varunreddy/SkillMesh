# Scikit-learn Nearest Neighbors Expert

Use this expert for `KNeighborsClassifier`, `KNeighborsRegressor`, and neighborhood-based methods in sklearn.

## When to use this expert
- Local similarity is central to prediction quality.
- You need non-parametric baselines with minimal training overhead.
- Distance metric choice materially affects results.

## Execution behavior
1. Scale features and define distance metric.
2. Tune `n_neighbors`, weighting strategy, and metric parameters.
3. Evaluate sensitivity to feature space noise and high dimensionality.
4. Compare brute-force vs tree-based neighbor search backends.
5. Report latency/memory implications for inference at scale.

## Anti-patterns
- NEVER use unscaled mixed-unit features.
- NEVER ignore inference latency growth with dataset size.
- NEVER assume Euclidean distance is always valid.

## Output contract
- Neighbor model config and metric rationale.
- Quality vs latency tradeoff summary.
- Deployment guidance for index/search strategy.

