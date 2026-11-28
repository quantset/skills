# Endpoint Notes: What Each Dataset Returns and Where It Bites

Every operation here was called against the live API. [LLMS.md](LLMS.md) lists the parameters; this file says how the responses behave. Every dataset has an MCP tool: where a line gives a REST path, the tool and view that read it are named beside it.

The gaps noted here (an empty field, a dataset with no rows, a stale date) are what the API returned on 27 November 2026. Check the response you get: when the value is there, use it.

## Contents

- Cost and defaults
- Prices, returns and risk
- Statements, ratios and screens
- Estimates, earnings and calendars
- Filings, ownership and insiders
- Funds
- Macro, rates and FX
- Datasets that returned nothing
- Coverage by listing

## Cost and defaults

- A call's cost follows the rows it returns. Pass `limit` on every list call, and `max_credits` (REST: `X-Max-Credits`) when exploring. `get_rate_card` is free.
- `GET /quotes/market-snapshot` (`get_market_activity`, `view="market_snapshot"`) with no filters returns 5,000 rows and cost about 1,000 credits in one call. Always filter it and set `limit`.
- Many series default to their full history or to a two-year window, and start with the oldest rows. Give `start` and `end` whenever you mean "recent".
- `GET /context?ticker=` (`get_company_snapshot`, `view="context"`) bundles a snapshot, annual highlights, top holders and peers in one call. It costs more than a snapshot; use it when you need all four.

## Prices, returns and risk

- `get_price_history` returns the newest window with rows oldest first inside it. `index:SPX` rows carry one value in open, high, low and close.
- `GET /analytics/correlations` (`get_returns_and_risk`, `view="correlations"`) takes 2 to 25 instruments of any kind, including non-US listings, crypto and `index:SPX`, converts to US dollars, and returns each instrument's return, volatility and drawdown plus every pair's correlation. Without `start` and `end` it spans all history.
- `GET /drawdowns` requires `start`. `GET /returns`, `/total-return` and `/benchmark-relative-returns` default to about two years of daily rows. They are the `drawdowns`, `returns`, `total_return` and `relative_returns` views of `get_returns_and_risk`, and cover US listings only: a non-US listing or crypto pair returns `unsupported_instrument`.
- `GET /total-return` anchors its window at the latest split unless `start` is given, and can refuse a fund without `start`.
- `get_quotes` returns each instrument's latest bar in its own currency and on its own date. Non-US and crypto dates differ from US dates.
- `GET /historical-valuations` (`get_returns_and_risk`, `view="valuation_history"`) returns a daily P/E series. When the P/E is empty on most days, do not chart it; use `get_financial_metrics` for one P/E per fiscal year and check it against the price history before quoting it.

## Statements, ratios and screens

- `get_financial_statements` takes many `tickers` and one `kind` per call. Line items are under `values`.
- `period="annual"` can include rolling twelve-month rows (`form` `10-Q`) between fiscal years. Quarterly rows are single quarters only when `period_basis` is `discrete_quarter`; the fiscal fourth quarter is often missing or year-to-date.
- `get_company_snapshot`: `free_cash_flow` and `ebitda_ttm` can be last fiscal year's figures, so take both from the statement row when the period matters. `total_debt`, `enterprise_value_b`, `roic_pct` and `pe_forward` can be empty: when they are, compute forward P/E as `price / forward_eps` and rebuild debt from the balance sheet lines.
- `get_financial_metrics` returns one row of ratios per fiscal period with `report_period`. Older rows can be distorted by share splits; check a surprising value before using it.
- `screen_stocks` filters on preset thresholds and returns snapshot rows with `total_count`. Market cap is in billions (`min_market_cap_b`) and growth and margins are in percent. A threshold on a field drops every company where that field is empty, and enterprise value was empty for about four in ten large companies. The `us` namespace includes foreign companies' depositary receipts.
- `search_screener` uses a different field list: read it from `get_screener_filters`. There market cap is in dollars (`market_cap`), and the fields have names such as `revenue_growth`, `pe_ratio` and `return_on_invested_capital`. Each hit carries `report_period`, `filing_date` and a `values` object.
- A past `as_of` on either screener returned no rows. When that happens, say point-in-time screening is not available for that date; do not present a current screen as a past one.
- `get_fundamentals` is an unordered market-wide browse. For named companies use `get_financial_statements`.
- `get_line_items` (`POST /financial-statements/line-items`) returns only the fields you name for up to 50 listings, with `period` `annual`, `quarterly` or `ttm`. A `ttm` row returned a single quarter's revenue for one company and no revenue for another: check `values.revenue` against the snapshot's `revenue_ttm` before using a `ttm` row. `get_financial_statements` with `kind="all"` returns the three statements of one listing, and `kind="as_reported"` the company's own XBRL line items by filing.

## Estimates, earnings and calendars

- `get_estimates_and_earnings` takes one `view` per call. `estimates` returns four rows (this and next quarter, this and next fiscal year) with month-end `period_end` labels; `year_ago` is the Street's figure.
- `view="earnings"` is the EPS surprise history on the Street's basis, US listings only. A consensus near zero produces absurd `surprise_pct` values; use the median.
- `view="calendar"` with a `ticker` often has no upcoming date. `view="consensus"` carries `next_earnings_date`, price targets, rating counts, `shares_short`, `short_pct_of_float`, `held_pct_insiders` and `held_pct_institutions` in one row. Use it as the fallback for the next report date.
- `GET /options?ticker=` (`get_market_activity`, `view="options"`) returns `atm_implied_volatility_pct`, `implied_move_pct` and the put/call ratios for the nearest expiration, plus `expiration_dates`. Pass `expiration` to pick the first one after an event; when that date is weeks after the event the implied move covers the whole stretch. Its `underlying_price` can differ from the latest close.
- `GET /short-volume` (`get_market_activity`, `view="short_volume"`) is daily short-sale volume, not short interest. The share of float sold short is `short_pct_of_float` in the consensus view.
- `GET /earnings-releases` (`get_estimates_and_earnings`, `view="releases"`) lists the latest earnings 8-Ks with their URLs; its guidance, non-GAAP and KPI lists were empty.

