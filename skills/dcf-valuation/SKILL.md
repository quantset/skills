---
name: dcf-valuation
description: Ask "What is NVDA worth?" or "Is SHEL.L overvalued?" to run a 5-year Discounted Cash Flow (DCF) valuation and Reverse-DCF across 36,000+ US and international companies in 67 countries using live 10Y Treasury WACC, SBC-adjusted Owner FCF, Net Debt bridge, and a 3x3 sensitivity matrix. Free to try with mw_demo.
metadata: {"clawdbot":{"emoji":"📐","os":["darwin","linux","win32"]}}
---

# Institutional DCF Valuation Skill (Powered by QuantSet)

Estimate intrinsic value per share from primary-source cash flows, live Treasury yields, and verified share counts—never guessed inputs.

## Workflow Checklist

Track every step explicitly:
- [ ] **1. Pull primary data in parallel** (snapshot, cash flows, revenue, shares, SBC, consensus, 10Y Treasury, peers)
- [ ] **2. Check sector applicability** (redirect REITs to FFO and Banks/Insurers to ROE–P/B)
- [ ] **3. Set base FCF, SBC-adjusted Owner FCF & the growth path**
- [ ] **4. Build live WACC** (live 10Y Treasury $R_f$ + [sector spread](references/sector-wacc.md)), **Terminal Value & the EV → Equity → Per-Share bridge**
- [ ] **5. Run 4 mandatory sanity checks, the 3×3 Sensitivity Matrix & Reverse-DCF ("What's Priced In")**
- [ ] **6. Report with a Sources table**

---

## Step 1: Gather Ground-Truth Data (Parallel Calls)

Each call is written exactly as the QuantSet MCP tool accepts it; swap the sample ticker for the user's listing and add `workflow="dcf-valuation"` to every call (REST: header `X-Workflow-Id: dcf-valuation`). Without MCP, call the QuantSet REST API (`X-API-Key` from `QUANTSET_API_KEY`, or `mw_demo` on sample tickers; if no key exists, see `https://api.quantset.dev/skill.md`). The fields after each arrow are the ones this skill reads. On statement rows the line items sit under `values` (for example `values.free_cash_flow`); dates, `period_basis` and `accession` sit on the row itself.

1. **Snapshot, price, balance sheet:** `get_company_snapshot(ticker="us:NVDA")` → `price`, `latest_date`, `market_cap_b`, `enterprise_value_b`, `total_debt`, `cash`, `balance_sheet_as_of`, `free_cash_flow`, `cash_flow_as_of`, `cash_flow_basis`, `revenue_ttm`, `sector`, `security_type`, `roic_pct`, `share_count_change_1y_pct`, `ffo_ttm`, `price_to_ffo`, `financial_currency`
   - `Net Debt = total_debt - cash` (negative = net cash). Dollar fields are in units of `financial_currency`; `market_cap_b` and `enterprise_value_b` are in billions.
   - `cash` is cash and equivalents only. Marketable securities are not in it, so net debt is overstated for a company holding a large investment portfolio; say so beside the bridge.
   - `cash_flow_basis` names the period `free_cash_flow` covers (a fiscal year or a trailing twelve months). Label the base with it.
2. **Annual cash flows (6 years):** `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="annual", limit_per_instrument=6)` → `period_end`, `available_at`, `accession`, `operating_cash_flow`, `capex`, `free_cash_flow`
   - `capex` is negative. If `free_cash_flow` is `null`, use `operating_cash_flow + capex`; if `capex` is `null` too, leave that year out and say so.
