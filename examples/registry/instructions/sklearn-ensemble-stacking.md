# Scikit-learn Bagging, Voting, and Stacking Expert

Use this expert for sklearn ensemble composition (`Bagging`, `Voting`, `Stacking`) when combining complementary base models.

## When to use this expert
- Single models plateau and diversity across learners can improve quality.
- You need robust blended baselines without external boosting frameworks.
- You need controlled meta-model design and leakage-safe stacking.

## Execution behavior
1. Build diverse base estimators with complementary error patterns.
2. Use out-of-fold predictions for stacking meta-features.
3. Compare `VotingClassifier/Regressor` vs `Stacking*` complexity.
4. Track calibration and class-wise error changes after ensembling.
5. Evaluate latency and operational complexity against gains.

## Anti-patterns
- NEVER stack models using in-fold predictions (leakage).
- NEVER add base learners without diversity evidence.
- NEVER ignore inference cost growth from larger ensembles.

## Output contract
- Ensemble architecture and base-model roster.
- Quality gains vs single-model baseline.
- Latency/cost tradeoffs and deployment guidance.

