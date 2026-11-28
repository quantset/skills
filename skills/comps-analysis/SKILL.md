---
name: comps-analysis
description: "Builds a comparable companies (trading comps) table with EV/Revenue, EV/EBIT, EV/EBITDA, EV/FCF, trailing and forward P/E, growth, FCF margin and ROIC, leading with peer-percentile positioning (25th/median/75th) and why the target trades at a premium or discount. Use when the user asks how a company compares with its peers, for trading multiples, relative valuation or a peer table. Covers 52,000+ stocks in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📊","os":["darwin","linux","win32"]}}
---

# Comparable Companies ("Trading Comps") Skill (Powered by QuantSet)

Build a peer valuation table in which every multiple compares like with like: one enterprise value per company, and revenue, EBITDA and free cash flow from the same fiscal year.

## Workflow Checklist

- [ ] **Step 1. Find the peers**
- [ ] **Step 2. Pull each company's snapshot, fiscal-year figures and debt**
- [ ] **Step 3. Compute multiples, benchmarks and the implied price range**
- [ ] **Step 4. Report, with a Sources table**

If you can run Python, do Step 3 with [scripts/comps_stats.py](scripts/comps_stats.py): write the companies to a JSON file in the layout documented at the top of the script, run `python scripts/comps_stats.py comps.json`, and use its table and notes as they come. It needs only the standard library. If you cannot run code, apply the same rules by hand.

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

