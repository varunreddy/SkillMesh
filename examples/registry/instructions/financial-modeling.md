# Financial Modeling Expert

Use this expert for building valuation models (DCF, comparable multiples), LBO analysis, scenario and sensitivity analysis, and pro-forma financial statement construction with proper separation of assumptions, calculations, and outputs.

## When to use this expert
- The task requires intrinsic valuation of a business using discounted cash flow or relative valuation with comparable multiples.
- A leveraged buyout (LBO) model or M&A accretion/dilution analysis is needed.
- Financial projections must be built as pro-forma income statements, balance sheets, and cash flow statements.
- Sensitivity tables or scenario analysis are required to stress-test key assumptions.

## Execution behavior

1. Organize the model into clearly separated sections: assumptions/drivers at the top, calculations in the middle, and outputs/summaries at the bottom. Every hardcoded input must live in the assumptions section.
2. Build the revenue model first: define revenue drivers (volume x price, growth rate, or segment-level detail) and project them forward based on explicit assumptions with stated rationale.
3. Construct the income statement from revenue through net income, linking cost of goods sold, operating expenses, depreciation, interest, and taxes to their respective driver assumptions.
4. Build the balance sheet using working capital ratios (DSO, DIO, DPO) tied to revenue or COGS, capital expenditure schedules, and debt repayment terms.
5. Derive the cash flow statement indirectly from changes in the income statement and balance sheet, ensuring the balance sheet balances in every projected period.
6. For DCF valuation, calculate unlevered free cash flow, select an appropriate discount rate (WACC), project a terminal value using either perpetuity growth or exit multiple, and discount everything to present value.
7. Build a sensitivity table varying the two most impactful assumptions (typically WACC and terminal growth rate, or revenue growth and margin) across a reasonable range.
8. For comparable company analysis, select peers by industry, size, and growth profile, collect relevant multiples (EV/EBITDA, P/E, EV/Revenue), and apply median or mean multiples to the target.

## Decision tree
- If valuing a mature, cash-generating business -> use a DCF based on free cash flow to firm, discounted at WACC, cross-checked against comparable multiples.
- If valuing a pre-profit startup or high-growth company -> use revenue multiples from comparable transactions; DCF is unreliable when near-term cash flows are negative and terminal value dominates.
- If evaluating an acquisition -> build an accretion/dilution analysis on EPS, and for a leveraged deal, build an LBO model with debt schedules and an IRR target.
- If the model has circular references (e.g., interest expense depends on debt, which depends on cash flow, which depends on interest) -> break the circularity with an iterative solver or a prior-period approximation and document the approach.
- If presenting to stakeholders -> build base, bull, and bear scenarios with clearly labeled assumption changes, not just a single-point estimate.
- If terminal value exceeds 75% of total enterprise value -> flag this as a risk and increase scrutiny on the terminal growth rate and exit multiple assumptions.

## Anti-patterns
- NEVER hardcode assumptions inside formula cells. Every input that could change must be a named driver in the assumptions section so it can be varied in sensitivity analysis.
- NEVER build a model without a scenario framework. A single-point estimate hides the uncertainty range and gives false precision.
- NEVER ignore terminal value sensitivity. Small changes in the perpetuity growth rate or exit multiple can swing the valuation by 30% or more.
- NEVER create uncontrolled circular references. They cause spreadsheet instability and make auditing impossible. Use explicit iteration with convergence checks.
- NEVER mix real and nominal cash flows. If projections are in nominal terms, the discount rate must also be nominal, and vice versa.
- NEVER omit the bridge from enterprise value to equity value. Subtract net debt, minority interests, and preferred stock to arrive at equity value per share.

## Common mistakes
- Using EBITDA as a proxy for cash flow without adjusting for capital expenditures, working capital changes, and taxes.
- Applying a terminal growth rate above the long-term GDP growth rate, which implies the company eventually becomes larger than the economy.
- Selecting comparable companies based on industry alone without controlling for growth rate, margin profile, and geographic mix.
- Forgetting to discount the terminal value back to the present. The terminal value is at the end of the explicit forecast period, not at time zero.
- Using the cost of equity (CAPM) to discount free cash flow to the firm. FCFF must be discounted at WACC; only FCFE uses cost of equity.
- Building a balance sheet that does not balance, indicating a missing plug or an error in the cash flow linkage.

## Output contract
- Present a clear assumptions summary with every driver labeled, its value, and its basis (historical average, management guidance, or analyst estimate).
- Include a DCF valuation bridge: projected UFCF by year, terminal value, discount factors, and the resulting enterprise value.
- Provide a comparable multiples table with peer names, relevant multiples, and the implied valuation range.
- Deliver a two-variable sensitivity table for the DCF showing how valuation changes across the two key assumptions.
- Include base, bull, and bear scenario summaries with the assumption changes and resulting valuations.
- Report equity value per share after the enterprise-to-equity bridge, with the share count basis stated.
- All projected financial statements (income statement, balance sheet, cash flow) must be internally consistent and the balance sheet must balance.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to normalize historical financial data from filings or data providers.
- Before this expert -> use the **SQL Queries Expert** to extract historical financials from a database before building projections.
- After this expert -> use the **Visualization Expert** to produce valuation football fields, sensitivity heat maps, and scenario comparison charts.
- Related -> the **Quantitative Finance Expert** for market-based risk metrics and portfolio-level analysis that complements fundamental valuation.
- Related -> the **Statistics Expert** for regression analysis on revenue drivers or cost structure trends.
