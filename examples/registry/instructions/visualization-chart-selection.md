# Visualization Chart Selection Expert

Use this expert to pick the right chart type for the analytical question before implementation.

## When to use this expert
- You need to decide between bars, lines, areas, tables, or ranking visuals.
- The task asks for executive-ready visuals with minimal ambiguity.
- Stakeholders need a clear mapping from question -> chart choice -> narrative.

## Execution behavior
1. Classify the question type: comparison, trend, composition, distribution, relationship, or process flow.
2. Choose the simplest chart that preserves meaning.
3. Validate axis semantics (time, category order, units, zero baseline requirements).
4. Specify annotation plan (highlights, reference lines, target thresholds).
5. Produce backup chart options when uncertainty exists.

## Decision tree
- Comparison across categories -> bar/column/lollipop.
- Trend over time -> line/area/step.
- Part-to-whole -> stacked bars, treemap, or donut only when category count is small.
- Exact lookup required -> table + compact visual summary.

## Anti-patterns
- NEVER use pie/donut charts for many categories.
- NEVER use dual y-axes without explicit risk explanation.
- NEVER choose chart aesthetics before clarifying the analytical question.

## Output contract
- Recommended primary chart type and fallback.
- Rationale linked to business question and data shape.
- Encoding plan: x/y, color, size, facets, and annotations.
- Known interpretation risks and mitigations.

## Composability hints
- After this expert -> use specific plotting experts for implementation.
- Related -> **Distribution and Outlier Visualization Expert** for histogram/box/violin needs.
