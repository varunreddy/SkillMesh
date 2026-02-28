# Time Series Analysis Expert

Use this expert for temporal data modeling including stationarity testing, seasonal decomposition, ARIMA/SARIMA forecasting, Prophet models, time-aware cross-validation, and lag-based feature engineering.

## When to use this expert
- The dataset has a datetime index and the task involves forecasting, trend detection, or seasonality analysis.
- Stationarity must be verified before fitting any parametric model.
- Cross-validation must respect temporal ordering (no random shuffling).
- Feature engineering from timestamps, lags, or rolling statistics is needed for ML-based forecasting.

## Execution behavior

1. Parse and sort the datetime index. Verify the frequency is consistent (daily, hourly, etc.) and fill or flag any gaps before proceeding.
2. Visualize the raw series, its rolling mean, and rolling standard deviation to form an initial hypothesis about trend and seasonality.
3. Test stationarity with the Augmented Dickey-Fuller (ADF) test and confirm with the KPSS test. If they disagree, apply differencing and retest.
4. Decompose the series using `seasonal_decompose` (additive or multiplicative) or STL decomposition to isolate trend, seasonal, and residual components.
5. Select the model family: use ARIMA/SARIMA for univariate with clear autocorrelation structure, Prophet for series with strong seasonality and holiday effects, or gradient boosting with lag features for multivariate settings.
6. Fit the model and inspect residuals: check for remaining autocorrelation (Ljung-Box test), normality (Q-Q plot), and heteroscedasticity. If residuals show structure, the model is underfit.
7. Validate using expanding-window or sliding-window cross-validation. Never use random k-fold splits on time series data.
8. Report point forecasts with prediction intervals. Quantify forecast accuracy using MAE, RMSE, and MAPE on the held-out period.

## Decision tree
- If the series shows strong, regular seasonality -> use SARIMA with seasonal order `(P,D,Q,m)` or Prophet with automatic seasonality detection.
- If multiple related series must be forecast together -> use hierarchical reconciliation (bottom-up, top-down, or optimal reconciliation) to ensure coherence.
- If exogenous variables are available and correlated with the target -> use ARIMAX, SARIMAX, or a supervised ML model with lag features and calendar features.
- If forecasts are consumed in real-time with incoming data -> use an expanding window for retraining, not a fixed-window model frozen at training time.
- If the series has abrupt level shifts or structural breaks -> segment the series at break points and model each regime separately, or use a model robust to changepoints (Prophet).
- If the data is high-frequency (sub-minute) with noise -> apply a smoothing filter (exponential, Savitzky-Golay) before decomposition, and note the lag introduced.

## Anti-patterns
- NEVER split time series data randomly into train and test sets. This leaks future information and produces unrealistically optimistic metrics.
- NEVER fit ARIMA on a non-stationary series without differencing. The model assumptions are violated and forecasts will diverge.
- NEVER overfit on small samples by using high-order AR or MA terms. Use AIC/BIC for order selection and validate out of sample.
- NEVER ignore residual autocorrelation after fitting. Significant autocorrelation means the model has not captured all learnable signal.
- NEVER report forecast accuracy without prediction intervals. Point forecasts alone hide the uncertainty range.

## Common mistakes
- Using `seasonal_decompose` with the wrong `period` parameter, producing meaningless seasonal components. Always match period to the true data frequency (e.g., 7 for daily data with weekly seasonality, 12 for monthly with annual seasonality).
- Confusing ADF and KPSS null hypotheses: ADF tests H0 = unit root (non-stationary), KPSS tests H0 = stationary. They are complementary, not interchangeable.
- Applying log transforms to series that contain zero or negative values, producing NaN or errors. Use a Box-Cox transform with a shift instead.
- Building lag features and then accidentally including the current-period target value as a feature, creating direct leakage.
- Evaluating multi-step forecasts with single-step accuracy metrics. Multi-step errors compound; measure at each horizon separately.
- Ignoring calendar effects (holidays, weekends, month-end) that produce systematic residual patterns in business data.

## Output contract
- Report stationarity test results (ADF p-value, KPSS p-value) and any differencing or transformations applied.
- Include a decomposition plot (trend, seasonal, residual) or describe its findings.
- Provide residual diagnostics: ACF plot summary, Ljung-Box p-value, and a normality assessment.
- Report forecast accuracy on held-out data with at least two metrics (MAE, RMSE, or MAPE).
- Include prediction intervals (e.g., 80% and 95%) alongside point forecasts.
- Document the cross-validation strategy used (expanding window size, step size, number of folds).
- State the forecast horizon and frequency explicitly.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle missing timestamps, duplicates, and timezone normalization.
- Before this expert -> use the **Advanced Pandas Expert** for resampling, datetime indexing, and lag feature construction.
- After this expert -> use the **Visualization Expert** to produce forecast plots with confidence bands and decomposition charts.
- Related -> the **Statistics Expert** for formal hypothesis tests on residuals or structural break detection.
- Related -> the **Quantitative Finance Expert** when the time series represents asset prices or returns requiring financial-specific treatment.
