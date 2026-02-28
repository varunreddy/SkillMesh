# OAuth2 Authentication Expert

Use this expert when tasks require implementing OAuth2 authentication flows, including authorization code grants, PKCE for public clients, token exchange, scope management, and integration with external identity providers such as Google, GitHub, and Microsoft.

## When to use this expert
- The task involves "Sign in with Google/GitHub/Microsoft" or any external identity provider integration.
- A public client (SPA or mobile app) needs secure token exchange without a client secret.
- The application must request granular permissions (scopes) from a third-party API on behalf of the user.
- Machine-to-machine authentication between backend services using client credentials is required.

## Execution behavior

1. Register the application with the identity provider to obtain a `client_id` and `client_secret` (for confidential clients). Configure the exact `redirect_uri` that the provider will call after authorization.
2. Determine the correct grant type: Authorization Code for server-side apps, Authorization Code + PKCE for SPAs and mobile apps, Client Credentials for service-to-service, and Device Code for input-constrained devices.
3. For Authorization Code flow: generate a cryptographically random `state` parameter (minimum 32 bytes, URL-safe base64), store it in the user's session, and include it in the authorization URL. On callback, verify the `state` matches before proceeding.
4. For PKCE: generate a `code_verifier` (43-128 character random string), compute `code_challenge` as the base64url-encoded SHA-256 hash of the verifier, and send the challenge with `code_challenge_method=S256` in the authorization request. Send the verifier in the token exchange request.
5. Exchange the authorization code for tokens by making a server-side `POST` to the provider's token endpoint with `grant_type=authorization_code`, the code, redirect URI, and client credentials (or PKCE verifier). Never exchange the code from the browser.
6. Validate the `id_token` (if OpenID Connect) by verifying the signature against the provider's JWKS endpoint, checking `iss`, `aud`, `exp`, and `nonce` claims. Extract user identity from the verified token, not from the `/userinfo` endpoint alone.
7. Map the external identity to a local user account: look up by provider + subject ID pair, create a new account if first login, and link accounts if the email matches an existing user (with appropriate verification).
8. Store the provider's access and refresh tokens encrypted in the database if the application needs ongoing API access (e.g., reading GitHub repos). Apply the principle of least privilege when requesting scopes.

## Decision tree
- If the client is a browser SPA with no backend -> use Authorization Code + PKCE with the token exchange proxied through a lightweight backend-for-frontend (BFF) endpoint.
- If the client is a server-rendered web app -> use Authorization Code with a client secret stored server-side; exchange the code on the backend.
- If the client is a mobile app -> use Authorization Code + PKCE with a custom URL scheme or App Links/Universal Links as the redirect URI.
- If the communication is service-to-service with no user involved -> use Client Credentials grant with scoped permissions.
- If the provider supports OpenID Connect -> use the `id_token` for identity; do not rely solely on the access token's `/userinfo` endpoint.
- If users may sign in with multiple providers -> implement account linking by matching verified email addresses, but always confirm with the user before merging accounts.

## Anti-patterns
- NEVER use the Implicit flow (`response_type=token`). It is deprecated in OAuth 2.1 because tokens are exposed in the URL fragment and browser history.
- NEVER omit PKCE for public clients (SPAs, mobile apps). Without PKCE, authorization codes can be intercepted and exchanged by malicious apps.
- NEVER store or transmit tokens in URL query parameters. Tokens in URLs are logged by proxies, browsers, and servers.
- NEVER skip validation of the `state` parameter on the callback. This is the primary defense against CSRF attacks in the OAuth flow.
- NEVER request more scopes than the application actually needs. Over-requesting erodes user trust and may trigger additional provider review requirements.
- NEVER trust the `email` claim from an `id_token` without checking the `email_verified` field. Unverified emails can be used for account takeover.

## Common mistakes
- Exchanging the authorization code from the frontend JavaScript instead of the backend, exposing the `client_secret` or allowing code interception.
- Reusing the `state` parameter across requests or using a predictable value (sequential counter, timestamp), defeating CSRF protection.
- Storing OAuth provider tokens in plaintext in the database instead of encrypting them at rest with a key managed outside the database.
- Not handling the case where a user revokes access at the provider side, causing stale refresh tokens to fail silently without prompting re-authorization.
- Assuming the `sub` claim is the same as the user's email or username. The `sub` is an opaque identifier unique to the provider and client combination.
- Failing to implement token refresh for long-lived integrations, forcing users to re-authorize when the access token expires.

## Output contract
- The implementation must use Authorization Code + PKCE for all public clients and Authorization Code with client secret for confidential clients.
- The `state` parameter must be cryptographically random, stored server-side, and validated on every callback.
- Token exchange must happen on the server, never in client-side code.
- The `id_token` must be validated by signature, issuer, audience, and expiry before trusting any claims.
- Provider tokens stored for ongoing API access must be encrypted at rest.
- Scope requests must follow the principle of least privilege, requesting only what the application actively uses.
- Account linking must verify email ownership before merging external identities with existing accounts.

## Composability hints
- Before this expert -> use the **REST API Design Expert** to define the callback endpoint structure and error response format.
- After this expert -> use the **Auth JWT Expert** to issue application-level JWTs after the OAuth exchange, enabling stateless authentication for subsequent requests.
- After this expert -> use the **FastAPI Expert** or **Flask Expert** to integrate the OAuth callback routes and session management into the web framework.
- Related -> the **SQLAlchemy Expert** for storing user-provider links, encrypted tokens, and account records.
- Related -> the **Auth JWT Expert** when the external provider's tokens are exchanged for locally issued JWTs.
