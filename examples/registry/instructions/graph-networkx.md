# Graph Analytics Expert (NetworkX)

Use this expert for graph-centric analysis, topology-aware insights, and network science workflows on relational data.

## When to use this expert
- The task involves relational data that is best modeled as nodes and edges (social networks, citation graphs, dependency trees, knowledge graphs).
- Centrality, community detection, shortest paths, or connectivity analysis is requested.
- The user needs to construct a graph from edge lists, adjacency matrices, or hierarchical data.
- Network visualization or topology-based feature extraction is required.

## Execution behavior

1. Build the graph from the data source with an explicit directed/undirected choice. Use `nx.from_pandas_edgelist(df, source, target, edge_attr)` for DataFrames or `G.add_edges_from(edge_list)` for raw lists. Validate that the expected node and edge counts match the input.
2. Inspect basic topology: `G.number_of_nodes()`, `G.number_of_edges()`, `nx.is_connected(G)` (undirected) or `nx.is_weakly_connected(G)` (directed), and `nx.density(G)`. Report disconnected components if present.
3. Compute centrality metrics aligned to the business question: degree centrality for popularity, betweenness for brokerage/bottlenecks, closeness for reachability, eigenvector or PageRank for influence propagation. Use `nx.pagerank(G)` for directed graphs with weighted edges.
4. Run community detection using `nx.community.louvain_communities(G)` or Girvan-Newman for small graphs. Compare partition quality using modularity (`nx.community.modularity`). Test stability by running with multiple random seeds.
5. Analyze shortest paths and connectivity: `nx.shortest_path_length(G, source, target)` for pairwise distances, `nx.average_shortest_path_length(G)` for global reachability (only on connected graphs), `nx.minimum_edge_cut` for vulnerability analysis.
6. For large graphs (> 50k nodes), prefer approximate algorithms or sampling. Use `nx.approximate_current_flow_betweenness_centrality` or compute metrics on the largest connected component only.
7. Generate graph visualizations using `nx.draw` with a layout algorithm suited to the graph structure: `spring_layout` for general graphs, `kamada_kawai_layout` for smaller graphs with meaningful distances, `circular_layout` for regular structures, `shell_layout` for hierarchical data.
8. Register graph-derived metrics, community assignments, and visual summaries as artifacts with metadata describing the graph properties and algorithms used.

## Decision tree
- If the graph is directed and represents flow (traffic, supply chain) -> use in-degree/out-degree centrality and `nx.maximum_flow` for capacity analysis.
- If the graph is social/collaboration -> use betweenness centrality for brokers and Louvain for community structure. Consider edge weights as interaction frequency.
- If the graph is a dependency tree (package deps, task DAGs) -> use topological sort (`nx.topological_sort`), check for cycles (`nx.find_cycle`), and compute longest paths for critical-path analysis.
- If nodes have attributes (features) -> combine graph metrics with node features for downstream ML. Export as a feature matrix with centrality columns appended.
- If the graph has > 100k edges -> avoid `O(n^3)` algorithms (all-pairs shortest path, exact betweenness on full graph). Use sampling or approximate methods.
- If comparing two graphs -> compute graph-level statistics (diameter, density, degree distribution) side by side rather than attempting graph isomorphism.

## Anti-patterns
- NEVER compute `average_shortest_path_length` on a disconnected graph. It will raise an error. Compute per-component or use the largest connected component.
- NEVER use `spring_layout` for graphs with > 5000 nodes without increasing `iterations` and `k` parameters. The default produces unreadable hairballs.
- NEVER interpret raw centrality scores as absolute rankings across different graphs. Centrality values are graph-size-dependent; normalize or compare within the same graph.
- NEVER assume an undirected graph when the data has inherent directionality (e.g., citations, follower relationships). Using the wrong graph type invalidates centrality and path results.
- NEVER run community detection without reporting the modularity score. Partitions with low modularity (< 0.3) may not represent meaningful community structure.

## Common mistakes
- Building a `Graph` (undirected) when the data represents directed relationships, causing edge loss when duplicate source-target pairs exist in both directions.
- Forgetting to handle self-loops, which inflate degree centrality and can cause issues in community detection algorithms.
- Using `nx.draw` with the default layout on a large graph, producing an uninformative visualization. Filter to a subgraph or use a specialized layout.
- Computing betweenness centrality on the full graph when only a subset of nodes is of interest. Use `nx.betweenness_centrality_subset` for targeted analysis.
- Not removing isolated nodes before computing metrics like average path length or clustering coefficient, which can skew results.
- Interpreting high degree centrality as "importance" without considering the domain. In some networks, hubs are noise (e.g., shared utility nodes).

## Output contract
- Specify graph assumptions: weighted or unweighted, directed or undirected, number of nodes and edges, number of connected components.
- Include top-k influential nodes with metric values and the centrality method used.
- Report disconnected components, isolated nodes, and reachability caveats.
- Keep node and edge provenance for reproducibility (original IDs, source data reference).
- When community detection is performed, report the number of communities, modularity score, and partition method.
- If graph visualization is produced, state the layout algorithm and any filtering applied.
- For path analysis, report the source, target, path length, and whether the graph is weighted.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to validate edge lists, resolve duplicate edges, and handle missing node attributes.
- After this expert -> use the **Visualization Expert** for publication-quality network plots with custom node coloring by community or centrality.
- After this expert -> use the **Scikit-learn Modeling Expert** to build classifiers using graph-derived features (centrality, clustering coefficient) as input columns.
- Related -> the **Statistics Expert** for testing whether observed network properties (e.g., degree distribution) differ from random graph baselines.
- Related -> the **NLP Expert** for constructing knowledge graphs from text extraction outputs.
