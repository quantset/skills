---
name: tear-sheet
description: "Builds a printable HTML company tear sheet: 5-year financial summary, valuation against peers, Street estimates, revenue segments, balance sheet, top holders and insider trades, every figure dated and sourced. Use when the user asks for a tear sheet, one-pager, company profile, fact sheet, snapshot or overview of a public company. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🗂️","os":["darwin","linux","win32"]}}
---

# Company Tear Sheet Skill (Powered by QuantSet)

Render a sourced, fact-only 1-page HTML company profile (`tearsheets/[SYMBOL]_[YYYY-MM-DD].html`) from [references/tear-sheet-template.html](references/tear-sheet-template.html)—no rating and no price target.

## Data Rules

- Statement figures sit under `values`; `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- Drop `form` `10-Q` rows from `period="annual"` to isolate fiscal years.
- `price`, `market_cap_b` and `enterprise_value_b` are USD; for non-US listings show `native_close` in `quote_currency` and note USD market cap/EV. `dividend_basis == "no_recorded_dividends"` displays `"none recorded"`.
- Show `null` as `n/a` (never `0` or memory). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Step 1: Parallel Evidence Gathering

Pass `workflow="tear-sheet"` on every call. If given a company name, resolve via `list_instruments(q="apple", limit=5)` → `instrument_id`, `name`, `exchange`, `country`, `asset_type` (pick the company's equity listing, preferring `us:` when available).

1. `get_company_snapshot(ticker="us:AAPL")` → `name`, `symbol`, `exchange`, `country`, `sector`, `industry`, `sic_description`, `employees`, `latest_date`, `price`, `native_close`, `quote_currency`, `financial_currency`, `market_cap_b`, `enterprise_value_b`, `high_52w`, `low_52w`, `change_1y_pct`, `beta`, `pe_ttm`, `forward_eps`, `current_fy_estimate_as_of`, `sic_code`, `fcf_yield_pct`, `dividend_yield_pct`, `annual_dividend`, `dividend_basis`, `roic_pct`, `roe_pct`, `total_debt`, `cash`, `share_count_change_1y_pct`, `fundamentals_as_of`, `balance_sheet_as_of`
2. `get_financial_statements(tickers=["us:AAPL"], kind="income", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `currency`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `ebitda`, `reported_diluted_eps`, `available_at`, `accession`
3. `get_financial_statements(tickers=["us:AAPL"], kind="cash_flow", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `operating_cash_flow`, `free_cash_flow` (keep 6 newest fiscal years so 5 years have YoY growth).
4. `get_estimates_and_earnings(view="estimates", ticker="us:AAPL", metric="revenue")` and `get_estimates_and_earnings(view="estimates", ticker="us:AAPL", metric="eps")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
5. `get_estimates_and_earnings(view="calendar", ticker="us:AAPL", start="2026-01-15", limit=4)` → `date`, `timing`, and `get_estimates_and_earnings(view="consensus", ticker="us:AAPL")` → `next_earnings_date`, `target_mean_price`, `shares_short`, `short_pct_of_float`, `held_pct_insiders`, `held_pct_institutions`, `observed_on`
6. `get_peers(ticker="us:AAPL", limit=12)` → `instrument_id`, `name`, `group_basis`, `peer_group`, `sic_code`, `market_cap_b`, `pe_ttm`, `fcf_yield_pct`, `dividend_yield_pct` (drop `market_cap_b < 1`; prefer matching `sic_code` if ≥3 peers).
7. `get_sec_filings(view="segments", ticker="us:AAPL", limit=60)` → `segment`, `period`, `flow`, `revenue` (latest `flow == "Y"` rows).
8. `get_sec_filings(view="debt_maturities", ticker="us:AAPL", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
   - Note if the schedule sum differs from snapshot `total_debt` by >20%.
9. `get_sec_filings(view="institutional_ownership", ticker="us:AAPL", limit=15)` → `holder`, `report_date`, `shares`, `market_value_usd`, `pct`, `put_call`, `shares_change_qoq_pct`, `filing_date` (top 5 non-option holders; never call `portfolio_weight_pct` ownership of the company).
10. `get_sec_filings(view="insider_transactions", ticker="us:AAPL", start="2025-01-15", transaction_code="P,S", limit=400)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `shares`, `transaction_value`, `filing_date` (count distinct open-market sale/buy dates, shares, and value split by `is_10b5_1`; follow `next_cursor` once if truncated).

## Deliverable, Conclusion & Worked Example

Fill every `{{slot}}` in [references/tear-sheet-template.html](references/tear-sheet-template.html) (numeric cells with `class="num"`, full call provenance in `{{sources}}`), save `./tearsheets/[SYMBOL]_[YYYY-MM-DD].html`, and reply in chat in 3–4 sentences summarizing the key profile figures + file path.

> **Worked chat reply (`us:AAPL`):**
> Saved `./tearsheets/AAPL_2026-11-28.html`. Apple (`$3.46T` market cap at **$228.50**) generated **$416.2B** FY26 revenue (+6.4% YoY, 46.9% gross margin) and **$108.8B** free cash flow (`3.1%` FCF yield vs. peer median `2.4%`), with Services reaching 25.8% of sales, `$19.9B` of debt due over FY27–FY28 against `$29.9B` cash, and net share count down **-2.6%** YoY.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that section `n/a`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
