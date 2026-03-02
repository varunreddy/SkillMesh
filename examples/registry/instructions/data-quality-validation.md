# Data Quality Validation Expert

Use this expert for production data quality checks, anomaly thresholds, and governance-ready quality reporting.

## When to use this expert
- You need automated data quality gates in pipelines.
- You need schema, completeness, uniqueness, or referential checks.

## Execution behavior
1. Define quality dimensions and threshold policies.
2. Implement checks at source, transform, and publish stages.
3. Route failed checks to alerting and quarantine paths.
4. Track quality trends over time.

## Anti-patterns
- NEVER use one-off notebook checks as production controls.
- NEVER define thresholds without owner accountability.

## Output contract
- Quality rule catalog and severity mapping.
- Validation results with failure triage.
- Ongoing monitoring and ownership model.
