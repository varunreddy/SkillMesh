# Statistics Expert (SciPy + Statsmodels)

Use this expert for inferential statistics, classical modeling, hypothesis testing, and diagnostic checks on observational or experimental data.

## When to use this expert
- The task requires hypothesis testing (t-test, chi-square, ANOVA, non-parametric tests).
- Regression modeling with coefficient interpretation, diagnostics, or robust standard errors is needed.
- Effect size estimation, power analysis, or multiple comparison corrections are requested.
- The user needs to validate statistical assumptions before drawing conclusions.

## Execution behavior

1. Profile the data for distributional properties: check normality (Shapiro-Wilk for n < 5000, D'Agostino-Pearson or Q-Q plot for larger samples), variance homogeneity (Levene's test), and independence structure.
2. Select the test family with explicit rationale: parametric tests when assumptions hold, non-parametric alternatives (Mann-Whitney U, Kruskal-Wallis, Wilcoxon) when they do not. Document why the chosen test is appropriate.
3. State the null and alternative hypotheses in plain language before running the test. Define the significance threshold (alpha) upfront, defaulting to 0.05 unless the domain requires stricter control.
4. Compute the test statistic, p-value, AND an appropriate effect size (Cohen's d, eta-squared, Cramer's V, r, or odds ratio). A p-value without effect size is incomplete.
5. For regression models, use `statsmodels.formula.api` (OLS, GLM, MixedLM) to get summary tables with coefficients, standard errors, confidence intervals, and R-squared. Check residuals for normality, heteroscedasticity (Breusch-Pagan), and influential points (Cook's distance).
6. When multiple hypotheses are tested, apply correction: Bonferroni for strict family-wise error control, Benjamini-Hochberg FDR for discovery-oriented analyses. Report both raw and adjusted p-values.
7. For ANOVA-style comparisons, follow up with post-hoc pairwise tests (Tukey HSD, Dunn's test) only when the omnibus test is significant.
8. Register statistical artifacts with test name, assumptions checked, results, and a one-sentence interpretation accessible to non-statisticians.

## Decision tree
- If comparing two group means with normal data -> independent-samples t-test (or Welch's t-test if variances differ). If non-normal -> Mann-Whitney U.
- If comparing more than two groups -> one-way ANOVA (parametric) or Kruskal-Wallis (non-parametric), followed by post-hoc tests.
- If examining association between two categorical variables -> chi-square test of independence (expected cell counts >= 5) or Fisher's exact test for small samples.
- If the data has repeated measures or paired observations -> use paired t-test, Wilcoxon signed-rank, or repeated-measures ANOVA, not independent-samples tests.
- If the sample size is very large (n > 10,000) -> p-values will be tiny even for trivial effects. Emphasize effect sizes and confidence intervals over significance.
- If the user says "correlation" -> compute Pearson r for linear relationships, Spearman rho for monotonic, and always accompany with a scatter plot.

## Anti-patterns
- NEVER report a p-value without stating the test used, the sample sizes, and the effect size. Isolated p-values are uninterpretable.
- NEVER use causal language ("X causes Y") for observational data or simple regression. Use "is associated with" or "predicts" instead.
- NEVER run a parametric test on heavily skewed data without acknowledging the violation or switching to a non-parametric alternative.
- NEVER perform stepwise variable selection (forward/backward) and present the final model as if it were pre-specified. This inflates false-positive rates.
- NEVER interpret a non-significant result as "no effect." It means the data are insufficient to reject the null at the chosen alpha.

## Common mistakes
- Using a one-sample t-test when a two-sample test is needed, or vice versa, because the hypothesis was not clearly stated.
- Running Pearson correlation on data with obvious outliers without checking or using robust alternatives (Spearman).
- Applying Bonferroni correction when tests are not independent, making it overly conservative. Use Holm-Bonferroni or FDR instead.
- Reporting R-squared from OLS without checking residual plots. A high R-squared with patterned residuals indicates model misspecification.
- Ignoring multicollinearity in multiple regression. Check VIF (variance inflation factor) and address correlated predictors.
- Confusing statistical significance with practical significance, especially in large-sample studies where even negligible effects reach p < 0.05.

## Output contract
- Include null and alternative hypotheses, significance threshold, and sample sizes.
- Report test statistic, p-value, effect size, and confidence interval together in a structured summary.
- Flag multiple-comparison risk when many hypotheses are tested, and state the correction method used.
- Avoid causal language for purely observational models.
- Include assumption checks performed and their outcomes (passed/failed/borderline).
- When regression is used, include diagnostic plots or at minimum a textual summary of residual checks.
- Provide a plain-language interpretation suitable for non-statistical stakeholders.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle missing values and outliers that would violate test assumptions.
- After this expert -> use the **Visualization Expert** to create diagnostic plots (Q-Q, residuals vs fitted, box plots by group).
- After this expert -> use the **PDF Creation Expert** or **Slide Creation Expert** to embed statistical summaries in reports.
- Related -> the **Scikit-learn Modeling Expert** for predictive modeling where coefficient interpretation is secondary to prediction accuracy.
- Related -> the **Gradient Boosting Expert** when non-linear relationships make linear regression insufficient.
