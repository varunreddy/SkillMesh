# Scikit-learn Naive Bayes Expert

Use this expert for fast probabilistic baselines with sklearn Naive Bayes variants (`GaussianNB`, `MultinomialNB`, `BernoulliNB`, `ComplementNB`).

## When to use this expert
- You need fast baseline classification with probabilistic outputs.
- Text/count features are present (`MultinomialNB` / `ComplementNB`).
- You need lightweight models for constrained deployment.

## Execution behavior
1. Match NB variant to feature type and distribution assumptions.
2. Build preprocessing pipeline appropriate for chosen variant.
3. Tune smoothing (`alpha`) and priors where needed.
4. Evaluate calibration and class imbalance effects.
5. Compare against logistic baseline for reliability.

## Anti-patterns
- NEVER apply GaussianNB to sparse count vectors without justification.
- NEVER ignore class prior mismatch.
- NEVER interpret NB probabilities as calibrated without checking.

## Output contract
- Variant selection rationale.
- Core metrics and calibration notes.
- Recommended fallback when assumptions break.

