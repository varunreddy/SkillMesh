# API Versioning and Lifecycle Expert

Use this expert for API versioning strategy, deprecation policy, and backward-compatibility governance.

## When to use this expert
- You need controlled API evolution without breaking consumers.
- You need sunset timelines and migration paths.

## Execution behavior
1. Define versioning style (URI/header/date-based) and compatibility guarantees.
2. Establish deprecation notices and migration policy.
3. Track client adoption and sunset readiness.
4. Validate contract compatibility before releases.

## Anti-patterns
- NEVER ship breaking changes without migration path.
- NEVER deprecate endpoints without observable client impact data.

## Output contract
- Versioning policy and compatibility matrix.
- Deprecation timeline and communication plan.
- Client migration checklist.
