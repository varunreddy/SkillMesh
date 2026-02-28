# FastAPI Async Web Framework Expert

Use this expert when tasks require building asynchronous web APIs with FastAPI, including endpoint design, dependency injection, request/response validation with Pydantic, middleware, CORS configuration, background tasks, and application lifespan management.

## When to use this expert
- The task involves building or extending an async Python HTTP API with automatic OpenAPI documentation.
- Request and response validation using Pydantic models is needed.
- The application requires dependency injection for auth, database sessions, or shared resources.
- WebSocket endpoints, background task scheduling, or middleware customization is involved.

## Execution behavior

1. Define the application using `FastAPI()` with explicit `title`, `version`, and `description` for the generated OpenAPI spec.
2. Organize endpoints into `APIRouter` instances grouped by resource domain (e.g., `users`, `items`, `orders`). Mount routers with a consistent URL prefix and tag.
3. Create Pydantic `BaseModel` subclasses for every request body and response payload. Use `Field()` with validation constraints (`min_length`, `ge`, `le`, `pattern`) and set `model_config = ConfigDict(strict=True)` where type coercion is undesirable.
4. Implement shared logic (authentication, DB sessions, pagination params) as `Depends()` callables. Prefer `async def` dependencies that yield for resource cleanup (e.g., closing a session).
5. Add middleware in the correct order: CORS first via `CORSMiddleware`, then custom timing or logging middleware. Register exception handlers for domain-specific error types.
6. For long-running work that should not block the response, use `BackgroundTasks` for lightweight jobs or delegate to Celery/ARQ for heavy processing. Return `202 Accepted` with a task ID.
7. Use the `lifespan` async context manager to initialize and tear down shared resources (connection pools, ML models, caches) instead of the deprecated `on_event` hooks.
8. Write tests using `httpx.AsyncClient` with `ASGITransport(app=app)` for async endpoint testing, ensuring full request/response cycle coverage.

## Decision tree
- If the app exposes CRUD for a resource -> create one router per resource with standard `POST`, `GET`, `PUT/PATCH`, `DELETE` endpoints and consistent Pydantic schemas.
- If authentication is required -> implement it as a dependency (`Depends(get_current_user)`) that raises `HTTPException(401)` on failure; never inline auth checks in route bodies.
- If a request triggers work lasting more than a few seconds -> use `BackgroundTasks` for fire-and-forget or a task queue (Celery, ARQ) for tracked jobs; return `202 Accepted`.
- If the API serves a browser SPA -> configure `CORSMiddleware` with explicit `allow_origins`, not `["*"]` in production.
- If real-time bidirectional communication is needed -> use `WebSocket` routes with proper accept/disconnect handling and authentication via query params or first message.
- If multiple Pydantic models share fields -> use a shared base model and inherit; do not duplicate field definitions across schemas.

## Anti-patterns
- NEVER use blocking I/O (`open()`, `requests.get()`, `time.sleep()`) inside `async def` endpoints. Use `aiofiles`, `httpx.AsyncClient`, or `asyncio.sleep`, or declare the endpoint as `def` to let FastAPI run it in a threadpool.
- NEVER skip Pydantic validation by accepting raw `dict` or `Request.json()` when a model is feasible. Unvalidated input is the top source of runtime errors.
- NEVER catch broad `Exception` silently in route handlers. Let FastAPI's exception handling return proper HTTP error responses; use custom exception handlers for domain errors.
- NEVER omit CORS configuration in API-first applications. The browser will block every cross-origin request without it.
- NEVER store application state in module-level mutable globals. Use `app.state` or dependency injection with lifespan-managed resources.
- NEVER use the deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")` decorators. Use the `lifespan` context manager instead.

## Common mistakes
- Declaring an endpoint as `async def` but calling synchronous ORM methods (e.g., SQLAlchemy sync session) inside it, which blocks the event loop and kills throughput.
- Forgetting to set `status_code=201` on `POST` creation endpoints, returning `200` by default and confusing API consumers.
- Using `response_model` without excluding internal fields (passwords, internal IDs), accidentally exposing sensitive data in responses.
- Not defining `Depends()` at the router level for shared dependencies, repeating the same dependency on every single endpoint.
- Returning a SQLAlchemy model directly instead of converting to a Pydantic schema, causing serialization errors or leaking ORM internals.
- Placing `CORSMiddleware` after other middleware, which can cause preflight `OPTIONS` requests to be intercepted before CORS headers are added.

## Output contract
- Every endpoint must use explicit Pydantic models for request and response typing.
- All routes must be organized under `APIRouter` instances, not defined directly on the `app` object.
- Authentication and authorization must be implemented via dependency injection, not inline logic.
- Error responses must follow a consistent JSON structure (at minimum `{"detail": "..."}` matching FastAPI defaults).
- Background tasks must return `202 Accepted` with a reference ID for status polling.
- The generated OpenAPI spec (`/docs`) must accurately describe all endpoints, schemas, and response codes.
- Application startup/shutdown resources must use the `lifespan` context manager pattern.

## Composability hints
- Before this expert -> use the **REST API Design Expert** to define resource naming, pagination strategy, and error format conventions.
- Before this expert -> use the **SQLAlchemy Expert** to set up async database models and session management.
- After this expert -> use the **Auth JWT Expert** or **Auth OAuth Expert** to implement token-based authentication dependencies.
- Related -> the **Flask Expert** for comparison when choosing between sync-first and async-first Python web frameworks.
- Related -> the **SQLAlchemy Expert** for async session integration via `Depends()` with `AsyncSession`.
