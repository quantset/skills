---
name: earnings-playbook
description: "Prepares a pre-earnings setup or a post-earnings beat/miss note: the consensus revenue and EPS bar, 8-quarter surprise history, positioning, segment and margin swing factors and a bull/base/bear reaction matrix, saved as a note plus a per-company workbook that grows each quarter. Use when the user asks for an earnings preview, what to watch into a report, how a company did this quarter, or a beat/miss summary. Covers 36,000+ companies. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📅","os":["darwin","linux","win32"]}}
---

# Institutional Earnings Preview & Post-Earnings Update Skill (Powered by QuantSet)

Run either a **Pre-Earnings Setup Brief** (before the print) or a **Post-Earnings Flash Update** (within 48h after results) using verified consensus bars, discrete quarterly statements, and segment trends.

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="earnings-playbook"` on every call (REST: header `X-Workflow-Id: earnings-playbook`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads. `get_estimates_and_earnings` takes one `view` per call.

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

## Mode A: Pre-Earnings Setup ("What's the Bar?")

1. **Report Date:** `get_estimates_and_earnings(view="calendar", ticker="us:NVDA", start="2026-01-15", limit=4)` → `date`, `timing`
   - Set `start` to today's date and use the earliest `date` returned. With no rows, use `next_earnings_date` from the consensus view in step 3 and say that is where it came from; if that is empty too, say the next report is not listed yet and do not guess a date.
2. **Consensus Bar (two calls):**
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="eps")` → `period`, `period_end`, `consensus`, `high`, `low`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `high`, `low`, `analyst_count`, `year_ago`, `as_of`
   - This quarter's row is the bar for this print; the two fiscal-year rows frame the guide. `year_ago` is the Street's figure for the year-ago period and can differ from the reported one.
3. **Price Targets & Ratings:**
   - `get_estimates_and_earnings(view="consensus", ticker="us:NVDA")` → `current_price`, `target_low_price`, `target_mean_price`, `target_high_price`, `strong_buy`, `buy`, `hold`, `sell`, `strong_sell`, `next_earnings_date`, `shares_short`, `short_pct_of_float`, `observed_on`
   - `get_estimates_and_earnings(view="analyst_ratings", ticker="us:NVDA", limit=4)` → `date`, `rank`, `vgm_grade`
4. **8-Quarter Beat/Miss Track Record:** `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct`
   - This history is EPS on the Street's basis. Give the beat rate and the median absolute `surprise_pct`; do not state a revenue beat rate from it.
5. **Positioning & Crowding Check:**
   - `get_price_history(ticker="us:NVDA", limit=91)` and `get_price_history(ticker="index:SPX", limit=91)` → `date`, `close`
   - Compute the 30-session and 90-session returns ending at the latest `close` for both, and print the dates. The latest `close` and its date are also the price in the note's header.
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-10-15", transaction_code="P,S", limit=250)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `shares`, `transaction_value`, `filing_date`
   - Set `start` to 90 days before today; without it the rows begin with the earliest years on file. Count open-market sales (`transaction_code` `S`) and buys (`P`) only; the other codes are awards, exercises, gifts and tax withholding. `is_10b5_1` true is scheduled, false is discretionary, `null` is not stated. Print the earliest and latest `transaction_date` among the rows, because coverage can stop short of today.
   - `get_etf_data(ticker="us:NVDA", view="exposures", limit=60)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`
   - Rows come ordered by weight, not size, and stop at 200, so large funds with a small weight can be missing; say so. Drop rows whose `as_of` is more than a year old and rows that repeat another fund's weight to the last decimal (keep the first), then show the five with the largest `market_value`.
   - **What the options market expects:** `get_market_activity(view="options", ticker="us:NVDA")` → `expiration_dates`
   - Call it again with `expiration` set to the first date after the report: `get_market_activity(view="options", ticker="us:NVDA", expiration="2026-01-30")` → `implied_move_pct`, `atm_implied_volatility_pct`, `put_call_open_interest_ratio`, `underlying_price`
   - (REST: `GET /api/v1/options`.) When `underlying_price` differs from the latest close by more than 2%, say so beside the implied move. When that expiration is within 14 days after the report, the implied move is roughly the reaction already priced. When it is later, the figure covers everything up to that date, not the print: give it as "the move priced to" that date and do not call it the earnings move.
   - Short positioning is `short_pct_of_float` from the consensus view, as of `observed_on`.
