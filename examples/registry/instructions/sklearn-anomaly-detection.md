# Scikit-learn Anomaly Detection Expert

Use this expert for outlier and novelty detection with sklearn (`IsolationForest`, `OneClassSVM`, `LocalOutlierFactor`, `EllipticEnvelope`).

## When to use this expert
- You need unsupervised or weakly supervised anomaly detection.
- Label scarcity prevents standard supervised classification.
- Detection thresholds and false-positive control are required.

## Execution behavior
1. Define anomaly objective and acceptable alert volume.
2. Choose estimator family by data geometry and scale.
3. Tune contamination/threshold settings against validation expectations.
4. Evaluate precision-recall behavior on available labeled slices.
5. Provide triage workflow for flagged anomalies.

## Anti-patterns
- NEVER ship fixed contamination defaults without domain validation.
- NEVER optimize only for recall in high-cost alerting systems.
- NEVER interpret anomaly score as probability by default.

## Output contract
- Model choice and threshold policy.
- Detection quality summary (and uncertainty if labels are sparse).
- Operational triage and retraining recommendations.

