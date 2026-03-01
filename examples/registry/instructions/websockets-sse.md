# WebSockets and Server-Sent Events Expert

Use this expert when tasks require implementing real-time communication between clients and servers, including WebSocket connection lifecycle management, Server-Sent Events for unidirectional streaming, reconnection strategies, heartbeat mechanisms, and scaling real-time connections across multiple server instances.

## When to use this expert
- The task involves establishing persistent bidirectional communication between a client and server using WebSockets.
- Server-Sent Events (SSE) are needed for efficient server-to-client push without the complexity of WebSockets.
- Reconnection logic with backoff strategies must be implemented to handle network interruptions gracefully.
- Heartbeat or ping/pong mechanisms are required to detect dead connections and free server resources.
- Real-time connections must be scaled horizontally across multiple server instances using a shared pub/sub backend.

## Execution behavior

1. Choose the transport based on communication direction: use **WebSockets** when bidirectional messaging is required (chat, collaborative editing, gaming). Use **Server-Sent Events** when only server-to-client push is needed (live dashboards, notifications, activity feeds). SSE is simpler, works over standard HTTP, and reconnects automatically in browsers.
2. Implement the WebSocket connection lifecycle: handle the upgrade handshake, authenticate during the upgrade (via query parameter token or first message), confirm the connection with an acknowledgment frame, process messages in a receive loop, and handle both graceful close (close frame exchange) and abnormal disconnection (network drop).
3. For SSE, configure the endpoint to return `Content-Type: text/event-stream` with `Cache-Control: no-cache` and `Connection: keep-alive`. Structure events with `event:`, `data:`, `id:`, and `retry:` fields. Set the `id` field on every event so the browser sends `Last-Event-ID` on reconnection, enabling the server to replay missed events.
4. Implement heartbeat mechanisms: for WebSockets, send ping frames at a regular interval (e.g., every 30 seconds) and expect pong responses within a timeout (e.g., 10 seconds). For SSE, send comment lines (`: heartbeat`) at regular intervals to keep the connection alive through proxies and load balancers that may close idle connections.
5. Design reconnection logic on the client: use exponential backoff starting at 1 second, doubling up to a cap (e.g., 30 seconds), with random jitter to prevent thundering herd when many clients reconnect simultaneously after a server restart. Track the last received event ID or sequence number to request missed events on reconnection.
6. Scale across multiple server instances by introducing a pub/sub backend (Redis Pub/Sub, Redis Streams, Kafka, or NATS). When a server needs to broadcast to a connected client, publish the event to the shared bus. Each server instance subscribes and delivers events to its locally connected clients. Map client-to-server affinity using connection metadata, not sticky sessions.
7. Implement graceful shutdown: on server termination, send a close frame (WebSocket) or a final event with a reconnect directive (SSE) before closing connections. Drain in-flight messages and give clients time to reconnect to another instance.

## Decision tree
- If the client only needs to receive updates from the server -> use SSE for simplicity, automatic browser reconnection, and HTTP/2 multiplexing support.
- If the client must send frequent messages to the server (chat, keystrokes, game state) -> use WebSockets for bidirectional, low-latency communication.
- If the deployment sits behind a reverse proxy or CDN that buffers responses -> ensure SSE responses are flushed immediately and not buffered; add `X-Accel-Buffering: no` for Nginx.
- If the system must guarantee no events are lost during client disconnections -> implement event ID tracking and a replay mechanism from a durable store (Redis Streams, database) on reconnection.
- If the server runs a single instance -> in-memory connection registries and broadcast loops are sufficient; no external pub/sub is needed.
- If the server runs multiple instances behind a load balancer -> introduce a pub/sub backend and ensure each instance subscribes to relevant channels for its connected clients.

## Anti-patterns
- NEVER authenticate WebSocket connections solely based on cookies without validating a token during the upgrade or in the first message. Cookie-based auth on WebSockets is vulnerable to cross-site WebSocket hijacking (CSWSH).
- NEVER keep connections open without heartbeats. Dead connections consume server resources (memory, file descriptors) and may not be detected until the OS TCP keepalive timeout fires, which can take minutes to hours.
- NEVER reconnect immediately without backoff after a disconnection. Instant reconnection from thousands of clients simultaneously creates a thundering herd that can overwhelm the server during recovery.
- NEVER use WebSockets for simple request-response patterns. If the client sends a request and waits for one response, standard HTTP is more efficient and better supported by infrastructure.
- NEVER buffer unbounded messages in memory on the server. If a client is slow to consume, apply backpressure by dropping old messages, pausing the producer, or disconnecting the slow consumer.
- NEVER send large binary blobs over WebSockets without chunking. Large frames block the connection and can cause out-of-memory errors on both sides.

## Common mistakes
- Forgetting to handle the SSE `Last-Event-ID` header on reconnection, causing clients to miss all events that occurred during the disconnection period.
- Not configuring reverse proxy timeouts (Nginx `proxy_read_timeout`, HAProxy `timeout tunnel`) for long-lived connections, causing proxies to close healthy WebSocket or SSE connections after the default 60-second idle timeout.
- Using sticky sessions instead of pub/sub for multi-instance scaling, creating uneven load distribution and single points of failure when one instance goes down.
- Sending JSON strings over WebSockets without defining a message envelope (type, payload, sequence number), making it impossible to distinguish message types or implement selective processing.
- Neglecting to close server-side connection resources (database cursors, subscriptions) when a WebSocket or SSE client disconnects, causing resource leaks under connection churn.
- Implementing SSE with `text/plain` content type instead of `text/event-stream`, which causes browsers to treat the response as a download rather than an event stream.

## Output contract
- WebSocket endpoints must handle the full lifecycle: upgrade, authentication, message processing, ping/pong heartbeats, graceful close, and abnormal disconnection cleanup.
- SSE endpoints must set `Content-Type: text/event-stream`, include `id` fields for resumability, and send periodic heartbeat comments.
- Client reconnection must use exponential backoff with jitter and resume from the last received event ID.
- Multi-instance deployments must use a shared pub/sub backend for cross-instance event delivery.
- All connections must have heartbeat or keepalive mechanisms with documented intervals and timeouts.
- Graceful shutdown must drain connections and give clients an opportunity to reconnect to healthy instances.

## Composability hints
- Before this expert -> use the **FastAPI Expert** for implementing WebSocket routes and SSE endpoints using `StreamingResponse` in an async Python framework.
- Before this expert -> use the **Flask Expert** for implementing SSE with Flask's streaming response or WebSocket support via Flask-SocketIO.
- After this expert -> use the **Nginx Expert** to configure reverse proxy settings (timeouts, buffering, upgrade headers) for long-lived WebSocket and SSE connections.
- After this expert -> use the **API Gateway Expert** for routing WebSocket and SSE traffic through the gateway with appropriate timeout and connection-upgrade configuration.
- Related -> the **Rate Limiting Expert** for throttling WebSocket connection attempts and message rates to prevent resource exhaustion.
