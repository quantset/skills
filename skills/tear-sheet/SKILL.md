---
name: tear-sheet
description: Ask "Give me a tear sheet on AAPL" or "One-pager on SHEL.L" to generate a printable 1-page HTML company profile across 36,000+ US and global companies (67 countries) with a 5-year financial summary, valuation vs. peers, Street estimates, revenue segments, balance sheet, top holders and insider activity, every figure dated and sourced to SEC filings. Use for a company one-pager, profile, fact sheet, snapshot or overview. Free to try with mw_demo.
metadata: {"clawdbot":{"emoji":"🗂️","os":["darwin","linux","win32"]}}
---

# Company Tear Sheet Skill (Powered by QuantSet)

Produce a one-page company profile that a reader can check line by line, rendered as a clean, printable HTML document (`tearsheets/[TICKER]_[YYYY-MM-DD].html`). It reports what the filings and the market say. It does not give a rating or a price target of its own.

## Workflow Checklist

- [ ] **1. Pull the evidence in parallel** (resolve the listing, then snapshot, statements, estimates, peers, segments, debt, holders, insiders)
- [ ] **2. Build the seven sections**, computing only what you can trace
- [ ] **3. Run the 5-point check**
- [ ] **4. Render [tear-sheet-template.html](references/tear-sheet-template.html) and reply with a short summary + file path**

---

## Step 1: Parallel Evidence Gathering

Each call is written exactly as the QuantSet MCP tool accepts it; swap the sample ticker for the user's listing and pass `workflow="tear-sheet"` on tool calls (or `X-Workflow-Id: tear-sheet` on REST calls). Without MCP, call the QuantSet REST API (`X-API-Key` from `QUANTSET_API_KEY`, or `mw_demo` on sample listings; see `https://api.quantset.dev/skill.md`). The fields after each arrow are the ones this skill reads. On statement rows the line items sit under `values` (for example `values.revenue`); dates, `currency` and `accession` sit on the row itself.

1. **Resolve the name if no ticker was given:** `list_instruments(q="apple", limit=5)` → `instrument_id`, `name`, `exchange`, `country`, `asset_type`. If several listings match, ask which one.
2. **Header, price, valuation, balance sheet:** `get_company_snapshot(ticker="us:AAPL")` → `name`, `symbol`, `exchange`, `country`, `sector`, `industry`, `sic_description`, `employees`, `latest_date`, `price`, `quote_currency`, `financial_currency`, `market_cap_b`, `enterprise_value_b`, `high_52w`, `low_52w`, `change_1y_pct`, `beta`, `pe_ttm`, `pe_forward`, `ev_to_ebitda`, `ev_to_fcf`, `fcf_yield_pct`, `dividend_yield_pct`, `annual_dividend`, `roic_pct`, `roe_pct`, `total_debt`, `cash`, `net_debt_to_ebitda`, `share_count_change_1y_pct`, `fundamentals_as_of`, `balance_sheet_as_of`
3. **Financial summary** (one `kind` per call; six rows so that five years of growth can be shown):
   - `get_financial_statements(tickers=["us:AAPL"], kind="income", period="annual", limit_per_instrument=6)` → `period_end`, `currency`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `reported_diluted_eps`, `available_at`, `accession`, `form`
   - `get_financial_statements(tickers=["us:AAPL"], kind="cash_flow", period="annual", limit_per_instrument=6)` → `period_end`, `operating_cash_flow`, `free_cash_flow`
4. **Street estimates** (one `view` per call):
   - `get_estimates_and_earnings(view="estimates", ticker="us:AAPL", metric="revenue")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="estimates", ticker="us:AAPL", metric="eps")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="calendar", ticker="us:AAPL", start="2026-11-27", limit=4)` → `date`, `timing`
   - Set `start` to today and use the earliest `date` returned; no rows means the next report is not listed yet.
5. **Peers for the valuation comparison:** `get_peers(ticker="us:AAPL", limit=8)` → `instrument_id`, `name`, `group_basis`, `pe_ttm`, `pe_forward`, `fcf_yield_pct`, `dividend_yield_pct`
6. **Revenue segments:** `get_sec_filings(view="segments", ticker="us:AAPL", limit=60)` → `segment`, `period`, `flow`, `revenue`
7. **Debt schedule:** `get_sec_filings(view="debt_maturities", ticker="us:AAPL", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
8. **Top holders:** `get_sec_filings(view="institutional_ownership", ticker="us:AAPL", limit=10)` → `holder`, `report_date`, `shares`, `market_value_usd`, `pct`, `shares_change_qoq_pct`, `filing_date`
9. **Insider trades, last 12 months:** `get_sec_filings(view="insider_transactions", ticker="us:AAPL", start="2025-11-27", limit=1000)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `is_buy`, `shares`, `transaction_value`, `owners`, `filing_date`
   - Set `start` to one year before today. Without it the rows begin with the earliest years on file.

