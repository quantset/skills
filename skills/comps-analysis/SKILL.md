---
name: comps-analysis
description: "Builds a comparable companies (trading comps) table with EV/Revenue, EV/EBIT, EV/EBITDA, EV/FCF, trailing and forward P/E, growth, FCF margin and ROIC, leading with peer-percentile positioning (25th/median/75th) and why the target trades at a premium or discount. Use when the user asks how a company compares with its peers, for trading multiples, relative valuation or a peer table. Covers 52,000+ stocks in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📊","os":["darwin","linux","win32"]}}
---

# Comparable Companies ("Trading Comps") Skill (Powered by QuantSet)

Compare a company against 5–8 real peers on matched-period valuation multiples, growth, margins, and returns on capital.

## Data Rules

- Statement figures sit under `values`; `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- Drop `form` `10-Q` rows from `period="annual"` to keep true fiscal years. Use quarterly rows only when `period_basis` is `discrete_quarter`.
- In `get_company_snapshot`, `revenue_ttm` and `operating_income_ttm` are trailing when `fundamentals_basis == "ttm"`, while `ebitda_ttm` and `free_cash_flow` can repeat the last fiscal year—take EBITDA and FCF from the fiscal-year statement row and label its `period_end`.
- `price`, `market_cap_b` and `enterprise_value_b` are USD; convert non-USD statements via `usd_rate` before computing EV multiples.
- Show `null` as `n/a` and non-positive multiples as `N/M` (neither enters benchmarks). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Step 1: Select Peers & Pull Batch Statements

Pass `workflow="comps-analysis"` on every call (REST: `X-Workflow-Id: comps-analysis`).

1. `get_company_snapshot(ticker="us:AMD")` and `get_peers(ticker="us:AMD", limit=12)` → `instrument_id`, `name`, `group_basis`, `peer_group`, `sic_code`, `sic_description`, `market_cap_b`, `rev_growth_yoy_pct`, `net_margin_pct`
   - Keep 5–8 peers: drop `market_cap_b < 1` or `null`, prefer matching `sic_code`, then largest `market_cap_b`. State any dropped peers. For `Financials`, compare on P/E only (EV does not apply).
2. Pull `get_company_snapshot(ticker="us:AMD")` for each kept peer → `price`, `latest_date`, `market_cap_b`, `enterprise_value_b`, `total_debt`, `cash`, `revenue_ttm`, `operating_income_ttm`, `fundamentals_basis`, `fundamentals_as_of`, `pe_ttm`, `forward_eps`, `rev_growth_yoy_pct`, `roic_pct`, `share_count_change_1y_pct`, `sector`, `sic_code`, `quote_currency`, `financial_currency`
3. `get_financial_statements(tickers=["us:AMD", "us:NVDA", "us:AVGO"], kind="income", period="annual", limit_per_instrument=5)` → `instrument_id`, `period_end`, `form`, `currency`, `revenue`, `ebitda`, `weighted_average_diluted_shares`
4. `get_financial_statements(tickers=["us:AMD", "us:NVDA", "us:AVGO"], kind="cash_flow", period="annual", limit_per_instrument=5)` → `instrument_id`, `period_end`, `form`, `free_cash_flow`
5. `get_financial_statements(tickers=["us:AMD", "us:NVDA", "us:AVGO"], kind="balance_sheet", period="quarterly", limit_per_instrument=3)` → `instrument_id`, `period_end`, `accession`, `long_term_debt`, `current_portion_long_term_debt`, `notes_payable`, `convertible_debt`
   - When snapshot `total_debt` is `null`, take the newest balance-sheet row with an `accession` or non-null debt line (skipping empty month-end stubs; check `period="annual"` if needed).

## Step 2: Run `scripts/comps_stats.py`

Run `python scripts/comps_stats.py comps.json` ([scripts/comps_stats.py](scripts/comps_stats.py) computes debt bridges, EV, trailing EV/Rev & EV/EBIT, fiscal-year EV/EBITDA & EV/FCF, trailing & forward P/E, 25th/median/75th peer quantiles, stale-FY flags, and mechanical peer-multiple translations). If you cannot run Python, apply the script's exact formulas by hand.

## Conclusion & Worked Example

Answer the user's question in the first sentence by stating where the target sits against peer quartiles on multiples versus growth, margins, and ROIC—inspecting the numbers to see what explains any premium or discount—followed by the peer & benchmark table, optional illustrative multiple range, and a compact `## Sources (Required)` table (`Data: QuantSet (https://quantset.dev), retrieved [date]`). *(Not investment advice.)*

> **Worked opening (`us:AMD` vs. 7 semiconductor peers):**
> At **$406.03** (`$663B` market cap), AMD trades **above the peer 75th percentile** on Forward P/E (**24.8x** vs. peer median **18.4x**) and trailing EV/Revenue (**14.7x** vs. **11.2x**), while its YoY revenue growth (**31.2%**) ranks in the top quartile behind only NVDA and MU, and its FY25 FCF margin (**19.4%**) sits below the **28.1%** peer median.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that column `n/a`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
