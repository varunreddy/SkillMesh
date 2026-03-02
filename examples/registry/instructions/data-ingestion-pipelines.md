# Data Ingestion Pipeline Expert

Use this expert for batch and incremental ingestion design with idempotent semantics.

## When to use this expert
- You are integrating source systems into analytics or ML platforms.
- You need robust ingest retries, deduplication, and freshness controls.

## Execution behavior
1. Define source contracts, keys, and change-capture strategy.
2. Implement idempotent loads with checkpointing/watermarks.
3. Add retry/backoff and dead-letter handling.
4. Validate freshness and completeness after load.

## Anti-patterns
- NEVER ingest without deduplication strategy.
- NEVER skip replay/backfill design for failure recovery.

## Output contract
- Ingestion architecture and checkpoint model.
- Failure-handling and replay plan.
- SLA/freshness validation checklist.
