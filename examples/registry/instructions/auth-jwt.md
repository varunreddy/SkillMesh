# JWT Authentication Expert

Use this expert when tasks require implementing JSON Web Token authentication, including token issuance, validation, refresh token flows, role-based access control via claims, token revocation strategies, and secure token storage.

## When to use this expert
- The task involves issuing and validating JWTs for stateless authentication in web or mobile applications.
- A refresh token rotation strategy is needed to balance security with user experience.
- Role-based or permission-based access control must be encoded in token claims.
- The architecture spans multiple services that need to independently verify identity without shared session state.

## Execution behavior

1. Choose a signing algorithm based on the deployment model: use `RS256` (asymmetric) when multiple services verify tokens independently, or `HS256` (symmetric) only for single-service applications where the secret never leaves one process.
2. Define a minimal access token payload: `sub` (user ID), `exp` (short-lived, 15-30 minutes), `iat`, `iss`, and a `roles` or `permissions` array for RBAC. Never store sensitive data (email, PII) in the payload.
3. Implement a refresh token as an opaque, high-entropy random string stored server-side (database or Redis) with a longer expiry (7-30 days). The refresh token is NOT a JWT.
4. On login, issue both an access token and a refresh token. Return the access token in the response body and the refresh token as an `httpOnly`, `Secure`, `SameSite=Strict` cookie (for SPAs) or in the response body (for mobile clients using secure storage).
5. On token refresh, validate the refresh token against the server-side store, issue a new access token AND a new refresh token (rotation), and invalidate the old refresh token immediately to detect reuse.
6. Implement middleware or a dependency that extracts the access token from the `Authorization: Bearer <token>` header, verifies the signature and expiry, and attaches the decoded claims to the request context.
7. For RBAC, create a permission-checking layer that reads the `roles` or `permissions` claim and compares it against the required permissions for the endpoint. Return `403 Forbidden` for insufficient permissions, `401 Unauthorized` for missing or invalid tokens.
8. Log all authentication events (login, refresh, revocation, failed verification) with timestamps and client metadata for audit purposes.

## Decision tree
- If the client is a browser SPA -> store access token in memory (JavaScript variable) and refresh token in an `httpOnly` cookie; never use `localStorage` for tokens.
- If the client is a mobile app -> store both tokens in the platform's secure storage (Keychain on iOS, EncryptedSharedPreferences on Android) and use refresh token rotation.
- If multiple services need to verify tokens independently -> use asymmetric signing (`RS256`); distribute the public key via a JWKS endpoint.
- If token revocation before expiry is required -> implement a token blacklist (Redis set of revoked `jti` values) checked on every request, or use very short-lived access tokens (5 min) with aggressive refresh.
- If the system requires fine-grained permissions -> encode a `permissions` array in the token rather than broad `roles`; keep the token payload under 1 KB.
- If tokens must work across domains -> ensure the `iss` and `aud` claims are validated to prevent token misuse across services.

## Anti-patterns
- NEVER store JWTs in `localStorage` or `sessionStorage`. These are accessible to any JavaScript on the page, making XSS attacks equivalent to full account compromise.
- NEVER issue tokens without an `exp` claim. Tokens without expiry are permanent credentials that cannot be safely rotated.
- NEVER use symmetric signing (`HS256`) in a multi-service architecture where the secret must be shared across services. A single compromised service can forge tokens for all others.
- NEVER embed secrets, API keys, or database credentials in token payloads. JWTs are base64-encoded, not encrypted; anyone can read the payload.
- NEVER skip refresh token rotation. Reusing the same refresh token indefinitely means a stolen refresh token grants permanent access.
- NEVER validate only the signature without checking `exp`, `iss`, and `aud` claims. A valid signature alone does not mean the token is current or intended for your service.

## Common mistakes
- Setting access token expiry too long (hours or days), which increases the window of exploitation if a token is leaked. Keep access tokens to 15-30 minutes.
- Implementing refresh tokens as JWTs instead of opaque server-side tokens, making them impossible to revoke without a blacklist.
- Returning `401` for both "no token provided" and "insufficient permissions" instead of distinguishing between `401 Unauthorized` and `403 Forbidden`.
- Not handling clock skew between servers, causing valid tokens to be rejected. Add a small `leeway` (30-60 seconds) to expiry validation.
- Forgetting to invalidate all refresh tokens when a user changes their password or is deactivated, leaving old sessions alive.
- Putting user profile data (name, email, avatar URL) in the access token, bloating every request header and leaking PII if the token is logged.

## Output contract
- Access tokens must be short-lived (15-30 minutes) JWTs with `sub`, `exp`, `iat`, `iss`, and role/permission claims.
- Refresh tokens must be opaque, stored server-side, and rotated on every use.
- Token verification must check signature, expiry, issuer, and audience at minimum.
- RBAC enforcement must be a reusable middleware or dependency, not inline logic in each endpoint.
- All auth events (login, refresh, logout, failure) must be logged with relevant metadata.
- The implementation must include a logout endpoint that revokes the refresh token.
- Error responses must distinguish between `401` (authentication failure) and `403` (authorization failure).

## Composability hints
- Before this expert -> use the **REST API Design Expert** to define which endpoints require authentication and what permission levels are needed.
- After this expert -> use the **FastAPI Expert** or **Flask Expert** to integrate the JWT middleware into the web framework.
- Related -> the **Auth OAuth Expert** when the JWT is issued after an OAuth2 authorization code exchange with an external provider.
- Related -> the **SQLAlchemy Expert** for storing user accounts, refresh tokens, and revocation records in the database.