## Step 1: Find the Peers

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="comps-analysis"` on every call (REST: header `X-Workflow-Id: comps-analysis`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

- Target first: `get_company_snapshot(ticker="us:AMD")` → `sic_code`, `sector`, `market_cap_b` (the full field list is in Step 2)
- `get_peers(ticker="us:AMD", limit=12)` → `instrument_id`, `name`, `group_basis`, `peer_group`, `sic_code`, `sic_description`, `market_cap_b`, `rev_growth_yoy_pct`, `net_margin_pct`
- Keep up to 8 peers, and at least 5 when the list allows, by these rules in order. List the ones you dropped with the reason:
  1. Drop a peer whose `market_cap_b` is `null` or below 1: ratios on companies that small are unstable.
  2. Prefer peers with the target's own `sic_code`. If fewer than five share it, fill from the rest of the list.
  3. Keep the largest by `market_cap_b`.
- The list is a starting universe. `group_basis` often says `sector` even when the rows share an industry code, and a sector group can mix unrelated businesses: say what the group is. You may drop a peer for a business reason only if you state it as your own judgement.
- **Financials:** when the target's `sector` is `Financials`, enterprise-value multiples do not apply. Compare on P/E only and say so.

## Step 2: Pull the Figures (One Batch per Statement)

1. **Snapshot, one call per company, target included:** `get_company_snapshot(ticker="us:AMD")` → `price`, `latest_date`, `market_cap_b`, `enterprise_value_b`, `total_debt`, `cash`, `revenue_ttm`, `operating_income_ttm`, `fundamentals_basis`, `fundamentals_as_of`, `pe_ttm`, `forward_eps`, `rev_growth_yoy_pct`, `roic_pct`, `share_count_change_1y_pct`, `sector`, `sic_code`, `quote_currency`, `financial_currency`
2. **Fiscal-year income, all companies in one call:** `get_financial_statements(tickers=["us:AMD", "us:NVDA", "us:AVGO"], kind="income", period="annual", limit_per_instrument=5)` → `instrument_id`, `period_end`, `form`, `currency`, `revenue`, `ebitda`, `weighted_average_diluted_shares`
3. **Fiscal-year cash flow, all companies in one call:** `get_financial_statements(tickers=["us:AMD", "us:NVDA", "us:AVGO"], kind="cash_flow", period="annual", limit_per_instrument=5)` → `instrument_id`, `period_end`, `form`, `free_cash_flow`
4. **Debt, all companies in one call:** `get_financial_statements(tickers=["us:AMD", "us:NVDA", "us:AVGO"], kind="balance_sheet", period="quarterly", limit_per_instrument=3)` → `instrument_id`, `period_end`, `accession`, `long_term_debt`, `current_portion_long_term_debt`, `notes_payable`, `convertible_debt`
   - Per company take the newest row that carries an `accession` or any non-null debt line (a month-end provider stub can sit above the filed `10-Q` with `null` debt lines; skip that stub). If quarterly balance sheets still have no debt line, check the fiscal-year balance sheet (`period="annual"`, `limit_per_instrument=2`) before declaring EV unavailable.

For each company take the newest fiscal-year row (drop `form` `10-Q` rows first) from calls 2 and 3. The target's diluted share count is `weighted_average_diluted_shares` on that row. A company that reports in another currency than the dollar stays out of the enterprise-value multiples unless you convert with `usd_rate`; say which you left out.

## Step 3: Multiples, Benchmarks, Implied Range

- **Debt:** the snapshot `total_debt`; when it is `null`, the sum of the debt lines from call 4 that have a value.
- **Enterprise value:** `enterprise_value_b`; when it is `null`, `market_cap_b × 1e9 + debt - cash`, marked as computed. With no debt figure at all, the company has no enterprise value: show `n/a`.
- **Trailing multiples:** when `fundamentals_basis` is `ttm`, EV / Revenue uses `revenue_ttm` and EV / EBIT uses `operating_income_ttm`, both as of `fundamentals_as_of`. These are the current, like-for-like multiples. For a company on another basis, EV / Revenue falls back to the fiscal year and EV / EBIT is `n/a`.
- **Fiscal-year multiples:** EV / EBITDA and EV / FCF use the fiscal-year row, because it is the one whose period is stated; the snapshot's `ebitda_ttm` and `free_cash_flow` can repeat the last fiscal year. Label them with the fiscal year. When that year ended more than 270 days before the price date they are stale: say so, and rest the conclusion on the trailing multiples.
- **P/E:** trailing P/E is `pe_ttm`. Forward P/E is the snapshot's `pe_forward` when it has a value, otherwise `price / forward_eps`; use one method for every company in the table and say which.
- **Not meaningful:** a multiple that is zero or negative is `N/M`; a missing one is `n/a`. Neither enters a benchmark.
- **Benchmarks, peers only:** 25th percentile, median and 75th percentile by linear interpolation, with the number of peers behind each. A benchmark needs at least three peers.
- **Implied share price:**
  - EV / EBIT, EV / EBITDA and EV / FCF: `(peer multiple × the target's own figure for that multiple - net debt) / diluted shares`, where `net debt = debt - cash`.
  - Forward P/E: `peer multiple × forward_eps`. This is already a price per share; do not subtract debt or divide by shares.
- Explain *why* the target deserves a premium or discount to the peer median, using numbers from the table.

## Output Format (Keep Concise — Positioning First, Caveats Last)

Keep the report crisp (~55–80 lines). Lead with where the company sits against its peers, not missing-field disclaimers:
1. **Top 3 Takeaways (3–4 lines max):** where the target sits against peer quartiles on valuation (Fwd P/E, EV/Rev, EV/FCF) vs. fundamentals (revenue growth, FCF margin, ROIC), and whether its growth/returns explain its premium or discount. *(Note: cyclical peak earnings—e.g. memory semiconductors at peak margins—naturally produce single-digit forward P/Es; explain cyclicality rather than calling it a data error.)*
2. **Peer Table + Quartile Benchmarks** (target first, then peers by market cap, followed immediately by the 25th / Median / 75th / Count rows):

| Company | Mkt Cap ($B) | EV ($B) | EV / Revenue | EV / EBIT | EV / EBITDA (FY) | EV / FCF (FY) | P/E (TTM) | Fwd P/E | Rev Growth YoY | FCF Margin (FY) | ROIC | 1Y Share Chg | Fiscal year end |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

3. **Illustrative Mechanical Peer-Multiple Translation (Optional Context at Bottom):** show what applying peer 25th/median/75th multiples to the target's figures produces mathematically, explicitly framed as an illustration rather than a price target. *(Not investment advice.)*
4. **Sources & Scope Notes (Compact Footer):** one compact `Sources` table + 1–2 short lines on any dropped peers or fiscal-year mismatches.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end` or `latest_date`), when it was filed or published where the row says (`available_at`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no such date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): write `n/a` for that column, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
