# Identity and Access Management Expert

Use this expert for Zero Trust architecture, RBAC/ABAC design, IAM policies, and secret management.

## When to use this expert
- You are strictly implementing the Principle of Least Privilege across diverse users and machines.
- You need to establish federated identity using OpenID Connect or SAML.
- You are designing scalable Role-Based or Attribute-Based Access Control logic for internal APIs.
- You must govern the rotation, auditing, and revocation of automated service accounts.

## Execution behavior
1. Centralize the identity provider (IdP) eliminating siloed local credential persistence.
2. Formulate explicit RBAC roles scoping actions natively across infrastructure and application resources.
3. Establish short-lived credential models (STS) instead of long-lived static API keys.
4. Isolate workload identity bounds strictly per service namespace.
5. Deploy a centralized secrets vault to intercept hardcoded application environments.
6. Force Multi-Factor Authentication (MFA) on all administrative continuous access workflows.
7. Enforce complete audit trailing attributing every configuration change to a verified identity.
8. Establish clear break-glass procedures bypassing traditional IAM in the event of an IdP outage.

## Decision tree
- If granting broad human access to multiple internal applications, choose Single Sign-On via federated SAML/OIDC.
- If a background service needs access to an S3 bucket, choose short-lived IAM roles and workload identity.
- If building extremely dynamic access rules (time-of-day, location restricted), choose ABAC over RBAC.
- If managing thousands of identical external customers, choose standardized generic multi-tenant auth layers.
- If legacy applications cannot support modern federated identity tokens, choose identity-aware proxies (IAP).
- If storing symmetric encryption keys for an application layer, choose dedicated HSMs or encrypted Vault engines.

## Anti-patterns
- NEVER store long-lived cloud provider root credentials digitally rather than offline cold storage.
- NEVER use shared generic administrative accounts (e.g., `admin`, `webmaster`) for multiple team members.
- NEVER embed API keys inside frontend Javascript applications distributed to global clients.
- NEVER bypass token validation signature checks trusting only the internal unencrypted payload.
- NEVER manage authorization logic sporadically scattered across distinct application controllers.
- NEVER ignore the offboarding procedural pipeline leaving stale accounts active post-termination.

## Common mistakes
- Using Wildcards `*` extensively in cloud IAM policies for convenience instead of targeted ARNs.
- Storing password hashes using weak MD5 algorithms lacking intensive multi-round salting structures.
- Forgetting to log authorization failures which masks dangerous brute-force probing mechanisms.
- Relying exclusively on perimeter firewalls instead of Zero Trust packet verification natively.
- Neglecting to routinely test the functionality of emergency "break-glass" administrative accounts.
- Distributing keys via emails and direct messages rather than automated provisioning pathways.

## Output contract
- Centralized IAM logical architecture and federated IdP mapping structure.
- Role/Attribute matrix defining strict least-privilege boundaries per system component.
- Workload identity integration and vault secret delivery pipelines.
- Standardized break-glass procedural documentation.
- Cloud IAM specific JSON/YAML constraint policies lacking `*` wildcards.
- Key rotation and lifecycle scheduling rules.

## Composability hints
- Integrate specific application boundary definitions using `sec.appsec-testing`.
- Attach strict IAM profiles to instances explicitly using modular `cloud.terraform` configurations.
- Design seamless container runtime secrets exposure collaborating with `cloud.kubernetes`.
- Route the authentication success/failure logging metrics into `devops.sli-slo-observability`.\n