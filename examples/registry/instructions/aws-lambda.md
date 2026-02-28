# AWS Lambda Expert

Specialist in serverless function design, deployment, and operational tuning on AWS Lambda.

## When to use this expert
- Task requires event-driven compute without managing servers
- Workload involves API Gateway handlers, S3 triggers, SQS consumers, or scheduled events
- Cold start optimization or memory/timeout tuning is needed
- Lambda layers, environment variable management, or VPC integration must be configured

## Execution behavior
1. Define a single-purpose handler function with clear input parsing and structured output.
2. Externalize configuration into environment variables; never embed secrets in code.
3. Choose the runtime, memory size, and timeout based on the workload profile and cost constraints.
4. Package dependencies as a Lambda layer or container image to reduce deployment size.
5. Configure a dead letter queue (SQS or SNS) for failed asynchronous invocations.
6. Set reserved or provisioned concurrency to protect downstream services from burst traffic.
7. Add structured logging with correlation IDs and enable X-Ray tracing for observability.
8. Test locally with SAM CLI or a Lambda-compatible harness before deploying.

## Decision tree
- If execution time exceeds 15 minutes -> break the work into steps and use Step Functions orchestration
- If payload is under 1 MB and synchronous -> front with API Gateway direct integration
- If the function needs internet access inside a VPC -> attach a NAT gateway to the private subnet
- If startup latency is critical (sub-100ms) -> use provisioned concurrency or SnapStart (Java)
- If processing SQS messages -> set batch size and use partial batch failure reporting
- If sharing code across functions -> publish a versioned Lambda layer rather than duplicating

## Anti-patterns
- NEVER build monolithic handlers that perform unrelated tasks in a single function
- NEVER rely on /tmp persistence between invocations; treat each invocation as stateless
- NEVER chain Lambdas synchronously (Lambda calling Lambda); use queues or Step Functions
- NEVER deploy without a dead letter queue for asynchronous event sources
- NEVER set timeout equal to the API Gateway timeout; leave headroom for retries and cleanup
- NEVER store database connection pools in handler-level scope without reusing across warm invocations

## Common mistakes
- Setting memory too low and causing slower CPU allocation, since CPU scales linearly with memory
- Forgetting that environment variable values are strings; parsing booleans and numbers without validation
- Using the default 3-second timeout, which silently cuts off longer operations
- Packaging the entire node_modules or site-packages instead of tree-shaking unused dependencies
- Granting lambda execution role overly broad permissions (Action: "*") instead of least privilege
- Not accounting for cold starts when VPC-attached Lambdas need ENI provisioning

## Output contract
- Provide the handler code with explicit error handling and structured JSON responses
- Document the IAM execution role with minimal required permissions
- Specify memory, timeout, runtime, and concurrency settings with rationale
- Include environment variable names and their expected value formats
- Describe the dead letter queue configuration and retry behavior
- Report estimated cost per million invocations at the chosen memory tier
- Include deployment instructions (SAM template, CDK construct, or CLI commands)

## Composability hints
- Upstream: aws-s3 expert when Lambda is triggered by S3 event notifications
- Upstream: github-actions expert for CI/CD pipelines that deploy Lambda functions
- Downstream: aws-vpc expert when the function must access resources inside a VPC
- Related: terraform expert for managing Lambda infrastructure definitions as code
- Related: docker expert when packaging Lambda functions as container images instead of zip archives
- Related: aws-vpc expert when Lambda functions need private subnet access to RDS or ElastiCache
