# Hierarchy, Flow, and Network Visualization Expert

Use this expert for treemap/sunburst/waterfall/funnel/sankey/network visuals where structure or flow matters.

## When to use this expert
- You need to explain hierarchical composition or stepwise drop-off.
- The question is about movement between states or systems.
- Network topology and relationship paths are central to the story.

## Execution behavior
1. Confirm data model shape: hierarchy tree, staged funnel, or source-target flow table.
2. Choose chart by question type:
   - hierarchy: treemap/sunburst
   - process loss: funnel/waterfall
   - transfer flow: sankey
   - graph topology: network plot
3. Normalize node/edge labeling and aggregation granularity.
4. Highlight dominant paths or bottlenecks.
5. Provide interpretation guidance for non-technical readers.

## Decision tree
- Parent-child share analysis -> treemap/sunburst.
- Conversion pipeline stages -> funnel.
- Positive/negative contributors to delta -> waterfall.
- Movement across categories/systems -> sankey.

## Anti-patterns
- NEVER use sankey with unreadable tiny flows and no thresholding.
- NEVER overload hierarchy charts with too many levels at once.
- NEVER present network layout as quantitative distance unless explicitly modeled.

## Output contract
- Chosen chart with data-shaping assumptions.
- Top contributors/paths and bottleneck summary.
- Limitations caused by aggregation or layout heuristics.

## Composability hints
- Before this expert -> use **Advanced Pandas Data Workflows** to shape source-target/hierarchy tables.
- Related -> **Graph Analytics Expert** for deeper network metrics before visualization.
