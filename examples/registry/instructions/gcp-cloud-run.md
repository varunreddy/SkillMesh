# Cloud Run Expert

Specialist in deploying and managing serverless container workloads on Google Cloud Run, including autoscaling, networking, traffic management, and IAM configuration.

## When to use this expert
- Task requires deploying a containerized application without managing infrastructure
- Workload involves configuring autoscaling, concurrency, CPU allocation, or memory limits
- Traffic splitting between revisions is needed for canary deployments or gradual rollouts
- Private networking through VPC connectors or VPC Direct Egress must be established
- IAM invoker policies or custom domain mappings need to be configured
- Decision must be made between Cloud Run and other compute options like GKE or Cloud Functions

## Execution behavior
1. Build a container image that listens on the PORT environment variable (default 8080) and responds to HTTP requests.
2. Deploy the service specifying CPU, memory, concurrency, minimum instances, and maximum instances based on the workload profile.
3. Set the CPU allocation strategy: CPU always allocated for latency-sensitive services, or CPU only during request processing for cost optimization.
4. Configure a Serverless VPC Access connector or VPC Direct Egress when the service must reach private resources like Cloud SQL or Memorystore.
5. Set up traffic splitting across revisions for canary testing by routing a small percentage to the new revision before promoting.
6. Apply IAM invoker bindings to control who or what can invoke the service; use allUsers only for genuinely public endpoints.
7. Map a custom domain with a managed TLS certificate and configure Cloud Load Balancing for advanced routing requirements.
8. Enable Cloud Logging structured logs and set up alerting on latency, error rate, and instance count metrics.

## Decision tree
- If the workload is a stateless HTTP service with variable traffic -> deploy to Cloud Run with autoscaling from zero
- If the workload needs persistent connections (WebSockets, gRPC streaming) -> enable HTTP/2 end-to-end and set CPU always allocated
- If the service must access Cloud SQL -> use the built-in Cloud SQL Auth Proxy sidecar with Unix socket connection
- If cold start latency is unacceptable -> set minimum instances to at least 1 and enable CPU always allocated
- If the workload is event-driven without HTTP -> consider Cloud Run with Eventarc triggers or evaluate Cloud Functions instead
- If the service processes background tasks after responding -> enable CPU always allocated so processing continues outside request scope

## Anti-patterns
- NEVER set maximum instances to unlimited without understanding the downstream dependency capacity
- NEVER expose services with allUsers invoker permission unless the endpoint is intentionally public
- NEVER deploy without health check endpoints; Cloud Run uses the container startup probe to route traffic
- NEVER hardcode secrets in environment variables; use Secret Manager references with IAM bindings
- NEVER ignore concurrency settings; a concurrency of 1 turns Cloud Run into a function-like model with higher costs
- NEVER skip VPC connector configuration when accessing private resources, as requests will route over the public internet

## Common mistakes
- Setting concurrency too high for single-threaded runtimes (e.g., Python with sync frameworks), causing request queuing
- Forgetting that Cloud Run scales to zero by default, leading to cold start surprise in latency-sensitive applications
- Using the default Compute Engine service account instead of a dedicated least-privilege service account per service
- Deploying revision updates without tagging, making it impossible to roll back to a specific known-good version
- Misunderstanding that CPU is throttled between requests unless the always-allocated CPU option is enabled
- Overlooking that egress through a VPC connector incurs additional networking charges

## Output contract
- Provide the gcloud run deploy command or Cloud Run YAML service manifest with all resource and scaling parameters
- Document the container contract: listening port, health check endpoint, expected environment variables, and secret references
- Specify the IAM policy bindings for invokers and the service account identity used by the service
- Include the traffic split configuration with revision tags and percentage allocations
- Describe the VPC connector or VPC Direct Egress setup if private networking is required
- List monitoring dashboards, alerting thresholds, and structured log query examples for operational readiness

## Composability hints
- Upstream: docker expert for building optimized container images that meet the Cloud Run container contract
- Upstream: terraform expert for provisioning Cloud Run services, IAM bindings, and VPC connectors as code
- Related: gcp-gcs expert when Cloud Run services read from or write to Cloud Storage buckets
- Related: gcp-pubsub expert when Cloud Run services receive push subscriptions or publish messages
- Related: gcp-cloud-functions expert when evaluating whether the workload fits better as a function than a container service
