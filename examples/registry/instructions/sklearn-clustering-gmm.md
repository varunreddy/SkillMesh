# Scikit-learn Clustering and GMM Expert

Use this expert for unsupervised segmentation with sklearn clustering methods, including centroid, density, hierarchical, and probabilistic mixture approaches.

## When to use this expert
- You need customer/behavior segments without labeled targets.
- The task requires `KMeans`, `DBSCAN`, `AgglomerativeClustering`, or `GaussianMixture`.
- You need reproducible cluster evaluation and interpretation.

## Execution behavior
1. Standardize and clean features before clustering.
2. Start with `KMeans` and a simple cluster-count sweep.
3. Add model-specific alternatives:
   - density-aware: `DBSCAN`
   - hierarchy-aware: `AgglomerativeClustering`
   - probabilistic soft assignment: `GaussianMixture`
4. Evaluate with silhouette, Davies-Bouldin, and stability checks across seeds.
5. Profile each cluster with key feature summaries and sizes.
6. Validate business usefulness with downstream KPI separation.
7. Persist clustering pipeline and labeling logic.

## Decision tree
- If you know approximate segment count -> start with `KMeans`.
- If arbitrary cluster shape/noise points matter -> use `DBSCAN`.
- If soft assignment probabilities are needed -> use `GaussianMixture`.
- If interpretability of merge hierarchy matters -> use agglomerative clustering.

## Anti-patterns
- NEVER treat cluster IDs as ordinal or causal labels.
- NEVER compare cluster metrics across differently scaled feature spaces.
- NEVER finalize a cluster count from one metric only.

## Common mistakes
- Ignoring small-cluster instability across random seeds.
- Using high-dimensional raw features without reduction.
- Forgetting to mark noise points (`DBSCAN`) in downstream analysis.

## Output contract
- Provide chosen clustering algorithm and key hyperparameters.
- Report internal metrics and stability summary.
- Include segment profile table with business interpretation.
- Document assignment strategy for new incoming records.

## Composability hints
- Before this expert -> use **Feature Engineering for ML** for scaling and transformation consistency.
- After this expert -> use **Visualization with Matplotlib and Seaborn** for cluster profile plots.
- Related -> **Scikit-learn Dimensionality Reduction Expert** for preprocessing high-dimensional features.
