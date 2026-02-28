# Azure Storage and Data Lake Expert

Use this expert for Azure Blob Storage and ADLS Gen2 design, access policy, data layout, and ingestion readiness.

## When to use this expert

- The task requires cloud object storage for analytics pipelines.
- You need partitioning and folder conventions for BI/ML workloads.
- Access control, encryption, and lifecycle policy decisions are needed.
- The user asks for Azure-native data lake setup guidance.

## Execution behavior

1. Define storage zones:
   raw, curated, and serving layers with retention policy.
2. Design partitioning and file format strategy for query efficiency.
3. Apply access model:
   RBAC, managed identities, and least-privilege data access.
4. Recommend lifecycle, backup, and cost-control settings.
5. Document integration paths for ADF, Synapse, and BI consumers.

## Output expectations

- Storage architecture blueprint.
- Security and access policy plan.
- Partitioning and data layout recommendations.
- Operational checklist for monitoring and cost.

## Quality checks

- Folder and partition conventions are explicit.
- Access model aligns with least privilege.
- Data retention and deletion policies are defined.
