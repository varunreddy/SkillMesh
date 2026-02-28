# SQL Query Design Expert

Use this expert for writing efficient, readable SQL queries including join design, CTEs, window functions, indexing strategies, and query performance analysis using EXPLAIN plans.

## When to use this expert
- The task requires multi-table joins, subqueries, or aggregation logic in a relational database.
- Window functions are needed for ranking, running totals, or lag/lead calculations.
- Query performance is poor and needs EXPLAIN-based diagnosis and index-aware rewriting.
- Complex business logic must be expressed as readable, maintainable SQL using CTEs.

## Execution behavior

1. Clarify the target database engine (PostgreSQL, MySQL, SQLite, SQL Server, BigQuery) because syntax for window functions, CTEs, and EXPLAIN varies across engines.
2. Identify all tables involved and map their relationships (primary keys, foreign keys, cardinality) before writing any query.
3. Structure complex queries top-down using CTEs (`WITH` clauses) for readability. Each CTE should perform one logical step: filter, join, aggregate, or transform.
4. Choose the correct join type explicitly: `INNER JOIN` for matching rows only, `LEFT JOIN` to preserve the driving table, `CROSS JOIN` only when a bounded cartesian product is intentional.
5. For ranking, running totals, or row comparison tasks, use window functions (`ROW_NUMBER`, `RANK`, `SUM() OVER`, `LAG`, `LEAD`) instead of self-joins or correlated subqueries.
6. Run `EXPLAIN` (or `EXPLAIN ANALYZE` in PostgreSQL) on every non-trivial query to verify the planner uses indexes and estimate row counts match expectations.
7. Recommend or create indexes on columns used in `WHERE`, `JOIN ON`, `ORDER BY`, and `GROUP BY` clauses when sequential scans appear in the plan on large tables.
8. Parameterize all user-supplied values using prepared statements or query parameters. Never concatenate strings into SQL.

## Decision tree
- If the task involves ranking or top-N per group -> use `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` with a CTE, not a self-join or correlated subquery.
- If the query needs hierarchical or recursive data traversal -> use a recursive CTE with a clear termination condition and a `MAXRECURSION` guard where supported.
- If both aggregate and detail columns are needed in the same result -> use a window function, not a subquery that re-scans the table.
- If query is slow on a table with > 1M rows -> run `EXPLAIN ANALYZE` first; add covering indexes before rewriting the query.
- If repeated filtering or transformation logic appears across multiple queries -> extract it into a view or a CTE referenced once.
- If data must be pivoted from rows to columns -> use `CASE WHEN` aggregation (portable) or engine-specific `PIVOT`/`CROSSTAB`.

## Anti-patterns
- NEVER use `SELECT *` in production queries. Explicitly list needed columns to reduce I/O, prevent schema-change breakage, and improve plan efficiency.
- NEVER write correlated subqueries in `SELECT` or `WHERE` when an equivalent join or window function exists. They execute once per outer row.
- NEVER build dynamic SQL by string concatenation with user input. This creates SQL injection vulnerabilities. Use parameterized queries.
- NEVER rely on implicit join syntax (`FROM a, b WHERE a.id = b.id`). Use explicit `JOIN ... ON` for clarity and to avoid accidental cartesian products.
- NEVER add indexes blindly. Each index slows writes and consumes storage. Index only columns that appear in frequently executed filter or join predicates.
- NEVER assume the optimizer will fix a poorly structured query. Measure with EXPLAIN, then optimize.

## Common mistakes
- Filtering on a function-wrapped column (`WHERE YEAR(date_col) = 2024`) which prevents index usage. Rewrite as a range predicate (`WHERE date_col >= '2024-01-01' AND date_col < '2025-01-01'`).
- Using `DISTINCT` to mask an accidental cartesian join instead of fixing the join condition.
- Confusing `WHERE` and `HAVING`: `WHERE` filters rows before aggregation, `HAVING` filters groups after aggregation. Putting a non-aggregate condition in `HAVING` hurts performance.
- Ignoring NULL semantics: `NULL = NULL` is false in SQL. Use `IS NULL` or `COALESCE` for null-safe comparisons and joins.
- Writing `ORDER BY` inside a CTE or subquery without `TOP`/`LIMIT`, which most engines ignore because intermediate result order is not guaranteed.
- Using `UNION` when `UNION ALL` is sufficient, paying an unnecessary deduplication sort cost.

## Output contract
- All queries must use explicit `JOIN ... ON` syntax with table aliases.
- CTEs must have descriptive names reflecting their logical purpose (e.g., `monthly_revenue`, `ranked_users`).
- Include `EXPLAIN` output or a summary for any query touching tables with more than 100K rows.
- Parameterize all external inputs; never embed literal user-supplied values.
- Annotate any engine-specific syntax with a comment noting the target database.
- Report expected result shape (row count estimate, column list) before execution.
- If indexes are recommended, specify the exact `CREATE INDEX` statement with column order.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to ensure source tables are deduplicated and typed correctly before complex joins.
- After this expert -> use the **Advanced Pandas Expert** for further in-memory transformation on the query result.
- After this expert -> use the **Visualization Expert** to chart aggregated query results.
- Related -> the **dbt Expert** for managing SQL transformations as version-controlled, tested models in a warehouse.
- Related -> the **Spark Expert** when SQL queries must scale beyond a single-database engine.
