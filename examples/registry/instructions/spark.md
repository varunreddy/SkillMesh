# Apache Spark Expert

Use this expert for distributed data processing with PySpark including partitioning strategy, join optimization, shuffle management, Spark SQL, caching policies, and memory tuning for large-scale datasets.

## When to use this expert
- The dataset exceeds single-machine memory and requires distributed processing.
- Join, aggregation, or transformation logic must scale across a cluster.
- Shuffle-heavy operations are causing performance bottlenecks or out-of-memory errors.
- The task involves migrating pandas logic to a Spark-native implementation.

## Execution behavior

1. Define the SparkSession with explicit configuration: set `spark.sql.shuffle.partitions` based on data size (default 200 is often wrong), configure memory fractions, and enable adaptive query execution (`spark.sql.adaptive.enabled=true`) on Spark 3+.
2. Read source data with schema inference disabled for production jobs. Provide an explicit schema using `StructType` to avoid a full data scan and prevent type mismatches.
3. Assess data volume and partition count: target 128 MB to 256 MB per partition. Use `repartition()` to increase parallelism or `coalesce()` to reduce partitions without a full shuffle.
4. For joins, identify the smaller table. If it fits in driver memory (< 100 MB by default, tunable via `spark.sql.autoBroadcastJoinThreshold`), let Spark broadcast it automatically or use `broadcast()` hint explicitly.
5. For skewed join keys, apply salting: append a random integer to the skewed key on the large side, replicate the small side with matching salt values, join, and then aggregate to remove the salt.
6. Prefer built-in Spark SQL functions (`pyspark.sql.functions`) and the DataFrame API over Python UDFs. If a UDF is unavoidable, use `pandas_udf` (vectorized) instead of row-wise `udf()` for an order-of-magnitude performance gain.
7. Cache or persist DataFrames that are reused across multiple actions. Use `MEMORY_AND_DISK` storage level for large intermediate results, and `.unpersist()` when no longer needed.
8. Monitor execution via the Spark UI: check stage durations, shuffle read/write sizes, and task skew (max vs. median task time). Optimize the slowest stage first.

## Decision tree
- If one join side is small (< 200 MB) -> broadcast it to avoid shuffle. Use `F.broadcast(small_df)` or increase `autoBroadcastJoinThreshold`.
- If a join key is heavily skewed (one key has > 10x the average row count) -> salt the skewed key to distribute rows evenly across partitions.
- If the job runs an iterative algorithm (ML training, graph processing) -> cache the input DataFrame and intermediate results to avoid recomputation on each iteration.
- If the operation is expressible in SQL -> prefer `spark.sql()` or the DataFrame API over RDD transformations. The Catalyst optimizer cannot optimize RDD code.
- If shuffle partitions cause many small files on write -> use `coalesce()` before writing, or set `spark.sql.shuffle.partitions` to match the output file count target.
- If a stage has tasks that take 10x longer than the median -> investigate data skew or partition imbalance; apply repartitioning or salting.

## Anti-patterns
- NEVER call `.collect()` or `.toPandas()` on a large DataFrame. This pulls all data to the driver and causes out-of-memory crashes. Filter or aggregate first.
- NEVER use a Python `udf()` when an equivalent built-in function exists. Python UDFs serialize data row-by-row between the JVM and Python, destroying performance.
- NEVER use too few partitions (under-parallelism wastes cluster resources) or too many (excessive scheduling overhead and small files). Target partition sizes of 128-256 MB.
- NEVER leave cached DataFrames in memory after they are no longer needed. Orphaned caches consume executor memory and cause spills.
- NEVER perform a cartesian join (`crossJoin`) without a subsequent filter or on unbounded data. The result size is the product of both sides.
- NEVER write shuffle-heavy logic inside a loop (e.g., repeated joins in a for loop). Restructure as a single wide join or a union followed by groupby.

## Common mistakes
- Relying on default `spark.sql.shuffle.partitions=200` for all job sizes. A 10 TB job needs thousands of partitions; a 1 GB job needs fewer than 20.
- Calling `.count()` or `.show()` for debugging in production code, which triggers a full job execution and doubles runtime.
- Writing output as a single file (`.coalesce(1).write`) for large datasets, which forces all data through one executor and eliminates parallelism.
- Forgetting that Spark transformations are lazy. Errors in transformation logic only surface when an action (`.count()`, `.write()`, `.collect()`) triggers execution.
- Using `.repartition(n)` when `.coalesce(n)` would suffice for reducing partitions. `repartition` performs a full shuffle; `coalesce` merges partitions locally.
- Not enabling adaptive query execution (AQE) on Spark 3+, which automatically handles skew joins and partition coalescing.

## Output contract
- Report the cluster configuration: number of executors, cores per executor, memory per executor, and Spark version.
- Include partition count and approximate partition size for key DataFrames.
- Document any broadcast hints, salting, or repartitioning applied and the rationale.
- Report job duration, total shuffle read/write, and any stages with significant skew from the Spark UI.
- If caching was used, list cached DataFrames and their storage levels.
- Output data must be written in a partitioned, columnar format (Parquet preferred) unless a specific format is required.
- Record the final output row count, file count, and total size on disk.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** or **Advanced Pandas Expert** for schema design and small-scale prototyping before scaling to Spark.
- Before this expert -> use the **SQL Queries Expert** to design and validate query logic on a sample before implementing in Spark SQL.
- After this expert -> use the **dbt Expert** if the Spark output feeds into a data warehouse with model layering and testing.
- Related -> the **Advanced Pandas Expert** for single-machine tasks that do not require distributed processing.
- Related -> the **Time Series Expert** when temporal data processed in Spark needs forecasting or decomposition downstream.
