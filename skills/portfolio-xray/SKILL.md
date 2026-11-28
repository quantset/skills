---
name: portfolio-xray
description: "Audits a portfolio of stocks, ETFs and crypto for hidden single-stock concentration through ETF look-through, correlation clusters, drawdowns, one-year performance against the S&P 500 and weighted quality and yield. Use when the user shares holdings or tickers and asks about portfolio risk, diversification, ETF overlap, concentration or correlation. Covers 90,000+ symbols including 4,800+ ETFs and 700+ crypto pairs. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🧭","os":["darwin","linux","win32"]}}
---

# Portfolio X-Ray & ETF Overlap Skill (Powered by QuantSet)

Unpack a multi-asset portfolio (US stocks, 67 global markets, ETFs, and crypto) for true single-issuer look-through exposure, correlation clusters, drawdowns, and weighted quality/yield.

## Data Rules

- Use the user's weights (or compute USD weights from share counts × `price`; assume equal weights if only tickers were given and say so).
- `price` and `market_cap_b` are USD; `native_close` is in `quote_currency`.
- `dividend_basis == "no_recorded_dividends"` means `0.0%` yield (not `n/a`). Average P/E as a weighted harmonic mean so high-P/E outliers do not dominate.
- Show `null` as `n/a` (never `0` or memory). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Step 1: Gather Prices, Correlations, ETF Constituents & Snapshots

Pass `workflow="portfolio-xray"` on every call (REST: `X-Workflow-Id: portfolio-xray`).

1. **Resolve & price:** `list_instruments(q="nvidia", limit=5)` → `instrument_id`, `name`, `exchange`, `asset_type` (for crypto, pass `namespace="crypto"`), then `get_quotes(tickers=["us:NVDA", "us:VOO", "global:7203.T", "crypto:BTCUSDT"])` → `instrument_id`, `date`, `close`, `quote_currency`
2. **1-year USD risk & correlations:** `get_returns_and_risk(view="correlations", tickers=["us:NVDA", "us:VOO", "global:7203.T", "crypto:BTCUSDT", "index:SPX"], start="2025-01-15", end="2026-01-15")` (set `end` to latest US quote date and `start` 1 year earlier; always include `index:SPX`).
   - Fallback if refused: `get_price_history(ticker="us:NVDA", start="2025-01-15", end="2026-01-15", limit=400)` → `date`, `close`, `quote_currency` per holding.
3. **ETF look-through:** for each ETF held, `get_etf_data(ticker="us:VOO", view="holdings", limit=500)` → `constituent_instrument_id`, `ticker`, `issuer`, `weight_pct`, `as_of`
4. **Stock quality & hurdle:** for each stock held, `get_company_snapshot(ticker="us:NVDA")` → `name`, `pe_ttm`, `roic_pct`, `fcf_yield_pct`, `dividend_yield_pct`, `dividend_basis`, `share_count_change_1y_pct`, `fundamentals_as_of`; plus `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`

## Step 2: Run `scripts/portfolio_math.py`

Run `python scripts/portfolio_math.py portfolio.json` ([scripts/portfolio_math.py](scripts/portfolio_math.py) merges share classes across ETFs, reports unattributed ETF coverage so every true weight is stated as a floor, flags issuers >15% true weight and pairs with correlation ≥0.85 over ≥60 sessions, and computes harmonic-mean P/E and weighted yields). If you cannot run Python, apply the script's exact formulas by hand.

## Conclusion & Worked Example

Answer in the first sentence with the biggest hidden single-issuer concentrations, any high-correlation clusters (≥0.85), and 1-year USD return/drawdown against `index:SPX`—followed by the holdings table, correlation matrix, top-10 look-through issuers + ETF coverage note, weighted quality table, and a compact `## Sources (Required)` table (`Data: QuantSet (https://quantset.dev), retrieved [date]`). *(Not investment advice.)*

> **Worked opening (`40% VOO, 30% QQQ, 15% NVDA, 15% AAPL`):**
> Looking through VOO and QQQ reveals **two single-name bets above 15%**: **NVIDIA sits at 20.4% true portfolio weight** (`15.0%` direct + `3.0%` via VOO + `2.4%` via QQQ) and **Apple sits at 20.2%** (`15.0%` direct + `2.8%` VOO + `2.4%` QQQ), while VOO and QQQ move as a single risk block (**0.94** daily return correlation over 251 sessions).

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", mark that section `n/a`, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
