---
name: dcf-valuation
description: "Runs a Reverse-DCF and two-stage (5- or 10-year) discounted cash flow valuation from filed financial statements, leading with what today's price implies plus Bear/Base/Bull scenarios, SBC-adjusted owner FCF, a net debt bridge and a 3x3 sensitivity matrix. Use when the user asks what a stock is worth, whether a company is overvalued or undervalued, for intrinsic or fair value, or what growth the share price implies. Covers 36,000+ companies in 67 countries. Free to try with mw_demo."
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
2. **Cash flows:** `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `available_at`, `accession`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - The newest row is the **base**: a `10-Q` row is the trailing twelve months to its `period_end`; any other row is the last fiscal year. Then keep the fiscal years (rows whose `form` is not `10-Q`), up to six.
   - `capex` is negative. If `free_cash_flow` is `null`, use `operating_cash_flow + capex`; if `capex` is `null` too, leave that year out and say so.
3. **Revenue and EBITDA:** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=10)` → `period_end`, `form`, `revenue`, `ebitda`, `weighted_average_diluted_shares`
   - Rolling rows often carry no revenue; the fiscal-year rows do. For a trailing base, use the snapshot `revenue_ttm` as the base-period revenue.
4. **Debt:** `get_financial_statements(tickers=["us:NVDA"], kind="balance_sheet", period="quarterly", limit_per_instrument=3)` → `period_end`, `accession`, `long_term_debt`, `current_portion_long_term_debt`, `notes_payable`, `convertible_debt`, `cash_and_equivalents`
   - Debt is the snapshot `total_debt`. When that is `null`, take the newest row here that carries an `accession` or any non-null debt line, add up the debt lines that have a value, and say you did. If every one is `null`, stop: without debt there is no equity bridge. Do not add lease lines.
   - `cash` is cash and equivalents only. Marketable securities are not in it, so net debt is overstated for a company holding a large investment portfolio; say so beside the bridge.
5. **Diluted shares:** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=2)` → `period_end`, `period_basis`, `weighted_average_diluted_shares`, `available_at`
   - When the share count is empty on the newest row, use the next row or the latest fiscal-year row from call 3.
6. **Stock-based compensation:** `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", start="2022-01-01", limit=200)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
   - Set `start` to three years before today (rows arrive unordered by `fact_id`, so `start` guarantees the newest `10-K` full-year row is inside the window). Keep `10-K` rows spanning a full year, take the latest `period_end`, and for that year the row with the latest `filed`.
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
2. **Normal-year check (catches heavy CapEx cycles):** compute FCF margin (`free_cash_flow / revenue`) for the 3 fiscal years before the base period. If the base is negative, or its margin differs from that 3-year median by more than **15%** of the median (for example, a hyperscaler spending surge), normalize the base to `median margin × base-period revenue`, note that you normalized it, and show the unadjusted reported-base value alongside.
3. **Stale base:** if the base period ended more than 200 days before `latest_date`, note that the base is stale.
4. **SBC Discipline:** report both FCF and **Owner FCF** (base FCF minus the latest fiscal year's stock-based compensation), and flag when SBC exceeds 15% of FCF or `share_count_change_1y_pct` is positive.
5. **Year-1 Growth ($g_1$) & 10-Year Smooth Fade:** average of consensus FY+1 revenue growth, consensus FY+2 revenue growth, and historical revenue CAGR over the newest fiscal years, capped at **20%** (raised to **28%** when both consensus years exceed 20% with `analyst_count` ≥ 5). Project over a **10-year** stage so durable compounders are not truncated at year 5 ($0.90\times$ annual fade when $g_1 \ge 12\%$, $0.80\times$ fade below $12\%$ so modest growers glide quickly to $g_\infty$ without a cliff jump at 12%).
6. **Three Scenarios + Both Bases in the Lead:** alongside the Base path, compute Bear ($0.65 \times g_1$, $WACC + 0.75\%$, $g_\infty - 0.5\%$) and Bull ($\min(\max(\text{raw growth}, 1.25 \times g_1), 35\%)$, $WACC - 0.75\%$, $g_\infty + 0.5\%$). Whenever the base FCF was normalized (e.g. a CapEx surge), print **both** the normalized Base value and the unadjusted reported-base value right in the lead line so neither choice is hidden.

---

## Step 4: Discount Rate, Terminal Value & the Bridge

- Find the company's `sector` in [sector-wacc.md](references/sector-wacc.md) and add the 10Y Treasury yield $R_f$ to the **midpoint** of that sector's spread band, applying the mega-cap / net-cash / small-cap / leverage adjustments in that file when inputs are present. Treat the result as $WACC$ (unless the user gave their own rate).
- **Terminal Growth ($g_\infty$):** **2.5%** by default (`2.0%` for `Energy`, `Materials`, `Utilities`), never above $R_f$.
- Bridge: $PV_{\text{stage 1}} + PV_{TV} = \text{Implied EV}$; $\text{Equity Value} = \text{Implied EV} - \text{Net Debt}$; $\text{Value / Share} = \text{Equity Value} / \text{Diluted Shares}$.

---

## Step 5: Mandatory Sanity Checks (Run Before Output)

1. **Reverse DCF ("What's Priced In" — Lead Finding):** solve for the constant $N$-year FCF growth rate that makes Value / Share equal today's `price`. Compare that market-implied growth rate directly against historical revenue CAGR and consensus growth—this is a fact about the price, not an opinion.
2. **Terminal Value & Exit Multiple:** state $PV_{TV} / \text{Implied EV}$ (flag above 82%) and $TV_N / FCF_N$ beside the peer median price-to-FCF (`100 / fcf_yield_pct`).
3. **Model Against Market:** when Base Value / Share differs from `price` by more than 45%, do **not** declare the stock over- or undervalued off one assumption set—lead with the Reverse DCF and the Bear/Base/Bull scenarios.
4. **Sensitivity Centre:** the centre cell of the 3×3 matrix must equal the Base Value / Share.

---

## Output Structure (Keep Concise — Findings First, Caveats Last)

Keep the whole report tight (~60–85 lines). Lead with the findings, not disclaimers:
1. **Top 3 Takeaways (3–4 lines max):** (a) **What's Priced In (Reverse DCF)** vs. historical/consensus growth; (b) **Bear / Base / Bull scenario range** + Owner FCF value; (c) the single biggest driver (e.g. normalized CapEx base, SBC share, or terminal multiple vs. peers).
2. **Scenario & Key Inputs Table:** compact Bear / Base / Bull table + 1-line summary of $R_f$, $WACC$, base FCF, net debt, and diluted shares.
3. **Cash Flow Trajectory & 3×3 Sensitivity Matrix:** stage cash flows + 3×3 WACC ($\text{base} \pm 1\%$) × Terminal Growth ($\text{base} \pm 0.5\%$) grid (centre cell = Base).
4. **Sources & Notes (Compact Footer):** one concise `Sources` table at the bottom + 2–3 one-line caveats/falsifiers. *(Not investment advice.)*

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
