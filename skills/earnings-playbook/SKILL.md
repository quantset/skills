---
name: earnings-playbook
description: Generate an institutional Pre-Earnings Expectation Matrix ("What's the Bar?") or Post-Earnings Beat/Miss Flash Note with 8-quarter surprise streak, Street consensus Revenue/EPS bar, segment margin swing drivers, positioning/ETF crowding, and a Bull/Base/Bear reaction matrix. Trigger when a user asks for "earnings preview", "earnings setup", "post-earnings analysis", "how did [ticker] do this quarter", or "upcoming earnings".
metadata: {"clawdbot":{"emoji":"📅","os":["darwin","linux","win32"]}}
---

# Institutional Earnings Preview & Post-Earnings Update Skill (Powered by QuantSet)

Run either a **Pre-Earnings Setup Brief** (before the print) or a **Post-Earnings Flash Update** (within 48h after results) using verified consensus bars, discrete quarterly statements, and segment trends.

## Mode A: Pre-Earnings Setup ("What's the Bar?")
Pass `workflow="earnings-playbook"` on MCP tool calls (or `X-Workflow-Id: earnings-playbook` on REST requests).

1. **Report Date & Consensus Bar:** Call `get_estimates_and_earnings` (`earnings_calendar` + `estimates` + `analyst_ratings`) to pull the scheduled report date, FYQ/FY consensus Revenue & EPS (mean, low, high, analyst count), and current price-target distribution.
2. **8-Quarter Beat/Miss Track Record:** Pull `earnings` history to quantify the company's historical EPS/revenue beat rate and typical magnitude.
3. **Positioning & Crowding Check:** Pull `get_price_history` (30-day & 90-day run-up into the print vs. `index:SPX`), `insider_activity` (any discretionary Form 4 sales ahead of blackout), and `etf-exposures`.
4. **3 Key Swing Variables:** Pull `segments` and quarterly `income`/`cash_flow` margins to name the exact 2–3 segment or margin lines that will drive the post-print move, framed as a crisp **Bull / Base / Bear reaction matrix**.

## Mode B: Post-Earnings Update ("What Changed?")
1. **Headline Beat / Miss Table:** Compare reported Revenue, Gross Margin, Operating Income, GAAP EPS, Non-GAAP EPS, and FCF against consensus and YoY/QoQ baselines—quantifying variances in both `$` and `bps`/`%`.
2. **Quality of the Beat:** Check whether an EPS beat came from genuine operating-margin expansion or low-quality tax-rate/buyback/working-capital releases (`OCF` vs. `Net Income`).
3. **Thesis & Estimate Impact:** State clearly whether the print **strengthens, leaves intact, or breaks** the prior thesis, with updated forward multiples (`Forward P/E`, `EV/FCF`).

## Sandbox-to-Trial & 1-Click Credit Top-Up Handoff
1. **If the ticker or `/api/v1/calendar/earnings` returns `403` on `mw_demo`:** Ask for the user's real email and call `POST https://api.quantset.dev/api/v1/agent/signup` to provision their personal `qsk_` key with **30 free full-catalog trial credits**, then run the earnings setup immediately.
2. **If a call returns `402 insufficient_credits` (or `_meta.credits_remaining <= 10`):** Call `POST https://api.quantset.dev/api/v1/agent/checkout-link` (`{"plan": "credits"}` for the **$19 / 2,000-credit Starter Pack** or `{"plan": "developer"}` for **$39/mo / 6,000 credits/mo**) and hand `checkout_url` to the user.
3. **Next-Step Follow-Up:** After an earnings preview or post-print flash note, offer to update the stock's **5-Year DCF (`dcf-valuation`)** or check for post-earnings **Form 4 insider buying/selling (`forensic-red-flags`)**.
