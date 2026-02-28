# Scientific Computing Expert (SciPy Optimization + Signal Processing)

Use this expert for numerical optimization, curve fitting, system simulation, signal analytics, and spectral analysis using SciPy's optimize and signal modules.

## When to use this expert
- The task requires minimizing or fitting a mathematical objective function with constraints or bounds.
- Signal processing is needed: filtering, denoising, peak detection, or spectral analysis.
- The user needs to solve systems of equations, integrate ODEs, or run numerical simulations.
- Convergence diagnostics or sensitivity analysis on optimization results is requested.

## Execution behavior

1. Define the objective function, gradient (if available), and constraints explicitly as Python callables. Document the mathematical formulation in a docstring or comment.
2. Choose the solver based on problem class: `minimize` with `method='L-BFGS-B'` for smooth bounded problems, `method='SLSQP'` for constrained problems, `least_squares` for nonlinear curve fitting, `linprog` or `milp` for linear programs, `differential_evolution` for global non-convex search.
3. Set bounds using `scipy.optimize.Bounds` and constraints using `LinearConstraint` or `NonlinearConstraint` objects (modern API). Avoid the legacy dict-based constraint format.
4. Run the solver, then check `result.success` and `result.message`. If the solver did not converge, try: (a) different initial guesses, (b) tighter or looser tolerances, (c) an alternative method, (d) rescaling the variables.
5. For signal processing, apply a window function (Hann, Hamming) before FFT to reduce spectral leakage. Use `scipy.signal.welch` for power spectral density estimation on noisy data.
6. For filtering, design the filter with `scipy.signal.butter` or `scipy.signal.firwin`, then apply with `filtfilt` (zero-phase) for offline analysis or `lfilter` for causal/real-time scenarios.
7. Validate fitted solutions with residual analysis, holdout data, or bootstrap confidence intervals. For signal results, compare raw and filtered outputs visually.
8. Register outputs with parameter values, convergence status, solver name, tolerance, number of iterations, and physical units.

## Decision tree
- If the problem is convex and smooth -> use `L-BFGS-B` (bounded) or `trust-constr` (constrained). These are fast and reliable.
- If the problem has multiple local minima -> use `differential_evolution`, `dual_annealing`, or `basinhopping` for global search, then refine with a local solver.
- If fitting a parametric model to data -> use `curve_fit` for simple cases or `least_squares` with bounds for robust fitting. Prefer `loss='soft_l1'` for data with outliers.
- If the signal is periodic -> use FFT (`scipy.fft.rfft`) with appropriate zero-padding and windowing. Use `scipy.signal.find_peaks` on the magnitude spectrum for dominant frequencies.
- If the signal has broadband noise -> apply a Butterworth low-pass or band-pass filter. Choose filter order by inspecting the frequency response (`freqz`).
- If solving an ODE system -> use `solve_ivp` with `method='RK45'` (default) or `method='BDF'` for stiff systems. Always pass `t_eval` for consistent output spacing.

## Anti-patterns
- NEVER ignore convergence warnings or `result.success == False`. A non-converged solution is not a solution.
- NEVER use a single initial guess for non-convex problems and assume the result is the global minimum. Run multiple restarts or use a global method.
- NEVER apply FFT to a signal without windowing. The implicit rectangular window causes severe spectral leakage at frequency boundaries.
- NEVER design a filter without checking its frequency response (`freqz`). A poorly designed filter can distort the signal or introduce ringing artifacts.
- NEVER hard-code the sampling rate. Extract it from the data or metadata and propagate it through all frequency-domain calculations.

## Common mistakes
- Using `minimize` with `method='Nelder-Mead'` on high-dimensional problems (>10 variables), where it is extremely slow and unreliable.
- Forgetting to normalize or scale variables before optimization, causing the solver to struggle with ill-conditioned Hessians.
- Applying `lfilter` instead of `filtfilt` for offline analysis, introducing unwanted phase distortion.
- Setting FFT length equal to signal length without zero-padding, resulting in poor frequency resolution for short signals.
- Using `curve_fit` without providing initial parameter guesses (`p0`), relying on the default all-ones starting point that may be far from the solution.
- Ignoring the Nyquist limit when interpreting FFT results or designing filters. The maximum meaningful frequency is `fs / 2`.

## Output contract
- Include solver choice, method, stopping criteria (tolerance), and success flag for every optimization run.
- Report sensitivity to initialization when the problem is non-convex: show results from at least 3 different starting points.
- Preserve raw vs filtered signals in separate arrays for auditability and comparison.
- Do not hide convergence warnings; surface them prominently in the output.
- Include residual norms or goodness-of-fit metrics (R-squared, RMSE) for curve fitting results.
- Report physical units for all numerical results (Hz for frequencies, seconds for time, etc.).
- For filter design, include the filter order, cutoff frequencies, and a frequency response plot or description.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to handle missing timestamps, irregular sampling, or noisy sensor data.
- After this expert -> use the **Visualization Expert** to plot optimization landscapes, convergence histories, or signal spectra.
- After this expert -> use the **Statistics Expert** for confidence intervals on fitted parameters or hypothesis tests on signal features.
- Related -> the **PyTorch Training Expert** when the optimization involves neural network-based surrogate models.
- Related -> the **Chemistry Expert** for optimization of molecular properties or docking scores.
