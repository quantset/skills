---
name: portfolio-xray
description: "Audits a portfolio of stocks, ETFs and crypto for hidden single-stock concentration through ETF look-through, correlation clusters, drawdowns, one-year performance against the S&P 500 and weighted quality and yield. Use when the user shares holdings or tickers and asks about portfolio risk, diversification, ETF overlap, concentration or correlation. Covers 90,000+ symbols including 4,800+ ETFs and 700+ crypto pairs. Free to try with mw_demo."
metadata: {"clawdbot":{"emoji":"🧭","os":["darwin","linux","win32"]}}
---

# Multi-Asset Portfolio X-Ray & Overlap Audit (Powered by QuantSet)

Turn a list of holdings (US stocks, 67 global markets, ETFs, and crypto) into a risk, overlap and quality teardown.

## Workflow Checklist

- [ ] **Step 1. Resolve and price the holdings**
- [ ] **Step 2. One-year return, volatility, drawdown and correlations, all in US dollars**
- [ ] **Step 3. Look through the funds to the issuers**
- [ ] **Step 4. Weighted quality and yield**
- [ ] **Step 5. Report, with a Sources table**

If you can run Python, do the arithmetic of Steps 2 to 4 with [scripts/portfolio_math.py](scripts/portfolio_math.py): write the holdings and the saved responses to a JSON file in the layout documented at the top of the script, run `python scripts/portfolio_math.py portfolio.json`, and use its tables and flags as they come. It needs only the standard library. If you cannot run code, apply the same rules by hand.

## Data Rules (They Apply to Every Call in This Skill)

- **Where figures sit:** statement line items are under `values` (for example `values.revenue`); `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` are on the row.
- **Fiscal years:** `period="annual"` can return rolling twelve-month windows between the fiscal years. Drop every row whose `form` is `10-Q`; the rows left are fiscal years. That is why the calls ask for more rows than the years needed. For a US listing a row with no `form` is not from a filing: use it only for a year that has no `10-K` row. For a listing outside the US no row has a `form`, and all of them are fiscal years.
- **Quarters:** a quarterly row is a single quarter only when its `period_basis` is `discrete_quarter`; any other basis holds year-to-date figures. Never add or compare the two kinds: set a single quarter beside single quarters, and a year-to-date figure only beside the same point a year earlier. The same quarter can come back twice, with period ends up to a few weeks apart: match rows by the year and month of `period_end`, keep one per quarter, and prefer the one that has an `accession`.
- **Estimate rows:** the `estimates` view returns four rows: this quarter, next quarter, this fiscal year and next fiscal year. Their `period` labels vary by listing and a quarter and a fiscal year can end on the same date, so read the label and `period_end` together; `period_end` is a month-end label. Estimates are per share in the listing's reporting currency and on the Street's basis: they can differ from filed figures, and a company can file a loss while the consensus is a profit.
- **The snapshot mixes periods:** in `get_company_snapshot`, `free_cash_flow` and `ebitda_ttm` can be the last fiscal year's figures while `revenue_ttm` is trailing. Take EBITDA and free cash flow from the latest fiscal-year statement row and label them with its `period_end`.
- **Currency:** `price`, `market_cap_b` and `enterprise_value_b` are in US dollars (the `_b` fields in billions). `native_close` is the price in `quote_currency`, and statement figures are in `financial_currency`. Convert with `usd_rate` before combining the two.
- **Dates on filings:** `available_at` on an older period is the date of the latest filing that repeated it, not its first publication. Cite it only for the newest period.
- **Empty is not zero:** show a `null` as `n/a`. Never fill a gap from memory or a web search.
- **US-only datasets:** the error code `unsupported_instrument` means the dataset covers US listings only. Mark that section `n/a (US listings only)` and carry on. A key does not change it.

---

