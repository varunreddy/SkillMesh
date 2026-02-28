# dbt (Data Build Tool) Expert

Use this expert for designing dbt projects with proper model layering, testing strategies, incremental materialization, macro development, source configuration, and documentation within a modern analytics engineering workflow.

## When to use this expert
- SQL transformations in a data warehouse need to be version-controlled, tested, and documented.
- A layered modeling architecture (staging, intermediate, marts) must be designed or refactored.
- Incremental models are needed for large tables where full refreshes are too slow or expensive.
- Reusable SQL logic should be extracted into macros or packages.

## Execution behavior

1. Define sources in a `sources.yml` file with database, schema, table names, and freshness checks. Never reference raw tables directly in models; always go through the source macro `{{ source('source_name', 'table_name') }}`.
2. Build the staging layer first: create one staging model per source table that renames columns to a consistent convention, casts types explicitly, and filters out known bad records. Staging models should be views materialized as `view`.
3. Create intermediate models for business logic that joins, aggregates, or transforms staging models. Name them with an `int_` prefix and materialize as `view` or `ephemeral` depending on reuse.
4. Build mart models as the final consumer-facing tables. These should be materialized as `table` or `incremental` and organized by business domain (e.g., `marts/finance/`, `marts/marketing/`).
5. Add tests to every model: `unique` and `not_null` on primary keys at minimum, `relationships` tests for foreign key integrity, and `accepted_values` for enum columns. Add custom data tests in the `tests/` directory for complex business rules.
6. For large tables (> 10M rows), use incremental materialization with a reliable `unique_key` and an `is_incremental()` filter on a timestamp or monotonically increasing column.
7. Extract repeated SQL patterns into macros in the `macros/` directory. Use Jinja templating for conditional logic, but keep macros focused and well-documented.
8. Write documentation in `schema.yml` files co-located with models. Every model and every column exposed to downstream consumers must have a description.

## Decision tree
- If the model reads from a raw external table -> it must be a staging model that references `{{ source() }}`, not a direct table reference.
- If a table has more than 10M rows and grows daily -> use `incremental` materialization with a `unique_key` and a timestamp-based `is_incremental()` filter.
- If the same SQL logic appears in three or more models -> extract it into a macro with clear parameter names and a docstring.
- If a model is referenced by other models but never queried directly -> consider `ephemeral` materialization to reduce warehouse object count.
- If another team or project has published a dbt package for a shared data source -> use `dbt deps` to install it rather than reimplementing the logic.
- If business logic involves complex conditional aggregation -> build it in an intermediate model with clear naming, not buried in a mart model CTE.

## Anti-patterns
- NEVER query raw source tables directly in intermediate or mart models. Always go through a staging model that normalizes the schema.
- NEVER ship a model without at least `unique` and `not_null` tests on its primary key. Untested models silently propagate data quality issues.
- NEVER build monolithic models with 500+ lines of SQL. Break them into composable staging and intermediate models with clear dependencies.
- NEVER hardcode schema or database names in SQL. Use `{{ target.schema }}`, `{{ source() }}`, or `generate_schema_name` macro for environment portability.
- NEVER run full-refresh on large incremental tables in production without a clear reason. It wastes compute and can cause downstream outages during rebuild.
- NEVER skip documentation for mart models. They are the contract with downstream consumers and must be self-describing.

## Common mistakes
- Forgetting the `{{ config(materialized='incremental') }}` block and the `{% if is_incremental() %}` filter, causing the model to full-refresh every run despite being named "incremental."
- Using `unique_key` in an incremental model but not ensuring the key is actually unique in the source, leading to silent row duplication.
- Defining sources in the model SQL with hardcoded strings instead of using `sources.yml`, which breaks lineage tracking in the DAG and documentation.
- Placing business logic in staging models (which should only rename, cast, and filter) instead of in intermediate or mart models.
- Not configuring `freshness` checks on sources, so stale data flows through the pipeline without any alerting.
- Creating circular dependencies between models (A references B, B references A), which dbt cannot resolve and will error on.

## Output contract
- Every model must have a corresponding entry in a `schema.yml` file with a description and column-level documentation for key fields.
- Primary key columns must have `unique` and `not_null` tests.
- Foreign key relationships must have `relationships` tests pointing to the parent model.
- Staging models must be named `stg_{source}__{table}` and only perform renaming, casting, and basic filtering.
- Mart models must be organized by business domain in subdirectories under `models/marts/`.
- Incremental models must specify `unique_key` and include an `is_incremental()` guard.
- The DAG must have no circular dependencies, and `dbt run` must complete without errors before merging.

## Composability hints
- Before this expert -> use the **SQL Queries Expert** to design and validate complex query logic before embedding it in dbt models.
- Before this expert -> use the **Data Cleaning Expert** to define the cleaning rules that staging models will implement.
- After this expert -> use the **Spark Expert** if dbt output needs further distributed processing beyond what the warehouse supports.
- After this expert -> use the **Visualization Expert** or a BI tool to build dashboards on top of mart models.
- Related -> the **Advanced Pandas Expert** for ad-hoc analysis on data exported from dbt marts.
