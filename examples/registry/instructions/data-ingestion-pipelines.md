# Data Ingestion Pipeline Expert

Use this expert for batch and incremental ingestion design with idempotent semantics.

## When to use this expert
- You are integrating source systems into analytics or ML platforms.
- You need robust ingest retries, deduplication, and freshness controls.
- You are transitioning from full-load scripts to change data capture (CDC) pipelines.
- You must scale multi-tenant API extractions with strict rate limiting.

## Execution behavior
1. Define source contracts, keys, and change-capture strategy based on velocity.
2. Implement idempotent loads using immutable staging tables and checkpoints.
3. Establish robust retry backoff polling routines against API limits.
4. Funnel un-parseable records directly to a dead-letter queue (DLQ).
5. Add row-level deduplication over primary keys at the staging layer.
6. Record detailed metadata logs (job_id, loaded_at, rows_inserted).
7. Validate source-to-target row counts and freshness SLAs immediately after load.
8. Set up automated schema drift detection warnings.

## Decision tree
- If the source lacks a reliable updated_at timestamp, choose full-load snapshot or log-based CDC.
- If the data volume exceeds network limits, choose partitioned batch incremental loads.
- If data arrives continuously and triggers immediate actions, choose streaming ingestion.
- If APIs throttle rapidly, choose deferrable asynchronous sensors or backoff libraries.
- If the data format changes unpredictably, choose schema-on-read formats like raw JSON staging.
- If strictly maintaining GDPR regulations, choose targeted hashing during the initial ingest phase.

## Anti-patterns
- NEVER ingest without a clear row-level deduplication strategy.
- NEVER skip replay/backfill design for failure recovery.
- NEVER use implicit `SELECT *` from mutable source databases.
- NEVER load directly into presentation tables without a staging/landing zone.
- NEVER drop errors silently instead of routing to a DLQ.
- NEVER hardcode credentials inside the ingestion script.

## Common mistakes
- Misinterpreting updated_at logic leading to skipped border records.
- Overloading production databases by running heavy extraction during peak business hours.
- Failing to capture soft-deletes since CDC logs weren't enabled.
- Using mismatched timezones between source and destination systems.
- Pulling data synchronously in a single thread when pagination supports parallel requests.
- Forgetting to explicitly enforce column data classes (e.g. converting everything to string).

## Output contract
- Finalized architecture diagram of connection endpoints.
- Idempotency and failure-handling specifications.
- Schema drift detection and DLQ implementation plan.
- SLA/freshness validation checklist.
- Extraction code patterns supporting backfilling and pagination.
- Security boundary definitions for secret management.

## Composability hints
- Integrate with `data.airflow` for robust daily scheduling and alerting overlays.
- Use `data.data-quality-validation` on the raw staging tables immediately post-ingest.
- Consult `cloud.aws-s3` or `cloud.gcp-gcs` for configuring the landing bucket architecture.
- Follow up with `data.warehouse-modeling` to structure the downstream core tables.
