---
name: tear-sheet
description: "Builds a printable HTML company tear sheet: 5-year financial summary, valuation against peers, Street estimates, revenue segments, balance sheet, top holders and insider trades, every figure dated and sourced. Use when the user asks for a tear sheet, one-pager, company profile, fact sheet, snapshot or overview of a public company. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🗂️","os":["darwin","linux","win32"]}}
---

# Company Tear Sheet Skill (Powered by QuantSet)

Produce a company profile that a reader can check line by line, rendered as a clean, printable HTML document (`tearsheets/[SYMBOL]_[YYYY-MM-DD].html`). It reports what the filings and the market say. It does not give a rating or a price target of its own.

## Workflow Checklist

- [ ] **Step 1. Pull the evidence in parallel**
- [ ] **Step 2. Build the seven sections**, computing only what you can trace
- [ ] **Step 3. Run the 5-point check**
- [ ] **Step 4. Render [tear-sheet-template.html](references/tear-sheet-template.html) and reply with a short summary + file path**

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

---

## Step 1: Parallel Evidence Gathering

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="tear-sheet"` on every call (REST: header `X-Workflow-Id: tear-sheet`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

1. **Resolve the name if no ticker was given:** `list_instruments(q="apple", limit=5)` → `instrument_id`, `name`, `exchange`, `country`, `asset_type`
   - A company name also returns funds built on the stock. Take the company's own shares, and its `us:` listing when it has one (the filing datasets cover US listings). Ask only when two different companies match.
2. **Header, price, valuation, balance sheet:** `get_company_snapshot(ticker="us:AAPL")` → `name`, `symbol`, `exchange`, `country`, `sector`, `industry`, `sic_description`, `employees`, `latest_date`, `price`, `native_close`, `quote_currency`, `financial_currency`, `market_cap_b`, `enterprise_value_b`, `high_52w`, `low_52w`, `change_1y_pct`, `beta`, `pe_ttm`, `forward_eps`, `current_fy_estimate_as_of`, `sic_code`, `fcf_yield_pct`, `dividend_yield_pct`, `annual_dividend`, `dividend_basis`, `roic_pct`, `roe_pct`, `total_debt`, `cash`, `share_count_change_1y_pct`, `fundamentals_as_of`, `balance_sheet_as_of`
3. **Financial summary** (one `kind` per call):
   - `get_financial_statements(tickers=["us:AAPL"], kind="income", period="annual", limit_per_instrument=24)` → `period_end`, `form`, `currency`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `ebitda`, `reported_diluted_eps`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:AAPL"], kind="cash_flow", period="annual", limit_per_instrument=24)` → `period_end`, `form`, `operating_cash_flow`, `free_cash_flow`
   - Keep the six newest fiscal years (the sixth only feeds the first growth figure).
4. **Street estimates** (one `view` per call):
   - `get_estimates_and_earnings(view="estimates", ticker="us:AAPL", metric="revenue")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="estimates", ticker="us:AAPL", metric="eps")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="calendar", ticker="us:AAPL", start="2026-01-15", limit=4)` → `date`, `timing`
   - Set `start` to today's date and use the earliest `date` returned. With no rows, use `next_earnings_date` from the next call.
   - `get_estimates_and_earnings(view="consensus", ticker="us:AAPL")` → `next_earnings_date`, `target_mean_price`, `shares_short`, `short_pct_of_float`, `held_pct_insiders`, `held_pct_institutions`, `observed_on`
5. **Peers:** `get_peers(ticker="us:AAPL", limit=12)` → `instrument_id`, `name`, `group_basis`, `peer_group`, `sic_code`, `market_cap_b`, `pe_ttm`, `fcf_yield_pct`, `dividend_yield_pct`
6. **Revenue segments:** `get_sec_filings(view="segments", ticker="us:AAPL", limit=60)` → `segment`, `period`, `flow`, `revenue`
7. **Debt schedule:** `get_sec_filings(view="debt_maturities", ticker="us:AAPL", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
8. **Top holders:** `get_sec_filings(view="institutional_ownership", ticker="us:AAPL", limit=15)` → `holder`, `report_date`, `shares`, `market_value_usd`, `pct`, `put_call`, `shares_change_qoq_pct`, `filing_date`
9. **Insider trades, last 12 months:** `get_sec_filings(view="insider_transactions", ticker="us:AAPL", start="2025-01-15", limit=1000)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `shares`, `transaction_value`, `filing_date`
   - Set `start` to one year before today. Without it the rows begin with the earliest years on file.

---

## Step 2: Build the Sections

1. **Business:** one line naming the `sector` and the `industry` (once, when `sic_description` repeats it), then the segment table: each segment's revenue and share of the total for the latest full fiscal year.
   - `flow` `Y` marks a full fiscal year and `Q` a single quarter; `period` is a label for the calendar quarter the row ends in. Use the latest `Y` rows and say which fiscal year they are; it can be a year behind the financial summary.
   - Segments are product lines or regions, as the company reports them. Read which from the names and label the table that way. They carry revenue only, in `financial_currency`; do not state a segment margin.
   - Describe what the company does only from these fields. `employees` carries no date; print it as "latest on file".
