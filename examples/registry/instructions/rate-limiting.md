# Rate Limiting Expert

Use this expert when tasks require designing or implementing rate limiting strategies, including token bucket and sliding window algorithms, Redis-backed distributed limiters, backpressure mechanisms, retry header communication, and quota management for multi-tenant APIs.

## When to use this expert
- The task involves protecting an API from abuse or overload by enforcing request rate limits per client, endpoint, or tenant.
- A distributed rate limiting solution backed by Redis or a similar store must be designed for multi-instance deployments.
- Retry and backoff headers (`Retry-After`, `X-RateLimit-*`) must be included in responses to guide well-behaved clients.
- Quota management is needed to enforce different rate tiers (free, pro, enterprise) for a multi-tenant platform.
- Backpressure strategies must be implemented to gracefully degrade service under sustained load.

## Execution behavior

1. Identify the rate limit dimensions: determine what constitutes a unique client (API key, user ID, IP address, or a composite key) and what scope is being limited (per endpoint, per resource, or globally). Define separate limits for each dimension when needed.
2. Select the algorithm based on requirements. Use **token bucket** for allowing controlled bursts above the sustained rate. Use **sliding window log** for precise per-second accuracy when fairness is critical. Use **fixed window counter** only for low-stakes internal rate limiting where boundary burst tolerance is acceptable.
3. Implement the limiter in a shared store for distributed deployments. Use Redis with atomic Lua scripts to perform check-and-decrement in a single round trip: `MULTI`/`EXEC` or `EVALSHA` to prevent race conditions. Set TTLs on rate limit keys to auto-expire and avoid unbounded memory growth.
4. Return standard rate limit headers on every response: `X-RateLimit-Limit` (max requests in window), `X-RateLimit-Remaining` (requests left), `X-RateLimit-Reset` (UTC epoch when window resets). On rejection, return `429 Too Many Requests` with a `Retry-After` header in seconds.
5. Design quota tiers for multi-tenant systems: define rate limits per plan (e.g., free: 100 req/min, pro: 1000 req/min, enterprise: 10000 req/min). Store quota configurations in a fast-access store and look up the client's tier on each request as part of the rate limit key.
6. Implement backpressure mechanisms for sustained overload: use response status `503 Service Unavailable` with `Retry-After` when the entire system is under stress, distinct from per-client `429` responses. Consider adaptive rate limiting that tightens limits automatically when backend latency exceeds thresholds.
7. Monitor and alert on rate limiting activity: track the ratio of rejected (429) to accepted requests per client and per endpoint. Alert when rejection rates spike for legitimate clients, which may indicate limits are too restrictive or a backend is degraded.

## Decision tree
- If the API must allow short bursts above the steady-state rate -> use a token bucket algorithm with a configurable burst size and refill rate.
- If precise fairness across a rolling time window is required and no bursts are acceptable -> use a sliding window log or sliding window counter algorithm.
- If the service runs on a single instance -> an in-memory limiter (e.g., Python `limits` library, Go `rate` package) is sufficient; avoid the complexity of Redis.
- If the service runs on multiple instances behind a load balancer -> use Redis-backed rate limiting with atomic operations to ensure consistent counts across instances.
- If different endpoints have different cost profiles (e.g., search is expensive, health check is cheap) -> assign different rate limits or cost weights per endpoint.
- If a client is repeatedly rate-limited and appears abusive -> escalate to temporary IP banning or CAPTCHA challenges rather than just returning 429 indefinitely.

## Anti-patterns
- NEVER implement rate limiting with non-atomic read-then-write operations in a distributed store. The race condition between reading the counter and incrementing it allows bursts that exceed the configured limit.
- NEVER use only IP-based rate limiting for authenticated APIs. Shared IPs (NAT, corporate proxies, VPNs) will cause false positives for legitimate users while attackers rotate IPs freely.
- NEVER return a rate limit rejection without `Retry-After` or `X-RateLimit-Reset` headers. Without guidance, clients resort to aggressive retries that worsen the overload.
- NEVER apply a single global rate limit to all endpoints equally. Expensive operations (full-text search, report generation) and cheap operations (health checks, metadata fetches) require different limits.
- NEVER fail open without monitoring when the rate limit store (Redis) is unavailable. Decide explicitly whether to allow all traffic (fail open) or reject all traffic (fail closed) and alert immediately.
- NEVER set rate limits based on guesswork. Measure actual traffic patterns, backend capacity, and latency budgets to derive limits that protect the system without penalizing normal usage.

## Common mistakes
- Using fixed window counters and being surprised by double-rate bursts at window boundaries (e.g., 100 requests at 11:59:59 and 100 more at 12:00:00, producing 200 in a 2-second span).
- Storing rate limit state in application memory in a multi-instance deployment, causing each instance to enforce its own independent limit and allowing N times the intended rate across N instances.
- Forgetting to set TTLs on Redis rate limit keys, causing memory to grow indefinitely as new client keys are created and never expired.
- Applying rate limits after expensive middleware (authentication, body parsing) instead of as early as possible in the request pipeline, wasting resources on requests that will be rejected anyway.
- Returning `403 Forbidden` or `400 Bad Request` instead of the standard `429 Too Many Requests` for rate limit violations, confusing clients and breaking automated retry logic.
- Configuring overly generous rate limits during development and never revisiting them for production traffic, leaving the API effectively unprotected.

## Output contract
- Every rate-limited response must include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers.
- Rejected requests must return `429 Too Many Requests` with a `Retry-After` header specifying seconds until the client may retry.
- Rate limit keys must include a client identifier (API key, user ID) and optionally an endpoint or resource scope.
- Distributed deployments must use atomic operations in the shared store to ensure consistent counting.
- Quota tiers must be documented per plan with clear limits for each endpoint or cost category.
- Monitoring must track acceptance and rejection rates per client, per endpoint, and per tier.

## Composability hints
- Before this expert -> use the **Nginx Expert** to apply basic connection-level rate limiting at the reverse proxy before requests reach the application.
- Before this expert -> use the **API Gateway Expert** to enforce rate limits at the gateway layer for centralized control across multiple services.
- After this expert -> use the **FastAPI Expert** or **Flask Expert** to integrate the rate limiter as middleware in the application framework.
- Related -> the **REST API Design Expert** for defining how rate limit information is communicated in the API specification and error responses.
- Related -> the **API Authentication Patterns Expert** for tying rate limit keys to authenticated client identities rather than raw IP addresses.
