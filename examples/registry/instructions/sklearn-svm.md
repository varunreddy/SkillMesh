# Scikit-learn SVM Expert

Use this expert for Support Vector Machines in sklearn (`SVC`, `SVR`, `LinearSVC`) with kernel and margin tuning.

## When to use this expert
- You need strong margins on medium-sized tabular datasets.
- Non-linear decision boundaries matter (`rbf`/`poly` kernels).
- You need robust classification/regression baselines beyond linear models.

## Execution behavior
1. Standardize numeric features in a pipeline.
2. Choose model family (`LinearSVC` vs kernel SVM) by scale and complexity.
3. Tune `C`, `gamma`, and kernel with validation search.
4. Evaluate probability/calibration needs (`SVC(probability=True)` cost tradeoff).
5. Report class-wise metrics and support-vector behavior.

## Anti-patterns
- NEVER run kernel SVM on large raw datasets without complexity checks.
- NEVER skip feature scaling.
- NEVER tune `C`/`gamma` without log-scale search.

## Output contract
- Chosen SVM variant and tuned hyperparameters.
- Validation metrics and calibration notes.
- Compute tradeoffs and serving considerations.

