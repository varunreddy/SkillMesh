# Chemistry Expert (RDKit)

Use this expert for molecule-level feature extraction, cheminformatics workflows, virtual screening, and structure-activity analysis using RDKit.

## When to use this expert
- The task involves parsing, validating, or manipulating molecular structures (SMILES, SDF, MOL).
- Molecular descriptors, fingerprints, or property calculations are needed for modeling or filtering.
- Substructure searching, similarity screening, or scaffold analysis is requested.
- The user needs to apply drug-likeness filters (Lipinski, Veber, PAINS) or assess ADMET properties.

## Execution behavior

1. Parse and sanitize all input molecules: use `Chem.MolFromSmiles(smi)` and check for `None` returns. Call `Chem.SanitizeMol(mol)` explicitly when reading from SDF or other formats. Log all unparseable inputs with their original identifiers.
2. Canonicalize SMILES with `Chem.MolToSmiles(mol, canonical=True)` to ensure consistent representation. Use canonical SMILES as the primary molecular identifier in all outputs.
3. Select fingerprint type based on the task: Morgan (ECFP-like, `radius=2, nBits=2048`) for general similarity and QSAR, MACCS keys (166 bits) for substructure-based screening, RDKit topological fingerprints for path-based similarity. Document the choice and parameters.
4. Compute molecular descriptors using `Descriptors.MolWt`, `Descriptors.MolLogP`, `Descriptors.NumHDonors`, `Descriptors.NumHAcceptors`, `Descriptors.TPSA`, and others as needed. Use `Descriptors.CalcMolDescriptors(mol)` for batch descriptor computation.
5. Apply drug-likeness filters: Lipinski Rule of Five (MW <= 500, LogP <= 5, HBD <= 5, HBA <= 10), Veber rules (TPSA <= 140, RotBonds <= 10). Flag violations rather than silently discarding molecules.
6. For similarity search, compute Tanimoto similarity on fingerprints using `DataStructs.TanimotoSimilarity`. Use bulk screening with `DataStructs.BulkTanimotoSimilarity` for large libraries.
7. For batch processing of large molecule sets (> 10k), use `Chem.ForwardSDMolSupplier` for streaming SDF reads, and process in chunks to control memory usage.
8. Register molecule artifacts with canonical SMILES, computed properties, filter pass/fail flags, and fingerprint parameters in metadata.

## Decision tree
- If the task is QSAR modeling -> use Morgan fingerprints (radius=2, 2048 bits) as features. Consider adding physicochemical descriptors (MW, LogP, TPSA) as supplementary features.
- If the task is substructure screening -> use `mol.HasSubstructMatch(pattern)` with SMARTS patterns. Pre-validate SMARTS with `Chem.MolFromSmarts`.
- If the task is diversity selection -> compute pairwise Tanimoto distances and use MaxMin or sphere-exclusion picking to select a diverse subset.
- If the task involves 3D conformers -> generate with `AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())` and optimize with `AllChem.MMFFOptimizeMolecule`. Always add hydrogens first with `Chem.AddHs(mol)`.
- If comparing molecular similarity -> Tanimoto on Morgan FP is the standard baseline; use Dice coefficient when the focus is on shared features rather than overall similarity.
- If molecules contain salts or mixtures -> use `rdMolStandardize.LargestFragmentChooser` to isolate the parent compound before computing properties.

## Anti-patterns
- NEVER skip SMILES validation. `Chem.MolFromSmiles` returns `None` for invalid input; processing `None` as a molecule will cause silent errors or crashes downstream.
- NEVER compare fingerprints generated with different parameters (e.g., radius=2 vs radius=3, or different bit lengths). Similarity scores are meaningless across different fingerprint spaces.
- NEVER use Euclidean distance on binary fingerprints. Use Tanimoto, Dice, or other set-based metrics appropriate for sparse binary vectors.
- NEVER assume all SMILES in a dataset are valid or canonical. Always validate and re-canonicalize on ingestion.
- NEVER report computed LogP or TPSA as experimental values. These are estimates from topological models and should be labeled as "predicted" or "calculated."

## Common mistakes
- Forgetting to call `Chem.AddHs(mol)` before 3D embedding, which produces incorrect geometries for molecules where hydrogen placement matters.
- Using Morgan fingerprint `radius=2` (ECFP4 equivalent) but calling it "ECFP2." The ECFP diameter is 2x the radius, so radius=2 corresponds to ECFP4.
- Computing descriptors on molecules containing explicit salts or counterions, skewing property values (e.g., inflated molecular weight).
- Using `GetMorganFingerprintAsBitVect` with too few bits (e.g., 256), causing excessive bit collisions that reduce fingerprint quality.
- Silently dropping invalid molecules from a dataset without reporting the count, making it unclear what fraction of the input was processable.
- Not handling stereochemistry: ignoring `@` and `@@` in SMILES leads to treating enantiomers as identical, which matters for bioactivity modeling.

## Output contract
- Report invalid or unsanitizable molecules with their original identifiers instead of silently dropping them. Include the count and fraction of failures.
- Include descriptor units and definitions where applicable (e.g., "TPSA: topological polar surface area in Angstrom squared").
- Keep fingerprint settings (type, radius, nBits) in artifact metadata for reproducibility.
- Distinguish computational screening heuristics (Lipinski flags, predicted LogP) from experimentally validated conclusions.
- Provide canonical SMILES as the molecular identifier in all output tables.
- When similarity searches are performed, report the threshold used and the number of hits.
- Include RDKit version in metadata, as descriptor calculations can vary between releases.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to standardize molecule identifiers and handle missing SMILES in tabular datasets.
- After this expert -> use the **Scikit-learn Modeling Expert** or **Gradient Boosting Expert** to build QSAR models using computed fingerprints and descriptors.
- After this expert -> use the **Visualization Expert** to plot chemical space maps (PCA/UMAP on fingerprints), property distributions, or activity cliffs.
- Related -> the **SciPy Optimization Expert** for molecular property optimization or docking score minimization.
- Related -> the **Statistics Expert** for analyzing structure-activity relationships or testing descriptor significance.
