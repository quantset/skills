---
name: forensic-red-flags
description: "Runs a 7-point forensic check from SEC filings: cash conversion against net income, GAAP versus adjusted EPS, stock-based compensation and dilution, the 24-month debt wall, insider selling with Rule 10b5-1 flags, segment decay and ETF crowding. Use when the user asks about accounting red flags, earnings quality, aggressive accounting, dilution, insider selling or a short-seller style audit. Covers 36,000+ companies and 127M+ SEC filing facts. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🔍","os":["darwin","linux","win32"]}}
---

# Forensic Accounting & Red-Flag Audit Skill (Powered by QuantSet)

Systematically audit an issuer across **7 institutional forensic checks** using primary SEC XBRL disclosures, Form 4 Rule 10b5-1 flags, debt maturity walls, and share-count history.

Each check below has its calls, one measure, and a stated line for `WATCH` and for `RED FLAG`. Score a check `CLEAN` when neither line is crossed and `NOT ASSESSED` when its inputs did not come back; never score a check you could not measure. The thresholds are screening lines, not proof: a flag means "read the filing", and you say so.

## Data Rules (They Apply to Every Call in This Skill)

- **Where figures sit:** statement line items are under `values` (for example `values.revenue`); `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` are on the row.
- **Fiscal years:** `period="annual"` can return rolling twelve-month windows between the fiscal years. Drop every row whose `form` is `10-Q`; the rows left are fiscal years. That is why the calls ask for more rows than the years needed. For a US listing a row with no `form` is not from a filing: use it only for a year that has no `10-K` row. For a listing outside the US no row has a `form`, and all of them are fiscal years.
- **Quarters:** a quarterly row is a single quarter only when its `period_basis` is `discrete_quarter`; any other basis holds year-to-date figures. Never add or compare the two kinds: set a single quarter beside single quarters, and a year-to-date figure only beside the same point a year earlier. The same quarter can come back twice, with period ends up to a few weeks apart: match rows by the year and month of `period_end`, keep one per quarter, and prefer the one that has an `accession`.
- **Estimate rows:** the `estimates` view returns four rows: this quarter, next quarter, this fiscal year and next fiscal year. Their `period` labels vary by listing and a quarter and a fiscal year can end on the same date, so read the label and `period_end` together; `period_end` is a month-end label. Estimates are per share in the listing's reporting currency and on the Street's basis: they can differ from filed figures, and a company can file a loss while the consensus is a profit.
- **The snapshot mixes periods:** in `get_company_snapshot`, `free_cash_flow` and `ebitda_ttm` can be the last fiscal year's figures while `revenue_ttm` is trailing. Take EBITDA and free cash flow from the latest fiscal-year statement row and label them with its `period_end`.
- **Currency:** `price`, `market_cap_b` and `enterprise_value_b` are in US dollars (the `_b` fields in billions). `native_close` is the price in `quote_currency`, and statement figures are in `financial_currency`. Convert with `usd_rate` before combining the two.
- **Dates on filings:** `available_at` on an older period is the date of the latest filing that repeated it, not its first publication. Cite it only for the newest period.
- **Empty is not zero:** show a `null` as `n/a`. Never fill a gap from memory or a web search.
- **US-only datasets:** the error code `unsupported_instrument` means the dataset covers US listings only. Mark that section `n/a (US listings only)` and carry on. A key does not change it.
- **Filing facts repeat:** `get_sec_filings` with `view="company_facts"` returns rows unordered, and each period appears in several filings. Keep the row with the latest `filed` for each period: a balance concept (no `period_start`) is one date, `period_end`; a flow concept is the span from `period_start` to `period_end`, and in a `10-Q` that span is year-to-date.

---

