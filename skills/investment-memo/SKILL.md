---
name: investment-memo
description: Draft a printable 1-page Swiss-editorial HTML Buyside Investment Memo (Long or Short) with a Variant View vs. Street consensus, Bear/Base/Bull driver scenarios, asymmetry ratio check (>=2.0x), falsifiable thesis tripwires, Form 4/13F/ETF crowding audit, and SEC filing citations. Trigger when a user asks to "write an investment memo", "pitch [ticker]", "long/short writeup", "thesis memo", or "research memo on [ticker]".
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

Use QuantSet MCP tools if connected (passing `workflow="investment-memo"` on tool calls or `X-Workflow-Id: investment-memo` on REST calls); otherwise call the QuantSet REST API (`X-API-Key` from `QUANTSET_API_KEY`, or `mw_demo` on sample listings; see `https://api.quantset.dev/skill.md` to auto-provision a key).

1. **Snapshot, Valuation & Peers:** `get_company_snapshot` and `get_peers`
2. **5Y Annual + 4Q Discrete Financials:** `get_financial_statements` (`income`, `balance_sheet`, `cash_flow`)
3. **Street Consensus & 8Q Beat/Miss Streak:** `get_estimates_and_earnings`
4. **Segments, Debt Maturity, Form 4 Insiders & 13F:** `get_sec_filings` (views `segments`, `debt_maturities`, `insider_transactions` and `institutional_ownership`), plus `GET /api/v1/shares-outstanding?ticker=NVDA`
5. **Passive / ETF Crowding:** `get_etf_data` (`etf-exposures` — top funds holding the stock and weight)
6. **Risk-Free Rate Context:** `get_macro_and_fx` (`treasury_yields`)

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
1. Every number cites its currency, period, and SEC filing/snapshot vintage (`provenance_citations`).
2. `null` values from QuantSet are reported as unavailable—never replaced with `0` or invented consensus numbers.
3. Bear narrative is at least as specific and persuasive as the Bull narrative.
4. Every risk row includes an **observable numerical tripwire** (not a generic platitude).

---

## Step 4: Render HTML Deliverable

Read [references/memo-template.html](references/memo-template.html), fill every `{{slot}}` cleanly, write the finished file to `./memos/[TICKER]_[LONG|SHORT]_[YYYY-MM-DD].html`, and reply in chat with a tight 4-line summary header + the saved file path.

## Sandbox-to-Trial & 1-Click Credit Top-Up Handoff
- If `mw_demo` hits `403`, ask for the user's email and call `POST https://api.quantset.dev/api/v1/agent/signup` to mint a personal `qsk_` key with **30 free trial credits**.
- If a call hits `402 insufficient_credits` (or `_meta.credits_remaining <= 15`), call `POST https://api.quantset.dev/api/v1/agent/checkout-link` (`{"plan": "credits"}` for **$19 / 2,000 credits** or `{"plan": "developer"}` for **$39/mo / 6,000 credits/mo**) and share `checkout_url` so the user can fund their key in 1 click.
