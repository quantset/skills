---
name: earnings-playbook
description: Ask "Run an earnings preview on MSFT" or "How did NVDA do this quarter?" to generate an expectation setup or post-earnings beat/miss note across 36,000+ companies with 8-quarter surprise history, consensus revenue/EPS bar, segment margin drivers, and a Bull/Base/Bear reaction matrix. Free to try with mw_demo.
metadata: {"clawdbot":{"emoji":"📅","os":["darwin","linux","win32"]}}
---

# Institutional Earnings Preview & Post-Earnings Update Skill (Powered by QuantSet)

Run either a **Pre-Earnings Setup Brief** (before the print) or a **Post-Earnings Flash Update** (within 48h after results) using verified consensus bars, discrete quarterly statements, and segment trends.

Each call below is written exactly as the QuantSet MCP tool accepts it; swap the sample ticker for the user's listing. Pass `workflow="earnings-playbook"` on MCP tool calls (or `X-Workflow-Id: earnings-playbook` on REST requests). `get_estimates_and_earnings` takes one `view` per call. The fields after each arrow are the ones this skill reads. On statement rows the line items sit under `values` (for example `values.revenue`); dates, `period_basis` and `accession` sit on the row itself.

## Mode A: Pre-Earnings Setup ("What's the Bar?")

1. **Report Date:** `get_estimates_and_earnings(view="calendar", ticker="us:NVDA", start="2026-11-27", limit=4)` → `date`, `timing`
   - Set `start` to today and use the earliest `date` returned. No rows means the next report is not listed yet; say so and do not guess a date.
2. **Consensus Bar (two calls):**
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="eps")` → `period`, `period_end`, `consensus`, `high`, `low`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `high`, `low`, `analyst_count`, `year_ago`, `as_of`
   - The `Current Quarter` row is the bar for this print; `Current Year` and `Next Year` frame the guide.
3. **Price Targets & Ratings:**
   - `get_estimates_and_earnings(view="consensus", ticker="us:NVDA")` → `target_low_price`, `target_mean_price`, `target_high_price`, `upside_pct`, `strong_buy`, `buy`, `hold`, `sell`, `strong_sell`, `observed_on`
   - `get_estimates_and_earnings(view="analyst_ratings", ticker="us:NVDA", limit=4)` → `date`, `rank`, `vgm_grade`
4. **8-Quarter Beat/Miss Track Record:** `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct`
   - This history is EPS. Quantify the beat rate and the typical size of a beat or miss; do not state a revenue beat rate from it.
5. **Positioning & Crowding Check:**
   - `get_price_history(ticker="us:NVDA", limit=90)` and `get_price_history(ticker="index:SPX", limit=90)` → `date`, `close` (30-day and 90-day run-up into the print vs. the index)
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2026-08-27", limit=1000)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `is_buy`, `shares`, `transaction_value`, `filing_date`
   - Set `start` to 90 days before today. Without `start` the rows begin with the earliest years on file. Treat `is_10b5_1` true as scheduled, false as discretionary and `null` as not stated, and print the first and last `transaction_date` returned, because insider coverage can lag. Open-market sales carry `transaction_code` `S`.
   - `get_etf_data(ticker="us:NVDA", view="exposures", limit=10)` → `fund_symbol`, `fund_name`, `weight_pct`, `as_of`
6. **3 Key Swing Variables:**
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=60)` → `segment`, `period`, `flow`, `revenue` (segment revenue only; margins come from the consolidated statements below). `flow` `Y` marks a full fiscal year and `Q` a single quarter, and `period` names the fiscal quarter the row ends in. Segments are product lines or regions, as the company reports them.
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=8)` → `period_end`, `period_basis`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `reported_diluted_eps`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="quarterly", limit_per_instrument=8)` → `period_end`, `period_basis`, `operating_cash_flow`, `free_cash_flow`
   - Read `period_basis`: compare a quarter only with rows on the same basis. A row that is not `discrete_quarter` holds year-to-date figures and cannot sit beside a single quarter.
   - Name the exact 2–3 segment or margin lines that will drive the post-print move, framed as a crisp **Bull / Base / Bear reaction matrix**.

## Mode B: Post-Earnings Update ("What Changed?")

Pull Mode A steps 4 and 6 again for the reported quarter, plus the bar as it stood before the print: `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue", as_of="2026-11-16")` and the same call with `metric="eps"` (set `as_of` to the day before the report).

1. **Headline Beat / Miss Table:** Compare reported Revenue, Gross Margin, Operating Income, GAAP EPS (`reported_diluted_eps`), Street EPS (`actual_eps` vs. `estimated_eps`), and FCF against consensus and YoY/QoQ baselines—quantifying variances in both `$` and `bps`/`%`.
2. **Quality of the Beat:** Check whether an EPS beat came from genuine operating-margin expansion or low-quality tax-rate/buyback/working-capital releases (`OCF` vs. `Net Income`).
3. **Thesis & Estimate Impact:** State clearly whether the print **strengthens, leaves intact, or breaks** the prior thesis, with updated forward multiples (`Forward P/E`, `EV/FCF`) from `get_company_snapshot(ticker="us:NVDA")` → `pe_forward`, `ev_to_fcf`, `price`, `fundamentals_as_of`.

## Deliverable: a Note and a Workbook

When you can write files, produce two that the user can open, check and reuse next quarter:
- **Note:** `earnings/[TICKER]_[PERIOD]_[preview|update].md`, in the layout below.
- **Workbook:** `earnings/[TICKER]_earnings.xlsx`, laid out as in [references/workbook.md](references/workbook.md). One workbook per company: if it already exists, add this quarter's rows and keep the earlier ones.

When you cannot write files, print the note in chat and the workbook sheets as CSV blocks under the same sheet names.

### Note Layout

1. **Header line:** company, ticker, fiscal period, report `date` and `timing` (or "reported" for an update), current `price`.
2. **The Bar** (preview) or **Beat / Miss** (update):

| Metric | Consensus | Low – High | # Analysts | Year Ago | Reported | Variance |
|---|---|---|---|---|---|---|

3. **Track Record:** 8 rows of `period_end`, `estimated_eps`, `actual_eps`, `surprise_pct`, then the beat rate.
4. **Positioning:** run-up vs. the index, discretionary insider sales, top ETF holders by `weight_pct`.
5. **Swing Variables / Quality of the Beat:** the 2–3 lines, each with its last 4 quarters of numbers.
6. **Reaction Matrix** (preview) or **Thesis Impact** (update):

| Case | What prints | Why it matters |
|---|---|---|
| Bull | | |
| Base | | |
| Bear | | |

7. **Sources:** see below. *(Not investment advice.)*

## Sources (Required)

Close the note with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end`, `date` or `as_of`), when it was filed or published (`available_at`, `filing_date` or `observed_on`), and the SEC `accession` when the row carries one.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- Never fill a gap from memory or a web search. Write `not available` and name the call that returned nothing.
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): mark that section `not available`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
