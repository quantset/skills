---
name: dcf-valuation
description: "Runs a 5-year discounted cash flow (DCF) valuation from filed financial statements, with a live 10-year Treasury discount rate, SBC-adjusted owner free cash flow, a net debt bridge, a reverse DCF and a 3x3 sensitivity matrix. Use when the user asks what a stock is worth, whether a company is overvalued or undervalued, for intrinsic or fair value, or what growth the share price implies. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"📐","os":["darwin","linux","win32"]}}
---

# Institutional DCF Valuation Skill (Powered by QuantSet)

Estimate intrinsic value per share from primary-source cash flows, live Treasury yields, and verified share counts—never guessed inputs.

## Workflow Checklist

- [ ] **Step 1. Pull the data in parallel**
- [ ] **Step 2. Check that a cash-flow DCF fits this company**
- [ ] **Step 3. Set the base cash flow, owner FCF and the growth path**
- [ ] **Step 4. Build the discount rate, terminal value and the bridge to a share price**
- [ ] **Step 5. Run the five sanity checks, the 3×3 matrix and the reverse DCF**
- [ ] **Step 6. Report, with a Sources table**

If you can run Python, do Steps 3 to 5 with [scripts/dcf_math.py](scripts/dcf_math.py): write the inputs to a JSON file in the layout documented at the top of the script, run `python scripts/dcf_math.py inputs.json`, and use its numbers and notes as they come. It needs only the standard library. If you cannot run code, follow the same steps by hand.

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

## Step 1: Gather Ground-Truth Data (Parallel Calls)

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="dcf-valuation"` on every call (REST: header `X-Workflow-Id: dcf-valuation`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

1. **Price, sector, cash:** `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `quote_currency`, `financial_currency`, `market_cap_b`, `total_debt`, `cash`, `sector`, `security_type`, `roic_pct`, `share_count_change_1y_pct`, `ffo_ttm`, `price_to_ffo`
2. **Cash flows:** `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=24)` → `period_end`, `form`, `available_at`, `accession`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - The newest row is the **base**: a `10-Q` row is the trailing twelve months to its `period_end`; any other row is the last fiscal year. Then keep the fiscal years (rows whose `form` is not `10-Q`), up to six.
   - `capex` is negative. If `free_cash_flow` is `null`, use `operating_cash_flow + capex`; if `capex` is `null` too, leave that year out and say so.
3. **Revenue and EBITDA:** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=24)` → `period_end`, `form`, `revenue`, `ebitda`, `weighted_average_diluted_shares`
   - Rolling rows often carry no revenue; the fiscal-year rows do. For a trailing base, use the snapshot `revenue_ttm` as the base-period revenue.
4. **Debt:** `get_financial_statements(tickers=["us:NVDA"], kind="balance_sheet", period="quarterly", limit_per_instrument=1)` → `period_end`, `long_term_debt`, `current_portion_long_term_debt`, `notes_payable`, `convertible_debt`, `cash_and_equivalents`
   - Debt is the snapshot `total_debt`. When that is `null`, add up the debt lines here that have a value and say you did. If every one is `null`, stop: without debt there is no equity bridge. Do not add lease lines.
   - `cash` is cash and equivalents only. Marketable securities are not in it, so net debt is overstated for a company holding a large investment portfolio; say so beside the bridge.
5. **Diluted shares:** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=1)` → `period_end`, `period_basis`, `weighted_average_diluted_shares`, `available_at`
   - When the share count is empty on that row, use the latest fiscal-year row from call 3.
6. **Stock-based compensation:** `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", limit=1000)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
   - Rows arrive unordered and each year appears in several filings. Keep `10-K` rows spanning a full year, take the latest `period_end`, and for that year the row with the latest `filed`.
7. **Consensus revenue:** `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `year_ago`, `analyst_count`, `as_of`
   - FY+1 growth = this fiscal year's `consensus / year_ago - 1`. FY+2 growth = next fiscal year's `consensus` divided by this fiscal year's, minus 1. Use `analyst_count` from this fiscal year's row.
8. **Risk-free rate ($R_f$):** `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`. Print its `date`; it can be several days old.
9. **Peers for the exit-multiple check:** `get_peers(ticker="us:NVDA", limit=8)` → `instrument_id`, `market_cap_b`, `fcf_yield_pct`

---

## Step 2: Does a Cash-Flow DCF Fit?

Stop and say so, without giving a value, when:
- **REITs (`security_type == "reit"`):** value on `ffo_ttm` and `price_to_ffo` from `get_company_snapshot` plus dividend sustainability.
- **Banks & Insurers (`sector` is `Financials`):** debt is operating inventory, not financing. Use a Residual Income / ROE vs. Cost of Equity ($P/B = (ROE - g)/(K_e - g)$) framework instead of EV/FCF.
- **No positive cash flow to grow:** the base free cash flow is negative and the 3-year median FCF margin is not positive either. Report what the company earns and invests, and that the price cannot be tested with this model.

---

## Step 3: Base FCF, Owner FCF & Growth Path

