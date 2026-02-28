# Hyperparameter Tuning Expert

Use this expert when tasks require systematic optimization of model hyperparameters, including search strategy selection, cross-validation design, early pruning, and multi-objective trade-offs.

## When to use this expert
- The task involves selecting optimal hyperparameters for any ML or DL model beyond default settings.
- The user needs to choose between grid, random, or Bayesian search strategies for their problem size and budget.
- Early pruning or multi-objective optimization (e.g., accuracy vs. latency) is required for expensive training runs.
- Cross-validation strategy must be designed to avoid overfitting the hyperparameter search to a single split.

## Execution behavior

1. Define the search space explicitly: specify each hyperparameter with its type (categorical, integer, float), range, and scale (linear or log-uniform). Use log-uniform for learning rates, regularization strengths, and any parameter spanning multiple orders of magnitude.
2. Select the search strategy based on space size and evaluation cost. For fewer than 50 total combinations, use `GridSearchCV`. For moderate spaces, use `RandomizedSearchCV` with at least 100 iterations. For large or expensive spaces, use Optuna with the TPE sampler.
3. Define the cross-validation scheme to match the data structure: `StratifiedKFold` for imbalanced classification, `TimeSeriesSplit` for temporal data, `RepeatedKFold` for small datasets. Use at least 5 folds.
4. Set an explicit evaluation metric via the `scoring` parameter (sklearn) or Optuna's objective return value. Never rely on the model's default score method without verifying it matches the business objective.
5. For expensive evaluations (training time > 2 minutes per trial), enable pruning. In Optuna, use `MedianPruner(n_startup_trials=5, n_warmup_steps=10)` or `HyperbandPruner` and report intermediate values with `trial.report(value, step)`.
6. Run the search, then inspect the importance of each hyperparameter using `optuna.importance.get_param_importances()` or partial dependence plots to understand which parameters matter most.
7. Validate the best configuration with a final evaluation on a held-out test set that was never seen during the search. If nested CV is required, wrap the entire search inside an outer `cross_val_score` loop.
8. Log all trial results (hyperparameters, metric, duration, pruning status) to a persistent store (Optuna storage, MLflow, or CSV) for reproducibility and future warm-starting.

## Decision tree
- If search space is small (< 50 combinations) -> use `GridSearchCV` for exhaustive coverage.
- If search space is moderate (50-500 effective combinations) -> use `RandomizedSearchCV` with `n_iter >= 100` and log-uniform distributions for scale-sensitive parameters.
- If search space is large or evaluation is expensive -> use Optuna with `TPESampler` for sample-efficient Bayesian optimization.
- If single trial takes > 5 minutes -> enable pruning with `MedianPruner` or `HyperbandPruner` and report intermediate metrics each epoch.
- If multiple conflicting objectives (e.g., accuracy vs. model size) -> use `optuna.create_study(directions=["maximize", "minimize"])` and select from the Pareto front.
- If reproducibility is critical -> set `TPESampler(seed=42)` and fix all random states in the training pipeline.

## Anti-patterns
- NEVER use grid search on a space with more than 4 hyperparameters or wide continuous ranges. The combinatorial explosion wastes compute on uninformative regions.
- NEVER tune hyperparameters using the test set directly. The test set must remain unseen until final evaluation; use a validation set or CV folds for tuning.
- NEVER run expensive trials without pruning. Unpruned Bayesian search on a 100-trial budget can waste 80% of compute on clearly inferior configurations.
- NEVER ignore the search budget. Define `n_trials` or `timeout` upfront so the search terminates predictably and resources are bounded.
- NEVER tune all hyperparameters simultaneously from scratch. Start with the most impactful ones (learning rate, regularization) and fix less sensitive ones at defaults, then refine.

## Common mistakes
- Using uniform distributions for learning rate or regularization instead of log-uniform, causing the search to over-sample large values and under-explore small ones.
- Setting `cv=3` to speed up evaluation, which increases variance in metric estimates and makes the search select noisy winners. Use at least 5 folds.
- Forgetting to pass `refit=True` (or the best metric name) to `GridSearchCV`/`RandomizedSearchCV`, so the final model is never refitted on the full training set.
- Comparing trials across different CV splits due to unseeded `KFold`, making metric comparisons meaningless. Always seed the splitter.
- Running Optuna without a persistent storage backend, losing all trial history when the process crashes. Use `optuna.storages.RDBStorage` for long runs.
- Reporting the best cross-validation score as the expected production performance without accounting for optimistic bias from the search itself.

## Output contract
- Report the best hyperparameter configuration with its CV metric (mean and standard deviation across folds).
- Include a ranked table of all trials (or top-20) with hyperparameters, metric, duration, and pruning status.
- Provide hyperparameter importance rankings to justify which parameters were most influential.
- Show the optimization history plot (objective value vs. trial number) to confirm convergence.
- Record the search strategy, sampler, pruner, number of trials, and total wall-clock time.
- If multi-objective, present the Pareto front with trade-off visualization.
- Save the Optuna study or search results to a reproducible artifact (database, JSON, or pickle).

## Composability hints
- Before this expert -> use the **Feature Engineering Expert** to finalize the feature set, so tuning operates on the correct input space.
- Before this expert -> use the **Scikit-learn Modeling Expert** or **PyTorch Training Expert** to define the base model and training loop.
- After this expert -> use the **Machine Learning Export Expert** to package the best model configuration for deployment.
- Related -> the **Gradient Boosting Expert** for XGBoost/LightGBM-specific parameter spaces and early-stopping patterns.
- Related -> the **Transformers Fine-tuning Expert** for tuning LoRA rank, learning rate, and warmup in HuggingFace workflows.
