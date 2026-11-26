# Sector Cost of Capital (WACC) Anchors

Use the live 10-Year U.S. Treasury yield (`y10` from QuantSet `get_macro_and_fx` / `/api/v1/macro/treasury-yields`) as the risk-free rate $R_f$, then add the sector spread below as your baseline equity/unlevered cost of capital before company-specific adjustments.

| Canonical QuantSet Sector | Typical Beta ($\beta$) | Spread over 10Y Treasury | Typical USD WACC Range (at 4.0–4.5% 10Y) | Notes |
| --- | --- | --- | --- | --- |
| Technology / Software / Semis | 1.15 – 1.45 | +5.5% to +7.0% | 9.5% – 11.5% | Semis & pre-profit SaaS sit at top of band; mega-cap net-cash platforms sit at 8.8%–9.8%. |
| Communication Services | 1.00 – 1.25 | +4.5% to +6.0% | 8.5% – 10.5% | Telecom carriers carry higher debt weight (lower WACC, lower terminal growth 1.0–1.5%). |
| Healthcare & Biopharma | 0.85 – 1.20 | +4.0% to +6.0% | 8.0% – 10.5% | Diversified pharma/medtech 8.0–9.0%; single-asset biotech requires probability-weighted pipeline DCF. |
| Consumer Cyclical / Retail | 1.05 – 1.35 | +5.0% to +6.5% | 9.0% – 11.0% | Account for operating lease liabilities in Enterprise Value bridge. |
| Consumer Defensive / Staples | 0.60 – 0.80 | +3.0% to +4.0% | 7.0% – 8.2% | Low cyclicality; cap terminal growth at 2.0–2.5%. |
| Industrials & Aerospace | 0.95 – 1.20 | +4.5% to +5.5% | 8.5% – 9.8% | Normalize CapEx across full cycle rather than extrapolating peak/trough year. |
| Energy & Materials | 1.05 – 1.35 | +5.0% to +6.5% | 9.0% – 11.0% | Use mid-cycle commodity FCF, never peak-cycle FCF; terminal growth 0.5–1.5%. |
| Utilities | 0.50 – 0.70 | +2.5% to +3.5% | 6.5% – 7.8% | Regulated rate-base CapEx often makes near-term FCF negative; cross-check DDM / EV/EBITDA. |
| Real Estate (REITs) | 0.75 – 1.00 | +3.5% to +5.0% | 7.5% – 9.2% | Do **not** use standard GAAP FCF; use `ffo_ttm` / `price_to_ffo` from QuantSet `get_company_snapshot`. |
| Financials (Banks & Insurers) | 0.90 – 1.20 | Cost of Equity ($K_e$) | $K_e$: 9.0% – 11.5% | Debt is raw material, not capital structure—value via Excess Return / ROE-P/B model instead of EV/FCF DCF. |

## Company-Specific Adjustments (bps)
- **Net cash > 10% of market cap & ROIC > 25%:** `-50 bps`
- **Small-cap (< $2B market cap) or single-customer concentration > 25%:** `+100 to +150 bps`
- **Net Debt / EBITDA > 3.5x:** `+75 to +150 bps`
- **Non-US emerging market listing (`global:`):** Add sovereign spread over U.S. 10Y Treasury and match currency of cash flows to currency of discount rate.