2. **Financial Summary:** the five latest fiscal years, oldest to newest, labelled by fiscal year from `period_end`:

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

   Growth and margins are computed within the column. State the unit once in the heading: billions of `financial_currency` to one decimal when the latest revenue is a billion or more, otherwise millions; per-share rows are in currency units. Negative figures go in parentheses. Percentages to one decimal throughout the sheet.
3. **Valuation vs. Peers:** trailing P/E (`pe_ttm`), forward P/E (`price / forward_eps`, computed), EV / EBITDA and EV / FCF (from `enterprise_value_b` and the latest fiscal-year `ebitda` and `free_cash_flow`, labelled with that fiscal year), `fcf_yield_pct`, `dividend_yield_pct`, then `roic_pct`, `roe_pct` and `beta`.
   - Forward P/E rests on `forward_eps`; cite `current_fy_estimate_as_of` as its date.
   - Peer median beside trailing P/E, FCF yield and dividend yield, with the number of peers behind it. First leave out peers whose `market_cap_b` is `null` or below 1. Then use the peers that share the company's `sic_code` when at least three remain; otherwise use the whole list and say it is a broad sector group. Within each measure, leave out a non-positive P/E and a yield outside -100 to 100 (the peer stays in the other measures). A median needs at least three values; otherwise `n/a`.
   - Name the peers behind the medians in a note, so the reader can judge how comparable they are.
   - A company whose `dividend_basis` is `no_recorded_dividends` shows "none recorded" for dividend yield, here and in section 5.
4. **Street Estimates:** `Current Year` and `Next Year` revenue and EPS, each labelled with its `period_end`: consensus, low to high, analyst count, and growth against `year_ago`, headed "vs. year-ago, estimate basis" (it can differ from the reported figure). The last row is the next report date, or "not listed yet".
5. **Balance Sheet & Capital Return:** cash, debt, net debt (`debt - cash`), net debt to the latest fiscal-year EBITDA, debt due in the two years after the schedule's fiscal `year` (`y1 + y2`), dividend per share and yield, 1-year share-count change.
   - `year` is the fiscal year of the filing the schedule comes from, and `y1` is the amount due in the year after it.
   - If `total_debt` and the schedule total (`y1` through `after5`) differ by more than 20% of the larger, print both, say they disagree, and do not present net cash as fact. In the header's Net Debt / EBITDA tile, use the schedule total and add "debt figures disagree".
   - `cash` is cash and equivalents only.
6. **Ownership & Insiders:** the top five holders by `shares`, leaving out rows whose `put_call` is set (options positions), with `market_value_usd` and quarter-on-quarter change, as of `report_date`.
   - Above the table, give the share of the company held by institutions and by insiders (`held_pct_institutions`, `held_pct_insiders`) and the share of the float sold short (`short_pct_of_float`), as of `observed_on`.
   - Show `pct` only when the row carries it. `portfolio_weight_pct` is the stock's weight in the holder's own portfolio, not the share of the company held; never present it as ownership.
   - Insider trades: count open-market sales (`transaction_code` `S`) and buys (`P`) only; other codes are awards, exercises, gifts and tax withholding. One sale is often reported as many rows at different prices, so give the number of distinct sale dates, the shares and the value, not the row count. Split the sales by `is_10b5_1`: true is scheduled, false is discretionary, `null` is not stated. Print the earliest and latest `transaction_date` among the rows, because coverage can stop short of today. No rows at all means `n/a`; rows with no buys means "none in the rows returned".
7. **What Stands Out:** three to five observations, each a number from the sheet and why a reader would care. Include any disagreement between figures you found. No rating, no target price.

Print `country` with spaces in place of hyphens. For a listing outside the US, show the price as `native_close` in `quote_currency` and say that market cap and enterprise value are in US dollars.

---

## Step 3: Mandatory 5-Point Check

Before writing the file, verify:
1. Every figure is on the page with its period or date, and its currency where it is money.
2. `null` values from QuantSet are shown as `n/a`, never as `0`, and never replaced with a remembered number.
3. No figure came from memory or a web search. A number not in a QuantSet response is computed from numbers that are (growth, margin, median, sum, ratio).
4. Annual columns come only from fiscal-year rows.
5. The `{{sources}}` slot names each call used and the date its data describes (`period_end`, `latest_date`, `as_of` or `report_date`), plus the `available_at` and `accession` of the latest annual report. Where a response carries no date, write `no date on row`.

---

## Step 4: Render HTML Deliverable

Read [references/tear-sheet-template.html](references/tear-sheet-template.html), fill every `{{slot}}` (tables as plain `<table>` markup, numeric cells with `class="num"`), write the finished file to `./tearsheets/[SYMBOL]_[YYYY-MM-DD].html` using the symbol without its market prefix, and reply in chat with a 4-line summary + the saved file path. If you cannot write files, print the sheet in chat as Markdown in the same section order.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): show that section as `n/a`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
