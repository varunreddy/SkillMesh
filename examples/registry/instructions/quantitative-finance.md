# Quantitative Finance Expert

Use this expert for portfolio optimization, risk measurement, backtesting strategies, factor modeling, and return calculations with proper treatment of financial data characteristics such as fat tails, autocorrelation, and survivorship bias.

## When to use this expert
- The task involves constructing or rebalancing a portfolio with optimization constraints.
- Risk metrics (VaR, CVaR, drawdown, Sharpe, Sortino) must be calculated or compared.
- A trading or allocation strategy must be backtested with realistic assumptions.
- Factor models or return attribution are needed to explain portfolio performance.

## Execution behavior

1. Collect and validate price or return data. Confirm the data is adjusted for splits and dividends, check for survivorship bias, and align all series to a common date index with explicit handling of missing trading days.
2. Compute log returns for multi-period compounding analysis or simple returns for portfolio-weighted aggregation. Never mix the two in the same calculation.
3. Characterize the return distribution: test for normality (Jarque-Bera), check skewness and kurtosis, and examine autocorrelation. Financial returns are rarely Gaussian.
4. For portfolio construction, use mean-variance optimization with a covariance shrinkage estimator (Ledoit-Wolf) to stabilize weights. Apply realistic constraints: long-only, max position size, sector limits.
5. Calculate risk metrics on out-of-sample data: Value at Risk (VaR) at 95% and 99%, Conditional VaR (Expected Shortfall), maximum drawdown, Sharpe ratio (annualized), and Sortino ratio.
6. Backtest with walk-forward methodology: train on an expanding or rolling window, predict/allocate on the next period, record returns net of transaction costs and slippage, and advance the window.
7. Decompose returns using a factor model (Fama-French 3 or 5 factor, or custom factors) to separate alpha from systematic exposure.
8. Stress test the portfolio against historical scenarios (2008 crisis, COVID crash, rate shocks) and report drawdown and recovery time.

## Decision tree
- If building a diversified portfolio -> use mean-variance optimization with Ledoit-Wolf shrinkage; add a maximum-weight constraint to prevent concentration.
- If the investor has views on specific assets -> use Black-Litterman to blend market equilibrium with subjective views before optimizing.
- If measuring downside risk on a portfolio with fat-tailed returns -> use historical simulation or Cornish-Fisher VaR, not parametric Gaussian VaR.
- If returns are approximately normal -> parametric VaR is acceptable, but always cross-check with historical VaR.
- If evaluating a strategy -> report Sharpe ratio, maximum drawdown, and Calmar ratio together. No single metric is sufficient.
- If comparing strategies with different volatilities -> use risk-adjusted metrics (Sharpe, Sortino) not raw returns.

## Anti-patterns
- NEVER introduce look-ahead bias in backtests. The model must use only information available at the time of each decision. This includes not using future data for parameter tuning, feature selection, or universe definition.
- NEVER use arithmetic mean of returns for multi-period compounding. Use geometric mean or log returns to avoid upward bias.
- NEVER ignore transaction costs and slippage in backtests. A strategy profitable before costs may be unprofitable after realistic friction.
- NEVER optimize on in-sample data only and report those results as expected performance. Always validate on out-of-sample periods.
- NEVER treat backtest results as a prediction of future returns. Past performance with known data is not an unbiased estimator of future performance.
- NEVER use a sample covariance matrix from short histories with many assets. The matrix will be noisy or singular; use shrinkage or factor-based covariance.

## Common mistakes
- Computing Sharpe ratio with daily returns but forgetting to annualize: multiply by `sqrt(252)` for daily data or `sqrt(12)` for monthly.
- Using the risk-free rate inconsistently: the rate must match the return frequency (daily risk-free for daily returns) and be subtracted before annualizing.
- Ignoring survivorship bias by using only currently listed assets, which excludes delisted losers and inflates historical performance.
- Rebalancing at unrealistic frequencies (e.g., daily) without accounting for the cumulative transaction cost drag.
- Confusing Sharpe and Sortino: Sortino uses downside deviation only, which is more appropriate when return distributions are skewed.
- Fitting a model to the entire backtest period and then reporting its "performance" on the same data as if it were out-of-sample.

## Output contract
- Report all return calculations with explicit frequency (daily, monthly, annual) and compounding method (simple or log).
- Include annualized Sharpe ratio, Sortino ratio, maximum drawdown, and Calmar ratio for any strategy evaluation.
- Provide VaR and CVaR at 95% confidence with the method used (parametric, historical, or Monte Carlo).
- Document all backtest assumptions: rebalancing frequency, transaction cost model, slippage, universe selection date.
- Include an equity curve and drawdown plot or describe the trajectory in measurable terms.
- Report factor exposures (betas) and the proportion of return explained by systematic factors vs. alpha.
- State the out-of-sample evaluation period clearly and separately from any in-sample tuning period.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle missing prices, adjust for splits/dividends, and align multi-asset date indexes.
- Before this expert -> use the **Time Series Expert** for stationarity testing and ARIMA-based return forecasting that feeds into allocation models.
- After this expert -> use the **Visualization Expert** to produce equity curves, drawdown charts, and efficient frontier plots.
- After this expert -> use the **Financial Modeling Expert** for fundamental valuation that informs asset selection before portfolio construction.
- Related -> the **Statistics Expert** for hypothesis testing on alpha significance or distribution fitting.
