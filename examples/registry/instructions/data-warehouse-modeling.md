# Data Warehouse Modeling Expert

Use this expert for dimensional modeling, grain design, and warehouse performance optimization.

## When to use this expert
- You are structuring raw operational data into analytical, business-facing semantic models.
- You need to build Kimball star schemas (facts and dimensions) or Data Vault topologies.
- You are dealing with slow-changing dimensions (SCDs) and complex many-to-many relationships.
- You want to optimize warehouse query performance through partitioning and clustering.

## Execution behavior
1. Gather analytical requirements to firmly establish the business process and granularity.
2. Design standardized Date and Time generic dimensions for all chronological merging.
3. Build immutable, additive Fact tables tracking specific business events.
4. Implement Type 1, 2, or 3 Slow-Changing Dimensions based on historical tracking needs.
5. Create bridging configurations to resolve many-to-many dimensional associations.
6. Enforce rigorous naming conventions mapping raw cryptic codes to human-readable columns.
7. Optimize physical storage using partitioning by date and clustering by highly-filtered columns.
8. Document the semantic layer metrics and column definitions in a centralized data dictionary.

## Decision tree
- If tracking state transitions over time with full historical accuracy, choose SCD Type 2.
- If business users query a single unified dashboard, choose a wide analytical datamart over pure 3NF.
- If centralizing massive disparate source systems requiring auditability, choose Data Vault patterns.
- If aggregating daily snapshot fact totals, choose periodic snapshot fact tables.
- If metrics cannot be summed across dimensions (e.g., account balances), choose semi-additive declarations.
- If tables span terabytes and queries filter by year, choose explicit time-based partitioning.

## Anti-patterns
- NEVER mix granularities inside a single fact table.
- NEVER expose raw source system column names (e.g., `x_bll_t`) to the BI presentation layer.
- NEVER use string natural keys as dimensional join keys (always formulate surrogate keys).
- NEVER resolve complex JSON arrays dynamically inside the BI tool instead of the warehouse.
- NEVER build circular dependencies across transformed analytical models.
- NEVER aggregate data before users have verified the lowest atomic grain logic.

## Common mistakes
- Misidentifying the true grain of a business transaction leading to Cartesian explosions.
- Forgetting to handle NULLs explicitly in dimension linkages resulting in dropped inner-join records.
- Creating too many tiny snowflake dimensions instead of flattening them into broader dimension tables.
- Treating physical table partitions like indexes, resulting in over-partitioning and metadata overhead.
- Ignoring timezone standardization across different source systems within the fact tables.
- Applying heavy business logic filters in views rather than materializing the transformations.

## Output contract
- Entity Relationship Diagram (ERD) mapping facts directly to dimensions.
- Explicit granularity definitions per physical model.
- Slow-Changing Dimension (SCD) strategy and surrogate key generation rules.
- Physical storage tuning config (partitions, clustering, sort keys).
- Naming convention standard sheet.
- Data dictionary mapping specific column definitions to business concepts.

## Composability hints
- Execute the logical models using declarative pipelines from `data.dbt`.
- Provide optimized, pre-aggregated semantic tables directly to `bi.looker-modeling`.
- Implement testing thresholds using `data.data-quality-validation` on all generated surrogate keys.
- Orchestrate the loading strategy with `data.data-orchestration` to populate dimensions before facts.
