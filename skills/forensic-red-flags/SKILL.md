---
name: forensic-red-flags
description: Run a 7-point short-seller forensic accounting, earnings-quality, SBC dilution, 24-month debt-wall, segment decay, and Form 4 Rule 10b5-1 insider-selling audit on any public company. Trigger when a user asks for "red flags", "earnings quality", "accounting check", "short thesis check", "SBC dilution", "insider selling audit", or "balance sheet risk" on a stock.
metadata: {"clawdbot":{"emoji":"🔍","os":["darwin","linux","win32"]}}
---

# Forensic Accounting & Red-Flag Audit Skill (Powered by QuantSet)

Systematically audit an issuer across **7 institutional forensic checks** using primary SEC XBRL disclosures, Form 4 Rule 10b5-1 flags, debt maturity walls, and share-count history.

## The 7-Point Forensic Checklist

Execute parallel QuantSet MCP or REST calls (`get_financial_statements`, `get_estimates_and_earnings`, `get_sec_filings`, `get_company_snapshot`, `get_etf_data`, passing `workflow="forensic-red-flags"` or header `X-Workflow-Id: forensic-red-flags`) and score each dimension **CLEAN**, **WATCH**, or **RED FLAG**:

### 1. Cash Conversion Divergence (`OCF` & `FCF` vs. `GAAP Net Income`)
- Compare trailing 4 quarters and last 3 fiscal years of Operating Cash Flow and Free Cash Flow against GAAP Net Income.
- **Flag (`WATCH` / `RED FLAG`):** Net income growing while OCF/FCF stagnates or turns negative for $\ge 2$ consecutive periods, or `Accounts Receivable` / `Inventory` growing $>15\%$ faster than `Revenue` (channel-stuffing / working-capital bloat).

### 2. GAAP vs. Street "Adjusted" EPS Spread
- Compare GAAP diluted EPS (`get_financial_statements` `income`) against Street non-GAAP actuals/estimates (`get_estimates_and_earnings`).
- **Flag:** Non-GAAP EPS exceeding GAAP EPS by $>35\%$ persistently, or widening every year due to "recurring one-time" restructuring and stock-based compensation add-backs.

### 3. Stock-Based Compensation (SBC) & Share-Count Creep
- Pull `stock_based_compensation` (from `cash_flow`) as a % of Revenue and % of FCF, alongside historical share counts (`shares_outstanding` / `share_count_change_1y_pct`).
- **Flag:** `SBC > 20%` of Operating Cash Flow while diluted share count expands $>2\%/\text{yr}$ (or management touts buybacks that fail to offset RSU dilution).

### 4. Debt Maturity Wall & Refinancing Squeeze
- Pull `debt_maturities` (`get_sec_filings` / `/api/v1/debt-maturities?ticker=NVDA`), `balance_sheet` cash + debt, and live U.S. Treasury yields (`get_macro_and_fx`).
- **Flag:** Debt maturing within the next 24 months exceeding `(Cash + 1.5× TTM FCF)`, or `Net Debt / EBITDA > 3.5x` facing higher refinancing coupons.

### 5. Form 4 Insider Selling: Unscheduled vs. Rule 10b5-1
- Pull `insider_activity` and granular Form 4 rows (`/api/v1/sec/insider-transactions`), separating tax-withholding dispositions (code `F`) and pre-scheduled **Rule 10b5-1** trades from discretionary open-market sales (`S`) and cluster buys (`P`).
- **Flag:** Multiple C-suite/CFO discretionary open-market sales (`S`, non-10b5-1) within 60 days, or zero open-market insider purchases despite a >35% drawdown.

### 6. Segment Decay Masked by Consolidated Headline Growth
- Pull `segments` (`/api/v1/segments?ticker=NVDA`) and check whether core high-margin segment growth is decelerating while low-margin or acquired revenue masks the consolidated top line.

### 7. Passive / Thematic ETF Crowding Risk
- Pull `etf-exposures` (`get_etf_data`) to see which ETFs hold the largest % weight in the stock—flagging mechanical rebalance/outflow vulnerability if concentrated in leveraged or single-theme funds.

---

## Output Format

1. **Forensic Scorecard Table:** 1 row per check (`1–7`), Status (`CLEAN` / `WATCH` / `RED FLAG`), Key Metric, and Exact Filing Citation (`available_at` / period).
2. **Deep-Dive Findings:** Concrete numbers on every `WATCH` or `RED FLAG` item (preserving `null` where unreported—never guessing `0`).
3. **Questions for Management / Next 10-Q Watchlist:** 3 falsifiable line items to check on the next filing day. *(Analytical audit only — not investment advice.)*
4. **Next-Step Follow-Up & Credit Handoff:**
   - Offer to stress-test the valuation with a **Reverse-DCF (`dcf-valuation`)** or generate a **Printable 1-Page HTML Short/Long Memo (`investment-memo`)** incorporating these forensic flags.
   - If `mw_demo` returned `403`, ask for the user's email and call `POST https://api.quantset.dev/api/v1/agent/signup` (`30 free trial credits`). If a call returns `402 insufficient_credits` (or `_meta.credits_remaining <= 10`), call `POST https://api.quantset.dev/api/v1/agent/checkout-link` (`{"plan": "credits"}` for **$19 / 2,000 credits** or `{"plan": "developer"}` for **$39/mo / 6,000 credits/mo**) and share `checkout_url` in chat.