## The 7-Point Forensic Checklist

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="forensic-red-flags"` on every call (REST: header `X-Workflow-Id: forensic-red-flags`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

Shared calls, used by several checks:
- `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `high_52w`, `cash`, `total_debt`, `market_cap_b`, `financial_currency`
- `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=24)` → `period_end`, `form`, `revenue`, `net_income`, `ebitda`, `weighted_average_diluted_shares`, `available_at`, `accession`
- `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=24)` → `period_end`, `form`, `operating_cash_flow`, `free_cash_flow`

Keep the four newest fiscal years from each.

### 1. Cash Conversion Divergence (`OCF` & `FCF` vs. `GAAP Net Income`)
- `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="AccountsReceivableNetCurrent", limit=1000)` → `value`, `period_end`, `form`, `filed`
- `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="InventoryNet", limit=1000)` → `value`, `period_end`, `form`, `filed`
- **Measure:** for each of the last 3 fiscal years, operating cash flow against net income; and the growth of receivables and of inventory at the fiscal year end, each minus revenue growth, in percentage points.
- There are three conditions: (a) operating cash flow below net income, (b) receivables growing more than 15 points faster than revenue, (c) inventory growing more than 15 points faster than revenue.
- **`WATCH`:** any one of them holds in the latest fiscal year.
- **`RED FLAG`:** the same one holds in the latest fiscal year and in the year before; or free cash flow is negative while net income is positive in both of those years.
- A condition that held only in an earlier year and has cleared is reported in the findings but does not set the status.

### 2. GAAP vs. Street "Adjusted" EPS Spread
- `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=12)` → `period_end`, `period_basis`, `reported_diluted_eps`
- `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`
- Match the two by quarter (the earnings rows use month-end dates; statement rows use the real period end, a few days earlier).
- **Measure:** the sum of Street EPS (`actual_eps`) over the last four quarters divided by the sum of GAAP diluted EPS (`reported_diluted_eps`) over the same quarters, minus 1. Do the same for the four quarters before.
- **`WATCH`:** Street exceeds GAAP by more than 35% over the last four quarters, or GAAP is a loss while Street is a profit.
- **`RED FLAG`:** more than 35% in both four-quarter windows.
- The data shows the gap, not its cause. Say that the reconciliation is in the earnings release.

