---
name: comps-analysis
description: Ask "How does NVDA stack up against peers?" to build a Comparable Companies ("Trading Comps") valuation table across 52,000+ US and global stocks in 67 countries with 25th/Median/75th percentile multiples (EV/Revenue, EV/EBITDA, EV/FCF, Forward P/E, ROIC, FCF margin) and an implied share price range. Free to try with mw_demo.
metadata: {"clawdbot":{"emoji":"📊","os":["darwin","linux","win32"]}}
---

# Comparable Companies ("Trading Comps") Skill (Powered by QuantSet)

Construct an investment-banking-grade peer valuation table grounded in consistent Enterprise Value, TTM discrete cash flows, and forward consensus estimates.

## Workflow

Each call is written exactly as the QuantSet MCP tool accepts it; swap the sample ticker for the user's listing. Pass `workflow="comps-analysis"` on MCP tool calls (or `X-Workflow-Id: comps-analysis` on REST requests) so multi-peer queries group together in usage reports. The fields after each arrow are the ones this skill reads. On statement rows the line items sit under `values` (for example `values.revenue`); dates, `period_basis` and `accession` sit on the row itself.

1. **Identify 5–8 True Economic Peers:**
   - `get_peers(ticker="us:NVDA", limit=12)` → `instrument_id`, `name`, `peer_group`, `group_basis`, `industry`, `market_cap_b`, `rev_growth_yoy_pct`, `net_margin_pct`, `roic_pct`, `pe_ttm`, `pe_forward`, `fcf_yield_pct`
   - The list is QuantSet's sector or 4-digit SIC group ordered by market cap; `group_basis` says which. Filter out conglomerates or mismatched business models so the peer set shares comparable margin structure and revenue model. Keep 5–8 and say which you dropped and why.
2. **Pull Standardized Multiples & Operating Metrics in Parallel (one call per company, target included):**
   - `get_company_snapshot(ticker="us:NVDA")` → `price`, `market_cap_b`, `enterprise_value_b`, `revenue_ttm`, `ebitda_ttm`, `free_cash_flow`, `ev_to_ebitda`, `ev_to_fcf`, `pe_ttm`, `pe_forward`, `forward_eps`, `rev_growth_yoy_pct`, `fcf_margin_pct`, `roic_pct`, `share_count_change_1y_pct`, `total_debt`, `cash`, `financial_currency`, `fundamentals_as_of`, `valuation_eligible`
   - `EV / TTM Revenue = enterprise_value_b × 1e9 / revenue_ttm` (the `_b` fields are in billions; `revenue_ttm` is in units of `financial_currency`). Compute it only when both sides are in the same currency.
   - Skip a company whose `valuation_eligible` is `false`, and say so.
3. **Diluted Shares for the Target:** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=1)` → `weighted_average_diluted_shares`, `period_end`, `available_at`
4. **Compute Statistical Benchmarks (Excluding Target):**
   - Calculate **25th Percentile**, **Median**, **Mean**, and **75th Percentile** across the peer group (excluding the target itself, and leaving negative/meaningless multiples as `N/M` rather than distorting averages).
5. **Derive Implied Football-Field Share Price Range:**
   - Apply the peer **25th–75th percentile** `EV/EBITDA`, `EV/FCF`, and `Forward P/E` multiples to the target's `ebitda_ttm`, `free_cash_flow` and `forward_eps`, bridge from Implied Enterprise Value (`Implied EV - Net Debt`, where `Net Debt = total_debt - cash`) to Equity Value, and divide by diluted shares.
   - Explain *why* the target deserves a premium or discount to the peer median (e.g., higher `ROIC`, faster organic growth, or cleaner SBC-adjusted FCF).

## Output Format

1. **Peer Table** (target first, then peers by market cap):

| Company | Mkt Cap ($B) | EV ($B) | EV / Revenue | EV / EBITDA | EV / FCF | P/E (TTM) | Fwd P/E | Rev Growth YoY | FCF Margin | ROIC | 1Y Share Chg | As of |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

2. **Benchmarks:** 25th / Median / Mean / 75th rows under the table, peers only.
3. **Implied Share Price Range:** one row per multiple (low, median, high) beside the current `price`.
4. **Premium or Discount:** two or three sentences with the numbers that justify it. *(Not investment advice.)*
5. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per company: the calls used, the snapshot date (`fundamentals_as_of`), and for the target the filing behind the share count (`period_end`, `available_at`).
- A figure that is not in a QuantSet response is **computed** (show the formula). Never fill a gap from memory or a web search; write `N/M` or `not available`.
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): write `not available` for that column, name the call, and keep going. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
