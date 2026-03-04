# DevOps Release Strategies Expert

Use this expert for designing CI/CD pipelines, blue/green deployments, canary releases, and feature flag management.

## When to use this expert
- You need to reduce deployment risk by isolating traffic away from immediate releases.
- You are transitioning from monolith big-bang deployments to continuous integration pipelines.
- You want to automate semantic versioning, container tagging, and rollback mechanisms.
- You need to synchronize stateful schema migrations alongside stateless application updates.

## Execution behavior
1. Map out the full pipeline from commit -> testing -> build -> artifact publish -> deploy.
2. Choose a deployment strategy (Rolling, Blue/Green, Canary) matched to business downtime tolerance.
3. Enforce pre-deployment gates utilizing unit tests, strict linting, and security static analysis.
4. Separate the build phase (creating immutable container images) from the release/deploy phase.
5. Decouple stateless application releases from database schema migrations (forward-only expansion).
6. Implement synthetic monitoring health-checks to validate releases instantly upon routing traffic.
7. Formalize progressive exposure via feature flags to test logic in production safely.
8. Validate fully reproducible automated rollbacks via GitOps synchronization.

## Decision tree
- If releasing to a stateful legacy system with strict downtime locks, choose Big-Bang during maintenance windows.
- If near-zero downtime is required without complex traffic routing, choose Rolling Updates.
- If instant rollback and A/B verification are mandatory, choose Blue/Green deployments.
- If limiting blast-radius of bugs to 5% of users tracking specific metrics, choose Canary releases.
- If decoupling code launch from feature launch, choose Feature Flags.
- If adopting Kubernetes-native declarative deployments, choose GitOps (ArgoCD/Flux).

## Anti-patterns
- NEVER rebuild container images across environments (always promote the exact identical immutable artifact).
- NEVER tie database schema destructive changes (drops) directly to the deployment of continuous code.
- NEVER manually SSH into servers to `git pull` application code.
- NEVER run slow multi-hour integration tests purely on the critical path to hotfix production.
- NEVER merge unreviewed PRs directly to the main production branch.
- NEVER deploy code directly from a local laptop terminal.

## Common mistakes
- Ignoring database backward compatibility, causing instant crash loops on rolling microservices.
- Establishing overly tight readiness probes causing new pods to be killed before they spin up completely.
- Using `latest` image tags instead of strict semantic versioning or commit-hash tags.
- Building brittle deployment scripts that hardcode environment IP addresses.
- Applying feature flags but forgetting to clean them up, leading to massive technical debt logic trees.
- Having identical pipelines for Dev and Prod but different foundational base images.

## Output contract
- Comprehensive CI/CD workflow topology architecture.
- Git branching and semantic versioning strategy.
- Concrete deployment pipeline blueprint (Rolling, Blue/Green, Canary mechanics).
- Automated rollback configuration and fallback mechanisms.
- Stateful database forward/backward compatibility guidelines.
- Deployment health check and synthetic testing specifications.

## Composability hints
- Integrate heavily with `cloud.docker` for robust, minimal immutable artifact creation.
- Utilize `cloud.kubernetes` native traffic shaping for executing strict canary rollouts.
- Implement security gates directly in the CI process using `sec.appsec-testing`.
- Coordinate automated rollback mechanisms connected to limits in `devops.sli-slo-observability`.
