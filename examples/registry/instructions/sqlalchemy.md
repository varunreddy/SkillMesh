# SQLAlchemy ORM Expert

Use this expert when tasks require database modeling and querying with SQLAlchemy, including session lifecycle management, relationship loading strategies, schema migrations with Alembic, connection pooling, and query optimization for both sync and async applications.

## When to use this expert
- The task involves defining database models, relationships, and constraints using SQLAlchemy's ORM layer.
- Query performance optimization is needed, particularly around N+1 queries and relationship loading strategies.
- Schema migrations must be managed with Alembic in a production-safe manner.
- The application requires async database access with `AsyncSession` and an async driver like `asyncpg` or `aiosqlite`.

## Execution behavior

1. Define models using the declarative base with mapped columns (`Mapped[type]`, `mapped_column()`) from SQLAlchemy 2.0 style. Specify `__tablename__`, primary keys, indexes, and unique constraints explicitly.
2. Define relationships using `relationship()` with explicit `back_populates` on both sides. Choose the loading strategy at the relationship level (`lazy="select"` default) and override per-query when needed.
3. Configure the engine with appropriate connection pooling: set `pool_size`, `max_overflow`, `pool_recycle` (especially for MySQL which drops idle connections), and `pool_pre_ping=True` to detect stale connections.
4. Manage sessions using a context manager or dependency injection pattern. In web applications, use one session per request with a `try/commit/except/rollback/finally/close` pattern or `Session.begin()` context manager.
5. For read-heavy queries with relationships, use `joinedload()` to fetch related objects in a single JOIN, `selectinload()` for one-to-many collections to avoid cartesian products, or `subqueryload()` when the main query has LIMIT/OFFSET.
6. Write schema migrations with Alembic: run `alembic revision --autogenerate -m "description"` to detect model changes, review the generated migration for correctness, and test both `upgrade()` and `downgrade()` paths before deploying.
7. For async applications, use `create_async_engine()` with `asyncpg` (PostgreSQL) or `aiosqlite` (SQLite), and `async_sessionmaker` for session creation. Use `await session.execute()` and `await session.commit()` consistently.
8. Profile slow queries by enabling `echo=True` on the engine during development or using SQLAlchemy's event system to log queries exceeding a duration threshold.

## Decision tree
- If a query loads a list of parent objects and accesses a relationship on each -> use `joinedload()` for to-one or small to-many, `selectinload()` for large to-many collections to avoid N+1 queries.
- If writing many rows at once -> use `session.bulk_insert_mappings()` or `session.execute(insert(Model).values(list_of_dicts))` for bulk operations; avoid creating individual ORM objects in a loop.
- If the query involves complex filtering, grouping, or subqueries -> use SQLAlchemy Core (`select()`, `func`, `join()`) instead of ORM query patterns for clarity and performance.
- If the application is async (FastAPI, aiohttp) -> use `AsyncSession` with `asyncpg`; never mix sync session calls into async code paths.
- If a migration alters a large table in production -> break it into non-locking steps: add new column (nullable), backfill data, add constraint, then drop old column in a separate migration.
- If models have soft-delete semantics -> add a `deleted_at` column and apply a default query filter rather than actually deleting rows.

## Anti-patterns
- NEVER rely on default `lazy="select"` loading when iterating over collections in a loop. This creates N+1 queries that scale linearly with result count, often the single biggest performance problem in ORM-based applications.
- NEVER let sessions leak by forgetting to close or commit them. Unclosed sessions hold database connections from the pool indefinitely, eventually exhausting the pool.
- NEVER construct queries with raw f-strings or string concatenation. Use SQLAlchemy's parameterized query system (`text()` with `:param` binds) or the ORM expression language to prevent SQL injection.
- NEVER disable connection pooling in production. Use `pool_pre_ping=True` and appropriate pool sizing instead of `NullPool`.
- NEVER mix sync `Session` with async code or vice versa. Sync sessions in async endpoints block the event loop; async sessions in sync code raise runtime errors.
- NEVER run `alembic revision --autogenerate` without reviewing the generated migration. Autogenerate misses some changes (table renames, data migrations) and can generate destructive operations.

## Common mistakes
- Using `lazy="joined"` on a relationship with large collections, which creates cartesian products that multiply result rows and consume memory. Prefer `selectinload()` per-query for large collections.
- Forgetting `expire_on_commit=False` when objects need to be accessed after `session.commit()`, causing unexpected `DetachedInstanceError` exceptions.
- Creating the engine inside a function called per-request, which spins up a new connection pool each time instead of reusing a single engine instance.
- Writing Alembic migrations that combine schema changes with data migrations in the same revision, making rollbacks unreliable.
- Not setting `pool_recycle` when using MySQL or MariaDB, causing `OperationalError: (2006, 'MySQL server has gone away')` after the server's `wait_timeout` elapses.
- Using `session.merge()` when `session.add()` is intended, which triggers an unnecessary SELECT before the INSERT.

## Output contract
- All models must use SQLAlchemy 2.0 declarative style with `Mapped` type annotations and explicit `mapped_column()` definitions.
- Relationships must specify `back_populates` on both sides and document the intended loading strategy.
- Every query that accesses relationships on multiple objects must use an explicit eager loading option, never relying on lazy loading in loops.
- Sessions must be managed with a context manager or a clear open/commit/rollback/close lifecycle.
- Schema changes must be tracked in Alembic migrations with both `upgrade()` and `downgrade()` functions.
- Connection pooling configuration must be explicit, with `pool_pre_ping=True` enabled.
- Async applications must use `AsyncSession` and an async-compatible database driver throughout.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to prepare and validate data before bulk insertion into the database.
- After this expert -> use the **FastAPI Expert** to wire async sessions into dependency injection, or the **Flask Expert** for Flask-SQLAlchemy integration.
- Related -> the **Auth JWT Expert** for storing user accounts and refresh tokens that the ORM models represent.
- Related -> the **REST API Design Expert** for mapping ORM models to API resource schemas and pagination strategies.
- Related -> the **Gradient Boosting Expert** or **Scikit-learn Expert** when querying training data from a database for ML pipelines.
