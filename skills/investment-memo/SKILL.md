---
name: investment-memo
description: Ask "Write a Long or Short investment memo on AAPL" to generate a printable 1-page HTML equity memo across 36,000+ US and global companies (67 countries) with a Variant View vs. consensus, Bear/Base/Bull scenarios, asymmetry ratio check, falsifiable tripwires, and SEC filing citations. Free to try with mw_demo.
metadata: {"clawdbot":{"emoji":"📄","os":["darwin","linux","win32"]}}
---

# Buyside Investment Memo Skill (Powered by QuantSet)

Produce an opinionated, falsifiable buyside equity memo rendered as a clean, printable HTML document (`memos/[TICKER]_[DIRECTION]_[YYYY-MM-DD].html`).

## Workflow Checklist

- [ ] **1. Frame the setup** (`ticker`, `LONG` or `SHORT`, `horizon` default 12m)
- [ ] **2. Pull primary evidence in parallel** (statements, segments, consensus, snapshot/peers, insiders/13F, ETF exposure, 10Y Treasury)
- [ ] **3. Derive the Variant View** (where evidence diverges from Street consensus)
- [ ] **4. Build driver-based Bear / Base / Bull scenarios** (probabilities = 100%, check Upside/Downside asymmetry $\ge 2.0\times$)
- [ ] **5. Run mandatory 6-point Self-Critique Pass**
- [ ] **6. Render [memo-template.html](references/memo-template.html) and output concise summary + file path**

---

## Step 1: Parallel Evidence Gathering

Each call is written exactly as the QuantSet MCP tool accepts it; swap the sample ticker for the user's listing and pass `workflow="investment-memo"` on tool calls (or `X-Workflow-Id: investment-memo` on REST calls). Without MCP, call the QuantSet REST API (`X-API-Key` from `QUANTSET_API_KEY`, or `mw_demo` on sample listings; see `https://api.quantset.dev/skill.md` to auto-provision a key). The fields after each arrow are the ones this skill reads. On statement rows the line items sit under `values` (for example `values.revenue`); dates, `period_basis` and `accession` sit on the row itself.

1. **Snapshot, Valuation & Peers:**
   - `get_company_snapshot(ticker="us:NVDA")` → `name`, `sector`, `price`, `market_cap_b`, `enterprise_value_b`, `pe_ttm`, `pe_forward`, `ev_to_ebitda`, `ev_to_fcf`, `roic_pct`, `fcf_margin_pct`, `fcf_yield_pct`, `rev_growth_yoy_pct`, `total_debt`, `cash`, `share_count_change_1y_pct`, `fundamentals_as_of`
   - `get_peers(ticker="us:NVDA", limit=8)` → `instrument_id`, `name`, `market_cap_b`, `rev_growth_yoy_pct`, `roic_pct`, `pe_forward`, `fcf_yield_pct`
