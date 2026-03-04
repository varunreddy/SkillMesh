# Apache Airflow Orchestration Expert

Use this expert for designing robust, scalable, and idempotent Data Engineering DAGs using Apache Airflow.

## When to use this expert
- You are orchestrating complex, multi-step data pipelines across various systems over time.
- You need to manage dependencies, scheduling, retries, and failure alerts systematically.
- You are transitioning bash/cron scripts into declarative Python DAGs.
- You want to implement task groups, dynamic task mapping, or sensor-based waiting.

## Execution behavior
1. Establish idempotency for all tasks, ensuring re-runs do not create duplicate data.
2. Separate business logic from orchestration logic (use Airflow for scheduling, not heavy compute).
3. Utilize appropriate Airflow operators (e.g., standard operators vs. KubernetesPodOperator for isolation).
4. Implement standardized error handling, SLAs, and Slack/email alerting callbacks.
5. Strategically map dependencies (`>>`, `<<`) and use Task Groups to visually organizing large DAGs.
6. Design with backfilling in mind, using `execution_date` and `data_interval_start` dynamically.
7. Manage connections and variables securely without hardcoding secrets in DAG files.
8. Enforce proper testing (DAG parse tests, unit tests for Python callables) before deployment.

## Decision tree
- If tasks require isolated heavy compute, choose `KubernetesPodOperator` or `DockerOperator`.
- If triggering external services, choose asynchronous sensors or deferrable operators to free up worker slots.
- If running logic identical across varying inputs, choose Dynamic Task Mapping (`expand`).
- If DAGs share identical structure but different data, choose DAG generation factories.
- If crossing DAG boundaries, choose `TriggerDagRunOperator` or native Datasets.
- If communicating small metadata between tasks, choose XCom; if large data, pass external storage URIs.
- If requiring complex conditional paths, choose `BranchPythonOperator`.

## Anti-patterns
- NEVER run heavy data manipulation directly inside a `PythonOperator` on the worker.
- NEVER use dynamic dates like `datetime.now()` inside DAG definitions (causes parsing instability).
- NEVER use large data payloads in XComs (can crash the metadata DB).
- NEVER create tasks that write to the same output without partitioning by execution date.
- NEVER leave `catchup=True` on new massive pipelines without restricting start dates.
- NEVER hardcode secrets or credentials in the DAG file layout.

## Common mistakes
- Misunderstanding `execution_date` vs `logical_date` leading to processing the wrong data slice.
- Forgetting to define task timeouts, causing hanging connections to block the worker pool.
- Overusing sensors without checking `mode='reschedule'`, consuming all worker slots in a deadlock.
- Modifying DAG structure (adding/removing tasks) without renaming the DAG, corrupting history.
- Returning non-JSON serializable objects into XComs.
- Neglecting to add top-level catch blocks in custom PythonCallables masking failures.

## Output contract
- Completed, syntax-valid Airflow DAG python script highlighting declarative structure.
- Idempotency proof and rollback strategy.
- Backfill execution instructions bridging historical data.
- Resource footprint estimation per task.
- Target connection/variable configurations required.
- Alerts and monitoring callback spec.
- Code coverage or DAG integrity test references.

## Composability hints
- Integrate with `data.ingestion-pipelines` for building the initial extract targets.
- Consult `cloud.aws-s3` or `cloud.gcp-gcs` for externalizing XCom storage paths.
- Combine with `data.warehouse-modeling` to orchestrate dbt transformations via `BashOperator`.
- Use `data.quality-validation` components as standalone sensor tasks before downstream loads.
- Pair with `devops.ci-cd` to handle zero-downtime DAG deployments.
