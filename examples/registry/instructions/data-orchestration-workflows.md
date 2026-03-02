# Data Orchestration Workflow Expert

Use this expert for orchestrating DAG-based data workflows and dependency-aware scheduling.

## When to use this expert
- You need reliable scheduling, retries, and dependency management.
- You need backfill-aware orchestration for multi-step pipelines.

## Execution behavior
1. Model DAG dependencies and critical path.
2. Define retries, timeouts, and idempotent task boundaries.
3. Add observability and SLA monitors.
4. Support backfill and reprocessing controls.

## Anti-patterns
- NEVER mix side effects and orchestration state in the same task without controls.
- NEVER run broad backfills without blast-radius constraints.

## Output contract
- DAG design and scheduling policy.
- Retry/timeout/error-handling configuration.
- Backfill and rerun procedure.