### 3. Stock-Based Compensation (SBC) & Share-Count Creep
- `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", limit=1000)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
- **Measure:** the latest fiscal year's SBC (the `10-K` row spanning the full year) as a share of that year's operating cash flow, free cash flow and revenue; and the change in `weighted_average_diluted_shares` between the last two fiscal years.
- **`WATCH`:** SBC above 20% of operating cash flow; or diluted shares up more than 2%; or option exercises (insider rows with `transaction_code` `M` from check 5) since the last fiscal year end add up to more than 2% of the diluted share count, which the fiscal-year comparison cannot yet show.
- **`RED FLAG`:** SBC above 20% of operating cash flow and diluted shares up more than 2%.

### 4. Debt Maturity Wall & Refinancing Squeeze
- `get_sec_filings(view="debt_maturities", ticker="us:NVDA", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
- `year` is the fiscal year of the filing, and `y1` and `y2` are the amounts due in the first and second year after it, in `financial_currency`. When that fiscal year ended more than nine months ago, most of `y1` has already come due: use `y2 + y3` and say so.
- **Measure:** debt due in the next two years against `cash + 1.5 ×` the latest fiscal-year free cash flow; and net debt (schedule total `y1` through `after5`, minus `cash`) against the latest fiscal-year `ebitda`.
- **`WATCH`:** debt due in two years exceeds `cash`, or net debt is above 3.5 times EBITDA.
- **`RED FLAG`:** debt due in two years exceeds `cash + 1.5 ×` free cash flow.
- If the snapshot `total_debt` differs from the schedule total by more than 20%, report both and use the schedule. An empty schedule means none was found, which is not the same as no debt: `NOT ASSESSED`.

### 5. Form 4 Insider Selling: Unscheduled vs. Rule 10b5-1
- `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-01-15", limit=1000)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `shares`, `price_per_share`, `transaction_value`, `owners`, `filing_date`, `accession`
- Set `start` to one year before today. Score only open-market sales (code `S`) and buys (code `P`). Report the other codes as counts: awards (`A`), exercises (`M`), tax withholding (`F`), gifts (`G`), other disposals (`D`).
- A sale with `is_10b5_1` true is scheduled; false is discretionary; `null` is not stated. Print the earliest and latest `transaction_date` among the rows, because coverage can stop short of today.
- **Measure:** discretionary sales, by insider and date; and buys.
- "Within 60 days" means any span of 60 days inside the window, of any size.
- **`WATCH`:** one insider made discretionary sales on two or more dates within 60 days, or two different insiders made discretionary sales within 60 days; or there are no buys while `price` is more than 35% below `high_52w`.
- **`RED FLAG`:** three or more different insiders made discretionary sales within 60 days.
- Always give the totals: sale dates, shares and value, split into scheduled, discretionary and not stated. One sale is often many rows at different prices.
- **Planned sales (not scored):** `get_sec_filings(view="form_144", ticker="us:NVDA", start="2025-01-15")` → `seller_name`, `shares_to_be_sold`, `aggregate_market_value_usd`, `approx_sale_date`, `filing_date`
  - These are notices of intended sales (REST: `GET /api/v1/sec/form-144`). Report the ones filed after the latest trade row, since they show selling the trade rows do not yet cover.

### 6. Segment Decay Masked by Consolidated Headline Growth
- `get_sec_filings(view="segments", ticker="us:NVDA", limit=100)` → `segment`, `period`, `flow`, `year`, `quarter`, `revenue`
- `flow` `Y` marks a full fiscal year and `Q` a single quarter; `period` is a label for the calendar quarter the row ends in. Segments are product lines or regions, as the company reports them, and carry revenue only.
- **Measure:** over the last three fiscal years (`Y` rows), the largest segment's revenue growth beside total revenue growth.
- **`WATCH`:** the largest segment's revenue fell in the latest fiscal year.
- **`RED FLAG`:** it fell in each of the last two fiscal years while total revenue was higher at the end of those two years than at the start.
- Fewer than three fiscal years of `Y` rows: `NOT ASSESSED`.

### 7. Passive / Thematic ETF Crowding Risk
- `get_etf_data(ticker="us:NVDA", view="exposures", limit=200)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`
- Drop rows whose `as_of` is more than a year old and rows that repeat another fund's weight to the last decimal (share classes of one fund).
- Take the funds holding more than 15% of their assets in this stock, largest `market_value` first, five at most, and profile each: `get_etf_data(ticker="us:IVV", view="profile")` → `fund_category`, `is_leveraged_or_inverse_index`, `daily_target_multiple`, `net_assets_usd`. Skip a fund whose profile call fails and say so.
- **Measure:** whether a leveraged or inverse fund (`is_leveraged_or_inverse_index` true, or `daily_target_multiple` other than 1) is among them.
- **`WATCH`:** one is.
- This check is context and never returns `RED FLAG`. The list is ordered by weight and capped, so the largest index funds may be missing; do not total it as a share of the company.

---

## Output Format

1. **Forensic Scorecard Table:** one row per check.

| # | Check | Status | Measure | Period | Filing or date |
|---|---|---|---|---|---|

   Cite `accession` and `available_at` where the row carries them; otherwise the date the row describes.
2. **Deep-Dive Findings:** the numbers behind every `WATCH` or `RED FLAG`, and for each the line that was crossed.
3. **Next Filing Watchlist:** three figures to check when the next 10-Q or 10-K arrives, each with the value that would change a status. *(Analytical audit only — not investment advice.)*
4. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end`, `transaction_date` or `as_of`), when it was filed or published where the row says (`available_at`, `filed` or `filing_date`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no such date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.
- A check with no data is scored `NOT ASSESSED`, never `CLEAN`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): score that check `NOT ASSESSED`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
