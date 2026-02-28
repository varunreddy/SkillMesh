# Geospatial Analysis Expert (GeoPandas)

Use this expert for location-aware data processing, spatial joins, geometry operations, and map preparation using GeoPandas and related libraries.

## When to use this expert
- The task involves geographic data with coordinates, polygons, or spatial relationships.
- Spatial joins, overlays, buffering, or distance calculations are needed.
- The user needs to create choropleths, point maps, or other geospatial visualizations.
- Coordinate reference system (CRS) management or projection selection is required.

## Execution behavior

1. Load spatial data with `gpd.read_file()` for shapefiles, GeoJSON, or GeoPackage. For CSV with lat/lon columns, create geometry with `gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")`. Always set the CRS at load time.
2. Validate geometry integrity immediately: check for null geometries (`gdf[gdf.geometry.is_empty | gdf.geometry.isna()]`), invalid geometries (`gdf[~gdf.is_valid]`), and fix with `gdf.geometry = gdf.geometry.buffer(0)` or `gdf.geometry = gdf.geometry.make_valid()`.
3. Reproject datasets to a compatible CRS before any spatial operation that involves distance, area, or overlay. Use `gdf.to_crs(epsg=...)`. Choose a projected CRS appropriate to the region (e.g., UTM zone for local analysis, Albers Equal Area for continental).
4. Use spatial joins with explicit predicates: `gpd.sjoin(left, right, predicate="intersects")` for overlap, `predicate="within"` for containment, `predicate="nearest"` for proximity. Understand that `sjoin` returns one row per match, which can duplicate left-side rows.
5. Build spatial indexes for large datasets by calling `gdf.sindex` before joins or queries. GeoPandas uses rtree or pygeos indexing automatically, but verifying the index exists before repeated operations avoids performance surprises.
6. Aggregate spatial features to target boundaries (e.g., points to census tracts): use `sjoin` followed by `groupby` and `agg`, or `overlay` for polygon-to-polygon operations.
7. For choropleth maps, normalize values (per-capita, per-area, percentiles) to avoid misleading visual comparisons between regions of different sizes. Use `gdf.plot(column="metric", legend=True, scheme="quantiles")` with a classification scheme.
8. Register map-ready GeoDataFrames and summary outputs as artifacts, including CRS information, row counts, and any geometries that were dropped or repaired.

## Decision tree
- If measuring distances or areas -> reproject to an equal-area or equidistant projected CRS first. NEVER compute distances in EPSG:4326 (geographic degrees); the results are meaningless as metric values.
- If joining points to polygons -> use `sjoin` with `predicate="within"`. If points fall on polygon boundaries, consider buffering slightly or using `predicate="intersects"`.
- If the dataset has global coverage -> use an equal-area projection like Mollweide (ESRI:54009) for area calculations. For local analysis, use the appropriate UTM zone.
- If creating a choropleth of counts -> normalize by area or population before mapping. Raw counts mislead because larger regions accumulate more events by chance.
- If geometries are invalid (self-intersecting polygons) -> apply `buffer(0)` or `make_valid()` before any overlay operation. Invalid geometries cause silent failures in spatial predicates.
- If performance is poor on large datasets -> ensure spatial indexing is active, simplify geometries with `gdf.geometry.simplify(tolerance)` for visualization, and consider GeoParquet format for faster I/O.

## Anti-patterns
- NEVER compute distances, areas, or buffers in a geographic CRS (EPSG:4326). Degree-based calculations produce incorrect metric results that vary by latitude.
- NEVER join two GeoDataFrames with different CRS without reprojecting first. The spatial predicates will produce nonsensical matches.
- NEVER plot raw counts on a choropleth without normalization. This produces a "population density map" regardless of the variable being shown.
- NEVER drop null or invalid geometries silently. Report the count and identifiers of dropped features so the user can investigate.
- NEVER use `gdf.plot()` for production maps without adding a basemap, scale bar, or north arrow context. Raw polygon plots lack geographic reference.

## Common mistakes
- Forgetting to set CRS when creating a GeoDataFrame from a CSV, resulting in a CRS-less dataset that silently fails spatial joins.
- Confusing `overlay` (polygon-polygon set operations like intersection, union, difference) with `sjoin` (attribute join based on spatial predicates). Using the wrong one produces incorrect results.
- Using `gdf.geometry.area` in EPSG:4326 and getting values in "square degrees" that have no physical meaning.
- Applying `simplify()` with too large a tolerance, causing polygons to collapse or lose important boundary detail.
- Not handling the duplicate rows created by `sjoin` when multiple right features match a single left feature. Always check for and handle duplicates after spatial joins.
- Plotting large polygon datasets without simplification, causing slow rendering and unresponsive notebooks.

## Output contract
- State the CRS (EPSG code and name) for every major geospatial artifact produced.
- Include the spatial join predicate used (`within`, `intersects`, `nearest`) and any buffer distances applied.
- Report dropped or invalid geometries explicitly with counts and identifiers.
- Preserve geospatial precision appropriate for the use case (do not over-simplify for analytical outputs).
- For choropleth outputs, state the normalization method and classification scheme used.
- Record the geometry types present (Point, Polygon, MultiPolygon) and any mixed-type issues encountered.
- Include data source attribution and vintage (year) for administrative boundaries.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to standardize location identifiers (FIPS codes, ISO codes) and handle missing coordinates.
- After this expert -> use the **Visualization Expert** for publication-quality static maps with annotations, scale bars, and insets.
- After this expert -> use the **PDF Creation Expert** or **Slide Creation Expert** to embed maps in deliverables.
- Related -> the **Statistics Expert** for spatial autocorrelation tests (Moran's I) or geographic regression models.
- Related -> the **Scikit-learn Expert** for spatial feature engineering (distance to nearest X, count within radius) fed into predictive models.
