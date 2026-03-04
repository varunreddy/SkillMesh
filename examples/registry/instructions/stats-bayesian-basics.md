# Bayesian Statistics Expert

Use this expert for priors, posteriors, credible intervals, and probabilistic updating workflows.

## When to use this expert
- You are estimating probabilities dynamically as small amounts of continuous data arrive.
- You want to incorporate expert domain knowledge (priors) into your final quantitative estimates.
- You need to report intuitive "credible intervals" instead of rigid frequentist p-values.
- You are constructing hierarchical models pulling group behavior to a global mean via partial pooling.

## Execution behavior
1. Map out the explicit generative probabilistic parameters defining the modeled process.
2. Select appropriate uninformative or highly-informed prior distributions based on available consensus.
3. Establish the likelihood function describing exactly how the data is generated given the parameters.
4. Calculate or simulate the posterior distributions linking the prior and data via Bayes' Theorem.
5. Use MCMC or variational inference methods for solving computationally expensive integrals.
6. Extract robust Highest Density Intervals (HDIs) demonstrating where parameter certainty lies.
7. Perform strictly documented posterior predictive checks simulating data from the modeled distribution.
8. Update the model continuously over time by converting the initial posterior efficiently into the subsequent prior.

## Decision tree
- If you have strong historical baseline data, choose a highly informative targeted prior distribution.
- If you are trying to minimize the impact of the prior entirely, choose an objective uniform prior.
- If modeling categorical event outcomes like CTR, choose to build conjugate Beta/Binomial models.
- If the likelihood function is exceedingly complicated lacking a closed form solution, choose MCMC (PyMC/Stan) solvers.
- If estimating parameters spread across multiple distinct but related clusters, choose hierarchical partial pooling.
- If speed is overwhelmingly more important than precise covariance understanding, choose variational inference wrappers.

## Anti-patterns
- NEVER conceal the explicit prior distributions selected when reporting the final posterior variance.
- NEVER equate a Bayesian 95% Credible Interval directly mathematically to a Frequentist 95% Confidence Interval.
- NEVER ignore catastrophic multi-chain MCMC convergence failures assuming the initial trace is valid.
- NEVER update a posterior with the exact same dataset twice, artificially boosting the confidence bounds.
- NEVER apply complex unidentifiable hierarchical layers without massive penalizing regularization priors.
- NEVER ship a complex MCMC model directly into real-time production inference loops expecting microsecond latency.

## Common mistakes
- Selecting overly narrow, dogmatic priors that overpower the incoming data completely despite massive contradictory evidence.
- Misinterpreting the HDI bounds as guaranteed strict frequentist thresholds rather than probability mass distributions.
- Failing to run multiple distinct initialization chains leaving the model stuck inside local probability wells.
- Skipping predictive posterior checks, leading to models that confidently synthesize entirely impossible logical values.
- Applying Bayesian approaches to basic deterministic logic failing to utilize the probabilistic variance.
- Not standardizing inputs before modeling causing wildly inefficient MCMC numerical exploration constraints.

## Output contract
- Explicit structural definitions mapping the generative model likelihood and priors.
- Trace convergence diagnostics (R-hat, Effective Sample Size) output validation.
- Highest Density Interval (HDI) summaries defining parameter certainty bounds.
- Predictive posterior simulation output graph validating theoretical vs observed alignment.
- Source code configurations explicitly targeting PyMC/Stan or conjugate distributions natively.
- Domain narrative translating probabilistic outcomes into actionable human assumptions.

## Composability hints
- Compare variance metrics directly against frequentist counterparts natively via `stats.hypothesis-testing`.
- Leverage continuous model testing pipelines supported by automated workflows via `data.orchestration-workflows`.
- Render the probabilistic trace density overlaps visually consulting plotting directives inside `viz.distribution-diagnostics`.
- Build the initial sample extraction logic for Bayesian A/B testing utilizing techniques generated natively by `stats.experiment-design`.\n