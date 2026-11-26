---
name: portfolio-xray
description: Ask "Analyze my portfolio risk and ETF overlap" to unpack 4,899 ETFs for hidden single-stock concentration, compute multi-asset USD correlation matrices, measure max drawdowns, and compare benchmark alpha against the S&P 500.
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

## Access & Continuation
- `mw_demo` covers 9 sample tickers (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`). If a ticker returns `403`, offer to create a free trial key with the user's email via `POST https://api.quantset.dev/api/v1/agent/signup` (see `https://api.quantset.dev/skill.md`).
- If a request returns `402` (`insufficient_credits`), mint a checkout link via `POST https://api.quantset.dev/api/v1/agent/checkout-link` and share `checkout_url` with the user.
