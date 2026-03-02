# Distribution and Outlier Visualization Expert

Use this expert for distribution-focused visuals such as histograms, KDEs, box plots, violin plots, and ridgeline views.

## When to use this expert
- You need to inspect spread, skew, tails, or outliers.
- The task involves cohort comparisons of numeric distributions.
- Model diagnostics require residual or error-distribution plots.

## Execution behavior
1. Validate numeric field quality (null handling, units, extreme-value policy).
2. Select primary distribution view (histogram/KDE/box/violin) based on audience and sample size.
3. Use consistent binning/scales for cross-group comparisons.
4. Add percentile markers and robust summary statistics.
5. Flag outliers with explicit rules (IQR, z-score, domain thresholds).

## Decision tree
- Large sample single variable -> histogram + KDE overlay.
- Group comparison with many cohorts -> box plot or violin with summary markers.
- Residual diagnostics -> residual histogram + QQ-style check note.

## Anti-patterns
- NEVER hide axis ranges that contain important tails.
- NEVER compare groups with different binning strategies.
- NEVER treat outlier visuals as automatic data-removal instructions.

## Output contract
- Chosen plot family and parameterization (bins, bandwidth, whisker policy).
- Distribution summary (median, IQR, tail notes, outlier counts).
- Cohort-level differences and confidence caveats.

## Composability hints
- Before this expert -> use **Advanced Pandas Data Workflows** for clean numeric inputs.
- Related -> **Statistical Model Diagnostics** for regression/classification residual checks.
