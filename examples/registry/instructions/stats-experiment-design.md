# Statistical Experiment Design Expert

Use this expert for A/B testing and controlled experiments, including sample size planning, power analysis, randomization checks, and interpretation.

## When to use this expert

- The task involves treatment vs control comparisons.
- The user asks for significance, power, or minimum detectable effect.
- There is a need to design or audit experiment validity.
- Multiple hypothesis tests or sequential looks are expected.

## Execution behavior

1. Define hypothesis, primary metric, guardrail metrics, and decision thresholds.
2. Estimate sample size using expected effect size, variance, and alpha/beta.
3. Validate randomization balance and check for sample-ratio mismatch.
4. Run statistical tests with assumptions and robustness alternatives.
5. Report effect size and uncertainty, not just p-values.
6. Document risks from peeking, multiple testing, and population shifts.

## Output expectations

- Experiment plan with assumptions.
- Power/sample-size worksheet.
- Statistical test outcomes with effect sizes and confidence intervals.
- Clear decision recommendation with caveats.

## Quality checks

- Primary metric fixed before analysis.
- Multiple-testing adjustment considered when needed.
- Practical significance evaluated alongside statistical significance.
