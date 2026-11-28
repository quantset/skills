---
name: investment-memo
description: "Writes a printable HTML long or short equity memo with a variant view against consensus, bear, base and bull scenarios built from the Street's own estimate range, an asymmetry check, falsifiable tripwires and filing citations. Use when the user asks for an investment memo, stock pitch, long or short thesis, or bull and bear case on a company. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📄","os":["darwin","linux","win32"]}}
---

# Buyside Investment Memo Skill (Powered by QuantSet)

Produce an opinionated, falsifiable buyside equity memo rendered as a clean, printable HTML document (`memos/[SYMBOL]_[DIRECTION]_[YYYY-MM-DD].html`).

## Workflow Checklist

- [ ] **Step 1. Frame the setup and pull the evidence in parallel**
- [ ] **Step 2. Build the scenarios, the variant view and the thesis**
- [ ] **Step 3. Run the 6-point self-critique**
- [ ] **Step 4. Render [memo-template.html](references/memo-template.html) and reply with a short summary + file path**

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

## Step 1: Frame the Setup, Then Gather Evidence in Parallel

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="investment-memo"` on every call (REST: header `X-Workflow-Id: investment-memo`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

**Frame:** direction is `LONG` unless the user asks for a short thesis. "A long memo" and "a short memo" can mean direction or length: take them as direction, and say in your reply which reading you took so the user can correct it. Horizon is 12 months unless they give one. If the user gave a name, resolve it: `list_instruments(q="toyota", limit=5)` → `instrument_id`, `name`, `exchange`, `asset_type`. Take the company's own shares, not a fund built on them; take the listing the user named, otherwise the `us:` listing when there is one, because the filing datasets cover US listings.

1. **Snapshot and peers:**
   - `get_company_snapshot(ticker="us:NVDA")` → `name`, `symbol`, `sector`, `latest_date`, `price`, `native_close`, `quote_currency`, `financial_currency`, `usd_rate`, `market_cap_b`, `enterprise_value_b`, `pe_ttm`, `forward_eps`, `roic_pct`, `fcf_yield_pct`, `rev_growth_yoy_pct`, `change_6m_pct`, `change_1y_pct`, `total_debt`, `cash`, `share_count_change_1y_pct`, `fundamentals_as_of`
   - `get_peers(ticker="us:NVDA", limit=8)` → `instrument_id`, `name`, `group_basis`, `market_cap_b`, `rev_growth_yoy_pct`, `roic_pct`, `pe_ttm`
2. **Financials** (one `kind` per call):
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `currency`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `ebitda`, `reported_diluted_eps`, `weighted_average_diluted_shares`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=8)` → `period_end`, `period_basis`, `revenue`, `operating_income`, `net_income`
   - Keep the five newest fiscal years.
