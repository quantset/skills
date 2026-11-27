---
name: forensic-red-flags
description: "Ask 'Any accounting red flags or insider selling on TSLA?' to run a 7-point forensic check across 36,000+ companies and 127M+ SEC filing facts (cash-conversion divergence, GAAP vs. non-GAAP EPS spread, SBC dilution, 24-month debt walls, segment decay, and Form 4 Rule 10b5-1 insider trades). Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🔍","os":["darwin","linux","win32"]}}
---

# Forensic Accounting & Red-Flag Audit Skill (Powered by QuantSet)

Systematically audit an issuer across **7 institutional forensic checks** using primary SEC XBRL disclosures, Form 4 Rule 10b5-1 flags, debt maturity walls, and share-count history.

## The 7-Point Forensic Checklist

Run the calls below in parallel and score each dimension **CLEAN**, **WATCH**, or **RED FLAG**. Each call is written exactly as the QuantSet MCP tool accepts it; swap the sample ticker for the user's listing and pass `workflow="forensic-red-flags"` (REST: header `X-Workflow-Id: forensic-red-flags`). The fields after each arrow are the ones this skill reads. On statement rows the line items sit under `values` (for example `values.revenue`); dates, `period_basis` and `accession` sit on the row itself.

Two rules apply to every check:
- `get_sec_filings` with `view="company_facts"` returns rows unordered. Sort by `period_end` yourself; `10-K` rows spanning a full year are annual, `10-Q` flow rows are year-to-date.
- Quarterly statement rows carry `period_basis`. Compare a quarter only with rows on the same basis; a row that is not `discrete_quarter` holds year-to-date figures.

### 1. Cash Conversion Divergence (`OCF` & `FCF` vs. `GAAP Net Income`)
- `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=4)` → `period_end`, `operating_cash_flow`, `free_cash_flow`, `available_at`, `accession`
- `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=4)` → `period_end`, `revenue`, `net_income`, `reported_diluted_eps`
- `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="AccountsReceivableNetCurrent", limit=1000)` → `value`, `period_end`, `form`, `filed`
- `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="InventoryNet", limit=1000)` → `value`, `period_end`, `form`, `filed`
- Compare the last 3 fiscal years of Operating Cash Flow and Free Cash Flow against GAAP Net Income (add the trailing 4 quarters only when the quarterly rows are discrete).
- **Flag (`WATCH` / `RED FLAG`):** Net income growing while OCF/FCF stagnates or turns negative for $\ge 2$ consecutive periods, or `Accounts Receivable` / `Inventory` growing $>15\%$ faster than `Revenue` (channel-stuffing / working-capital bloat).

### 2. GAAP vs. Street "Adjusted" EPS Spread
- `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=8)` → `period_end`, `period_basis`, `reported_diluted_eps`
- `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct`
- Compare GAAP diluted EPS (`reported_diluted_eps`) against the Street actual (`actual_eps`) for the same quarter, matching each to the nearest fiscal quarter end.
- **Flag:** Non-GAAP EPS exceeding GAAP EPS by $>35\%$ persistently, or widening every year due to "recurring one-time" restructuring and stock-based compensation add-backs.

### 3. Stock-Based Compensation (SBC) & Share-Count Creep
- `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", limit=1000)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
- `get_company_snapshot(ticker="us:NVDA")` → `share_count_change_1y_pct`, `revenue_ttm`, `operating_cash_flow`, `free_cash_flow`, `cash`, `total_debt`, `net_debt_to_ebitda`, `price`, `high_52w`, `fundamentals_as_of`
- Report annual SBC as a % of Revenue, of Operating Cash Flow and of FCF, alongside the 1-year share-count change.
- **Flag:** `SBC > 20%` of Operating Cash Flow while diluted share count expands $>2\%/\text{yr}$ (or management touts buybacks that fail to offset RSU dilution).

### 4. Debt Maturity Wall & Refinancing Squeeze
- `get_sec_filings(view="debt_maturities", ticker="us:NVDA", limit=3)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
- `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`
- `year` is the fiscal year of the filing; `y1` and `y2` are the amounts due in the first and second year after it. The row carries no currency, so read it in the company's `financial_currency`; cash, debt and FCF come from the snapshot in check 3.
- **Flag:** Debt maturing within the next 24 months exceeding `(Cash + 1.5× TTM FCF)`, or `Net Debt / EBITDA > 3.5x` facing higher refinancing coupons. An empty result means no maturity schedule was found, which is not the same as no debt.

### 5. Form 4 Insider Selling: Unscheduled vs. Rule 10b5-1
- `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-11-27", limit=1000)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `is_buy`, `shares`, `price_per_share`, `transaction_value`, `owners`, `filing_date`, `accession`
- Set `start` to one year before today. Without `start` the rows begin with the earliest years on file. Treat `is_10b5_1` true as scheduled, false as discretionary and `null` as not stated, and print the first and last `transaction_date` returned, because insider coverage can lag.
- Separate tax-withholding dispositions (code `F`) and pre-scheduled **Rule 10b5-1** trades from discretionary open-market sales (`S`) and cluster buys (`P`).
- **Flag:** Multiple C-suite/CFO discretionary open-market sales (`S`, non-10b5-1) within 60 days, or zero open-market insider purchases despite a >35% drawdown (`price` vs. `high_52w`).

### 6. Segment Decay Masked by Consolidated Headline Growth
- `get_sec_filings(view="segments", ticker="us:NVDA", limit=100)` → `segment`, `period`, `flow`, `year`, `quarter`, `revenue`
- Check whether the core segment's growth is decelerating while smaller or acquired revenue masks the consolidated top line. Segment rows carry revenue only; do not state a segment margin. `flow` `Y` marks a full fiscal year and `Q` a single quarter, and `period` names the fiscal quarter the row ends in. Segments are product lines or regions, as the company reports them.

### 7. Passive / Thematic ETF Crowding Risk
- `get_etf_data(ticker="us:NVDA", view="exposures", limit=25)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`
- For the two or three funds with the largest `weight_pct`: `get_etf_data(ticker="us:IVV", view="profile")` → `fund_category`, `is_leveraged_or_inverse_index`, `daily_target_multiple`, `net_assets_usd`
- Flag mechanical rebalance/outflow vulnerability if the stock is concentrated in leveraged or single-theme funds.

---

## Output Format

1. **Forensic Scorecard Table:** 1 row per check (`1–7`), Status (`CLEAN` / `WATCH` / `RED FLAG`), Key Metric, and Exact Filing Citation (`available_at` / period).

| # | Check | Status | Key Metric | Period | Filing |
|---|---|---|---|---|---|

2. **Deep-Dive Findings:** Concrete numbers on every `WATCH` or `RED FLAG` item (preserving `null` where unreported—never guessing `0`).
3. **Questions for Management / Next 10-Q Watchlist:** 3 falsifiable line items to check on the next filing day. *(Analytical audit only — not investment advice.)*
4. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end`, `transaction_date` or `as_of`), when it was filed (`available_at`, `filed` or `filing_date`), and the SEC `accession` when the row carries one.
- A check with no data is scored `NOT ASSESSED`, never `CLEAN`.
- Never fill a gap from memory or a web search. Write `not available` and name the call that returned nothing.
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): score that check `NOT ASSESSED`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
