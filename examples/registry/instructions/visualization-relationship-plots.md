# Relationship and Correlation Visualization Expert

Use this expert for scatter/bubble/hexbin and related plots that explain relationships between variables.

## When to use this expert
- You need to show correlation, interaction, clusters, or heteroskedasticity.
- The dataset includes dense point clouds where overplotting is a risk.
- You want explanatory relationship visuals for model features.

## Execution behavior
1. Define variable roles (x, y, color, size, facet) and expected relationship shape.
2. Start with scatter; switch to hexbin/density for high point counts.
3. Add trend lines or local smoothers only when assumptions are stated.
4. Use transparent marks/jitter/aggregation to handle overlap.
5. Report notable segments, leverage points, and non-linear regions.

## Decision tree
- Low to moderate sample size -> scatter with subgroup encoding.
- High density -> hexbin or density contour.
- Third quantitative variable important -> bubble chart with size legend safeguards.

## Anti-patterns
- NEVER infer causality from correlation plots alone.
- NEVER apply misleading bubble scaling (area must encode value, not radius directly).
- NEVER omit subgroup context when Simpson's paradox is plausible.

## Output contract
- Plot choice and overplotting mitigation strategy.
- Relationship summary (direction, strength, non-linearity notes).
- Segment-level findings and caveats.

## Composability hints
- Related -> **Scikit-learn Linear Models** for interpretable baseline feature effects.
- Related -> **Scikit-learn Tree and Forest Models** for non-linear alternative diagnostics.
