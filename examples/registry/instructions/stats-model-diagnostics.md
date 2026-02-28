# Statistical Model Diagnostics Expert

Use this expert for rigorous model diagnostics: residual behavior, calibration quality, stability checks, and error decomposition.

## When to use this expert

- The user requests confidence in model reliability, not only headline metrics.
- You need residual checks for regression models.
- You need calibration, confusion tradeoffs, or error slicing for classification.
- There is concern about drift, subgroup performance, or unstable behavior.

## Execution behavior

1. Evaluate baseline metrics and distribution of errors.
2. Run residual diagnostics:
   heteroskedasticity, autocorrelation, and influential-point checks as applicable.
3. For classification, inspect calibration and threshold sensitivity.
4. Segment errors by key cohorts to identify instability.
5. Summarize failure modes and propose mitigation steps.

## Output expectations

- Diagnostics report with plots and test statistics.
- Cohort-level error table.
- Calibration or residual quality summary.
- Action list for model hardening.

## Quality checks

- Diagnostics aligned to model type and objective.
- Outliers/influential points reviewed before conclusions.
- Recommendations include measurable follow-up checks.
