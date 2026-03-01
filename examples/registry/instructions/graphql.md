# GraphQL API Expert

Use this expert when tasks require designing or implementing GraphQL APIs, including schema design, resolver architecture, DataLoader batching to solve N+1 queries, federation for distributed graphs, and real-time subscriptions.

## When to use this expert
- The task involves designing a GraphQL schema with types, queries, mutations, and subscriptions.
- Resolver logic must be structured to avoid N+1 query problems using batching or DataLoader.
- A federated GraphQL architecture is needed to compose multiple subgraphs into a unified API.
- Real-time data delivery via GraphQL subscriptions over WebSockets is required.
- The team needs guidance on query complexity analysis, depth limiting, or persisted queries for security.

## Execution behavior

1. Define the schema using SDL (Schema Definition Language) with clearly named types, input types, and enums. Use `type Query` for reads, `type Mutation` for writes, and `type Subscription` for real-time streams. Prefer domain-specific type names (`Order`, `LineItem`) over generic ones (`Data`, `Result`).
2. Design resolver functions that map each field to a data-fetching operation. Keep resolvers thin: delegate business logic to service layers and data access to repository modules. Return only the fields the client requests.
3. Identify N+1 query patterns by examining resolvers that fetch related entities inside list resolvers. Introduce DataLoader instances (one per request context) to batch and deduplicate database calls for each entity type.
4. For large schemas spanning multiple teams, adopt Apollo Federation or a compatible gateway. Mark shared entity types with `@key` directives and implement `__resolveReference` in each subgraph to enable cross-service joins.
5. Implement subscriptions using WebSocket transport (e.g., `graphql-ws` protocol). Define a pub/sub backend (Redis, Kafka) for broadcasting events across server instances. Authenticate subscribers at connection init, not per message.
6. Add query protection layers: set a maximum query depth (e.g., 10), calculate query cost scores, and reject queries exceeding the cost budget. Consider persisted queries (allowlisting) in production to block arbitrary queries from untrusted clients.
7. Generate and maintain introspection documentation. Disable introspection in production environments to prevent schema enumeration by attackers.

## Decision tree
- If a field resolver triggers a database call for each item in a parent list -> wrap that data source in a DataLoader to batch all IDs into a single query per tick.
- If the schema is owned by a single team and is moderate in size -> use a monolithic GraphQL server; federation adds operational complexity that is not justified.
- If multiple teams own distinct domains that must appear in one graph -> adopt federation with a gateway that composes subgraph schemas at build time or runtime.
- If clients need live updates (chat messages, stock prices, notifications) -> use subscriptions over WebSockets with a shared pub/sub backend.
- If the API is public-facing -> enforce persisted queries, depth limits, and cost analysis; disable introspection to reduce attack surface.
- If clients routinely over-fetch or under-fetch with REST -> GraphQL's field selection naturally solves this; migrate incrementally starting with the highest-traffic endpoint.

## Anti-patterns
- NEVER place business logic directly inside resolvers. Resolvers should orchestrate calls to service or repository layers, not contain SQL, validation, or transformation code.
- NEVER allow unbounded query depth or complexity. A deeply nested query can trigger exponential resolver calls and exhaust server resources.
- NEVER create a new DataLoader instance per resolver call. DataLoaders must be scoped to the request context so batching and caching work correctly across the entire query.
- NEVER expose raw database errors in GraphQL error responses. Map internal errors to user-safe messages with structured `extensions` for debugging in non-production environments.
- NEVER use GraphQL subscriptions for high-throughput firehose data. Subscriptions are designed for targeted, low-to-moderate frequency events; use dedicated streaming for bulk data.
- NEVER rely solely on introspection for API documentation. Maintain human-readable descriptions in SDL and publish generated docs separately.

## Common mistakes
- Designing a schema that mirrors the database table structure instead of modeling the domain from the client's perspective, resulting in awkward queries and unnecessary joins.
- Forgetting to initialize DataLoader per-request, which causes stale cached results to leak between different users or requests.
- Returning nullable fields without documenting when and why they are null, forcing clients into defensive null-checking for every field.
- Using a single monolithic resolver that fetches all data upfront instead of leveraging GraphQL's lazy field resolution, wasting resources when clients select only a subset of fields.
- Implementing mutations that return only a success boolean instead of the modified object, forcing clients to make a follow-up query to get the updated state.
- Enabling introspection in production, allowing attackers to enumerate the full schema and craft targeted malicious queries.

## Output contract
- The schema must be defined in SDL with descriptions on all types, fields, and arguments.
- Every list field resolver must use DataLoader or an equivalent batching mechanism to prevent N+1 queries.
- Mutations must return the affected object (not just a boolean or ID) to enable cache updates on the client.
- Query depth and cost limits must be configured and documented.
- Subscription events must be authenticated at connection init and scoped to authorized data.
- Error responses must follow a consistent structure with `message`, `path`, and optional `extensions` fields.

## Composability hints
- Before this expert -> use the **FastAPI Expert** or **Flask Expert** to set up the Python web server that hosts the GraphQL endpoint (e.g., via Strawberry, Ariadne, or Graphene).
- Before this expert -> use the **REST API Design Expert** when deciding whether REST or GraphQL better fits the use case.
- After this expert -> use the **Rate Limiting Expert** to protect the GraphQL endpoint from abusive queries based on cost or request count.
- After this expert -> use the **API Authentication Patterns Expert** to implement API key or service-to-service authentication for the GraphQL layer.
- Related -> the **API Gateway Expert** for routing and load balancing traffic to federated subgraph services.
