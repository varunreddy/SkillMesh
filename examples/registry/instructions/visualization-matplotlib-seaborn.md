# Visualization Expert (Matplotlib + Seaborn)

Use this expert when the task needs clear, publication-quality figures that communicate data insights accurately and accessibly.

## When to use this expert
- The user needs charts, plots, or visual summaries to accompany analysis results.
- A report or presentation requires embedded figures with consistent styling.
- Exploratory data analysis needs visual diagnostics (distributions, correlations, trends).
- The task explicitly mentions chart type selection, styling, or figure export.

## Execution behavior

1. Clarify the analytical goal before choosing a chart type: comparison (bar, dot), distribution (histogram, KDE, box), relationship (scatter, heatmap), composition (stacked bar, pie only if few categories), or trend (line, area).
2. Use seaborn as the primary API for statistical plots (`sns.histplot`, `sns.boxplot`, `sns.scatterplot`) and fall back to matplotlib for fine-grained layout control (`fig, axes = plt.subplots(...)`).
3. Apply a consistent theme early: call `sns.set_theme(style="whitegrid")` or equivalent, and set a colorblind-safe palette (`sns.color_palette("colorblind")` or cubehelix).
4. Label every axis with a human-readable name and units (e.g., "Revenue (USD, thousands)"). Add a descriptive title that states the insight, not just the variable name.
5. Add legends only when needed (multiple series). Position legends outside the plot area when they overlap data.
6. For multi-panel figures, use `plt.subplots(nrows, ncols, figsize=(...))` with shared axes where scales are comparable. Use `fig.suptitle()` for an overarching title.
7. Export with `fig.savefig(path, dpi=200, bbox_inches="tight")` for raster formats and `format="svg"` for vector output. Always call `plt.close(fig)` after saving to free memory.
8. Register each figure as an artifact with a caption explaining what the reader should take away from the chart.

## Decision tree
- If comparing groups -> use bar chart (vertical for few groups, horizontal for long labels) or dot plot; avoid pie charts unless categories sum to a meaningful whole and there are fewer than 6 slices.
- If showing distribution -> prefer `histplot` with KDE overlay for continuous data; use `countplot` for categorical. Use violin or box plots when comparing distributions across groups.
- If showing correlation -> use a heatmap with `annot=True` and diverging colormap centered at zero; mask the upper triangle for symmetric matrices.
- If the y-axis does not start at zero -> add a visible axis break annotation or explicitly state the truncation in the caption. Do not silently truncate.
- If the figure has more than 8 colors -> switch to a sequential or grouped color strategy; too many distinct hues become indistinguishable.
- If the audience is non-technical -> simplify: remove grid lines, reduce tick density, and add direct annotations on key data points.

## Anti-patterns
- NEVER use rainbow/jet colormaps. They are perceptually non-uniform and misleading for continuous data.
- NEVER produce a chart without axis labels or a title. Unlabeled charts are uninterpretable outside the notebook.
- NEVER use 3D plots for data that lives in 2D. 3D bar charts and 3D scatter plots distort perception and add no information.
- NEVER rely on color alone to encode meaning. Use markers, line styles, or hatching as redundant channels for accessibility.
- NEVER embed raw matplotlib figures in reports without calling `bbox_inches="tight"`, which clips whitespace and prevents label cutoff.

## Common mistakes
- Using `plt.show()` inside a script that also calls `savefig`, causing a blank saved image because `show()` clears the figure.
- Setting `figsize` too small for the number of subplots, resulting in overlapping tick labels.
- Forgetting to convert datetime columns before plotting, which produces unreadable x-axis labels.
- Using seaborn's default `hue` without controlling the legend order, leading to inconsistent color-to-category mapping across figures.
- Saving figures at 72 DPI (screen default) for print, where 200+ DPI is needed.
- Plotting raw counts on a bar chart when the groups have vastly different sizes, making comparison misleading. Use rates or normalized values.

## Output contract
- Include at least one explanatory caption per figure stating the insight, not just the chart type.
- Export at `dpi >= 200` for report integration; use PNG for documents and SVG for web where supported.
- Keep figure code reproducible from raw DataFrame inputs. No manual pixel editing.
- Use colorblind-safe palettes by default. Document palette choice in code comments.
- When multiple figures are produced, maintain consistent axis scales and color mappings across related charts.
- Close all figure handles after saving to avoid memory leaks in long-running sessions.
- Report the file path and format of each saved figure as an artifact.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to ensure tidy data suitable for plotting (long format for seaborn).
- Before this expert -> use the **Statistics Expert** to compute summary statistics, confidence intervals, or test results to annotate on charts.
- After this expert -> use the **PDF Creation Expert** or **Slide Creation Expert** to embed figures in deliverables.
- Related -> the **Geospatial Expert** for map-based visualizations that require projected coordinates.