6. **Swing Variables:**
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=100)` → `segment`, `period`, `flow`, `revenue`
   - `flow` `Q` is a single quarter and `Y` a full fiscal year; `period` is a label for the calendar quarter the row ends in. The fiscal fourth quarter often comes only inside the `Y` row: derive it as the `Y` row minus that fiscal year's three `Q` rows, only when all three are present, and mark it derived. Segments are product lines or regions, as the company reports them, and carry revenue only; margins come from the consolidated statements.
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=14)` → `period_end`, `period_basis`, `revenue`, `cost_of_revenue`, `gross_profit`, `operating_income`, `net_income`, `reported_diluted_eps`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="quarterly", limit_per_instrument=14)` → `period_end`, `period_basis`, `operating_cash_flow`, `free_cash_flow`
   - Keep one row per quarter and the twelve newest quarters, so that eight quarters have a year-ago figure. When `gross_profit` is `null`, use `revenue - cost_of_revenue`. Cash-flow rows are often year-to-date: compare a quarter's cash flow only with another `discrete_quarter` row, or year-to-date with the same point a year earlier, and say which.
   - Name the three lines that moved most: a segment whose year-on-year growth rate changed most from the quarter before, and a margin (gross or operating) that moved most in basis points against the year-ago quarter.
7. **Reaction Matrix, by rule:** take the median absolute `surprise_pct` from step 4 as the normal size of a surprise, and apply it as a band around the EPS `consensus` (Street basis). Every outcome lands in exactly one case: **Bull** is EPS above the band, **Base** is EPS inside it or on its edge, **Bear** is EPS below it. In each case say what revenue against its `consensus` would add or take away, and name the swing line that would cause it.

## Mode B: Post-Earnings Update ("What Changed?")

Pull Mode A steps 4 and 6 again for the reported quarter, plus the bar as it stood before the print: `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue", as_of="2026-01-14")` and the same call with `metric="eps"` (set `as_of` to the day before the report).

1. **Headline Beat / Miss Table:** reported Revenue, Gross Margin, Operating Income, GAAP EPS (`reported_diluted_eps`), Street EPS (`actual_eps` vs. `estimated_eps`), and FCF against consensus and the year-ago quarter—variances in both `$` and `bps`/`%`.
2. **Quality of the Beat:** whether an EPS beat came from operating-margin expansion or from a lower tax rate, fewer shares or working capital (operating cash flow against net income).
3. **Thesis & Estimate Impact:** whether the print **strengthens, leaves intact, or breaks** the prior thesis, and which case of the reaction matrix it landed in, with `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `pe_ttm`, `forward_eps` for the multiples after the print.

## Deliverable: a Note and a Workbook

When you can write files, produce two that the user can open, check and reuse next quarter. `[SYMBOL]` is the symbol without its market prefix and `[YYYY-MM]` is the `period_end` month of the quarter being reported.
- **Note:** `earnings/[SYMBOL]_[YYYY-MM]_[preview|update].md`, in the layout below.
- **Workbook:** `earnings/[SYMBOL]_earnings.xlsx`, laid out as in [references/workbook.md](references/workbook.md). One workbook per company: if it already exists, add this quarter's rows and keep the earlier ones.

When you cannot write files, print the note in chat and the workbook sheets as CSV blocks under the same sheet names.

### Note Layout (Keep Concise — ~60–80 Lines, Findings First)

1. **Header + Top 3 Takeaways (4 lines max):** company, symbol, quarter, report `date`/`timing`, latest `close`, followed immediately by the 3 sharpest numbers (e.g. consensus bar vs. 8Q beat rate, options-implied move vs. 30D run-up, and #1 segment swing factor).
2. **The Bar** (preview) or **Beat / Miss** (update):

| Metric | Consensus | Low – High | # Analysts | Year Ago (Street) | Reported | Variance |
|---|---|---|---|---|---|---|

3. **Track Record:** 8 rows of `period_end`, `estimated_eps`, `actual_eps`, `surprise_pct`, then the beat rate and the median absolute surprise.
4. **Positioning:** run-up vs. the index with dates, the options-implied move and its expiration, short interest as a share of float, price targets and ratings, discretionary insider sales, the five largest ETF holders by `market_value`.
5. **Swing Variables / Quality of the Beat:** the two or three lines, each with its last 4 quarters of numbers.
6. **Reaction Matrix** (preview) or **Thesis Impact** (update):

| Case | What prints | Why it matters |
|---|---|---|
| Bull | | |
| Base | | |
| Bear | | |

7. **Sources:** see below. *(Not investment advice.)*

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end`, `date` or `as_of`), when it was filed or published where the row says (`available_at`, `filing_date` or `observed_on`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no such date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): mark that section `n/a`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
