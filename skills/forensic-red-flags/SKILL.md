---
name: forensic-red-flags
description: "Runs a 7-point forensic check from SEC filings: cash conversion against net income, GAAP versus adjusted EPS, stock-based compensation and dilution, the 24-month debt wall, insider selling with Rule 10b5-1 flags, segment decay and ETF crowding. Use when the user asks about accounting red flags, earnings quality, aggressive accounting, dilution, insider selling or a short-seller style audit. Covers 36,000+ companies and 127M+ SEC filing facts. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🔍","os":["darwin","linux","win32"]}}
---

# Forensic Accounting & Red-Flag Audit Skill (Powered by QuantSet)

Audit an issuer across **7 screening checks** from SEC XBRL facts, Form 4 Rule 10b5-1 flags, debt maturity walls, and share counts. Score each check `CLEAN`, `WATCH`, `RED FLAG`, or `NOT ASSESSED` (never score a check `CLEAN` when its inputs are missing). Thresholds are screening lines ("read the filing"), not proof.

## Data Rules

- Statement figures sit under `values`; `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- Drop `form` `10-Q` rows from `period="annual"` to isolate fiscal years. Use quarterly rows only when `period_basis` is `discrete_quarter`.
- `company_facts` rows arrive unordered and repeat across filings: pass `start` to bound the window and keep the latest `filed` row per period (`10-K` full-year span for flow concepts; point-in-time `period_end` for balance concepts).
- Show `null` as `n/a` (never `0` or memory). On `unsupported_instrument`, mark `NOT ASSESSED (US listings only)`.

## The 7 Checks

Pass `workflow="forensic-red-flags"` on every call (REST: `X-Workflow-Id: forensic-red-flags`).

**Shared baseline (4 newest fiscal years):**
- `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `high_52w`, `cash`, `total_debt`, `market_cap_b`, `financial_currency`
- `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=8)` → `period_end`, `form`, `revenue`, `net_income`, `ebitda`, `weighted_average_diluted_shares`, `available_at`, `accession`
- `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=8)` → `period_end`, `form`, `operating_cash_flow`, `free_cash_flow`

1. **Cash Conversion (`OCF`/`FCF` vs. `Net Income` & Working Capital):**
   - `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="AccountsReceivableNetCurrent", start="2021-01-01", limit=200)` → `value`, `period_end`, `form`, `filed`
   - `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="InventoryNet", start="2021-01-01", limit=200)` → `value`, `period_end`, `form`, `filed`
   - Check (a) `operating_cash_flow < net_income`, (b) receivables growth > revenue growth + 15 pts, (c) inventory growth > revenue growth + 15 pts. `WATCH`: 1 condition in latest FY. `RED FLAG`: same condition in last 2 FYs, or negative FCF alongside positive net income in both years.
2. **GAAP vs. Street EPS Spread:**
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=12)` → `period_end`, `period_basis`, `reported_diluted_eps`
   - `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`
   - Compare trailing-4Q `actual_eps` sum vs. GAAP `reported_diluted_eps` sum. `WATCH`: Street > GAAP by >35% (or Street profit vs. GAAP loss). `RED FLAG`: >35% in both trailing-4Q and prior-4Q windows.
3. **Stock-Based Compensation & Dilution:**
   - `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", start="2022-01-01", limit=200)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
   - `WATCH`: latest `10-K` SBC > 20% of `operating_cash_flow`, or `weighted_average_diluted_shares` up >2% YoY (or post-FY code-`M` option exercises >2% of shares). `RED FLAG`: both SBC > 20% of OCF and shares up >2%.
4. **24-Month Debt Maturity Wall:**
   - `get_sec_filings(view="debt_maturities", ticker="us:NVDA", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5` (`y2 + y3` if filing `year` ended >9 months ago).
   - `WATCH`: 2-year maturities > `cash`, or schedule net debt > 3.5× EBITDA. `RED FLAG`: 2-year maturities > `cash + 1.5 × free_cash_flow`.
5. **Form 4 Insider Selling (`10b5-1` vs. Discretionary):**
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-01-15", limit=500)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `shares`, `price_per_share`, `transaction_value`, `owners`, `filing_date`, `accession`
   - `get_sec_filings(view="form_144", ticker="us:NVDA", start="2025-01-15")` → `seller_name`, `shares_to_be_sold`, `aggregate_market_value_usd`, `approx_sale_date`, `filing_date`
   - Rows arrive newest first (if `next_cursor` is not `null`, fetch one more page or state earliest `transaction_date`). Score open-market `S` and `P` only (`is_10b5_1 == false` is discretionary; report `A`/`M`/`F`/`G` counts and newer Form 144 notices as context). `WATCH`: ≥2 discretionary sale dates by 1 insider or ≥2 insiders within 60 days (or 0 buys while `price` is >35% off `high_52w`). `RED FLAG`: ≥3 insiders selling discretionarily within 60 days.
6. **Segment Decay:**
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=100)` → `segment`, `period`, `flow`, `year`, `quarter`, `revenue`
   - On `flow == "Y"` rows: `WATCH` if largest segment revenue fell in latest FY; `RED FLAG` if it fell 2 straight FYs while consolidated revenue grew.
7. **Leveraged ETF Crowding (Context Only — Max `WATCH`):**
   - `get_etf_data(ticker="us:NVDA", view="exposures", limit=60)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`, then `get_etf_data(ticker="us:IVV", view="profile")` → `fund_category`, `is_leveraged_or_inverse_index`, `daily_target_multiple`, `net_assets_usd` on up to 5 fresh funds with `weight_pct > 15%`. `WATCH` if any is leveraged/inverse.

## Conclusion & Worked Example

Answer in the first sentence with the scorecard tally and the sharpest numeric flags, followed by the 7-row scorecard table, short numeric notes on **`WATCH`/`RED FLAG` checks only** (skip paragraphs on `CLEAN` checks), 3 measurable next-filing tripwires, and a compact `## Sources (Required)` table (`Data: QuantSet (https://quantset.dev), retrieved [date]`). *(Not investment advice.)*

> **Worked opening (`us:TSLA`):**
> Tesla triggers **1 RED FLAG and 2 WATCH flags** (4 CLEAN) on its latest filings: Street non-GAAP EPS (`$2.42`) exceeded GAAP diluted EPS (`$1.28`) by **89%** over the trailing four quarters (**RED FLAG**, >35% in two consecutive 4Q windows), 4 of the CFO's 5 open-market sales (`$4.1M`) were unscheduled outside a 10b5-1 plan (**WATCH**), and single-stock leveraged ETFs hold `$6.8B` at 2× daily exposure (**WATCH**), while operating cash flow (`$14.9B`) cleanly covered GAAP net income (`$7.1B`).

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that check `NOT ASSESSED`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
