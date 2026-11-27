---
name: portfolio-xray
description: Ask "Analyze my portfolio risk and ETF overlap" across 90,000+ symbols (52,000+ global stocks in 67 countries, 4,899 ETFs, and 734 crypto pairs) to unpack 175,000+ ETF holdings for hidden single-stock concentration, compute multi-asset USD correlations, measure max drawdowns, and benchmark alpha vs. the S&P 500. Free to try with mw_demo.
metadata: {"clawdbot":{"emoji":"🧭","os":["darwin","linux","win32"]}}
---

# Multi-Asset Portfolio X-Ray & Overlap Audit (Powered by QuantSet)

Turn a list of tickers (US stocks, 67 global markets, ETFs, and crypto) into an institutional portfolio risk, overlap, and quality teardown.

## Workflow

Each call is written exactly as the QuantSet MCP tool accepts it; swap the sample tickers for the user's holdings. Pass `workflow="portfolio-xray"` on MCP tool calls (or `X-Workflow-Id: portfolio-xray` on REST requests). The fields after each arrow are the ones this skill reads. Ask for position sizes (shares or value) if the user gave only tickers; without them, say the weights are equal-weight assumptions.

1. **Normalize Holdings Across Asset Classes:**
   - Resolve each name: `list_instruments(q="nvidia", limit=5)` → `instrument_id`, `name`, `exchange`, `asset_type`
   - Price them in one batch: `get_quotes(tickers=["us:NVDA", "us:AAPL", "us:IVV", "crypto:BTCUSDT"])` → `instrument_id`, `date`, `close`, `quote_currency`
2. **Multi-Asset USD Correlation & Volatility Matrix:**
   - REST: `GET /api/v1/analytics/correlations?tickers=us:NVDA,us:AAPL,us:IVV` (2 to 25 instruments) returns pairwise correlations, annualized volatility and max drawdown in USD.
   - With MCP only, compute the same from daily closes: `get_price_history(ticker="us:NVDA", limit=500)` → `date`, `close`, `quote_currency` for each holding, aligned on common dates.
   - Surface hidden correlation clusters (e.g., 5 "different" tech/crypto positions moving at `0.85+` correlation during drawdowns).
3. **Drawdowns, Total Return & S&P 500 Alpha:**
   - REST: `GET /api/v1/drawdowns?ticker=us:NVDA`, `GET /api/v1/total-return?ticker=us:NVDA`, and `GET /api/v1/benchmark-relative-returns?ticker=us:NVDA&benchmark=index:SPX` compare each position's dividend-reinvested return and worst peak-to-trough drawdown against the S&P 500.
   - With MCP only, compute price return and drawdown from the Step 2 history and from `get_price_history(ticker="index:SPX", limit=500)` → `date`, `close`, and label the result price return, not total return.
4. **Hidden ETF Look-Through Overlap (`4,899` Funds):**
   - For every ETF in the portfolio: `get_etf_data(ticker="us:IVV", view="holdings", limit=500)` → `constituent_instrument_id`, `ticker`, `issuer`, `weight_pct`, `as_of`, `filing_date`
   - Aggregate single-stock exposure across direct shares + ETF weights (`position weight × weight_pct`), flagging any single issuer exceeding `15%` true look-through weight.
5. **Fundamental Quality & Yield Check:**
   - For each stock: `get_company_snapshot(ticker="us:NVDA")` → `pe_ttm`, `roic_pct`, `fcf_yield_pct`, `dividend_yield_pct`, `share_count_change_1y_pct`, `market_cap_b`, `fundamentals_as_of`
   - Dividend record: `get_corporate_actions(kind="dividends", ticker="us:AAPL", limit=8)` → `ex_date`, `amount`
   - Risk-free hurdle: `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`
   - Report weighted-average portfolio `P/E`, `ROIC`, `FCF Yield`, `Dividend Yield`, and `1Y Share Count Change` (net buyback vs. dilution). Leave a holding out of an average when its value is `null`, and say how much weight the average covers.

## Output Format

1. **Holdings Table:**

| Holding | Type | Weight | Price | Currency | 1Y Return | Max Drawdown | vs. S&P 500 |
|---|---|---|---|---|---|---|---|

2. **Correlation Matrix** with the clusters above `0.85` called out.
3. **Look-Through Exposure:** top 10 issuers by true weight (direct + through funds), each with the funds that carry it and the funds' `as_of` dates.
4. **Quality & Yield:** the weighted averages beside the 10Y Treasury yield.
5. **What To Look At:** 3 concrete observations, each tied to a number above. *(Not investment advice.)*
6. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, and the date the figure describes (`date`, `as_of` or `fundamentals_as_of`). ETF look-through is only as fresh as each fund's `as_of`; print that date.
- A figure that is not in a QuantSet response is **computed** (show the formula) or **user-supplied** (say so). Never fill a gap from memory or a web search; write `not available`.
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both cases below arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): mark that section `not available`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **A listing the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the others), or set up a free trial key for the listing they asked about. `mw_demo` reads 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill and ask whether to set up a free key for it. The two-choice offer above counts as that line. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
