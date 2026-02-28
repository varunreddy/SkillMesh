# Advanced Pandas Expert

Use this expert for complex DataFrame manipulation including groupby aggregations, multi-table merges, memory optimization, method chaining, and vectorized transformations on structured tabular data.

## When to use this expert
- The task involves multi-step groupby, pivot, or reshape operations beyond simple filtering.
- Multiple DataFrames must be joined with explicit merge strategies based on key cardinality.
- Memory pressure is a concern (datasets approaching or exceeding 1 GB in RAM).
- Performance-critical code needs to replace row-wise iteration with vectorized operations.

## Execution behavior

1. Profile the DataFrame first: inspect `df.info(memory_usage='deep')`, `df.dtypes`, and `df.nunique()` to identify optimization opportunities before writing any transformation logic.
2. Downcast numeric columns early using `pd.to_numeric(col, downcast='integer')` or `downcast='float'` to reduce memory footprint before heavy operations.
3. Convert low-cardinality string columns (unique ratio < 50%) to `category` dtype to compress memory and speed up groupby and merge operations.
4. For multi-table joins, explicitly choose the merge strategy: use `how='inner'` for intersection, `how='left'` to preserve the driving table, `how='outer'` for union, and `how='cross'` only when a full cartesian product is intentional and bounded.
5. Validate merge results immediately: check row count against expectations, inspect `_merge` indicator column from `indicator=True`, and assert no unintended row duplication from many-to-many keys.
6. Build transformations as method chains using `.pipe()`, `.assign()`, and `.query()` for readability. Each chain step should perform one logical operation.
7. Prefer vectorized operations (`np.where`, `.str` accessor, `.dt` accessor) over `.apply()`. Use `.apply()` only when no vectorized alternative exists, and document why.
8. For datasets exceeding available RAM, use chunked reading with `pd.read_csv(chunksize=...)` and process each chunk identically, or switch to a Spark-based expert.

## Decision tree
- If dataset > 1 GB in memory -> downcast numerics, convert strings to categoricals, and consider chunked processing before any transformation.
- If a string column has fewer than 5% unique values relative to row count -> convert to `category` dtype immediately.
- If joining two tables -> check key cardinality on both sides; one-to-many is safe, many-to-many requires explicit deduplication or aggregation first.
- If aggregation needs multiple output columns -> use `.agg()` with a dictionary or named aggregation syntax, not multiple separate groupby calls.
- If row-wise logic involves simple conditionals -> use `np.select()` or `np.where()` instead of `.apply(lambda)`.
- If the operation is a running or rolling calculation -> use `.rolling()`, `.expanding()`, or `.shift()` instead of manual loops.

## Anti-patterns
- NEVER iterate rows with `for index, row in df.iterrows()`. This is orders of magnitude slower than vectorized alternatives.
- NEVER use chained indexing like `df['a']['b'] = value`. Use `.loc[row, col]` to avoid the SettingWithCopyWarning and silent failures.
- NEVER ignore memory usage on large DataFrames. Calling `.copy()` carelessly can double RAM consumption.
- NEVER use `.apply()` with a lambda that wraps a vectorized pandas or numpy function. Call the vectorized function directly.
- NEVER merge without validating the key relationship. Unexpected many-to-many joins silently explode row counts.

## Common mistakes
- Using `inplace=True` in method chains, which breaks the chain and returns `None` instead of the modified DataFrame.
- Forgetting that `groupby().transform()` returns a Series aligned to the original index, while `groupby().agg()` returns a reduced DataFrame. Mixing them up causes shape mismatches.
- Passing `on=` column names that have different dtypes across the two DataFrames (e.g., int vs. string), producing zero matches silently.
- Resetting the index after a groupby but forgetting that the grouped columns become the index by default unless `as_index=False` is specified.
- Using `.fillna(0)` indiscriminately, which masks genuine missing data and corrupts downstream statistical calculations.
- Sorting a large DataFrame repeatedly inside a loop instead of sorting once and using `.searchsorted()` or merge-based lookups.

## Output contract
- Report memory usage before and after optimization steps (e.g., "Reduced from 2.1 GB to 640 MB via downcasting and categoricals").
- Include row and column counts at key transformation stages to make the data lineage auditable.
- Validate merge results with `indicator=True` and summarize match rates (both, left_only, right_only).
- Return the final DataFrame with a clean, reset integer index unless the index carries semantic meaning.
- Document any columns dropped, renamed, or type-coerced during the pipeline.
- Emit dtype summary of the output DataFrame.
- If chunked processing was used, report total rows processed and any chunks that raised warnings.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle nulls, deduplication, and type normalization.
- After this expert -> use the **Visualization Expert** to plot distributions, aggregation summaries, or merge diagnostics.
- After this expert -> use the **SQL Queries Expert** if the transformed data needs to be loaded into a relational database.
- Related -> the **Spark Expert** when data volume exceeds single-machine memory limits.
- Related -> the **Time Series Expert** when datetime indexing and temporal aggregation are the primary concern.
