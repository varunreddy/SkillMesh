# Scikit-learn Feature Selection Expert

Use this expert for selecting stable, predictive features with sklearn while preventing leakage and overfitting.

## When to use this expert
- Feature count is high relative to sample size.
- You need embedded/wrapper/filter selection with validation.
- You need compact feature sets for interpretability or latency.

## Execution behavior
1. Perform selection inside CV folds only.
2. Start with simple filters (`VarianceThreshold`, correlation pruning).
3. Compare embedded methods (`SelectFromModel`, L1-based selection).
4. Use wrapper methods (`RFECV`) only when feature count is manageable.
5. Track stability of selected features across folds/seeds.

## Anti-patterns
- NEVER select features on full data before split.
- NEVER report one selected set without stability checks.
- NEVER optimize solely for smallest feature count.

## Output contract
- Selected feature subset and selection method.
- Performance before/after selection.
- Stability summary and deployment caveats.