1. **Base FCF:** the base row from Step 1.2. State the period it covers.
2. **Normal-year check:** compute FCF margin (`free_cash_flow / revenue`) for the 3 fiscal years before the base period. If the base is negative, or its margin differs from that 3-year median by more than 25% of the median, the base is not a normal year (often a spending surge): use `median margin × base-period revenue` instead, say so in the verdict, and treat the result as low confidence. Either way, show the value on the normal-year base beside the value on the reported base, so the reader sees how much rests on this choice.
3. **Stale base:** if the base period ended more than 200 days before the price date (`latest_date`), say the base is stale and which way the results since then point.
4. **SBC Discipline:** always report both FCF and **Owner FCF** (the base FCF minus the latest fiscal year's stock-based compensation, whatever period the base covers), and call it out when SBC exceeds 15% of FCF or the share count is rising (`share_count_change_1y_pct` above zero).
5. **Year-1 Growth ($g_1$):** the average of consensus FY+1 revenue growth, consensus FY+2 revenue growth, and the historical revenue CAGR over the six newest fiscal years, capped at **18%**. Raise the cap to **22%** only when both consensus rates exceed 22% and `analyst_count` is at least 5. Few companies sustain more than that for five years; the reverse DCF shows what the market assumes instead.
6. **Fade:** each later year grows at 87.5% of the previous year's rate (Year 2 = $g_1 \times 0.875$, and so on), never below the base-case $g_\infty$. Growth reverts toward the economy's; the user may give a different path, and then you say so.

---

## Step 4: Discount Rate, Terminal Value & the Bridge

- Find the company's `sector` in [sector-wacc.md](references/sector-wacc.md) and add the 10Y Treasury yield $R_f$ to the **midpoint** of that sector's spread band. Apply an adjustment from that file only when the data for it is on hand, and say which you applied. Treat the result as the discount rate ($WACC$).
- **Terminal Growth ($g_\infty$):** **2.5%** by default, never above $R_f$. Use **2.0%** for `Energy`, `Materials` and `Utilities`, whose volumes track the economy. Say which you used.
- **Formulas:**
  - $PV_{\text{stage 1}} = \sum_{t=1}^{5} \frac{FCF_t}{(1 + WACC)^t}$
  - $TV_5 = \frac{FCF_5 \times (1 + g_\infty)}{WACC - g_\infty}$, $\quad PV_{TV} = \frac{TV_5}{(1 + WACC)^5}$
  - $\text{Implied EV} = PV_{\text{stage 1}} + PV_{TV}$; $\text{Equity Value} = \text{Implied EV} - \text{Net Debt}$; $\text{Fair Value / Share} = \frac{\text{Equity Value}}{\text{Diluted Shares}}$

---

## Step 5: Mandatory Sanity Checks (Run Before Output)

1. **Terminal Value Dominance:** compute $PV_{TV} / \text{Implied EV}$. Above $82\%$, say that the value is mostly the terminal assumption.
2. **What the Terminal Value Assumes:** state $TV_5 / FCF_5$, the multiple of year-5 cash flow the model says the company is then worth, beside the peer median price-to-FCF from Step 1.9 (`100 / fcf_yield_pct`, peers with a yield between 0 and 100 only, at least three of them). The first depends only on the discount rate and terminal growth; a market that pays far more is assuming growth lasts beyond year 5.
3. **Reverse DCF ("What's Priced In"):** solve for the constant 5-year FCF growth, followed by $g_\infty$, that makes Fair Value / Share equal today's `price`, starting from the same base you valued.
4. **Model Against Market:** when the model value differs from the price by more than 50% in either direction, treat the result as low confidence. A five-year model with capped growth cannot explain a gap that wide: lead the verdict with what the price implies, and do not call the stock over- or undervalued by that figure.
5. **Sensitivity Centre:** the centre cell of the 3×3 matrix must equal the base Fair Value / Share. Every cell uses the same growth path.

---

## Output Structure

A decision-ready Markdown report, every figure dated and currency-labelled:
1. **Executive Verdict:** current price vs. model value (% difference), the reverse-DCF growth, the SBC-adjusted value and the normal-year value. When the result is low confidence (normalized or stale base, or a gap above 50%), lead with what the price implies.
2. **Inputs & Provenance Table:** $R_f$ and its date, spread and adjustments, WACC, base FCF and its period, SBC, debt and where it came from, cash, diluted shares, with filing dates (`available_at`).
3. **5-Year Cash Flow Projection Table:** Year 1–5 growth, FCF, discount factor, present value.
4. **3×3 Sensitivity Matrix:** WACC ($\text{base} - 1\%$, $\text{base}$, $\text{base} + 1\%$) × Terminal Growth ($\text{base} - 0.5\%$, $\text{base}$, $\text{base} + 0.5\%$), so the centre cell is the base case.
5. **Key Risks & Falsifiers:** 2–3 concrete operating metrics that would break the valuation. *(Not investment advice.)*
6. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end`, `date`, `as_of` or `latest_date`), when it was filed or published where the row says (`available_at` or `filed`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no such date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): write `not available` for that input, name the call, and keep going. An input the model cannot run without, such as the risk-free rate, may come from the user instead, labelled user-supplied. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
