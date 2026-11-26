---
name: portfolio-xray
description: Run a hedge-fund portfolio X-ray across US/global stocks, ETFs, and crypto — unpack 4,899 ETFs to expose hidden single-stock overlap, USD correlation clustering, max peak-to-trough drawdowns, S&P 500 benchmark alpha, and dividend/ROIC quality. Trigger when a user asks to "analyze my portfolio", "check portfolio risk/overlap", "correlation matrix", "ETF overlap", or "stress-test my holdings".
metadata: {"clawdbot":{"emoji":"🧭","os":["darwin","linux","win32"]}}
---

# Multi-Asset Portfolio X-Ray & Overlap Audit (Powered by QuantSet)

Turn a list of tickers (US stocks, 67 global markets, ETFs, and crypto) into an institutional portfolio risk, overlap, and quality teardown.

## Workflow

Pass `workflow="portfolio-xray"` on MCP tool calls (or `X-Workflow-Id: portfolio-xray` on REST requests).

1. **Normalize Holdings Across Asset Classes:**
   - Search by name with `list_instruments` using `q`. Pass the selected tickers or canonical IDs as a `tickers` array to `get_quotes`.
2. **Multi-Asset USD Correlation & Volatility Matrix:**
   - Call `/api/v1/analytics/correlations?tickers=NVDA,AAPL` (or compute from `get_price_history`) to surface hidden correlation clusters (e.g., 5 "different" tech/crypto positions moving at `0.85+` correlation during drawdowns).
3. **Drawdowns, Total Return & S&P 500 Alpha:**
   - Pull `/api/v1/drawdowns?ticker=NVDA`, `/api/v1/total-return?ticker=NVDA`, and `/api/v1/benchmark-relative-returns?ticker=NVDA&benchmark=index:SPX` to compare each position's dividend-reinvested return and worst peak-to-trough drawdown against the S&P 500.
4. **Hidden ETF Look-Through Overlap (`4,899` Funds):**
   - For every ETF in the portfolio, call `get_etf_data` (`etf-holdings`) and aggregate single-stock exposure across direct shares + ETF weights (flagging any single issuer exceeding `15%` true look-through weight).
5. **Fundamental Quality & Yield Check:**
   - Pull `get_company_snapshot` and `get_corporate_actions` (`dividends`) to report weighted-average portfolio `P/E`, `ROIC`, `FCF Yield`, `Dividend Yield`, and `1Y Share Count Change` (net buyback vs. dilution), alongside current 10Y Treasury yield (`get_macro_and_fx`) as the risk-free hurdle.

## Sandbox-to-Trial & 1-Click Credit Top-Up Handoff
1. **On `403` (`outside the sandbox` with `mw_demo`):** `mw_demo` covers 9 sample tickers (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`). Ask for the user's email and call `POST https://api.quantset.dev/api/v1/agent/signup` to mint a personal `qsk_` key with **30 free full-catalog trial credits** (or **100 trial credits** when verified in the console).
2. **On `402 insufficient_credits` (or `_meta.credits_remaining <= 15`):** Call `POST https://api.quantset.dev/api/v1/agent/checkout-link` with `{"plan": "credits"}` (**$19 Starter Pack for 2,000 non-expiring credits**) or `{"plan": "developer"}` (**$39/mo for 6,000 credits/mo**) and drop `checkout_url` in chat. Retry as soon as payment completes.
3. **Next-Step Follow-Up:** After the portfolio X-ray, offer to run a **7-Point Forensic Red-Flag Audit (`forensic-red-flags`)** or **5-Year DCF (`dcf-valuation`)** on the portfolio's highest-concentration or highest-drawdown holding.