---

## Step 2: Build the Sections

1. **Business:** one line from the classification fields (`sector`, `industry`, `sic_description`) and `employees`, then the segment table: each segment's revenue and share of the total for the latest full fiscal year.
   - `flow` `Y` marks a full fiscal year and `Q` a single quarter; `period` names the fiscal quarter the row ends in. Use the latest `Y` rows and say which fiscal year they are (it can be a year behind the financial summary).
   - Segments are product lines or regions, as the company reports them; label the table accordingly. They carry revenue only, in the company's `financial_currency`; do not state a segment margin.
   - Describe what the company does only from these fields.
2. **Financial Summary:** the five latest fiscal years, oldest to newest, labelled by actual fiscal year from `period_end` (the sixth row exists only to compute the first growth figure):

| | FY | FY | FY | FY | FY |
|---|---|---|---|---|---|
| Revenue | | | | | |
| Revenue growth | | | | | |
| Gross margin | | | | | |
| Operating margin | | | | | |
| Net income | | | | | |
| Diluted EPS | | | | | |
| Operating cash flow | | | | | |
| Free cash flow | | | | | |

   Growth and margins are computed from the same column. State the unit once in the heading: billions of `financial_currency` to one decimal when the latest revenue is a billion or more, otherwise millions. Money and percentages that are negative go in parentheses; percentages to one decimal.
3. **Valuation vs. Peers:** the company's `pe_ttm`, `pe_forward`, `ev_to_ebitda`, `ev_to_fcf`, `fcf_yield_pct` and `dividend_yield_pct`, then `roic_pct`, `roe_pct` and `beta`.
   - Beside `pe_ttm`, `pe_forward`, `fcf_yield_pct` and `dividend_yield_pct`, show the peer median and how many peers it rests on. A median needs at least three peers with a value; otherwise write `n/a`. Leave negative P/E values out of the median.
   - Say whether the peer group is a sector or an industry group (`group_basis`).
4. **Street Estimates:** `Current Year` and `Next Year` revenue and EPS: consensus, low to high, analyst count, and growth against `year_ago`, labelled "vs. year-ago estimate basis". Add the next report date as the last row when the calendar returned one.
5. **Balance Sheet & Capital Return:** cash, total debt, net debt (`total_debt - cash`), `net_debt_to_ebitda`, debt due in the two years after the filing (`y1 + y2`, from the fiscal `year` on the row, read in `financial_currency`), dividend per share and yield, 1-year share-count change. `cash` is cash and equivalents only.
6. **Ownership & Insiders:** top five holders by `shares` with `market_value_usd` and quarter-on-quarter change, as of `report_date`.
   - Show `pct` only when the row carries it. `portfolio_weight_pct` is the stock's weight in the holder's own portfolio, not the share of the company held; never present it as ownership.
   - Insider trades: open-market sales (`transaction_code` `S`) and buys (`P`), with `is_10b5_1` true as scheduled, false as discretionary and `null` as not stated. Print the first and last `transaction_date` returned, because insider coverage can lag. No rows means `n/a`, not zero.
7. **What Stands Out:** three to five observations, each a number from the sheet and why a reader would care. No rating, no target price.

Print `country` with spaces in place of hyphens.

---

## Step 3: Mandatory 5-Point Check

Before writing the file, verify:
1. Every figure is on the page with its period or date, and its currency where it is money.
2. `null` values from QuantSet are shown as `n/a`, never as `0`, and never replaced with a remembered number.
3. No figure came from memory or a web search. A number not in a QuantSet response is computed from numbers that are (growth, margin, median, sum).
4. Annual columns come only from annual rows. Quarterly rows are not mixed in.
5. The `{{sources}}` slot names each call used and the date its data describes (`period_end`, `latest_date`, `as_of` or `report_date`), plus the `available_at` and `accession` of the latest annual report. Where a response carries no date, write `no date on row`.

---

## Step 4: Render HTML Deliverable

Read [references/tear-sheet-template.html](references/tear-sheet-template.html), fill every `{{slot}}` (tables as plain `<table>` markup, numeric cells with `class="num"`), write the finished file to `./tearsheets/[TICKER]_[YYYY-MM-DD].html`, and reply in chat with a 4-line summary + the saved file path. If you cannot write files, print the sheet in chat as Markdown in the same section order.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): show that section as `n/a`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
