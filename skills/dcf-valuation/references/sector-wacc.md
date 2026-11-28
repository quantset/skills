# Sector Discount-Rate Spreads

Add the live 10-Year U.S. Treasury yield (`yield_10y_pct` from `get_macro_and_fx` with `view="treasury_yields"`) to the midpoint of the sector's spread band. The sector names are the ones `get_company_snapshot` returns in `sector`.

| Sector | Spread over the 10Y Treasury | Midpoint | Notes |
| --- | --- | --- | --- |
| Information Technology | +4.0% to +5.5% | +4.75% | Mature software/cloud platforms sit at the low end; cyclical hardware/semiconductors higher. |
| Communication Services | +3.75% to +5.0% | +4.35% | Carriers have more debt and slower growth than media and platforms. |
| Health Care | +3.5% to +5.0% | +4.25% | A single-asset biotech needs a probability-weighted pipeline model, not this one. |
| Consumer Discretionary | +4.25% to +5.5% | +4.85% | Lease liabilities are not in the debt figure; say so for retailers. |
| Consumer Staples | +2.75% to +3.75% | +3.25% | Low cyclicality. |
| Industrials | +3.75% to +4.75% | +4.25% | Capital spending moves with the cycle; check the normal-year test carefully. |
| Energy | +4.25% to +5.5% | +4.85% | Value on mid-cycle cash flow, never a peak year. Terminal growth 2.0%. |
| Materials | +4.25% to +5.5% | +4.85% | Value on mid-cycle cash flow, never a peak year. Terminal growth 2.0%. |
| Utilities | +2.25% to +3.25% | +2.75% | Regulated spending often makes free cash flow negative; the model may not fit. Terminal growth 2.0%. |
| Real Estate | not applicable | | Do not use this model; value on `ffo_ttm` and `price_to_ffo`. |
| Financials | not applicable | | Do not use this model; use a residual income or ROE against P/B approach. |

These bands are judgement, not data: they approximate institutional equity risk premia by sector cyclicality. A user who gives their own discount rate overrides this table, and you state theirs.

## Adjustments

Apply every adjustment whose inputs are in the responses you have; skip any whose inputs are missing.

- **Mega-cap balance-sheet strength (`market_cap_b` ≥ 200 and net debt below 1.5× EBITDA):** subtract 0.5 points (gives ~8.5%–9.0% WACC for quality mega-cap compounders).
- **High-return net cash (`cash` above debt and `roic_pct` above 25):** subtract 0.25 points.
- **Small-cap risk (`market_cap_b` below 2):** add 1.0 point.
- **High leverage (net debt above 3.5× latest fiscal-year `ebitda`):** add 1.0 point.
- **Listing outside the United States:** this table adds no country risk premium and the rate is a US dollar rate. Say so, and keep cash flows and the discount rate in one currency.
