# Frequentist Hypothesis Testing Expert

Use this expert for t-tests, ANOVA, chi-square, and rigorous false positive (alpha) control frameworks.

## When to use this expert
- You are determining if an observed metric difference between two major groups was likely due to random chance.
- You need to maintain strict classical statistical significance controls (alpha/beta thresholds) for regulatory or operational audits.
- You are isolating variance contributions across multiple interlocking conditional factors natively via ANOVA workflows.
- You must handle multiple simultaneous comparison corrections using robust Bonferroni or FDR logic.

## Execution behavior
1. Define the exact Null Hypothesis (H0) explicitly and the expected Alternative Hypothesis (H1).
2. Set the desired significance level (alpha) explicitly prior to commencing any data aggregation.
3. Test key programmatic assumptions rigorously: normality boundaries, variance homogeneity, and absolute independence.
4. Select the correct parametric statistical test directly matched structurally against the continuous or categorical parameter.
5. Compute the precise test statistic comparing expected baseline vs observed localized deviation.
6. Calculate the resultant p-value specifying the conditional probability regarding the observed extremes.
7. Correct the p-value aggressively whenever performing isolated simultaneous multiple comparisons natively.
8. Report the exact absolute effect size calculations providing practical, not merely statistical, contextual relevance.

## Decision tree
- If analyzing two strictly continuous normally-distributed independent groups, choose an independent two-sample t-test framework.
- If data fails to meet normality structural distributions completely, choose continuous nonparametric pathways.
- If comparing categorical count proportions rather than continuous metric means, choose a Chi-Square test natively.
- If isolating differences spanning more than three distinct simultaneous groups, choose factorial ANOVA configurations.
- If samples represent paired longitudinal measurements tracking the identical entity chronologically, choose a paired t-test directly.
- If conducting 50 interlocking tests simultaneously, choose the Benjamini-Hochberg FDR to limit overall false-discovery inflation rates.

## Anti-patterns
- NEVER evaluate the exact same data recursively adjusting tests simply hacking to find a significant p-value (p-hacking).
- NEVER alter the predefined alpha structural boundaries arbitrarily after the experiment data has been actively rendered.
- NEVER interpret a p-value as the implicit probability regarding truth surrounding the exact alternative hypothesis structure.
- NEVER equate massive statistical significance generated from multi-million sample sizes against real-world practical significance inherently.
- NEVER perform continuous sequential validation testing on rolling data completely identical without adjusting statistical boundaries efficiently.
- NEVER arbitrarily drop significant outliers from distributions entirely before formally identifying statistical generation defects.

## Common mistakes
- Misinterpreting a high p-value natively indicating the explicit verification of the null baseline (failure to reject vs absolute confirmation).
- Running thousands of A/B metrics ignoring the massive accumulated inflation risk surrounding the overall structural False Positive Rate completely.
- Using a one-tailed directional test improperly attempting to artificially boost the native baseline predictive power purely.
- Over-relying entirely upon the absolute p-value metrics while fundamentally ignoring the underlying practical effect size magnitude directly.
- Applying parametric testing constraints against heavily skewed, heavy-tailed data distributions structurally unsuited for standard variance limits.
- Treating absolute proportional correlations identically equal to strict independent verified directional structural causation.

## Output contract
- Completed structural analytical plan outlining distinct baseline assumptions and explicitly declared target thresholds natively.
- Descriptive test statistic summaries tracking the resulting calculated p-value parameters comprehensively.
- Practical metric effect size estimates (e.g., Cohen's d) tracking real-world impact implications.
- Multiple-comparison structural adjustment pathways specifically identifying statistical corrections.
- Explicit visual distribution outputs mapping parametric assumptions matching theoretical quantiles directly.
- Detailed interpretation narrative summarizing the data results specifically avoiding probabilistic logical fallacies entirely.

## Composability hints
- Generate pre-experiment statistical limits utilizing configurations via `stats.power-sample-size`.
- Route assumption validation discrepancies failing normality constraints immediately toward `stats.nonparametric-tests`.
- Build the initial experimental blocking and randomized stratification designs consulting natively `stats.experiment-design`.
- Present the structural hypothesis divergence visuals explicitly referencing guidelines provided natively by `viz.distribution-diagnostics`.\n