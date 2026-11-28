---
name: investment-memo
description: "Writes a printable HTML long or short equity memo with a variant view against consensus, bear, base and bull scenarios built from the Street's own estimate range, an asymmetry check, falsifiable tripwires and filing citations. Use when the user asks for an investment memo, stock pitch, long or short thesis, or bull and bear case on a company. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📄","os":["darwin","linux","win32"]}}
---

# Buyside Investment Memo Skill (Powered by QuantSet)

Render a falsifiable 1-page HTML equity memo (`memos/[SYMBOL]_[LONG|SHORT]_[YYYY-MM-DD].html`) using [references/memo-template.html](references/memo-template.html), anchored to the Street's estimate dispersion and filed statements.

## Data Rules

- Statement figures sit under `values`; `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- Drop `form` `10-Q` rows from `period="annual"` to isolate fiscal years. Compare `discrete_quarter` rows only with single quarters.
- Work in the listing's own currency (`native_close` in `quote_currency`; statements and estimates in `financial_currency`; convert via `usd_rate` if mismatched).
- Show `null` as `n/a` (never `0` or memory). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Step 1: Frame & Gather Evidence in Parallel

Pass `workflow="investment-memo"` on every call. Default direction is `LONG` (12-month horizon) unless the user asked for a short pitch; state which reading you took. Resolve names via `list_instruments(q="toyota", limit=5)` → `instrument_id`, `name`, `exchange`, `asset_type`.

1. **Snapshot & peers:** `get_company_snapshot(ticker="us:NVDA")` → `name`, `symbol`, `sector`, `latest_date`, `price`, `native_close`, `quote_currency`, `financial_currency`, `usd_rate`, `market_cap_b`, `enterprise_value_b`, `pe_ttm`, `forward_eps`, `roic_pct`, `fcf_yield_pct`, `rev_growth_yoy_pct`, `change_6m_pct`, `change_1y_pct`, `total_debt`, `cash`, `share_count_change_1y_pct`, `fundamentals_as_of`; plus `get_peers(ticker="us:NVDA", limit=8)` → `instrument_id`, `name`, `group_basis`, `market_cap_b`, `rev_growth_yoy_pct`, `roic_pct`, `pe_ttm`
2. **Statements:**
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `currency`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `ebitda`, `reported_diluted_eps`, `weighted_average_diluted_shares`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=8)` → `period_end`, `period_basis`, `revenue`, `operating_income`, `net_income`
3. **Consensus:**
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="eps")` and `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct`
   - `get_estimates_and_earnings(view="consensus", ticker="us:NVDA")` → `current_price`, `target_low_price`, `target_mean_price`, `target_high_price`, `next_earnings_date`, `short_pct_of_float`, `observed_on`
4. **SEC filings, ETFs & hurdle:**
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=60)` → `segment`, `period`, `flow`, `revenue`
   - `get_sec_filings(view="debt_maturities", ticker="us:NVDA", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-01-15", transaction_code="P,S", limit=400)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `transaction_value`, `owners`, `filing_date` (newest first; follow `next_cursor` once or state earliest `transaction_date` if truncated).
   - `get_sec_filings(view="institutional_ownership", ticker="us:NVDA", limit=15)` → `holder`, `report_date`, `shares`, `market_value_usd`, `put_call`, `shares_change_qoq_pct`, `filing_date` (exclude option rows with `put_call` set).
   - `get_etf_data(ticker="us:NVDA", view="exposures", limit=25)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`; and `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`

## Step 2: Scenarios, Asymmetry & HTML Slots

- **Scenario rule (`P/E today` = `native_close` / current-FY `consensus` EPS):** Base = next-FY `consensus` EPS × P/E today (50%); Bear = next-FY `low` EPS × `0.8 ×` P/E today (25%); Bull = next-FY `high` EPS × `1.2 ×` P/E today (25%). State both default and custom numbers if changed; fall back to `target_low_price`/`target_mean_price`/`target_high_price` if EPS ≤ 0.
- **Expected Return & Asymmetry:** $\sum p_i r_i$ in the pitch direction (`SHORT` flips sign), and Upside / Downside ratio (mark `"Weak (<2.0x)"` when `< 2.0×`; flag in the first line if expected return is negative).
- Every thesis bullet needs `[Claim] — [Dated figure]. Wrong if: [measurable quarterly tripwire]`, with a steelmanned opposite case and complete `{{provenance_citations}}`.

## Conclusion & Worked Example

Write `./memos/[SYMBOL]_[LONG|SHORT]_[YYYY-MM-DD].html` from [references/memo-template.html](references/memo-template.html) (filling `{{business_snapshot}}`, `{{whats_priced_in}}`, `{{ownership_and_insiders}}`, `{{risks_and_catalysts_table}}`, and `{{provenance_citations}}`), then reply in chat in 3–4 sentences leading with the expected return, asymmetry ratio, and variant view + saved path. *(Not investment advice.)*

> **Worked chat reply (`us:AAPL` LONG):**
> Saved `./memos/AAPL_LONG_2026-11-28.html`. At **$228.50** (`27.4x` FY26E consensus EPS of `$8.34`), Street FY27 EPS dispersion (`$8.60–$10.10`, `38` analysts) yields **Bear $188 (-18%) / Base $252 (+10%) / Bull $332 (+45%)**—a **+11.8%** expected return and **2.5×** asymmetry ratio, though Services growth slowing below 10% YoY breaks the multiple.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that slot `not available`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