3. **Annual revenue (6 years):** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="annual", limit_per_instrument=6)` → `period_end`, `revenue`
4. **Quarterly cash flows (TTM check):** `get_financial_statements(tickers=["us:NVDA"], kind="cash_flow", period="quarterly", limit_per_instrument=4)` → `period_end`, `period_basis`, `operating_cash_flow`, `free_cash_flow`
   - Read `period_basis` on every row. Sum the four rows into TTM **only** when all four say `discrete_quarter`. Any other basis holds year-to-date figures, and adding them overstates cash flow several times over; in that case use the snapshot `free_cash_flow` dated `cash_flow_as_of`.
5. **Diluted shares:** `get_financial_statements(tickers=["us:NVDA"], kind="income", period="quarterly", limit_per_instrument=1)` → `weighted_average_diluted_shares`, `period_end`, `available_at`
6. **Stock-based compensation:** `get_sec_filings(view="company_facts", ticker="us:NVDA", concept="ShareBasedCompensation", limit=1000)` → `value`, `period_start`, `period_end`, `form`, `filed`, `accession`
   - Rows arrive unordered. Keep the `10-K` rows whose period spans a full year, sort by `period_end`, and take the latest years. When a year appears in more than one filing, use the row with the latest `filed`. `10-Q` rows are year-to-date, so never add them to a full year.
7. **Consensus revenue:** `get_estimates_and_earnings(view="estimates", ticker="us:NVDA", metric="revenue")` → `period`, `period_end`, `consensus`, `year_ago`, `analyst_count`, `as_of`
   - FY+1 growth = `Current Year` `consensus / year_ago - 1`. FY+2 growth = `Next Year` `consensus` / `Current Year` `consensus` `- 1`.
8. **Live risk-free rate ($R_f$):** `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`
9. **Peers for the exit-multiple check:** `get_peers(ticker="us:NVDA", limit=8)` → `instrument_id`, `market_cap_b`, `fcf_yield_pct`, `pe_ttm`

---

## Step 2: Sector Guardrail (Do Not Force Unsuitable Models)

- **REITs (`security_type == "reit"`):** Stop standard GAAP FCF DCF; value using `ffo_ttm` and `price_to_ffo` from `get_company_snapshot` plus dividend sustainability.
- **Banks & Insurers:** Debt is operating inventory, not financing—use a Residual Income / ROE vs. Cost of Equity ($P/B = (ROE - g)/(K_e - g)$) framework instead of EV/FCF.

---

## Step 3: Base FCF, Owner FCF & Growth Path

1. **Base FCF:** TTM FCF when Step 1.4 allows it, otherwise the latest fiscal-year FCF (the snapshot `free_cash_flow`). State the period it covers. If `cash_flow_as_of` is more than two quarters before the price date (`latest_date`), say in the verdict that the base is stale and which way the results since then point.
2. **Normalization check:** Compute FCF margin (`free_cash_flow / revenue`) for each of the last 3 fiscal years. If the base year's margin differs from the 3-year median by more than 25% of the median, anchor on `median margin × base-period revenue` and say so.
3. **SBC Discipline:** Always report both FCF and **Owner FCF (`FCF - Stock-Based Compensation`)**, and call it out when SBC exceeds 15% of FCF or the share count is rising (`share_count_change_1y_pct` above zero). Never ignore SBC while holding share count flat.
4. **Year-1 Growth ($g_1$):** the average of consensus FY+1 revenue growth, consensus FY+2 revenue growth, and the historical FCF CAGR over the annual rows that have FCF (say how many years), capped at **18%**. Raise the cap to **22%** only when both consensus growth rates exceed 22% and `analyst_count` is at least 5.
5. **Fade:** each later year grows at 87.5% of the previous year's rate (Year 2 = $g_1 \times 0.875$, and so on), never below $g_\infty$.

---

## Step 4: Build Live WACC, Terminal Value & the Bridge

- Look up the company's sector in [sector-wacc.md](references/sector-wacc.md) and add the live 10Y Treasury yield $R_f$ to its spread. Use the midpoint of the sector's spread band unless a note in that row or a company-specific adjustment below it applies (leverage, size, net cash), and say which you used. Treat the result as the discount rate ($WACC$).
- **Terminal Growth ($g_\infty$):** Default **2.5%** for USD compounders (never exceed the 10Y nominal Treasury yield $R_f$, and use **1.0%–2.0%** for cyclical/commodity/ex-growth businesses). Say which you chose and why.
- **Formulas:**
  - $PV_{\text{stage 1}} = \sum_{t=1}^{5} \frac{FCF_t}{(1 + WACC)^t}$
  - $TV_5 = \frac{FCF_5 \times (1 + g_\infty)}{WACC - g_\infty}$, $\quad PV_{TV} = \frac{TV_5}{(1 + WACC)^5}$
  - $\text{Implied EV} = PV_{\text{stage 1}} + PV_{TV}$
  - $\text{Implied Equity Value} = \text{Implied EV} - \text{Net Debt}$
  - $\text{Fair Value / Share} = \frac{\text{Implied Equity Value}}{\text{Diluted Shares}}$

---

## Step 5: Mandatory Sanity Checks (Run Before Output)

1. **Terminal Value Dominance Check:** Compute $PV_{TV} / \text{Implied EV}$. If $>82\%$, flag terminal-assumption sensitivity explicitly.
2. **Implied Exit Multiple Cross-Check:** Compute $TV_5 / FCF_5$ (implied Year-5 exit P/FCF multiple). If $>30\times$, either $g_\infty$ is too high or $WACC$ is too low—explain or tighten. Then compare it with the peer median price-to-FCF from Step 1.9 (`100 / fcf_yield_pct`, peers with a positive yield only). If the two differ by more than 1.5× in either direction, explain why; the peer figure is today's trailing multiple and the exit multiple is five years out.
3. **Reverse-DCF ("What's Priced In"):** Solve for the constant 5-year FCF CAGR, followed by $g_\infty$, that makes Fair Value / Share equal today's `price` at your base $WACC$. Comparing *Implied Market Growth* vs. *Consensus Growth* is often more actionable than a single point target; when they point opposite ways from the base case, say so in the verdict.
4. **Sensitivity Centre Check:** The centre cell of the 3×3 matrix must equal the base Fair Value / Share. If it does not, the matrix is wrong—rebuild it.

---

## Output Structure

Present a clean, decision-ready Markdown report (no fluff, every figure dated and currency-labeled):
1. **Executive Verdict:** Current Price vs. Base Intrinsic Value (% upside/downside), Reverse-DCF Implied 5Y FCF CAGR, and SBC-Adjusted Fair Value.
2. **Inputs & Provenance Table:** Live 10Y Treasury ($R_f$), WACC, Base FCF and the period it covers, SBC, Net Debt, Diluted Shares, and SEC filing dates (`available_at`).
3. **5-Year Cash Flow Projection Table:** Year 1–5 FCF growth, Projected FCF, Discount Factor, and Present Value.
4. **3×3 Sensitivity Matrix:** WACC ($\text{base} - 1\%$, $\text{base}$, $\text{base} + 1\%$) × Terminal Growth ($\text{base} - 0.5\%$, $\text{base}$, $\text{base} + 0.5\%$), so the centre cell is the base case.
5. **Key Risks & Falsifiers:** 2–3 concrete operating metrics that would break the valuation. *(Not investment advice.)*
6. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`period_end`, `date`, `as_of` or `fundamentals_as_of`), when it was filed or published (`available_at` or `filed`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no filing date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- Never fill a gap from memory or a web search. Write `not available` and name the call that returned `null`.
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): write `not available` for that input, name the call, and keep going. An input the model cannot run without, such as the risk-free rate, may come from the user instead, labelled user-supplied. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
