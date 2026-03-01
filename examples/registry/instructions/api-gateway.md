# API Gateway Expert

Use this expert when tasks require designing or operating an API gateway layer, including request routing, load balancing, circuit breakers, distributed tracing, service discovery, and integration with a service mesh for microservice architectures.

## When to use this expert
- The task involves routing external or internal traffic to backend microservices through a centralized gateway.
- Circuit breaker patterns are needed to prevent cascading failures when downstream services become unhealthy.
- Distributed tracing must be configured to track requests as they traverse multiple services.
- Service discovery and dynamic load balancing are required to route traffic to healthy, registered instances.
- A decision must be made between API gateway products (Kong, AWS API Gateway, Envoy, Traefik, APISIX).

## Execution behavior

1. Define the gateway's routing table by mapping external URL paths to internal backend services. Use path-based routing (`/api/users -> user-service:8080`) as the default strategy and header-based or host-based routing when multi-tenant or versioned APIs require it.
2. Configure load balancing across service instances using round-robin for uniform workloads or least-connections for variable-latency backends. Enable health checks (active HTTP probes and passive error tracking) to remove unhealthy instances from the rotation automatically.
3. Implement circuit breaker policies per upstream service: define thresholds for consecutive failures (e.g., 5 failures in 30 seconds), a half-open probe interval, and fallback responses. Use exponential backoff for retry policies and cap retries at 2-3 attempts to avoid retry storms.
4. Inject distributed tracing headers (W3C Trace Context or B3 propagation) at the gateway. Ensure the gateway creates a root span for each inbound request and propagates `traceparent` / `tracestate` headers to all upstream calls. Export spans to a collector (Jaeger, Zipkin, or OpenTelemetry Collector).
5. Integrate service discovery so the gateway resolves backend addresses dynamically. Use DNS-based discovery (Kubernetes Services, Consul DNS) for simplicity or API-based discovery (Consul HTTP, Eureka) when metadata-driven routing (canary weights, instance tags) is needed.
6. Apply cross-cutting concerns at the gateway: authentication token validation, request/response transformation, CORS preflight handling, request ID injection, and response compression. Implement these as middleware or plugin chains with a defined execution order.
7. Configure observability: emit request count, latency percentiles (p50, p95, p99), and error rate metrics per route and per upstream service. Set up alerts for error rate spikes and latency degradation.

## Decision tree
- If the architecture has fewer than 5 services and simple routing needs -> a lightweight reverse proxy (Nginx, Caddy) with manual configuration may suffice over a full gateway.
- If the architecture involves 10+ microservices with independent deployment -> use a dedicated API gateway (Kong, Envoy, APISIX) with service discovery and dynamic configuration.
- If the team runs on Kubernetes -> leverage the Kubernetes Gateway API or an ingress controller (Envoy-based, Traefik) that natively integrates with service discovery.
- If a downstream service is latency-sensitive and failure-prone -> enable circuit breakers with aggressive thresholds and provide a cached or degraded fallback response.
- If end-to-end request tracing is needed across services -> ensure the gateway initiates trace context and every downstream service propagates it; use OpenTelemetry for vendor-neutral instrumentation.
- If canary or blue-green deployments are required -> configure weighted routing at the gateway to split traffic between versions based on percentage or header matches.

## Anti-patterns
- NEVER allow the API gateway to contain business logic. The gateway handles routing, security, and observability; business rules belong in the backend services.
- NEVER configure unlimited retries on upstream failures. Unbounded retries amplify load on struggling services and cause retry storms that deepen outages.
- NEVER skip health checks for upstream services. Routing traffic to an unhealthy instance causes user-facing errors that the gateway could have avoided.
- NEVER hardcode backend service addresses in gateway configuration when running in dynamic environments. Use service discovery to handle instance scaling and replacement.
- NEVER log full request and response bodies at the gateway in production. This leaks sensitive data, inflates storage costs, and degrades throughput. Log metadata only (method, path, status, latency).
- NEVER use a single global timeout for all routes. Different backends have different latency profiles; set per-route timeouts based on measured p99 latencies with headroom.

## Common mistakes
- Setting circuit breaker thresholds too aggressively (e.g., 1 failure opens the circuit), causing transient errors to trigger unnecessary service isolation and degraded user experience.
- Forgetting to propagate trace context headers through the gateway, breaking the trace chain and producing disconnected spans that are useless for debugging.
- Placing authentication enforcement in each backend service instead of at the gateway, duplicating logic and creating inconsistent security policies across services.
- Configuring load balancing without health checks, allowing the gateway to keep routing traffic to crashed or overloaded instances.
- Using the gateway as a message broker by buffering large request bodies, exceeding memory limits and creating a single point of failure for throughput.
- Neglecting to set connection pool limits per upstream, allowing one misbehaving backend to exhaust all gateway connections and starve other routes.

## Output contract
- Every external route must map to an internal upstream service with explicit timeout and retry configuration.
- Circuit breaker settings must be defined per upstream with failure thresholds, recovery intervals, and fallback behavior documented.
- Distributed tracing headers must be injected at the gateway and propagated to all upstream calls.
- Health checks (active and/or passive) must be configured for every upstream service.
- Gateway metrics (request rate, latency percentiles, error rate) must be emitted per route and per upstream.
- Authentication and cross-cutting middleware must execute in a documented, deterministic order.

## Composability hints
- Before this expert -> use the **Nginx Expert** for understanding reverse proxy fundamentals that underpin most gateway implementations.
- Before this expert -> use the **Docker Expert** or **Kubernetes Expert** to containerize and orchestrate the services the gateway will route to.
- After this expert -> use the **Rate Limiting Expert** to enforce per-client or per-route rate limits at the gateway layer.
- After this expert -> use the **Prometheus and Grafana Expert** to build dashboards and alerts from the metrics the gateway emits.
- Related -> the **Secrets Management Expert** for securely storing TLS certificates and API keys used by the gateway.
