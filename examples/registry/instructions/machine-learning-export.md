# Machine Learning Export Expert

Use this expert when trained models must be packaged for reproducible reuse, serving, and deployment.

## When to use this expert
- You need to serialize Scikit-Learn or XGBoost models for offline batch inference.
- You are transitioning prototypes to production and require strict metadata provenance.
- You need to cross language boundaries and export models via ONNX for C++/C# ingestion.
- You must ensure the exported representation avoids latency bottlenecks during fast reload cycles.

## Execution behavior
1. Capture detailed training metadata (library versions, feature schema, preprocessing steps).
2. Establish feature selection masks strictly aligned to the model input architecture.
3. Export baseline artifact with `joblib` or `pickle` for Python-native environments.
4. Export interoperable artifact (ONNX/PMML) when cross-runtime, cross-language serving is specified.
5. Record model checksum metadata (SHA256) for artifact integrity checks in the registry.
6. Validate exports by injecting mock data and running a smoke prediction test immediately after save/load.
7. Profile latency of loading the model to ensure it meets production service-level objectives (SLOs).
8. Version the exported files to guarantee backwards compatibility with previous data schemas.

## Decision tree
- If strictly using Python environments without latency pressure, choose `joblib` over `pickle`.
- If strict cross-platform or cross-language (Node.js/C#) support is required, choose `ONNX`.
- If memory overhead on the inference server is a concern, choose `mmap_mode` with localized `joblib`.
- If the model is a massive PyTorch/Tensorflow graph, prefer `TorchScript` or `SavedModel` over generic formats.
- If security and arbitrary code execution is a risk in your loading pipeline, choose strictly non-executable formats like `safetensors`.
- If evaluating legacy rules engines alongside ML, consider `PMML`.

## Anti-patterns
- NEVER export a model without validating inference parity on the exact loaded artifact.
- NEVER use standard `pickle` for untrusted model inputs (critical deserialization vulnerability).
- NEVER hardcode absolute file paths into the deployment wrapper logic.
- NEVER export a pipeline that excludes the required text-preprocessing or scaling steps.
- NEVER omit exact library dependencies (e.g. Scikit-learn=1.2.2) when creating the artifact package.
- NEVER skip schema validation of columns on the inference side before passing to the artifact.

## Common mistakes
- Forgetting to export the label encoder, breaking classification outputs at runtime.
- Saving deep learning models with optimizer states attached, doubling the file size unnecessarily.
- Using mismatched library versions between the training sandbox and the inference production server.
- Failing to capture the Python version used during `pickle` creation, leading to `UnpicklingError`.
- Exporting pandas DataFrames inside the pipeline metadata causing bloat.
- Ignoring timezone serialization issues inside custom transformers.

## Output contract
- Serialized model artifact (`.pkl`, `.joblib`, `.onnx` files).
- Model metadata manifest JSON (versions, metrics, date).
- Inference compatibility report and smoke-test validation code.
- Serialization size and load-time metrics.
- Fallback serving behavior configuration.
- Checksums and provenance tags.
- Expected data dictionary and input schema.

## Composability hints
- Pair with `ml.sklearn-modeling` to lock the pipeline structure before calling the export phase.
- Use `devops.ci-cd-pipelines` to automate the checksum generation upon merging to master.
- Connect with `cloud.aws-s3` or `cloud.gcp-gcs` for robust external object storage of the artifacts.
- Combine with `web.api-performance` to ensure the loaded model wrapper satisfies load testing limits.
