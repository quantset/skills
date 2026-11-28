---
name: dcf-valuation
description: "Runs a Reverse-DCF and two-stage discounted cash flow valuation from filed financial statements, leading with what today's price implies plus Bear/Base/Bull scenarios, SBC-adjusted owner FCF, a net debt bridge and a 3x3 sensitivity matrix. Use when the user asks what a stock is worth, whether a company is overvalued or undervalued, for intrinsic or fair value, or what growth the share price implies. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📐","os":["darwin","linux","win32"]}}
---

# DCF Valuation Skill (Powered by QuantSet)

Test what a company's share price implies about future cash-flow growth, then run a discounted cash-flow model from filed statements, live Treasury yields, and verified share counts.

## Data Rules

- Statement figures sit under `values` (e.g. `values.revenue`); `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- `period="annual"` can include rolling `10-Q` windows; drop rows with `form` `10-Q` to isolate fiscal years. Non-US rows have no `form` and are all fiscal years.
- Use quarterly rows only when `period_basis` is `discrete_quarter` (never sum YTD rows); deduplicate by `period_end` year-month, preferring rows with an `accession`.
- `estimates` returns 4 rows (this/next quarter, this/next fiscal year) in reporting currency; distinguish by `period` + `period_end`.
- `price`, `market_cap_b` and `enterprise_value_b` are USD; `native_close` is in `quote_currency`; statements are in `financial_currency` (convert via `usd_rate`).
- Show `null` as `n/a` (never `0`, memory, or web search). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Step 1: Pull the Inputs in Parallel

Pass `workflow="dcf-valuation"` on every call (REST: `X-Workflow-Id: dcf-valuation`, `X-API-Key` from `QUANTSET_API_KEY` or `mw_demo`).

1. `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `quote_currency`, `financial_currency`, `market_cap_b`, `total_debt`, `cash`, `sector`, `security_type`, `roic_pct`, `share_count_change_1y_pct`, `ffo_ttm`, `price_to_ffo`
2. `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `available_at`, `accession`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - Newest row is the base (`10-Q` = trailing 12 months; otherwise fiscal year). Keep up to 6 fiscal-year rows. If `free_cash_flow` is `null`, use `operating_cash_flow + capex` (`capex` is negative).
3. `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `revenue`, `ebitda`, `weighted_average_diluted_shares`
   - For a `10-Q` base, pair with snapshot `revenue_ttm`.
4. `get_financial_statements(tickers=["us:NVDA"], kind="balance_sheet", period="quarterly", limit_per_instrument=3)` → `period_end`, `accession`, `long_term_debt`, `current_portion_long_term_debt`, `notes_payable`, `convertible_debt`, `cash_and_equivalents`
   - Use snapshot `total_debt`; if `null`, take the newest row with an `accession` or non-null debt line and sum its present debt lines (excluding leases). Note that `cash` excludes marketable securities.
5. `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=2)` → `period_end`, `period_basis`, `weighted_average_diluted_shares`, `available_at` (fallback to call 3).
6. `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", start="2022-01-01", limit=200)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
   - Set `start` 3 years back; keep the latest `filed` full-year `10-K` row.
7. `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `year_ago`, `analyst_count`, `as_of` (FY1 growth = `consensus / year_ago - 1`; FY2 = next FY / current FY `- 1`).
8. `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`
9. `get_peers(ticker="us:NVDA", limit=8)` → `instrument_id`, `market_cap_b`, `fcf_yield_pct`

## Step 2: Check Fit, Then Run `scripts/dcf_math.py`

- **Stop without a DCF value** for REITs (`security_type == "reit"`, discuss `ffo_ttm` / `price_to_ffo`), `Financials` (debt is operating funding; discuss ROE vs. P/B), or companies with negative base FCF **and** non-positive 3-year median FCF margin.
- Look up the sector discount spread and size/leverage adjustments in [references/sector-wacc.md](references/sector-wacc.md) (override any assumption the user gave).
- Run `python scripts/dcf_math.py inputs.json` ([scripts/dcf_math.py](scripts/dcf_math.py) holds all base-normalization, growth-fade, Reverse-DCF, Bear/Base/Bull scenario, Owner-FCF, and 3×3 WACC vs. Terminal Growth matrix math, with the centre cell equal to the Base case). Print the assumptions the script used and let the user override them. If you cannot execute Python, read the script's formulas and compute the same steps directly.

## Conclusion & Worked Example

Answer the user's question in the first sentence by leading with **what today's price implies** (the Reverse DCF vs. historical and consensus growth), followed by the Bear/Base/Bull scenario range (and both normalized and reported-base values whenever the base year was normalized), the Owner FCF (post-SBC) figure, the cash-flow & 3×3 sensitivity tables, and a compact `## Sources (Required)` table (`call`, `period_end`/`date`, `available_at`/`filed`, `accession`, ending with `Data: QuantSet (https://quantset.dev), retrieved [date]`). *(Not investment advice.)*

> **Worked opening (`us:MSFT` at `$489.93`):**
> At **$489.93**, Microsoft's share price implies **15.3%** annual free-cash-flow growth over the next 10 years (at an 8.75% WACC and 2.5% terminal growth), virtually in line with its **14.6%** historical revenue CAGR and **15.0%** FY1 Street consensus. Across scenarios on a normalized 30% FCF margin base (adjusting for FY26's AI CapEx surge), model value spans **$245 (Bear) / $380 (Base) / $575 (Bull)**—or **$273** on unadjusted FY26 FCF (`$67.4B`), and **$352** after `$10.7B` of stock-based compensation.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that input `not available`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
