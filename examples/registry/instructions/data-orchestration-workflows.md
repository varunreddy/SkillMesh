# Data Workflow Orchestration Expert

Use this expert for DAG orchestration, retry/timeouts, backfills, and scalable dependency-aware scheduling.

## When to use this expert
- You are stitching together disparate tasks (ingest, transform, test) into a coherent run.
- You need resilient architectures that automatically recover from transient network failures.
- You are moving from cron-based scripts to sensor-driven directed acyclic graphs (DAGs).
- You want to implement cross-team data SLAs with clear alert ownership.

## Execution behavior
1. Map out strict upstream dependency requirements for every downstream job.
2. Abstract complex logic into isolated execution containers instead of the orchestrator.
3. Configure bounded retries, exponential backoffs, and strict task execution timeouts.
4. Introduce data presence sensors to trigger tasks conditionally.
5. Partition pipeline runs strictly by execution_date to isolate failures.
6. Configure asynchronous execution states (deferrable operators) for long-waiting remote jobs.
7. Set up on-failure and on-retry callback hooks sending messages to PagerDuty/Slack.
8. Establish clear backfill and catchup policies for newly deployed pipelines.

## Decision tree
- If upstream data arrival time varies heavily, choose sensor-driven triggers over time-schedules.
- If task environments conflict with orchestrator packages, choose containerized execution hooks.
- If passing data between tasks, choose object-storage URIs over metadata database payloads (XCom).
- If processing the same logic across 100 tables, choose dynamic task mapping.
- If distinct pipelines share dependencies, choose external task sensors or dataset-driven scheduling.
- If tasks are solely waiting on remote compute (e.g., Snowflake), choose deferrable asynchronous operators.

## Anti-patterns
- NEVER write heavy data-processing code inside the orchestrator's worker space.
- NEVER interlock cyclical dependencies within your DAG design.
- NEVER leave default unlimited timeouts on tasks calling third-party APIs.
- NEVER pass multi-megabyte payloads through the internal orchestrator bus.
- NEVER schedule scripts without partitioning by a logical data window (execution_date).
- NEVER alter historical task structure dynamically relying on runtime local time variables.

## Common mistakes
- Confusing the orchestrator trigger wall-clock time with the logical data window being processed.
- Storing hardcoded secrets in the DAG file repository instead of a secure vault backend.
- Putting multiple independent components into a single gigantic monolithic DAG.
- Deploying catchup=True on a 5-year-old table creating thousands of immediate concurrent tasks.
- Forgetting to assign dedicated isolated resource pools to long-running heavy tasks.
- Not defining clear SLAs and owner tags at the DAG level.

## Output contract
- Validated declarative DAG blueprint specifying clear linear or branched dependencies.
- Alerting schema matching on-failure and SLA-miss thresholds.
- Detailed task lifecycle configuration (retries, timeouts, parallelism limits).
- Container isolation layout for task execution.
- Backfill procedure documentation.
- Secret management integration spec.

## Composability hints
- Leverage `data.ingestion-pipelines` for the external extraction operator nodes.
- Orchestrate `data.dbt` via command-line execution blocks for scalable transformations.
- Pair with `devops.incident-response` to map pipeline failures to on-call paging tools.
- Consult `data.data-quality-validation` to implement halting checks before publishing tasks succeed.