## Step 1: Resolve and Price

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="portfolio-xray"` on every call (REST: header `X-Workflow-Id: portfolio-xray`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

- **Weights:** use the percentages the user gave. If they gave share counts, value each holding in US dollars with the snapshot `price`. If they gave only tickers, say that equal weights are assumed.
- **Resolve each name:** `list_instruments(q="nvidia", limit=5)` → `instrument_id`, `name`, `exchange`, `asset_type`
  - Search by ticker when the user gave one. Take the `us:` listing of a stock or fund unless the user named another market; it is not always the first row.
  - A crypto holding is a pair: search its pair symbol in the crypto namespace, `list_instruments(q="BTCUSDT", namespace="crypto", limit=5)`.
- **Latest prices in one batch:** `get_quotes(tickers=["us:NVDA", "us:VOO", "global:7203.T", "crypto:BTCUSDT"])` → `instrument_id`, `date`, `close`, `quote_currency`. The dates and currencies differ by market; print them.

## Step 2: Risk in One Call

- `get_returns_and_risk(view="correlations", tickers=["us:NVDA", "us:VOO", "global:7203.T", "crypto:BTCUSDT", "index:SPX"], start="2025-01-15", end="2026-01-15")`
  - REST: `GET /api/v1/analytics/correlations` with `tickers` as a comma-separated list.
  - Set `end` to the latest US quote date and `start` to one year before it. Without them the call spans all history. Always add `index:SPX` as the benchmark. It takes 2 to 25 instruments.
  - It returns, in US dollars, each instrument's `cumulative_return_pct`, `annualized_volatility_pct` and `max_drawdown_pct` with its `first_date` and `last_date`, and each pair's `correlation` with its `overlapping_sessions`.
  - It accepts stocks, funds, non-US listings, crypto and the index alike, so use it for every holding.
- **Against the S&P 500:** each holding's `cumulative_return_pct` minus that of `index:SPX` over the same window. This is price return for both; say so.
- **Clusters:** call out pairs of holdings with a `correlation` of 0.85 or more: they fall together. A fund against the benchmark it tracks is not a cluster. Treat a pair with fewer than 60 `overlapping_sessions` as `n/a`. Markets that trade in different time zones are paired by calendar date, which understates their correlation; say so for non-US holdings.
- **If that call is refused or leaves a holding out:** `get_price_history(ticker="us:NVDA", start="2025-01-15", end="2026-01-15", limit=400)` → `date`, `close`, `quote_currency`
  - Make that call for each holding and for `index:SPX`, then let the script compute the same figures. A non-dollar holding's figures are then in its own currency, not dollars; say so.

## Step 3: Hidden ETF Look-Through Overlap (`4,899` Funds)

- For every fund held: `get_etf_data(ticker="us:VOO", view="holdings", limit=2000)` → `constituent_instrument_id`, `ticker`, `issuer`, `weight_pct`, `as_of`
- **True weight of an issuer** = its direct weight + the sum over funds of `fund weight × weight_pct / 100`. Match a fund row to a direct holding by `constituent_instrument_id`, then by `ticker`; add up share classes of one issuer.
- **Coverage:** a fund can return fewer rows than it holds. Add up the `weight_pct` of the rows returned and print it per fund with the row count and `as_of`. Everything not covered is unattributed, so each true weight is a floor; give the unattributed share of the whole portfolio.
- **Flag** any issuer above 15% true weight.

## Step 4: Fundamental Quality & Yield Check

- For each stock held (not funds, not crypto): `get_company_snapshot(ticker="us:NVDA")` → `name`, `pe_ttm`, `roic_pct`, `fcf_yield_pct`, `dividend_yield_pct`, `dividend_basis`, `share_count_change_1y_pct`, `fundamentals_as_of`
- Risk-free hurdle: `get_macro_and_fx(view="treasury_yields", limit=1)` → `date`, `yield_10y_pct`
- **Weighted averages** over the stocks that have a value, with the portfolio weight each average covers. Average P/E as a weighted harmonic mean (the script does this), so one very high P/E cannot dominate. A stock whose `dividend_basis` is `no_recorded_dividends` has a dividend yield of zero, not `n/a`.

## Output Format

1. **Holdings Table**, one-year window stated above it:

| Holding | Type | Weight | Price | Currency | 1Y Return (USD) | Max Drawdown | Volatility | vs. S&P 500 |
|---|---|---|---|---|---|---|---|---|

2. **Correlation Matrix**, with the clusters at 0.85 or more called out.
3. **Look-Through Exposure:** top 10 issuers by true weight (direct + through funds), named, each with the funds that carry it; then each fund's coverage and `as_of`, and the unattributed share of the portfolio.
4. **Quality & Yield:** the weighted averages and the weight each covers, beside the 10Y Treasury yield and its date.
5. **What To Look At:** three observations, each tied to a number above. *(Not investment advice.)*
6. **Sources:** see below.

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`date`, `as_of`, `last_date` or `fundamentals_as_of`), when it was filed or published where the row says (`filing_date`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no such date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): mark that section `n/a`, name the call, and keep going. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
