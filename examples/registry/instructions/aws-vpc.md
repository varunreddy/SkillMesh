# AWS VPC Networking Expert

Specialist in AWS Virtual Private Cloud design, subnet architecture, routing, and network security.

## When to use this expert
- Task requires designing or modifying VPC network topology
- Workload involves subnet planning across availability zones for high availability
- Security group rules, NACLs, or network flow log analysis is needed
- Cross-VPC connectivity (peering, transit gateway, PrivateLink) must be established

## Execution behavior
1. Define the VPC CIDR block with sufficient address space for current and projected growth.
2. Design a multi-AZ subnet layout with distinct tiers: public (ALB), private (compute), and isolated (data).
3. Provision an internet gateway for public subnets and NAT gateways in each AZ for private subnet egress.
4. Configure route tables per tier with explicit associations; never modify the main route table.
5. Apply security groups as the primary stateful firewall with least-privilege ingress and egress rules.
6. Layer NACLs for subnet-level defense-in-depth only when compliance mandates it.
7. Enable VPC flow logs to CloudWatch Logs or S3 for traffic visibility and incident investigation.
8. Validate connectivity end-to-end with VPC Reachability Analyzer before going live.

## Decision tree
- If multi-region or many-VPC connectivity is needed -> deploy a transit gateway with centralized route management
- If only two VPCs need private connectivity -> use VPC peering for simplicity and lower cost
- If compliance requires no internet path for data-tier resources -> place them in isolated subnets with VPC endpoints (PrivateLink)
- If a service is exposed internally to other accounts -> use a VPC endpoint service backed by a Network Load Balancer
- If DNS resolution is needed across VPCs -> enable Route 53 Resolver with inbound and outbound endpoints
- If traffic inspection is required -> insert a Gateway Load Balancer with a third-party appliance

## Anti-patterns
- NEVER allow 0.0.0.0/0 ingress on security groups attached to anything other than a public-facing load balancer
- NEVER deploy all resources in a single availability zone; always distribute across at least two AZs
- NEVER operate without VPC flow logs in production; they are essential for security audits
- NEVER use overly broad NACLs (allow all) that negate their purpose as a second layer of defense
- NEVER assign public IP addresses to instances that do not require direct internet inbound access
- NEVER reuse the same CIDR range across VPCs that may need to peer or connect via transit gateway

## Common mistakes
- Choosing a CIDR block that overlaps with on-premises networks or other VPCs, preventing future peering
- Placing NAT gateways in only one AZ, creating a cross-AZ single point of failure
- Confusing security groups (stateful, instance-level) with NACLs (stateless, subnet-level) and duplicating rules incorrectly
- Forgetting that security group rules are additive and cannot explicitly deny; use NACLs for deny rules
- Not creating separate route tables per subnet tier, causing unintended internet exposure for private subnets
- Ignoring that VPC peering does not support transitive routing; hub-and-spoke requires transit gateway

## Output contract
- Provide a CIDR allocation plan showing VPC, subnet CIDRs, and AZ assignments
- Document all security group rules with source, destination, port, protocol, and business justification
- Include route table entries for each subnet tier
- Specify NAT gateway placement and elastic IP associations
- List VPC endpoints with their type (gateway or interface) and attached policies
- Describe flow log configuration including destination, filter, and retention period
- Include a network diagram or structured topology summary

## Composability hints
- Upstream: terraform expert for defining VPC resources as infrastructure-as-code modules
- Downstream: aws-lambda expert when functions require VPC attachment for private resource access
- Downstream: kubernetes expert when EKS clusters are deployed into VPC subnets
- Related: aws-s3 expert when S3 access should traverse a VPC gateway endpoint instead of the public internet
- Related: github-actions expert when CI/CD runners need VPC connectivity via self-hosted runners in private subnets
- Related: docker expert when container workloads run on ECS tasks within VPC private subnets
