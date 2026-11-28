# Sector Discount-Rate Spreads

Add the live 10-Year U.S. Treasury yield (`yield_10y_pct` from `get_macro_and_fx` with `view="treasury_yields"`) to the midpoint of the sector's spread band. The sector names are the ones `get_company_snapshot` returns in `sector`.

| Sector | Spread over the 10Y Treasury | Midpoint | Notes |
| --- | --- | --- | --- |
| Information Technology | +5.5% to +7.0% | +6.25% | Wide dispersion in outcomes; semiconductors are cyclical. |
| Communication Services | +4.5% to +6.0% | +5.25% | Carriers have more debt and slower growth than media and platforms. |
| Health Care | +4.0% to +6.0% | +5.0% | A single-asset biotech needs a probability-weighted pipeline model, not this one. |
| Consumer Discretionary | +5.0% to +6.5% | +5.75% | Lease liabilities are not in the debt figure; say so for retailers. |
| Consumer Staples | +3.0% to +4.0% | +3.5% | Low cyclicality. |
| Industrials | +4.5% to +5.5% | +5.0% | Capital spending moves with the cycle; check the normal-year test carefully. |
| Energy | +5.0% to +6.5% | +5.75% | Value on mid-cycle cash flow, never a peak year. Terminal growth 2.0%. |
| Materials | +5.0% to +6.5% | +5.75% | Value on mid-cycle cash flow, never a peak year. Terminal growth 2.0%. |
| Utilities | +2.5% to +3.5% | +3.0% | Regulated spending often makes free cash flow negative; the model may not fit. Terminal growth 2.0%. |
| Real Estate | not applicable | | Do not use this model; value on `ffo_ttm` and `price_to_ffo`. |
| Financials | not applicable | | Do not use this model; use a residual income or ROE against P/B approach. |

These bands are judgement, not data: they place riskier, more cyclical sectors higher. A user who has their own discount rate should give it, and then you use theirs and say so.

## Adjustments

Apply one only when its inputs are in the responses you have. Otherwise skip it and say it was not assessed.

- **Net cash (the bridge's `cash` above its debt) with `roic_pct` above 25:** subtract 0.5 points.
- **`market_cap_b` below 2:** add 1.0 point.
- **Net debt above 3.5 times the latest fiscal-year `ebitda`:** add 1.0 point.
- **A listing outside the United States:** this table adds no country risk premium and the rate is a US dollar rate. Say so, and keep cash flows and the discount rate in one currency.
