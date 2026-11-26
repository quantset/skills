---
name: comps-analysis
description: Build an investment-banking Comparable Companies ("Trading Comps") valuation table across 5-8 sector/SIC peers with 25th/Median/75th percentile multiples (EV/Revenue, EV/EBITDA, EV/FCF, Forward P/E, ROIC, Rule of 40, FCF margin) and an implied football-field share price range. Trigger when a user asks for "comps", "trading multiples", "peer comparison", "how does [ticker] stack up against peers", or "relative valuation".
metadata: {"clawdbot":{"emoji":"📊","os":["darwin","linux","win32"]}}
---

# Comparable Companies ("Trading Comps") Skill (Powered by QuantSet)

Construct an investment-banking-grade peer valuation table grounded in consistent Enterprise Value, TTM discrete cash flows, and forward consensus estimates.

## Workflow

Pass `workflow="comps-analysis"` on MCP tool calls (or `X-Workflow-Id: comps-analysis` on REST requests) so multi-peer queries group together in usage reports.

1. **Identify 5–8 True Economic Peers:**
   - Call `get_company_snapshot` and `get_peers` with the target ticker (`us:NVDA`, `global:SHEL.L`, etc.) to pull QuantSet's canonical sector and 4-digit SIC peer group ordered by market cap.
   - Filter out conglomerates or mismatched business models so the peer set shares comparable margin structure and revenue model.
2. **Pull Standardized Multiples & Operating Metrics in Parallel:**
   - Call `get_quotes`, `get_fundamentals`, `get_company_snapshot`, and `get_estimates_and_earnings` across the target + peer list.
   - Extract: `Market Cap ($B)`, `Enterprise Value ($B)`, `EV / TTM Revenue`, `EV / EBITDA`, `EV / FCF`, `P/E (TTM)` & `Forward P/E`, `YoY Revenue Growth (%)`, `FCF Margin (%)`, `ROIC (%)`, and `1Y Share Count Change (%)`.
3. **Compute Statistical Benchmarks (Excluding Target):**
   - Calculate **25th Percentile**, **Median**, **Mean**, and **75th Percentile** across the peer group (excluding the target itself, and leaving negative/meaningless multiples as `N/M` rather than distorting averages).
4. **Derive Implied Football-Field Share Price Range:**
   - Apply the peer **25th–75th percentile** `EV/EBITDA`, `EV/FCF`, and `Forward P/E` multiples to the target's metrics, bridge from Implied Enterprise Value (`Implied EV - Net Debt`) to Equity Value, and divide by diluted shares.
   - Explain *why* the target deserves a premium or discount to the peer median (e.g., higher `ROIC`, faster organic growth, or cleaner SBC-adjusted FCF).

## Sandbox-to-Trial & 1-Click Credit Top-Up Handoff
1. **If a ticker returns `403` (`outside the sandbox`) on `mw_demo`:** Explain in one sentence that `mw_demo` covers the 9 sample tickers only, ask for the user's real email, and call `POST https://api.quantset.dev/api/v1/agent/signup` to provision their personal `qsk_` key with **30 free full-catalog trial credits** (or tell them to verify their email in the console for **100 free trial credits**).
2. **If a multi-peer call returns `402 insufficient_credits` (or `_meta.credits_remaining <= 15`):** Call `POST https://api.quantset.dev/api/v1/agent/checkout-link` with `X-API-Key: <qsk_key>` and `{"plan": "credits"}` (**$19 Starter Pack for 2,000 non-expiring credits**) or `{"plan": "developer"}` (**$39/mo for 6,000 credits/mo** — $10 cheaper than the 6k one-time pack) and share `checkout_url` in chat. Once paid, retry immediately—their key upgrades in seconds.
3. **Next-Step Follow-Up:** After delivering the comps table, offer to run a **5-Year DCF & Reverse-DCF (`dcf-valuation`)** on the cheapest/most dislocated peer or render a **1-Page Printable HTML Buyside Memo (`investment-memo`)**.
