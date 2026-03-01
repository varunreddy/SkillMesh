# API Authentication Patterns Expert

Use this expert when tasks require designing or implementing API authentication mechanisms beyond standard user-facing OAuth and JWT flows, including API key management, mutual TLS, HMAC request signing, webhook signature verification, and service-to-service authentication in distributed systems.

## When to use this expert
- The task involves issuing, rotating, and revoking API keys for third-party integrations or programmatic access.
- Mutual TLS (mTLS) must be configured for zero-trust service-to-service communication.
- Requests must be signed with HMAC to guarantee integrity and authenticity without transmitting secrets.
- Incoming webhook payloads must be verified against provider signatures to prevent forgery.
- A service-to-service authentication strategy must be chosen for an internal microservice architecture.

## Execution behavior

1. Identify the authentication boundary: determine whether the consumer is an external third-party developer (API keys, HMAC), an internal service (mTLS, signed JWTs), or a webhook sender (signature verification). Each boundary requires a different pattern and trust model.
2. For API key authentication: generate cryptographically random keys (minimum 32 bytes, base64- or hex-encoded). Store only a hashed version (SHA-256) of the key in the database. Transmit keys via the `Authorization: Bearer <key>` header or a custom `X-API-Key` header, never in URL query parameters.
3. For HMAC request signing: define a canonical request format (method, path, sorted query parameters, body hash, timestamp). Compute `HMAC-SHA256(secret, canonical_request)` and transmit the signature in an `Authorization` header with scheme identifier. The server recomputes and compares using constant-time comparison.
4. For mutual TLS: provision client certificates signed by an internal CA. Configure the server to require and verify client certificates against the CA trust chain. Extract the client identity from the certificate's Common Name or Subject Alternative Name for authorization decisions.
5. For webhook verification: validate the provider's signature header (e.g., `X-Hub-Signature-256`) by computing `HMAC-SHA256(webhook_secret, raw_body)` and comparing with constant-time equality. Reject requests with missing, expired, or invalid signatures. Check the timestamp header to prevent replay attacks outside a tolerance window (e.g., 5 minutes).
6. Implement key lifecycle management: support key creation with scoped permissions, key listing (showing only a prefix for identification), key rotation with a grace period where both old and new keys are valid, and key revocation with immediate effect. Log all lifecycle events for audit.
7. For service-to-service auth in microservices: use short-lived signed JWTs issued by an internal identity provider (e.g., SPIFFE/SPIRE) or mTLS with auto-rotated certificates. Avoid long-lived shared secrets between services. Validate tokens at each service boundary, not just at the edge.

## Decision tree
- If the consumer is an external developer integrating via a public API -> issue API keys with scoped permissions, rate limit per key, and provide a self-service rotation mechanism.
- If request integrity and non-repudiation are required (e.g., financial transactions) -> use HMAC request signing so that both parties can verify the payload was not tampered with in transit.
- If zero-trust networking is mandated and both parties are services you control -> use mTLS with certificates issued by an internal CA and rotated automatically.
- If the system receives webhooks from a third-party provider -> implement signature verification using the provider's documented algorithm and reject unsigned or expired payloads.
- If microservices communicate over an internal network -> prefer short-lived JWT tokens from an identity provider (SPIFFE) or mTLS over static shared secrets.
- If the team cannot manage a PKI infrastructure for mTLS -> use signed JWTs with asymmetric keys (RS256, ES256) where the issuer holds the private key and verifiers use the public key.

## Anti-patterns
- NEVER store API keys in plaintext in the database. Store a SHA-256 hash and compare hashes on lookup. Plaintext storage means a database breach exposes every active key.
- NEVER transmit API keys or secrets in URL query parameters. URLs are logged by proxies, browsers, CDNs, and web servers; secrets in URLs are effectively public.
- NEVER use string equality (`==`) to compare signatures or hashes. Use constant-time comparison (`hmac.compare_digest` in Python, `crypto.timingSafeEqual` in Node.js) to prevent timing side-channel attacks.
- NEVER accept webhook payloads without verifying the signature. Unverified webhooks allow attackers to forge events and trigger unauthorized actions in your system.
- NEVER use long-lived shared secrets between microservices without a rotation mechanism. Secrets that never rotate accumulate exposure risk and cannot be revoked gracefully.
- NEVER skip certificate revocation checks in mTLS deployments. A compromised client certificate must be revocable via CRL or OCSP to prevent unauthorized access.

## Common mistakes
- Issuing API keys without scoped permissions, giving every key full administrative access when most integrations only need read access to specific resources.
- Implementing HMAC signing without including a timestamp in the canonical request, leaving the signature valid indefinitely and vulnerable to replay attacks.
- Verifying webhook signatures against a parsed/modified body instead of the raw request body, causing signature mismatches because JSON parsing and re-serialization can alter whitespace or key order.
- Configuring mTLS but not extracting and checking the client identity from the certificate, authenticating that the client has a valid cert but not authorizing what it may access.
- Logging full API keys or secrets in application logs during debugging, creating a persistent credential leak in log storage systems.
- Implementing key rotation as an instantaneous swap with no grace period, breaking active integrations that are still using the previous key.

## Output contract
- API keys must be generated with at least 32 bytes of cryptographic randomness and stored as SHA-256 hashes.
- HMAC signatures must use SHA-256 or stronger, include a timestamp for replay protection, and be verified with constant-time comparison.
- mTLS configurations must specify the CA trust chain, client certificate requirements, and identity extraction rules.
- Webhook verification must validate the signature against the raw request body and reject payloads outside the timestamp tolerance window.
- Key lifecycle operations (create, rotate, revoke, list) must be implemented with audit logging.
- All secrets (API keys, HMAC secrets, webhook secrets) must be stored in a secrets manager, not in source code or environment files.

## Composability hints
- Before this expert -> use the **Auth JWT Expert** or **Auth OAuth Expert** when the authentication need is user-facing session or delegation-based rather than machine-to-machine.
- Before this expert -> use the **Secrets Management Expert** to establish secure storage and retrieval for API keys, HMAC secrets, and webhook signing keys.
- After this expert -> use the **API Gateway Expert** to enforce API key validation and mTLS termination at the gateway layer before requests reach backend services.
- Related -> the **REST API Design Expert** for documenting authentication requirements in the OpenAPI specification.
- Related -> the **Rate Limiting Expert** for tying rate limit enforcement to authenticated API key identities.
