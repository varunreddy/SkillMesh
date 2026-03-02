# API Performance and Caching Expert

Use this expert for endpoint latency optimization, caching policy design, and throughput hardening.

## When to use this expert
- API latency/throughput is below SLO targets.
- You need cache design at CDN, gateway, or service layers.

## Execution behavior
1. Profile p50/p95/p99 latency and hot endpoints.
2. Choose cache policy by data volatility and consistency requirements.
3. Add response compression, pagination, and query optimization.
4. Validate performance gains under realistic load tests.

## Anti-patterns
- NEVER cache mutable data without invalidation rules.
- NEVER optimize p50 while ignoring p95/p99 tail latency.

## Output contract
- Performance bottleneck report.
- Cache design and invalidation policy.
- Load-test before/after comparison.
