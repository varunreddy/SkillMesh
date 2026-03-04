# Data Quality Validation Expert

Use this expert for production-grade data quality rules, anomaly thresholds, and quality alerting workflows.

## When to use this expert
- You need to guarantee the integrity, uniqueness, and completeness of core tables.
- You are preventing downstream dashboards from displaying silently corrupted reports.
- You want to set up statistical anomaly detection on data volume and distribution drifts.
- You need a standardized framework to reject bad records without failing whole data pipelines.

## Execution behavior
1. Audit column types to define generic non-null and primary key uniqueness rules.
2. Build domain-specific referential integrity checks (foreign key matching).
3. Set up boundary distributions (min, max, std-dev) for continuous numeric measures.
4. Implement row-count freshness audits contrasting historical averages.
5. Quarantine violating records to specific error tables instead of crashing implicitly.
6. Tag severity levels on rules (WARN vs. ERROR) to avoid alerting fatigue.
7. Compile tests into the transformation layer (like dbt tests or Great Expectations).
8. Emit clear, human-readable alerts when threshold boundaries are breached.

## Decision tree
- If a primary key constraint is violated, choose ERROR severity and halt downstream pushes.
- If a known column occasionally receives nulls expected by the business, choose WARN or drop the constraint.
- If validating categorical enums, choose accepted_values assertion lists.
- If detecting sudden systemic volume drops, choose time-series anomaly thresholds over static numbers.
- If dealing with highly complex inter-table logic, choose custom SQL validation scripts.
- If bad records should not stop the good records, choose row-level routing to quarantine tables.

## Anti-patterns
- NEVER push aggregated data to executives without confirming base-table referential integrity.
- NEVER spam Slack with trivial WARN anomalies ignoring clear severity routing.
- NEVER test for exact row counts on live dynamic streaming sources.
- NEVER build validation logic directly into the BI layer instead of the warehouse.
- NEVER assume incoming API schemas won't drift or change column casing.
- NEVER suppress primary key violations without documenting the edge case anomaly.

## Common mistakes
- Testing post-aggregated models but forgetting to test the raw landing data.
- Creating overly tight statistical boundaries that break pipelines during normal seasonal spikes.
- Using generic test names, making it impossible to debug alerts without executing queries.
- Failing to delete old quarantine data leading to massive storage bloat over time.
- Applying heavy full-table scans for quality checks on multi-terabyte unpartitioned tables.
- Running quality suites separately from the DAG flow, creating race conditions.

## Output contract
- Suite of declarative tests capturing schema, validity, and relationship checks.
- Execution timing integration mapping tests to pipeline boundaries.
- Error quarantine table schema and retention policy.
- Alerting playbook dictating SLA responses to ERROR vs WARN triggers.
- Anomaly detection query thresholds for key volume metrics.
- Documentation mapping business rules to technical assertions.

## Composability hints
- Directly attach to `data.dbt` to run natively configured YAML tests during transformation.
- Expose test output metadata directly to `data.warehouse-modeling` for data lineage lineage tracking.
- Orchestrate halting constraints via `data.data-orchestration` sensors.
- Feed anomalies into `stats.nonparametric-tests` for advanced statistical drift analytics.
