---
name: earnings-playbook
description: "Prepares a pre-earnings setup or a post-earnings beat/miss note: the consensus revenue and EPS bar, 8-quarter surprise history, positioning, segment and margin swing factors and a bull/base/bear reaction matrix, saved as a note plus a per-company workbook that grows each quarter. Use when the user asks for an earnings preview, what to watch into a report, how a company did this quarter, or a beat/miss summary. Covers 36,000+ companies. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📅","os":["darwin","linux","win32"]}}
---

# Earnings Preview & Post-Earnings Update Skill (Powered by QuantSet)

Build a **Pre-Earnings Setup** (consensus bar, 8-quarter surprise distribution, options-implied move, positioning, segment swing factors) or a **Post-Earnings Flash Update** (beat/miss table, earnings quality, thesis impact), saved as a Markdown note plus a reusable `.xlsx` workbook ([references/workbook.md](references/workbook.md)).

## Data Rules

- Statement figures sit under `values`; `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- Compare quarterly statement rows only when `period_basis` is `discrete_quarter` (or YTD against the same YTD point a year earlier); deduplicate by `period_end` year-month, preferring rows with an `accession`.
- `estimates` returns 4 rows (this/next quarter, this/next FY) in reporting currency; `earnings` surprise history is Street EPS (use median absolute `surprise_pct` so near-zero denominators do not skew averages).
- Show `null` as `n/a` (never `0` or memory). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Mode A: Pre-Earnings Setup ("What's the Bar?")

Pass `workflow="earnings-playbook"` on every call (`get_estimates_and_earnings` takes one `view` per call).

1. **Date & Bar:**
   - `get_estimates_and_earnings(view="calendar", ticker="us:NVDA", start="2026-01-15", limit=4)` → `date`, `timing` (fallback to `next_earnings_date` in `consensus`; never guess if unlisted).
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="eps")` and `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `high`, `low`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="consensus", ticker="us:NVDA")` → `current_price`, `target_low_price`, `target_mean_price`, `target_high_price`, `strong_buy`, `buy`, `hold`, `sell`, `strong_sell`, `next_earnings_date`, `shares_short`, `short_pct_of_float`, `observed_on`
   - `get_estimates_and_earnings(view="analyst_ratings", ticker="us:NVDA", limit=4)` → `date`, `rank`, `vgm_grade`
   - `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct`
2. **Positioning & Implied Move:**
   - `get_price_history(ticker="us:NVDA", limit=91)` and `get_price_history(ticker="index:SPX", limit=91)` → `date`, `close` (compute 30- and 90-session returns).
   - `get_market_activity(view="options", ticker="us:NVDA")` → `expiration_dates`, then `get_market_activity(view="options", ticker="us:NVDA", expiration="2026-01-30")` → `implied_move_pct`, `atm_implied_volatility_pct`, `put_call_open_interest_ratio`, `underlying_price` (pick first expiration after report; if >14 days out, label as "move priced to [date]").
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-10-15", transaction_code="P,S", limit=250)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `shares`, `transaction_value`, `filing_date` (90-day window).
   - `get_etf_data(ticker="us:NVDA", view="exposures", limit=60)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`
3. **Swing Factors & Reaction Band:**
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=100)` → `segment`, `period`, `flow`, `revenue` (`Q` = quarter, `Y` = FY; derive Q4 as `Y - Q1 - Q2 - Q3` when all 3 quarters exist).
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=14)` → `period_end`, `period_basis`, `revenue`, `cost_of_revenue`, `gross_profit`, `operating_income`, `net_income`, `reported_diluted_eps`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="quarterly", limit_per_instrument=14)` → `period_end`, `period_basis`, `operating_cash_flow`, `free_cash_flow`
   - Center the **Bull / Base / Bear** band on EPS `consensus` ± the 8-quarter median absolute `surprise_pct`, pairing each case with revenue guide and top margin/segment swing drivers.

## Mode B: Post-Earnings Update ("What Changed?")

Pull Mode A steps 1 and 3 for the reported quarter, `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `pe_ttm`, `forward_eps`, and the pre-print bar via `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue", as_of="2026-01-14")` + `metric="eps"` (`as_of` = day before report). Check whether any EPS beat came from operating margins vs. tax rate, share count, or working capital.

## Deliverable, Conclusion & Worked Example

Save `earnings/[SYMBOL]_[YYYY-MM]_[preview|update].md` and update `earnings/[SYMBOL]_earnings.xlsx` per [references/workbook.md](references/workbook.md) (or print CSV blocks if file writes are unavailable). Answer in the first sentence with the consensus bar (or beat/miss), the options-implied move vs. recent run-up, and the #1 swing line, ending with `## Sources (Required)` (`Data: QuantSet (https://quantset.dev), retrieved [date]`). *(Not investment advice.)*

> **Worked opening (`us:NVDA` Q4 preview):**
> Going into its Feb 25 AMC report at **$149.30** (+11.4% over 30 sessions vs. +2.1% for `SPX`), NVIDIA faces a Street bar of **$131.2B revenue** and **$0.89 EPS** (`38` analysts), with options pricing a **±7.4%** move through Feb 27 against an **8-for-8** EPS beat streak (median surprise **+6.2%**) and Data Center YoY growth deceleration as the swing variable.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that item `n/a`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