2. **5Y Annual + Recent Quarterly Financials** (one `kind` per call):
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=5)` → `period_end`, `revenue`, `gross_profit`, `operating_income`, `net_income`, `reported_diluted_eps`, `available_at`, `accession`
   - `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=5)` → `period_end`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - `get_financial_statements(tickers=["us:NVDA"], kind="balance_sheet", period="quarterly", limit_per_instrument=1)` → `period_end`, `cash_and_equivalents`, `long_term_debt`, `total_equity`, `shares_outstanding`
   - `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=4)` → `period_end`, `period_basis`, `revenue`, `operating_income`, `weighted_average_diluted_shares`
   - Use quarterly rows side by side only when `period_basis` matches; a row that is not `discrete_quarter` is year-to-date.
3. **Street Consensus & 8Q Beat/Miss Streak** (one `view` per call):
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `high`, `low`, `year_ago`, `analyst_count`, `as_of`
   - `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="eps")` → `period`, `consensus`, `high`, `low`, `year_ago`
   - `get_estimates_and_earnings(view="earnings", ticker="us:NVDA", limit=8)` → `period_end`, `actual_eps`, `estimated_eps`, `surprise_pct`
   - `get_estimates_and_earnings(view="consensus", ticker="us:NVDA")` → `target_low_price`, `target_mean_price`, `target_high_price`, `upside_pct`, `observed_on`
4. **Segments, Debt Maturity, Form 4 Insiders & 13F:**
   - `get_sec_filings(view="segments", ticker="us:NVDA", limit=60)` → `segment`, `period`, `flow`, `revenue`
   - Segment rows carry revenue only. `flow` `Y` marks a full fiscal year and `Q` a single quarter, and `period` names the fiscal quarter the row ends in. Segments are product lines or regions, as the company reports them.
   - `get_sec_filings(view="debt_maturities", ticker="us:NVDA", limit=3)` → `year`, `y1`, `y2`, `y3`, `y4`, `y5`, `after5`
   - `get_sec_filings(view="insider_transactions", ticker="us:NVDA", start="2025-11-27", limit=1000)` → `transaction_date`, `transaction_code`, `is_10b5_1`, `is_buy`, `transaction_value`, `owners`, `filing_date`
   - Set `start` to one year before today. Without `start` the rows begin with the earliest years on file. Treat `is_10b5_1` true as scheduled, false as discretionary and `null` as not stated, and print the first and last `transaction_date` returned, because insider coverage can lag.
   - `get_sec_filings(view="institutional_ownership", ticker="us:NVDA", limit=20)` → `holder`, `report_date`, `shares`, `market_value_usd`, `shares_change_qoq_pct`, `position_change`, `filing_date`
   - `portfolio_weight_pct` on these rows is the stock's weight in the holder's own portfolio, not the share of the company held. Do not present it as ownership.
5. **Passive / ETF Crowding:** `get_etf_data(ticker="us:NVDA", view="exposures", limit=10)` → `fund_symbol`, `fund_name`, `weight_pct`, `as_of` (top funds holding the stock and weight)
6. **Risk-Free Rate Context:** `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`

---

## Step 2: Construct Driver-Based Scenarios & Falsifiable Pillars

1. **Variant View (3 sentences max):** State *what the market prices in*, *where our FY+1/FY+2 operating driver diverges from consensus*, and *why*.
2. **Falsifiable Thesis Bullets (3–5 `<li>` items):** Every bullet MUST follow:
   `<li><strong>[Specific Claim]</strong> — [Dated numerical evidence]. <em>Wrong if: [observable quarterly tripwire].</em></li>`
   Never write vague adjectives ("strong moat", "great management") without bps/percentage figures.
3. **Bear / Base / Bull Table:**
   - Specify for each case: Probability (must sum to 100%), Revenue CAGR, Operating/FCF Margin, Exit Multiple, Implied Target Price, and % Return vs. Current Price (`class="pos"` or `class="neg"`).
   - Compute **Expected Return** ($\sum p_i r_i$) and **Asymmetry Ratio** ($|\text{Bull Return}| / |\text{Bear Return}|$). If Asymmetry $< 2.0\times$, flag `"Weak (<2.0x)"` explicitly in the header strip rather than massaging numbers.
4. **Steelmanned Bear Case:** Write the Bear paragraph as if pitching the opposite side of the trade (specific margin compression, debt wall, SBC dilution, or competitive displacement).

---

## Step 3: Mandatory Self-Critique Pass

Before writing the HTML file, verify:
1. Every number cites its currency, period, and SEC filing/snapshot vintage in the `{{provenance_citations}}` slot: one line per call used, with the date it describes (`period_end` or `as_of`), when it was filed (`available_at` or `filing_date`) and the `accession` when the row carries one.
2. `null` values from QuantSet are reported as unavailable—never replaced with `0` or invented consensus numbers.
3. Bear narrative is at least as specific and persuasive as the Bull narrative.
4. Every risk row includes an **observable numerical tripwire** (not a generic platitude).
5. No figure came from memory or a web search. A number not in a QuantSet response is computed (show the formula) or user-supplied (say so).
6. Scenario probabilities sum to 100% and each implied target price follows from its own row's growth, margin and multiple.

---

## Step 4: Render HTML Deliverable

Read [references/memo-template.html](references/memo-template.html), fill every `{{slot}}` cleanly, write the finished file to `./memos/[TICKER]_[LONG|SHORT]_[YYYY-MM-DD].html`, and reply in chat with a tight 4-line summary header + the saved file path. If you cannot write files, print the memo in chat in the same section order.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): mark that evidence `not available`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
