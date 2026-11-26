---
name: dcf-valuation
description: Ask "What is NVDA worth?" or "Is PLTR overvalued?" to run a 5-year Discounted Cash Flow (DCF) valuation and Reverse-DCF ("What growth is priced in?") using live 10Y U.S. Treasury WACC, SBC-adjusted Owner FCF, Net Debt bridge, and a 3x3 sensitivity matrix.
metadata: {"clawdbot":{"emoji":"📐","os":["darwin","linux","win32"]}}
---

# Institutional DCF Valuation Skill (Powered by QuantSet)

Estimate intrinsic value per share from primary-source cash flows, live Treasury yields, and verified share counts—never guessed inputs.

## Workflow Checklist

Track every step explicitly:
- [ ] **1. Pull primary data in parallel** (cash flows, balance sheet, shares, snapshot, 10Y Treasury)
- [ ] **2. Check sector applicability** (redirect REITs to FFO and Banks/Insurers to ROE–P/B)
- [ ] **3. Compute normalized FCF & SBC-adjusted FCF** (5Y history + TTM discrete quarters)
- [ ] **4. Build live WACC** (live 10Y Treasury $R_f$ + [sector spread](references/sector-wacc.md))
- [ ] **5. Project Years 1–5 FCF (with fade) + Gordon Growth Terminal Value**
- [ ] **6. Bridge Enterprise Value → Equity Value → Intrinsic Value / Share**
- [ ] **7. Run 3×3 Sensitivity Matrix & Reverse-DCF ("What's Priced In")**
- [ ] **8. Execute 3 mandatory sanity checks before reporting**

---

## Step 1: Gather Ground-Truth Data (Parallel Calls)

Use QuantSet MCP tools if connected (pass `workflow="dcf-valuation"` on tool calls, or send header `X-Workflow-Id: dcf-valuation` on REST calls); otherwise call the QuantSet REST API (`X-API-Key` from `QUANTSET_API_KEY`, or `mw_demo` on sample tickers; if no key exists, see `https://api.quantset.dev/skill.md`).

1. **Annual & TTM Cash Flows:** `get_financial_statements` (`kind="cash_flow"`, `period="annual"`, `limit_per_instrument=6`) + (`period="quarterly"`, `limit_per_instrument=4`)
   - Extract Operating Cash Flow, CapEx, Free Cash Flow (`OCF - |CapEx|` if `free_cash_flow` is `null`), and Stock-Based Compensation (`stock_based_compensation`).
2. **Balance Sheet & Net Debt:** `get_financial_statements` (`kind="balance_sheet"`, `period="quarterly"`, `limit_per_instrument=1`)
   - Extract Total Debt, Cash & Short-Term Investments (`Net Debt = Total Debt - Cash & Short-Term Investments`; negative Net Debt = Net Cash).
3. **Diluted Share Count:** `GET /api/v1/shares-outstanding?ticker=NVDA` + `get_financial_statements` (`kind="income"`, `period="quarterly"`, `limit_per_instrument=1`)
   - Use latest **diluted** shares (never outdated cover-page basic shares when options/RSUs are material).
4. **Snapshot, Price, Consensus & Sector:** `get_company_snapshot` + `get_estimates_and_earnings`
   - Extract current `price`, `market_cap_b`, `enterprise_value_b`, `roic_pct`, `sector`, `security_type`, and FY+1 / FY+2 consensus revenue growth.
5. **Live Risk-Free Rate ($R_f$):** `get_macro_and_fx` (`view="treasury_yields"`, `limit=1`)
   - Read the latest 10-Year U.S. Treasury yield (`y10`) rather than hardcoding a stale constant.

---

## Step 2: Sector Guardrail (Do Not Force Unsuitable Models)

- **REITs (`security_type == "reit"`):** Stop standard GAAP FCF DCF; value using `ffo_ttm` and `price_to_ffo` from `get_company_snapshot` plus dividend sustainability.
- **Banks & Insurers:** Debt is operating inventory, not financing—use a Residual Income / ROE vs. Cost of Equity ($P/B = (ROE - g)/(K_e - g)$) framework instead of EV/FCF.

---

## Step 3: Normalize Base FCF & Growth Trajectory

