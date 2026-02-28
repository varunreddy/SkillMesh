# REST API Design Expert

Use this expert when tasks require designing RESTful APIs, including resource naming conventions, HTTP method semantics, pagination strategies, filtering and sorting, error response formats, content negotiation, and API versioning.

## When to use this expert
- The task involves designing a new API surface or refactoring an existing one to follow REST conventions.
- Decisions about URL structure, HTTP methods, status codes, or error response formats are needed.
- A pagination strategy must be chosen for list endpoints that may return large collections.
- API versioning is required to support backward compatibility while evolving the interface.

## Execution behavior

1. Identify the core resources (nouns) in the domain and map them to URL paths using plural nouns: `/users`, `/orders`, `/products`. Avoid verbs in URLs; let HTTP methods convey the action.
2. Map operations to HTTP methods consistently: `GET` for reads (safe, idempotent), `POST` for creation, `PUT` for full replacement (idempotent), `PATCH` for partial update, `DELETE` for removal (idempotent). Return appropriate status codes for each.
3. Design sub-resources for relationships: `/users/{id}/orders` to list orders belonging to a user. Limit nesting to two levels; deeper hierarchies should use top-level resources with query parameter filters.
4. Choose a pagination strategy for all list endpoints: use cursor-based pagination (opaque `next_cursor` token) for large or frequently changing datasets, or offset/limit for simple use cases where total count is needed. Include `next`, `previous`, and `total` metadata in the response envelope.
5. Implement filtering via query parameters: `GET /orders?status=shipped&created_after=2025-01-01`. Support sorting with a `sort` parameter: `?sort=-created_at,name` (prefix `-` for descending). Document allowed filter fields explicitly.
6. Standardize error responses using RFC 7807 Problem Details format: `{"type": "uri", "title": "string", "status": int, "detail": "string", "instance": "uri"}`. Map all application errors to this structure with appropriate HTTP status codes.
7. Version the API using a URL prefix (`/v1/`, `/v2/`) for major breaking changes. Use additive, non-breaking changes (new optional fields, new endpoints) within a version. Deprecate old versions with a timeline communicated via `Deprecation` and `Sunset` response headers.
8. Document the API with an OpenAPI 3.x specification that covers all endpoints, request/response schemas, authentication requirements, and example payloads.

## Decision tree
- If the collection can grow to thousands of items or rows are frequently inserted/deleted -> use cursor-based pagination to avoid offset drift and O(n) database scans.
- If the client needs to jump to arbitrary pages or needs a total count -> use offset/limit pagination with a capped maximum limit (e.g., 100) and include `total` in metadata.
- If a breaking change is needed (removing a field, renaming a resource, changing semantics) -> increment the major version prefix (`/v1/` to `/v2/`) and support the old version for a deprecation period.
- If the change is additive (new optional field, new endpoint, new enum value) -> release within the current version; additive changes do not require a version bump.
- If error details vary by context -> use the RFC 7807 `type` URI to distinguish error categories and `detail` for human-readable specifics.
- If a resource action does not map cleanly to CRUD -> use a sub-resource verb as a last resort (`POST /orders/{id}/cancel`) rather than putting verbs in the main resource path.

## Anti-patterns
- NEVER use verbs in resource URLs (`/getUsers`, `/createOrder`). The HTTP method already communicates the action; URLs should represent resources (nouns).
- NEVER return inconsistent error formats across endpoints. Every error response in the API must follow the same structure (preferably RFC 7807) regardless of which endpoint produced it.
- NEVER return unbounded list responses without pagination. A single `GET /items` returning 100,000 rows will exhaust memory and timeout.
- NEVER introduce breaking changes without versioning. Removing a field or changing a response structure silently breaks all existing clients.
- NEVER use `GET` requests for operations that modify state. `GET` must be safe and idempotent; mutations belong to `POST`, `PUT`, `PATCH`, or `DELETE`.
- NEVER return `200 OK` for error conditions. Use the correct HTTP status code: `400` for client errors, `404` for missing resources, `409` for conflicts, `422` for validation failures, `500` for server errors.

## Common mistakes
- Using singular nouns for collection endpoints (`/user` instead of `/users`), creating inconsistency when the same path is used for both list and single-resource operations.
- Returning `200 OK` with an empty body for `DELETE` instead of `204 No Content`, or returning `200` for `POST` creation instead of `201 Created` with a `Location` header.
- Nesting resources too deeply (`/users/{uid}/orders/{oid}/items/{iid}/reviews`) when a flatter structure with filters (`/reviews?item_id={iid}`) would be simpler and more flexible.
- Including sensitive data in URLs or query parameters (tokens, passwords, PII), which get logged by proxies, browsers, and web servers.
- Using HTTP status code `500` for all errors instead of distinguishing client errors (4xx) from server errors (5xx), making it impossible for clients to handle errors programmatically.
- Designing filtering with `POST` request bodies instead of query parameters for `GET` requests, breaking cacheability and violating HTTP semantics.

## Output contract
- All resource URLs must use plural nouns, lowercase, hyphen-separated (`/user-profiles`, not `/UserProfiles` or `/user_profiles`).
- Every list endpoint must include pagination with documented limits and metadata (`next`, `previous`, `total` or `has_more`).
- All error responses must follow RFC 7807 Problem Details format with `type`, `title`, `status`, and `detail` fields.
- HTTP methods must be used correctly: `GET` (read), `POST` (create), `PUT` (replace), `PATCH` (partial update), `DELETE` (remove).
- Response status codes must match the operation: `200` (success), `201` (created), `204` (no content), `400` (bad request), `401` (unauthorized), `403` (forbidden), `404` (not found), `409` (conflict), `422` (unprocessable entity).
- The API must be versioned, with the strategy documented and applied consistently.
- An OpenAPI 3.x specification must describe all endpoints, schemas, and auth requirements.

## Composability hints
- After this expert -> use the **FastAPI Expert** or **Flask Expert** to implement the designed API endpoints in a Python web framework.
- After this expert -> use the **Auth JWT Expert** or **Auth OAuth Expert** to design and implement the authentication layer referenced in the API spec.
- Related -> the **SQLAlchemy Expert** for mapping resource schemas to database models and implementing pagination at the query level.
- Related -> the **Data Cleaning Expert** when API input data requires validation and normalization beyond what the framework provides.
- Related -> any domain expert (Scikit-learn, NLP, Visualization) when the API serves ML predictions, text analysis, or chart generation.
