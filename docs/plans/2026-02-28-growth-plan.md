# SkillMesh 30-Day Growth Plan

Date: 2026-02-28  
Owner: Maintainer team  
Goal: increase qualified users, stars, and repeat usage for SkillMesh.

## North-star metrics

- GitHub page views -> stars conversion rate
- Stars -> first successful `skillmesh emit` run
- 7-day repeat usage from first run
- External references (posts, videos, docs mentions)

## Baseline to collect on Day 1

- Current stars, forks, watchers
- Last 30-day views and unique visitors
- Clone count and unique cloners
- Open issues, median time-to-first-response

## Target for 30 days

- 2x stars vs baseline
- >= 15% improvement in view-to-star conversion
- >= 20 public "first run successful" confirmations (issues/discussions/X/LinkedIn)
- Median maintainer response time under 24 hours

## Week 1: conversion foundation

Objective: improve homepage-to-install conversion.

- Ship a conversion-focused README with a 60-second demo command.
- Add 3 example queries that map to common user jobs.
- Verify quickstart from clean environment on Python 3.10, 3.11, 3.12.
- Open `good first issue` tickets (5 to 10) with clear acceptance criteria.
- Pin project positioning in one sentence:
  `Top-K skill routing for large LLM tool catalogs`.

Exit criteria:

- A new user can run `skillmesh emit` in under 5 minutes.
- README CTR signals improve (measured via stars/view trend).

## Week 2: proof and trust

Objective: prove that retrieval routing is better than loading all skills.

- Publish one benchmark note in `docs/`:
  prompt size reduction, retrieval precision, and latency.
- Add one end-to-end notebook/example:
  `dirty data -> routed cards -> cleaned data + prediction + viz`.
- Record and publish one short terminal demo video (45 to 90 seconds).
- Add a changelog entry for all user-visible changes.

Exit criteria:

- At least one reproducible comparison with clear metrics.
- At least one shareable artifact (video, notebook, blog post).

## Week 3: distribution and acquisition

Objective: drive targeted traffic from developer communities.

- Publish 3 launch posts:
  X thread, LinkedIn post, one technical forum post (HN/Reddit/dev.to).
- Each post must include:
  problem, before/after, command snippet, and result screenshot.
- Run 1 integration-focused post:
  `SkillMesh + Codex` or `SkillMesh + Claude Desktop MCP`.
- Reach out to 10 maintainers building multi-tool agents for feedback.

Exit criteria:

- >= 3 external channels posted with measurable traffic.
- >= 5 new external references or discussions.

## Week 4: retention and compounding

Objective: convert first-time users to repeat users and contributors.

- Add templates:
  bug report, feature request, expert-card contribution template.
- Start weekly release cadence (small releases with notes).
- Host one public "office hours" session (live routing and Q&A).
- Prioritize top 5 friction issues from Week 1 to Week 3 feedback.

Exit criteria:

- Repeat usage signals increase week-over-week.
- First external PRs or issue triage contributions appear.

## Distribution checklist for every release

- One concrete use case headline
- One copy-paste command that works
- One screenshot or short clip
- One benchmark or metric
- One CTA:
  `Star if useful`, `open issue with your routing miss`, or `share your registry`.

## Content backlog (execute in order)

1. "Why static SKILLS.md breaks at scale"
2. "How to route dirty data + prediction + viz in one prompt"
3. "Dense reranking vs sparse retrieval in SkillMesh"
4. "SkillMesh with Azure and PySpark tool catalogs"
5. "How to debug wrong expert retrieval"

## Risk register

- Risk: noisy routing results reduce trust.
  Mitigation: publish multi-pass routing guidance and guardrail rules.
- Risk: setup friction lowers conversion.
  Mitigation: keep quickstart to minimal commands and test weekly.
- Risk: irregular shipping cadence.
  Mitigation: commit to weekly release notes, even for small updates.

## Weekly review template

- What changed in stars/views/clones this week?
- Which channel brought highest quality users?
- Where did users fail in first 10 minutes?
- Which one change will improve conversion next week?
