# Geo and Timeline Visualization Expert

Use this expert for choropleth, proportional-symbol maps, timelines, and Gantt-style schedule visuals.

## When to use this expert
- Location is a core analytical dimension.
- Time planning, sequencing, or milestone tracking is required.
- You need map/timeline visuals for operational or executive reporting.

## Execution behavior
1. Validate geospatial keys (region codes, lat/lon CRS) or time schema (start/end/milestones).
2. Choose chart family:
   - region intensity -> choropleth
   - point magnitude -> bubble/proportional symbol map
   - schedule dependencies -> Gantt/timeline
3. Normalize color scales and legends to avoid false emphasis.
4. Label critical hotspots or schedule risks with callouts.
5. Include a table companion for exact values when needed.

## Decision tree
- Areal comparison by region -> choropleth.
- Point events with magnitude -> bubble map.
- Project phases and overlaps -> Gantt chart.
- Milestone communication -> timeline chart.

## Anti-patterns
- NEVER use raw counts on choropleths without normalization where population/exposure differs.
- NEVER mix inconsistent geographic boundaries across periods.
- NEVER hide timezone/calendar assumptions in timeline charts.

## Output contract
- Selected map/timeline type and encoding rationale.
- Data-quality assumptions (geography and time).
- Hotspot/risk summary and interpretation caveats.

## Composability hints
- Related -> **GeoPandas Spatial Analytics Expert** for geospatial preprocessing.
- Related -> **Dashboard Design and KPI Storytelling Expert** for executive narrative packaging.