## Filings, ownership and insiders

- `get_sec_filings` with `view="company_facts"`: rows are unordered and each period repeats across filings. Keep the latest `filed` per period.
- `view="insider_transactions"` starts with the earliest years. Pass `start`. One sale is often several rows at different prices. For a single ticker or `issuer_cik`, filings after the latest quarterly SEC archive are supplemented live from EDGAR XML; unfiltered market-wide queries stop at the latest quarterly archive.
- `view="institutional_ownership"`: `pct` is empty; `portfolio_weight_pct` is the holder's own portfolio weight. Rows with `put_call` set are option positions.
- `view="segments"`: `flow` `Y` is a fiscal year and `Q` a quarter; revenue only. `view="debt_maturities"`: `year` is the filing's fiscal year, `y1` the amount due in the following year.
- Filing text (`get_filing_documents`, views `search`, `sections`, `index` and `item_catalog`): `GET /sec/filing-search?ticker=&q=` returns excerpts with `item`, `filing_date` and a `citation_url`; `GET /sec/filing-sections?ticker=&form=&item=` returns the full text of an item, newest filing first, and `accession_number` picks an older one. `GET /sec/filings?ticker=&form_type=` lists filings with their accession numbers and, for an 8-K, its `items`. `GET /sec/filing-items` names the items of each form as `Item-1A`; the calls take `1A`. A section can sit under an unexpected item number (a 10-K's discussion of results under `6` with only a heading under `7`), an 8-K item named in the filing list can come back with no text, and section text carries page numbers mid-sentence. Search excerpts are cut at about 1,000 characters.
- `GET /sec/form-144?ticker=&start=` (`get_sec_filings`, `view="form_144"`) lists planned insider sales with `seller_name`, `shares_to_be_sold`, `aggregate_market_value_usd` and `approx_sale_date`. Always pass `ticker`.
- `GET /sec/beneficial-ownership` (13D and 13G filings; `get_sec_filings`, `view="beneficial_ownership"`) had little after 2024. Check the newest `filing_date` before calling it current.
- `GET /executive-compensation?ticker=` (`get_sec_filings`, `view="executive_compensation"`) returns rows for most large companies and none for some.
- `GET /institutional-holders` (`view="institutional_holders"`) needs `holder` or `holder_cik`; `GET /sec/insiders` (`view="insider_profile"`) needs `owner_cik`; `GET /sec/insider-holdings` needs a `ticker`, `issuer_cik` or `owner_cik`.

## Funds

- `get_etf_data` with `view="holdings"`: some funds return every position and others only the largest 10 or 100, dated months apart. Add up `weight_pct` and print the coverage and `as_of`. `filing_date` is empty.
- `view="exposures"` is ordered by the fund's weight in the stock, not by size, and capped at 200 rows, so the largest index funds can be missing. Some rows are years old: filter on `as_of`.
- `view="profile"` carries `is_leveraged_or_inverse_index` and `daily_target_multiple`. A share-class symbol can return `unknown_instrument`.

## Macro, rates and FX

- `get_macro_and_fx` with `view="treasury_yields"` can lag by a week. `view="treasury_rates"` (`GET /treasury`) returns the same curve as `rates_pct` keyed by tenor (`10Y`); it returns the newest rows oldest first, so the last row is the latest. Print the date either way, and use the newer of the two.
- `view="series"` lists the indicator IDs (free); `view="indicators"` with no `series_ids` mixes every series in one page.
- `view="inflation"`, `"labor"` and `"gdp"` return a latest-value table by default; pass `mode="historical"` for a series.
- `view="fx_rates"` returns `usd_per_unit` by date, newest first.

## Datasets with partial or sparse coverage

A past `as_of` on the screeners currently returns no rows (point-in-time `as_of` works on statements, ratios, estimates, ownership and ETF holdings). `GET /earnings/feed` and an unfiltered `GET /sec/form-144` can answer `temporarily_unavailable`. `/kpi/guidance`, `/kpi/metrics` and `/kpi/non-gaap` (`guidance`, `kpis` and `non_gaap` views of `get_estimates_and_earnings`) parse numeric outlook ranges and non-GAAP tables from recent Form 8-K earnings releases, so issuers that do not issue numeric guidance in an 8-K return empty rows. Call once: use the rows when they come back, and when they do not, say the dataset is empty. Do not substitute a web search and call it QuantSet data.

## Coverage by listing

- **US listings:** every dataset.
- **Listings outside the US (`global:`):** prices, snapshot, statements, estimates, consensus and peers. The SEC datasets (segments, debt schedule, insiders, holders, filing text, earnings surprise history) and the US analytics endpoints return `unsupported_instrument` or `resource_not_found`. Statement rows carry no `form`, `available_at` or `accession`. `GET /regional-filings` (`get_filing_documents`, `view="regional"`) and `GET /reference/series` (`get_market_activity`, `view="reference_series"`; markets `jp`, `uk`, `hk`, `world`) cover them instead.
- **Crypto and indices:** prices, quotes and the correlations endpoint only.
