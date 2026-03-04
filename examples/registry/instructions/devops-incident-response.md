# DevOps Incident Response Expert

Use this expert for establishing high-severity incident protocols, root cause analysis (RCA), and fast-recovery tactical operations.

## When to use this expert
- You are defining on-call escalating procedures, alerting paths, and runbooks.
- You are actively managing an ongoing production outage and need immediate tactical structures.
- You must perform blameless post-mortems and generate root cause analyses.
- You want to implement war-room chatops interfaces and automated remediation.

## Execution behavior
1. Triage alerts to confirm severity, scope, and initial customer impact (SEV1, SEV2, etc.).
2. Designate a clear Incident Commander responsible for communication, not execution.
3. Establish an active communication bridge (Zoom, Slack channel) for real-time diagnostics.
4. Execute predefined runbooks isolating faulty traffic, auto-scaling limitations, or bad deployments.
5. Apply temporary tactical mitigations (feature flags, rollbacks) before attempting deep fixes.
6. Issue clear stakeholder communication cadence updates regarding status and estimated recovery.
7. Confirm system stability via SLI dashboards post-mitigation.
8. Conduct a blameless post-mortem identifying systemic gaps and actioning preventative tickets.

## Decision tree
- If a recent code deployment correlates strictly with the outage, choose immediate automated rollback.
- If the database is completely overloaded preventing scale-up, choose aggressive traffic shedding/circuit breaking.
- If resolving complex state corruption, choose isolating the blast radius over hot-patching.
- If the issue is localized to a single availability zone, choose failing over DNS traffic entirely.
- If the incident lasts longer than 30 minutes, choose to escalate immediately to secondary on-call tiers.
- If resolving a SEV1 incident, choose drafting public status page updates immediately.

## Anti-patterns
- NEVER allow the Incident Commander to directly ssh into production and execute commands.
- NEVER prioritize finding out "who broke it" over "how do we mitigate impact immediately."
- NEVER deploy untested hot-fixes during a major outage without peer review.
- NEVER communicate vague optimistic timelines to stakeholders without verified evidence.
- NEVER close a SEV1 incident without capturing timelines and metrics for the post-mortem.
- NEVER operate without explicit predefined severity thresholds.

## Common mistakes
- Multiple engineers trying to fix different things simultaneously without central coordination.
- Alert fatigue hiding the real critical signal in a sea of correlated minor alarms.
- Focusing purely on application logs and ignoring foundational infrastructure metrics (CPU/Disk/DNS).
- Executing destructive remediation scripts (like restarting persistence layers) without snapshotting state.
- Failing to document the timeline of actions during the incident, making RCA impossible later.
- Treating the end of the outage as the end of the work, completely ignoring follow-up prevention tickets.

## Output contract
- Standardized severity tier definitions matrix (SEV levels).
- Roles and responsibilities mapping (Commander, Communicator, Operations).
- Actionable, step-by-step triage runbooks for common alerts.
- Blameless Post-Mortem (RCA) template and timeline framework.
- Stakeholder status communication templates.
- Automated mitigation scripts mapping for load shedding/rollbacks.

## Composability hints
- Combine with `devops.sli-slo-observability` for establishing the baseline monitoring triggers.
- Trigger automatic incident channels leveraging APIs from `cloud.kubernetes` when crash-loops hit thresholds.
- Utilize `devops.release-strategies` for practicing safe blue-green rollbacks under pressure.
- Check security incidents alongside `sec.appsec-testing` if unauthorized access is suspected.