3. **Street consensus** (one `view` per call):
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="eps")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`, `as_of`
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `low`, `high`, `analyst_count`, `year_ago`
   - `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct` (US listings only)
   - `get_estimates_and_earnings(view="consensus", ticker="us:NVDA")` → `current_price`, `target_low_price`, `target_mean_price`, `target_high_price`, `next_earnings_date`, `short_pct_of_float`, `observed_on`
   - Price targets are per share in the listing's own currency.
4. **Segments, debt, insiders, holders** (US listings only):
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=60)` → `segment`, `period`, `flow`, `revenue`
   - `get_sec_filings(view="debt_maturities", ticker="us:NVDA", limit=1)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-01-15", transaction_code="P,S", limit=300)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `transaction_value`, `owners`, `filing_date`
   - `get_sec_filings(view="institutional_ownership", ticker="us:NVDA", limit=15)` → `holder`, `report_date`, `shares`, `market_value_usd`, `put_call`, `shares_change_qoq_pct`, `filing_date`
   - `year` on the debt row is the fiscal year of the filing, and `y1` and `y2` are the amounts due in the first and second year after it.
   - Set `start` to one year before today. Count open-market sales (`transaction_code` `S`) and buys (`P`) only; `is_10b5_1` true is scheduled, false discretionary, `null` not stated. Print the earliest and latest `transaction_date` among the rows. Leave out holder rows whose `put_call` is set. `flow` `Y` marks a full fiscal year of segment revenue and `Q` a single quarter.
5. **ETF crowding:** `get_etf_data(ticker="us:NVDA", view="exposures", limit=25)` → `fund_symbol`, `fund_name`, `weight_pct`, `market_value`, `as_of`. Drop rows whose `as_of` is more than a year old.
6. **Hurdle rate:** `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`. It is the US dollar risk-free return the expected return has to beat; for a non-dollar listing say that it is a dollar rate.

---

## Step 2: Scenarios, Variant View, Thesis

Work in the listing's own currency: the price is `native_close` in `quote_currency`.

1. **Scenario targets, by rule.** Each target is next fiscal year's EPS times a P/E.
   - **P/E today** = `native_close` divided by this fiscal year's consensus EPS.
   - **Base:** next fiscal year's `consensus` EPS × the P/E today.
   - **Bear:** next fiscal year's `low` EPS × 0.8 × the P/E today.
   - **Bull:** next fiscal year's `high` EPS × 1.2 × the P/E today.
   - **Probabilities:** 25% bear, 50% base, 25% bull.
   - The estimate range is the Street's own disagreement; the one-fifth move in the multiple and the probabilities are defaults. Change a default only for a reason you write in the memo, and show both the default and your figure.
   - When either of those consensus EPS figures is missing or not positive, there is no earnings-based target: say so, give the consensus price targets (`target_low_price`, `target_mean_price`, `target_high_price`) as the range, and mark the scenario table `n/a`.
   - When the latest fiscal year's filed `reported_diluted_eps` is not positive, the P/E today rests on forecast earnings alone: say so beside the table and hold conviction at Medium or lower.
2. **Bear / Base / Bull table:** probability, EPS and where it comes from, the matching revenue estimate, P/E, target price, and % return against the current price (`class="pos"` or `class="neg"`).
   - Returns are the position's: for `LONG`, the price change; for `SHORT`, its negative. The favourable case is Bull for a long and Bear for a short.
   - **Expected Return** = $\sum p_i r_i$ of the position. **Asymmetry Ratio** = the favourable case's gain divided by the adverse case's loss. If Asymmetry $< 2.0\times$, write `"Weak (<2.0x)"` in the header strip rather than massaging numbers.
   - **Conviction:** High when Asymmetry is at least 2.0× and the expected return is at least 10 points above `yield_10y_pct`; Medium when Asymmetry is at least 1.0× and the expected return is positive; otherwise Low. When the expected return is negative, the numbers do not support the direction: say so in the header strip and in the first line of your reply.
3. **Variant View (3 sentences max):** what the price implies (the P/E today against the consensus growth, and the move over six and twelve months), where the filed results point away from consensus (a margin or growth figure from the statements against what the estimates imply), and why.
4. **Falsifiable Thesis Bullets (3–5 `<li>` items):** every bullet MUST follow:
   `<li><strong>[Specific Claim]</strong> — [Dated numerical evidence]. <em>Wrong if: [observable quarterly tripwire].</em></li>`
   Never write vague adjectives ("strong moat", "great management") without bps/percentage figures.
5. **Steelmanned Bear Case:** write the Bear paragraph as if pitching the opposite side of the trade (specific margin compression, debt due, SBC dilution, or competitive displacement), with numbers.

**Where each piece goes in the template:** peers and segments in `{{business_snapshot}}`; the P/E today, consensus and price targets in `{{whats_priced_in}}`; holders, insiders and ETF crowding in `{{ownership_and_insiders}}`; debt due in the next two years and the next report date (`next_earnings_date`) as rows of `{{risks_and_catalysts_table}}`. These three slots take block markup, so tables are allowed in them.

---

## Step 3: Mandatory 6-Point Self-Critique

Before writing the HTML file, verify:
1. Every number carries its currency and its period or date. The `{{provenance_citations}}` slot has one line per call used, with the date it describes and, where the row carries them, `available_at` and `accession`. For a listing outside the US those are absent: write "no filing date on row".
2. `null` values from QuantSet are reported as unavailable—never replaced with `0` or invented numbers. Sections that returned `unsupported_instrument` say `n/a (US listings only)`.
3. The Bear narrative is at least as specific and persuasive as the Bull narrative.
4. Every risk row includes an **observable numerical tripwire** (not a generic platitude).
5. No figure came from memory or a web search. A number not in a QuantSet response is computed (show the formula) or user-supplied (say so).
6. Scenario probabilities sum to 100%, each target equals its own row's EPS times its P/E, and any default you changed is shown beside your figure.

---

## Step 4: Render HTML Deliverable

Read [references/memo-template.html](references/memo-template.html), fill every `{{slot}}` cleanly, write the finished file to `./memos/[SYMBOL]_[LONG|SHORT]_[YYYY-MM-DD].html` using the symbol without its market prefix, and reply in chat with a tight 4-line summary header + the saved file path. If you cannot write files, print the memo in chat in the same section order.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): mark that evidence `not available`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