1. Compute trailing-12-month (TTM) FCF from the 4 discrete quarterly cash-flow statements and compare against the latest fiscal year. If working-capital swings distorted TTM by >25%, anchor on normalized 3-year median FCF margin × latest revenue.
2. **SBC Discipline:** Report *both* standard Unlevered FCF and **Owner FCF (`FCF - Stock-Based Compensation`)** when SBC exceeds 15% of FCF, or explicitly account for ongoing annual share dilution (`share_count_change_1y_pct`). Never ignore SBC while holding share count flat.
3. **Base Year-1 Growth ($g_1$):** Anchor on consensus FY+1/FY+2 revenue growth blended with historical 5Y FCF CAGR, capped at **18%** (or **22%** only for hyper-growth compounders with verified consensus backing). Decay growth linearly by 10–15% per year toward terminal growth by Year 5.

---

## Step 4: Build Live WACC & Terminal Value

- Look up the company's sector in [sector-wacc.md](references/sector-wacc.md), add the live 10Y Treasury yield $R_f$, and apply company-specific adjustments (leverage, size, net cash).
- **Terminal Growth ($g_\infty$):** Default **2.5%** for USD compounders (never exceed the 10Y nominal Treasury yield $R_f$, and use **1.0%–2.0%** for cyclical/commodity/ex-growth businesses).
- **Formulas:**
  - $PV_{\text{stage 1}} = \sum_{t=1}^{5} \frac{FCF_t}{(1 + WACC)^t}$
  - $TV_5 = \frac{FCF_5 \times (1 + g_\infty)}{WACC - g_\infty}$, $\quad PV_{TV} = \frac{TV_5}{(1 + WACC)^5}$
  - $\text{Implied EV} = PV_{\text{stage 1}} + PV_{TV}$
  - $\text{Implied Equity Value} = \text{Implied EV} - \text{Net Debt}$
  - $\text{Fair Value / Share} = \frac{\text{Implied Equity Value}}{\text{Diluted Shares}}$

---

## Step 5: Mandatory Sanity Checks (Run Before Output)

1. **Terminal Value Dominance Check:** Compute $PV_{TV} / \text{Implied EV}$. If $>82\%$ for a mature issuer, flag terminal-assumption sensitivity explicitly.
2. **Implied Exit Multiple Cross-Check:** Compute $TV_5 / FCF_5$ (implied Year-5 exit P/FCF multiple). If $>30\times$, either $g_\infty$ is too high or $WACC$ is too low—explain or tighten.
3. **Reverse-DCF ("What's Priced In"):** Solve for the 5-year FCF CAGR required at your base $WACC$ to justify today's market price. Comparing *Implied Market Growth* vs. *Consensus Growth* is often more actionable than a single point target.

---

## Output Structure

Present a clean, decision-ready Markdown report (no fluff, every figure dated and currency-labeled):
1. **Executive Verdict:** Current Price vs. Base Intrinsic Value (% upside/downside), Reverse-DCF Implied 5Y FCF CAGR, and SBC-Adjusted Fair Value.
2. **Inputs & Provenance Table:** Live 10Y Treasury ($R_f$), WACC, Base TTM FCF, SBC, Net Debt, Diluted Shares, and SEC filing dates (`available_at`).
3. **5-Year Cash Flow Projection Table:** Year 1–5 Revenue/FCF growth, Projected FCF, Discount Factor, and Present Value.
4. **3×3 Sensitivity Matrix:** WACC ($\text{base} - 1\%$, $\text{base}$, $\text{base} + 1\%$) × Terminal Growth ($2.0\%$, $2.5\%$, $3.0\%$).
5. **Key Risks & Falsifiers:** 2–3 concrete operating metrics that would break the valuation. *(Not investment advice.)*

## Access & Continuation
- If `mw_demo` returns `403` (`outside the sandbox`), explain that `mw_demo` covers the 9 sample tickers and offer to create a free trial key with the user's email via `POST https://api.quantset.dev/api/v1/agent/signup` (see `https://api.quantset.dev/skill.md`).
- If a request returns `402` (`insufficient_credits`), mint a checkout link via `POST https://api.quantset.dev/api/v1/agent/checkout-link` and share `checkout_url` with the user.
