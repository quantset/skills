# QuantSet API

> Financial data for research agents: daily prices, quotes, fundamentals, historical statements, corporate actions, ownership, filings, exchange rates and macroeconomic observations.

API origin: https://api.quantset.dev
OpenAPI 3.1: https://api.quantset.dev/openapi.json
Dataset coverage: https://api.quantset.dev/api/v1/capabilities

## First request

Use one credential: X-API-Key, Authorization: Bearer, or apikey in the query for spreadsheet reads. The sandbox key mw_demo reads documented sample listings. The operation entries below identify keyless and sample access.

```sh
curl 'https://api.quantset.dev/api/v1/prices?ticker=NVDA&limit=5' -H 'X-API-Key: mw_demo'
```

## Read and interpret a data page

- Use ticker for one listing and tickers for a batch. In GET queries, join batch selectors with commas. In JSON bodies, send arrays. Use the listed selectors for each operation.
- A canonical instrument_id identifies the returned listing. Search with q on /api/v1/instruments. If an ambiguous_instrument error returns candidates, choose a listed canonical ID and resubmit.
- Data pages identify schema_version and contain data, total_count, next_cursor, snapshot_id and provenance. Keep the operationId with any saved page. Inspect units, scale, currency, basis and limitations. A zero is an observation. A null represents a missing or withheld value. A null total_count means the count is unavailable.
- Pass next_cursor unchanged as cursor and reuse the previous snapshot_id and filters. A null cursor ends the read. A snapshot_changed response requires restarting at page one. Price pages move backward in time, with ascending dates inside each page. Prepend earlier pages to assemble ascending history.
- snapshot_id pins a warehouse generation. as_of and filed_before constrain the data's public availability where supported. Check availability dates and filing citations before using rows in point-in-time analysis. Live observations report their observation time.
- Use CSV where the operation lists text/csv. In Google Sheets use a data-only key entitled to the screener:

```text
=IMPORTDATA("https://api.quantset.dev/api/v1/screener?min_market_cap_b=10&limit=20&format=csv&apikey=YOUR_DATA_ONLY_KEY")
```

## Credits and receipts

Every operation's price is on the rate card at GET https://api.quantset.dev/api/v1/billing/rate-card. A rows tariff settles against the collection rows actually returned.
Set X-Max-Credits on the data request to cap its charge. Pass X-Workflow-Id to group related calls. Read X-Credit-Cost and X-Rate-Card-Version from the receipt. A 402 costs zero and reports the required_credits or maximum_credits separately from credits_remaining. SDK pagination supports a cumulative budget.

## Recover from an error

Read the stable code and detail. Inspect any field, hint, candidates or snapshot_id. Correct invalid input before retrying. Wait Retry-After seconds on rate_limited. For transient errors, use bounded retries for reads. After a mutation times out, reconcile the account state before repeating the request.

## Operations

### Prices and sessions

Latest quotes, multi-market daily history (with verified adj_close & market_cap), hourly US bars, live session quotes and exchange hours.

#### Latest quotes

`GET /api/v1/quotes` · `get_quotes` · sandbox sample key

Read the most recent daily quote for one to 100 listings. Each quote has its own observation date. Use price history for earlier bars.

- `tickers` (array, required) Comma-separated distinct listing selectors, 1–100.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `quote_currency` (string), `date` (string), `open` (number), `high` (number), `low` (number), `close` (number), `split_adj_close` (number), `adj_close` (number), `adjusted_as_of` (string), `change_pct` (number), `volume` (number), `dollar_volume` (number), `market_cap` (number), `shares_outstanding` (number), `volume_unit` (shares | base_asset_units | index_points), `adjustment` (string)

```sh
curl 'https://api.quantset.dev/api/v1/quotes?tickers=NVDA,AAPL' -H 'X-API-Key: mw_demo'
```

#### Price history

`GET /api/v1/prices` · `get_price_history` · sandbox sample key

Read daily OHLCV for one listing across US, international, crypto and index markets. The latest available window comes first, with ascending dates within each page. Use latest quotes for a batch of recent daily observations.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `basis` (raw | comparable, optional, default raw) raw preserves all bars; comparable starts at the latest split or unit discontinuity.
- `format` (json | csv, optional, default json) Response format: json or csv.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `quote_currency` (string), `date` (string), `open` (number), `high` (number), `low` (number), `close` (number), `split_adj_close` (number), `adj_close` (number), `adjusted_as_of` (string), `change_pct` (number), `volume` (number), `dollar_volume` (number), `market_cap` (number), `shares_outstanding` (number), `volume_unit` (shares | base_asset_units | index_points), `adjustment` (string)

```sh
curl 'https://api.quantset.dev/api/v1/prices?ticker=NVDA&limit=5' -H 'X-API-Key: mw_demo'
```

#### Intraday bars

`GET /api/v1/intraday` · `get_intraday_prices` · sandbox sample key

Hourly 60-minute bars for US symbols, cross-checked against daily closes.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) Start ISO timestamp or YYYY-MM-DD exchange date
- `end` (string, optional) End ISO timestamp or YYYY-MM-DD exchange date
- `limit` (integer, optional, default 5000) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `quote_currency` (string), `ts_utc` (string), `date_local` (string), `open` (number), `high` (number), `low` (number), `close` (number), `volume` (number), `cross_checked` (boolean), `quarantined_days` (integer)

```sh
curl 'https://api.quantset.dev/api/v1/intraday?ticker=us:NVDA&limit=50' -H 'X-API-Key: mw_demo'
```

#### Live market session

`GET /api/v1/market-session` · `get_market_session` · sandbox sample key

Current session quote or 5-minute intraday points with a 60-second cache. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `interval` (quote | 5m, optional, default quote)
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `date` (string), `timezone` (string), `currency` (string), `previousClose` (number), `daily` (string), `quote` (string), `points` (array)

```sh
curl 'https://api.quantset.dev/api/v1/market-session?ticker=us:NVDA&interval=quote' -H 'X-API-Key: mw_demo'
```

#### Market status

`GET /api/v1/market-status` · `get_market_status` · keyless

Whether the US market is open, with the open and close times of the current or next session.

- `at` (string, optional) UTC ISO timestamp; default is now

Response fields: `schema_version` (string), `snapshot_id` (string), `market` (string), `timezone` (string), `is_open` (boolean), `session` (object), `local_time` (string), `next_session` (object)

```sh
curl 'https://api.quantset.dev/api/v1/market-status'
```

### Returns, risk and historical multiples

Daily returns, reinvested total returns, drawdowns, multi-asset correlation matrices, historical P/E and benchmark comparisons.

#### Daily returns

`GET /api/v1/returns` · `get_daily_returns` · sandbox sample key

Price or total return between consecutive US sessions, with explicit reason codes when withheld.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `basis` (price | total, optional, default price)
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `date` (string), `previous_date` (string), `session_count` (integer), `return_basis` (price | total), `return_pct` (number), `status` (available | no_previous_close | session_gap | split_boundary | adjusted_close_unavailable), `adjusted_as_of` (string)

```sh
curl 'https://api.quantset.dev/api/v1/returns?ticker=us:AAPL&limit=10' -H 'X-API-Key: mw_demo'
```

#### Dividend-reinvested total return

`GET /api/v1/total-return` · `get_total_return_series` · sandbox sample key

Compounded return series reinvesting independently verified cash dividends on their ex-dates.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) Start date YYYY-MM-DD; anchors to the latest share-basis boundary crossed in the window
- `end` (string, optional) End date YYYY-MM-DD
- `limit` (integer, optional, default 20000) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `window` (object), `share_basis_boundary` (string), `dividend_events` (array), `dividend_basis` (verified_cash_events | no_recorded_dividends), `dividend_convention` (string), `price_return_pct` (number), `total_return_pct` (number), `series` (array)

```sh
curl 'https://api.quantset.dev/api/v1/total-return?ticker=us:AAPL&limit=250' -H 'X-API-Key: mw_demo'
```

#### Drawdowns

`GET /api/v1/drawdowns` · `get_drawdowns` · sandbox sample key

Closing drawdown from the running peak within each uninterrupted segment from start.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, required) First date to include, as an ISO date (YYYY-MM-DD).
- `basis` (price | total, optional, default price)
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `date` (string), `return_basis` (price | total), `drawdown_pct` (number), `peak_date` (string), `segment_start_date` (string), `status` (available | new_segment | adjusted_close_unavailable), `adjusted_as_of` (string)

```sh
curl 'https://api.quantset.dev/api/v1/drawdowns?ticker=us:AAPL&start=2026-10-02&limit=10' -H 'X-API-Key: mw_demo'
```

#### Benchmark-relative returns

`GET /api/v1/benchmark-relative-returns` · `get_relative_returns` · sandbox sample key

Subtracts the matching daily benchmark return in percentage points (US listing or index:SPX).

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `benchmark` (string, required) A US instrument ID, or index:SPX with basis=price for the S&P 500 price index.
- `basis` (price | total, optional, default price)
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `date` (string), `previous_date` (string), `session_count` (integer), `return_basis` (price | total), `return_pct` (number), `status` (available | no_previous_close | session_gap | split_boundary | adjusted_close_unavailable), `adjusted_as_of` (string), `benchmark_id` (string), `benchmark_return_pct` (number), `benchmark_adjusted_as_of` (string), `benchmark_status` (available | no_previous_close | session_gap | split_boundary | adjusted_close_unavailable), `relative_return_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/benchmark-relative-returns?ticker=us:AAPL&benchmark=index:SPX&limit=10' -H 'X-API-Key: mw_demo'
```

#### Historical trailing P/E

`GET /api/v1/historical-valuations` · `get_historical_valuations` · sandbox sample key

Point-in-time daily US common-share P/E using diluted earnings filed before each close date.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `quote_currency` (string), `date` (string), `close` (number), `cik` (string), `eps_ttm` (number), `eps_period_end` (string), `eps_filed_at` (string), `eps_basis` (reported_annual | four_reported_quarters), `eps_accessions` (array), `pe_ttm` (number), `status` (available | unverified_share_basis | no_comparable_eps | nonpositive_eps)

```sh
curl 'https://api.quantset.dev/api/v1/historical-valuations?ticker=us:AAPL&limit=10' -H 'X-API-Key: mw_demo'
```

#### Multi-asset correlations and risk

`GET /api/v1/analytics/correlations` · `get_analytics_correlations` · sandbox sample key

USD-aligned pairwise daily return correlations, annualized volatility, cumulative return and max drawdown across 2 to 25 instruments.

- `tickers` (array, required) 2 to 25 distinct comma-separated listing selectors
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `basis` (price | total, optional, default price) price or total (verified US adjusted closes).
- `currency` (native | USD, optional, default USD) USD converts international closes with dated FX rates; native keeps local units.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `return_basis` (price | total), `currency` (string), `window_start` (string), `window_end` (string), `instruments` (array), `correlations` (array)

```sh
curl 'https://api.quantset.dev/api/v1/analytics/correlations?tickers=us:NVDA,us:AAPL,crypto:BTCUSDT' -H 'X-API-Key: mw_demo'
```

### Instruments, ETFs and capabilities

Search 70,000+ listings across 67 countries, inspect ETF constituent weights, and check active snapshot coverage.

#### Options chain & implied move

`GET /api/v1/options` · `get_options_chain` · eligible API key

Listed US options chain with ATM implied volatility, ATM straddle implied_move_pct, put/call volume & open-interest ratios, and strike contracts. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `expiration` (string, optional) Optional expiration date YYYY-MM-DD
- `max_strikes` (integer, optional, default 40)
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `underlying_price` (number), `expiration_dates` (array), `selected_expiration` (string), `atm_strike` (number), `atm_implied_volatility_pct` (number), `implied_move_pct` (number), `put_call_volume_ratio` (number), `put_call_open_interest_ratio` (number), `calls` (array), `puts` (array)

```sh
curl 'https://api.quantset.dev/api/v1/options?ticker=us:NVDA' -H 'X-API-Key: YOUR_API_KEY'
```

#### FINRA daily short-sale volume

`GET /api/v1/short-interest` · `get_short_interest` · eligible API key

Official FINRA Consolidated Reg-SHO daily short volume, short-exempt volume, total volume and short_volume_ratio_pct.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `days` (integer, optional, default 10)
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `date` (string), `short_volume` (number), `short_exempt_volume` (number), `total_volume` (number), `short_volume_ratio_pct` (number), `markets` (string)

```sh
curl 'https://api.quantset.dev/api/v1/short-interest?ticker=us:NVDA&days=10' -H 'X-API-Key: YOUR_API_KEY'
```

#### Agent research context pack

`GET /api/v1/context` · `get_agent_context_pack` · eligible API key

One-call, token-budgeted research bundle combining identity, snapshot multiples, 4-year highlights, top Form 13F holders, peers and recent news. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `instrument` (object), `snapshot` (object), `annual_highlights` (array), `top_13f_holders` (array), `peers` (array), `recent_news` (array)

```sh
curl 'https://api.quantset.dev/api/v1/context?ticker=us:NVDA' -H 'X-API-Key: YOUR_API_KEY'
```

#### Whole-market quote snapshot

`GET /api/v1/quotes/market-snapshot` · `get_market_quote_snapshot` · eligible API key

Latest price, OHLC, 1-day change %, volume, market cap and trailing P/E across all active US or global listings in a single request.

- `namespace` (us | global, optional, default us)
- `country` (string, optional)
- `asset_type` (stock | etf, optional)
- `active_only` (boolean, optional, default True)
- `limit` (integer, optional, default 5000) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `name` (string), `exchange` (string), `asset_type` (string), `security_type` (string), `sector` (string), `date` (string), `price` (number), `open` (number), `high` (number), `low` (number), `change_1d_pct` (number), `volume` (number), `market_cap_b` (number), `pe_ttm` (number)

```sh
curl 'https://api.quantset.dev/api/v1/quotes/market-snapshot?namespace=us&asset_type=stock&limit=50' -H 'X-API-Key: YOUR_API_KEY'
```

#### Capabilities

`GET /api/v1/capabilities` · `get_capabilities` · keyless

The namespaces, sector taxonomy, datasets, statement fields and limits available in the current snapshot.

- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.

Response fields: `schema_version` (string), `snapshot_id` (string), `namespaces` (object), `sector_taxonomy` (object), `resources` (array), `statement_fields` (object), `statement_units` (object), `unsupported` (array), `limits` (object), `coverage` (object)

```sh
curl 'https://api.quantset.dev/api/v1/capabilities'
```

#### Search instruments

`GET /api/v1/instruments` · `search_instruments` · sandbox sample key

Search or page through US, global, crypto, and index instruments, ranked by relevance when q is supplied.

- `namespace` (us | global | crypto | index, optional) Limit results to us, global, crypto, or index.
- `q` (string, optional) Search symbol, listing name, or sector
- `country` (string, optional) Exact country or comma-separated countries (e.g. United-States,Japan)
- `exclude_country` (string, optional) Comma-separated countries to exclude
- `exchange` (string, optional) Exact exchange or comma-separated exchanges (e.g. NASDAQ,LSE)
- `sector` (string, optional) Exact canonical warehouse sector, case-insensitive
- `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified, optional)
- `legacy_sector` (string, optional) Substring of a legacy sector or industry label
- `asset_type` (string, optional)
- `has_financials` (boolean, optional)
- `has_prices` (boolean, optional)
- `active_only` (boolean, optional, default False) When true, omit delisted/defunct and stale (>30d) historical symbols
- `sort_by` (instrument_id | relevance | market_cap_b | pe_ttm | dividend_yield_pct | rev_growth_qoq_pct, optional)
- `sort_dir` (ASC | DESC | asc | desc, optional)
- `offset` (integer, optional, default 0)
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `sector` (string), `sector_as_of` (string), `sector_funds` (array), `directory_sector` (string), `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified), `sector_asset_type` (string), `sector_isin` (string), `sector_link_venue` (string), `sector_link_ticker` (string), `directory_link_venue` (string), `directory_link_ticker` (string), `industry_label` (string), `sic_code` (string), `sic_description` (string), `instrument_id` (string), `namespace` (us | global | crypto | index), `symbol` (string), `listing_symbol` (string), `name` (string), `country` (string), `exchange` (string), `asset_type` (string), `quote_currency` (string), `base_asset` (string), `quote_asset` (string), `cik` (string), `sic` (string), `industry` (string), `sector_label` (string), `sector_scheme` (sec_division | directory), `has_financials` (boolean), `reference_market` (string), `reference_group` (string), `reference_symbol` (string), `is_active` (boolean), `listing_status` (active | stale | inactive_or_delisted), `latest_price_date` (string), `latest_close` (number), `usd_price` (number), `market_cap_b` (number), `pe_ttm` (number), `dividend_yield_pct` (number), `rev_growth_qoq_pct` (number), `etf_asset_class` (string), `backing_type` (string), `fund_category` (string), `category_basis` (string), `daily_target_multiple` (number), `multiple_basis` (string), `direction` (string), `corroboration_status` (string), `weighted_maturity_years` (number), `credit_quality` (string), `benchmark_index` (string), `benchmark_instrument_id` (string), `underlying_instrument_id` (string), `expense_ratio_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/instruments?q=nvidia&limit=10' -H 'X-API-Key: mw_demo'
```

#### Get an instrument

`GET /api/v1/instruments/{instrument_id}` · `get_instrument` · sandbox sample key

Name, country, exchange, asset type, quote currency, CIK, canonical sector and headline multiples for one instrument.

- `instrument_id` (string, required) Namespaced identifier, such as us:NVDA, global:SHEL.L, crypto:BTCUSDT, or index:SPX.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `sector` (string), `sector_as_of` (string), `sector_funds` (array), `directory_sector` (string), `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified), `sector_asset_type` (string), `sector_isin` (string), `sector_link_venue` (string), `sector_link_ticker` (string), `directory_link_venue` (string), `directory_link_ticker` (string), `industry_label` (string), `sic_code` (string), `sic_description` (string), `instrument_id` (string), `namespace` (us | global | crypto | index), `symbol` (string), `listing_symbol` (string), `name` (string), `country` (string), `exchange` (string), `asset_type` (string), `quote_currency` (string), `base_asset` (string), `quote_asset` (string), `cik` (string), `sic` (string), `industry` (string), `sector_label` (string), `sector_scheme` (sec_division | directory), `has_financials` (boolean), `reference_market` (string), `reference_group` (string), `reference_symbol` (string), `is_active` (boolean), `listing_status` (active | stale | inactive_or_delisted), `latest_price_date` (string), `latest_close` (number), `usd_price` (number), `market_cap_b` (number), `pe_ttm` (number), `dividend_yield_pct` (number), `rev_growth_qoq_pct` (number), `etf_asset_class` (string), `backing_type` (string), `fund_category` (string), `category_basis` (string), `daily_target_multiple` (number), `multiple_basis` (string), `direction` (string), `corroboration_status` (string), `weighted_maturity_years` (number), `credit_quality` (string), `benchmark_index` (string), `benchmark_instrument_id` (string), `underlying_instrument_id` (string), `expense_ratio_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/instruments/us:NVDA' -H 'X-API-Key: mw_demo'
```

#### ETF & trust profile

`GET /api/v1/etf-profile` · `get_etf_profile` · sandbox sample key

Read the structure, benchmark, expenses and exposure profile for a US ETF, unit investment trust or grantor trust. Use ETF holdings for its dated constituent weights.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `series_id` (string), `class_id` (string), `cik` (string), `official_fund_name` (string), `sponsor` (string), `exchange` (string), `asset_class` (string), `backing_type` (string), `fund_category` (string), `category_basis` (filed | derived-holdings | sec_10k_xbrl | sec_prospectus | provider_profile | unclassified), `is_index_fund` (boolean), `is_leveraged_or_inverse_index` (boolean), `is_rule_18f4_derivatives` (boolean), `direction` (long | inverse), `daily_target_multiple` (number), `multiple_basis` (derived | filed_unleveraged_index), `corroboration_status` (corroborated | disagreement | not_leveraged | insufficient_data), `net_assets_usd` (number), `net_assets_scope` (fund | series_all_classes), `share_class_assets_usd` (number), `physical_equity_usd` (number), `swap_notional_usd` (number), `swap_unrealized_usd` (number), `swap_exposure_usd` (number), `futures_notional_usd` (number), `computed_exposure_ratio` (number), `weighted_maturity_years` (number), `weighted_coupon_pct` (number), `us_treasury_pct` (number), `investment_grade_pct` (number), `high_yield_pct` (number), `credit_quality` (string), `benchmark_index` (string), `benchmark_index_identifier` (string), `benchmark_instrument_id` (string), `underlying_instrument_id` (string), `underlying_symbol` (string), `underlying_isin` (string), `underlying_name` (string), `management_fee_pct` (number), `expense_ratio_pct` (number), `expense_ratio_basis` (string), `ncen_accession` (string), `ncen_report_date` (string), `ncen_filed_at` (string), `nport_accession` (string), `nport_report_date` (string), `nport_filed_at` (string), `quality_issues` (array)

```sh
curl 'https://api.quantset.dev/api/v1/etf-profile?ticker=IVV' -H 'X-API-Key: mw_demo'
```

#### ETF constituent holdings

`GET /api/v1/etf-holdings` · `get_etf_holdings` · sandbox sample key

Dated equity constituents, weights, share counts, market values, ISINs and canonical US/global instrument IDs across 1,800+ US and international ETFs from SEC Form N-PORT (175,000+ holdings) and dated portfolio disclosures.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `q` (string, optional) Search text, matched against ticker, exchange, country and name.
- `sector` (string, optional)
- `as_of` (string, optional) Point-in-time historical date YYYY-MM-DD (uses N-PORT filings filed on or before as_of)
- `limit` (integer, optional, default 200) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `fund_instrument_id` (string), `fund_symbol` (string), `fund_name` (string), `as_of` (string), `filing_date` (string), `constituent_instrument_id` (string), `ticker` (string), `issuer` (string), `country` (string), `exchange` (string), `sector` (string), `weight_pct` (number), `shares` (number), `market_value` (number), `isin` (string), `market_currency` (string)

```sh
curl 'https://api.quantset.dev/api/v1/etf-holdings?ticker=IVV&limit=20' -H 'X-API-Key: mw_demo'
```

#### Stock ETF exposures

`GET /api/v1/etf-exposures` · `get_etf_exposures` · sandbox sample key

Reverse lookup showing which tracked ETFs hold a given US or international equity and at what weight.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `fund_instrument_id` (string), `fund_symbol` (string), `fund_name` (string), `as_of` (string), `filing_date` (string), `constituent_instrument_id` (string), `ticker` (string), `issuer` (string), `country` (string), `exchange` (string), `sector` (string), `weight_pct` (number), `shares` (number), `market_value` (number), `isin` (string), `market_currency` (string)

```sh
curl 'https://api.quantset.dev/api/v1/etf-exposures?ticker=us:NVDA' -H 'X-API-Key: mw_demo'
```

### Fundamentals and screening

Financial statements, cross-sectional snapshots, institutional factor screening (EV/EBITDA, FCF margin, share buybacks) and peer groups.

#### Line-item picker

`POST /api/v1/financial-statements/line-items` · `project_financial_line_items` · eligible API key

Fetch only chosen statement metrics (e.g. revenue, net_income, free_cash_flow, total_debt) across multiple US or global tickers in one compact call.

- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `report_period` (string), `period` (annual | quarterly | ttm), `currency` (string), `values` (object)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/financial-statements/line-items' -H 'X-API-Key: YOUR_API_KEY' -H 'Content-Type: application/json' --data '{"line_items":["revenue","net_income","free_cash_flow","total_debt"],"period":"annual","limit_per_instrument":2,"tickers":["us:NVDA","us:AAPL"]}'
```

#### All three financial statements

`GET /api/v1/financial-statements/all` · `get_all_financial_statements` · eligible API key

Income statements, balance sheets and cash flow statements for one US or global company in a single call.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `period` (annual | quarterly, optional, default annual) Reporting period.
- `limit` (integer, optional, default 8) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `period` (string), `income_statements` (array), `balance_sheets` (array), `cash_flow_statements` (array)

```sh
curl 'https://api.quantset.dev/api/v1/financial-statements/all?ticker=us:NVDA&period=annual&limit=2' -H 'X-API-Key: YOUR_API_KEY'
```

#### As-reported XBRL statements

`GET /api/v1/financial-statements/as-reported` · `get_as_reported_statements` · eligible API key

Company-reported SEC XBRL line items grouped by accession number and period end without standardization.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `form` (string, optional, default 10-K) SEC form filter, e.g. 10-K or 10-Q
- `limit` (integer, optional, default 4) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `cik` (string), `accession_number` (string), `form_type` (string), `filed_date` (string), `period_start` (string), `period_end` (string), `currency_or_units` (array), `fact_count` (integer), `facts` (object), `statements` (object)

```sh
curl 'https://api.quantset.dev/api/v1/financial-statements/as-reported?ticker=us:NVDA&form=10-K&limit=2' -H 'X-API-Key: YOUR_API_KEY'
```

#### DSL screener filter catalog

`GET /api/v1/screener/filters` · `get_screener_filters` · keyless

Machine-discoverable schema of all 95+ income statement, balance sheet, cash flow, financial ratio, and company fields plus operators (gt, gte, lt, lte, eq, in) accepted by /api/v1/screener/search.

- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.

Response fields: `metrics` (object), `company_filters` (object), `aliases` (object), `operators` (array), `percent_format_note` (string)

```sh
curl 'https://api.quantset.dev/api/v1/screener/filters'
```

#### Multi-statement DSL stock screener

`POST /api/v1/screener/search` · `search_screener` · eligible API key

Screen US or global companies across any combination of financial statement line items, 45+ ratios, short volume, insider buys, and GICS sector/industry via GET or POST, with lookahead-free as_of backtesting.

- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `name` (string), `sector` (string), `industry` (string), `report_period` (string), `filing_date` (string), `currency` (string), `values` (object)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/screener/search' -H 'X-API-Key: YOUR_API_KEY' -H 'Content-Type: application/json' --data '{"filters":[{"field":"revenue","operator":"gt","value":10000000000},{"field":"quick_ratio","operator":"gt","value":1.5}],"limit":10}'
```

#### Historical financial ratios & efficiency metrics

`GET /api/v1/financial-metrics` · `get_historical_financial_metrics` · eligible API key

36 annual, quarterly or TTM valuation, profitability, working-capital efficiency (DSO, asset/inventory/receivables turnover, operating cycle), liquidity (current/quick/cash/OCF ratios), leverage and YoY growth metrics, with optional point-in-time as_of.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `period` (annual | quarterly | ttm, optional, default annual) Reporting period.
- `as_of` (string, optional) Point-in-time date YYYY-MM-DD (uses filings filed on or before as_of)
- `limit` (integer, optional, default 12) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `report_period` (string), `period` (string), `currency` (string), `filing_date` (string), `accession_number` (string), `form_type` (string), `price` (number), `market_cap` (number), `enterprise_value` (number), `pe_ratio` (number), `pb_ratio` (number), `ps_ratio` (number), `ev_to_ebitda` (number), `ev_to_revenue` (number), `peg_ratio` (number), `fcf_yield_pct` (number), `payout_ratio_pct` (number), `gross_margin_pct` (number), `operating_margin_pct` (number), `net_margin_pct` (number), `roe_pct` (number), `roa_pct` (number), `roic_pct` (number), `asset_turnover` (number), `inventory_turnover` (number), `receivables_turnover` (number), `days_sales_outstanding` (number), `operating_cycle_days` (number), `working_capital_turnover` (number), `current_ratio` (number), `quick_ratio` (number), `cash_ratio` (number), `operating_cash_flow_ratio` (number), `debt_to_equity` (number), `debt_to_assets` (number), `interest_coverage` (number), `rev_growth_yoy_pct` (number), `operating_income_growth_yoy_pct` (number), `ebitda_growth_yoy_pct` (number), `net_income_growth_yoy_pct` (number), `eps_growth_yoy_pct` (number), `fcf_growth_yoy_pct` (number), `book_value_growth_yoy_pct` (number), `diluted_eps` (number), `book_value_per_share` (number), `fcf_per_share` (number)

```sh
curl 'https://api.quantset.dev/api/v1/financial-metrics?ticker=us:NVDA&period=annual&limit=8' -H 'X-API-Key: YOUR_API_KEY'
```

#### Instrument snapshot

`GET /api/v1/snapshots` · `get_company_snapshot` · sandbox sample key

Read the latest available company fundamentals and valuation metrics for one listing. Use price history for dated bars or statements for financial periods and filing availability.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `sector` (string), `sector_as_of` (string), `sector_funds` (array), `directory_sector` (string), `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified), `sector_asset_type` (string), `sector_isin` (string), `sector_link_venue` (string), `sector_link_ticker` (string), `directory_link_venue` (string), `directory_link_ticker` (string), `industry_label` (string), `sic_code` (string), `sic_description` (string), `instrument_id` (string), `namespace` (us | global | crypto | index), `symbol` (string), `name` (string), `country` (string), `exchange` (string), `security_type` (string), `asset_type` (string), `cik` (string), `sic` (string), `industry` (string), `sec_sector` (string), `gics_sector` (string), `latest_date` (string), `stale_days` (integer), `is_active` (boolean), `has_financials` (boolean), `quote_currency` (string), `native_close` (number), `usd_rate` (number), `fx_date` (string), `price` (number), `daily_open` (number), `daily_high` (number), `daily_low` (number), `volume` (number), `shares_out` (number), `price_adjustment` (string), `last_share_change` (string), `change_1d_pct` (number), `change_5d_pct` (number), `change_1m_pct` (number), `change_6m_pct` (number), `change_1y_pct` (number), `ytd_pct` (number), `total_return_start_date` (string), `total_return_1y_pct` (number), `dividend_basis` (string), `dividend_price_observation` (string), `sma_50` (number), `sma_50_days` (integer), `sma_200` (number), `sma_200_days` (integer), `ema_15` (number), `rsi14` (number), `mfi14` (number), `realized_volatility` (number), `beta` (number), `high_52w` (number), `low_52w` (number), `range_52w_days` (integer), `weekly_high` (number), `weekly_low` (number), `monthly_high` (number), `monthly_low` (number), `market_cap_b` (number), `quote_market_cap_b` (number), `market_cap_basis` (string), `market_cap_shares_as_of` (string), `market_cap_filed` (string), `market_cap_accession` (string), `market_cap_ordinary_per_us_share` (number), `financial_currency` (string), `valuation_eligible` (boolean), `fundamentals_basis` (string), `fundamentals_as_of` (string), `latest_fy_date` (string), `revenue_ttm` (number), `revenue_prev` (number), `rev_growth_yoy_pct` (number), `rev_growth_qoq_pct` (number), `rev_growth_qyoy_pct` (number), `gross_profit_ttm` (number), `operating_income_ttm` (number), `net_income_ttm` (number), `ebitda_ttm` (number), `eps_ttm` (number), `eps_ttm_basis` (string), `eps_fy` (number), `eps_growth_yoy_pct` (number), `eps_growth_3y_cagr_pct` (number), `eps_growth_5y_cagr_pct` (number), `gross_margin_pct` (number), `operating_margin_pct` (number), `net_margin_pct` (number), `roe_pct` (number), `roic_pct` (number), `debt_to_equity` (number), `current_ratio` (number), `interest_coverage` (number), `balance_sheet_as_of` (string), `balance_equation_consistent` (boolean), `cash` (number), `total_assets` (number), `long_term_debt` (number), `total_debt` (number), `total_liabilities` (number), `total_equity` (number), `book_value_per_share` (number), `operating_cash_flow` (number), `capex` (number), `free_cash_flow` (number), `cash_flow_as_of` (string), `cash_flow_currency` (string), `cash_flow_basis` (string), `fcf_shares_used` (number), `fcf_share_basis` (string), `fcf_per_share` (number), `fcf_yield_pct` (number), `pe_ttm` (number), `pe_forward` (number), `pb_ratio` (number), `ffo_ttm` (number), `price_to_ffo` (number), `enterprise_value_b` (number), `ev_to_ebitda` (number), `ev_to_fcf` (number), `net_debt_to_ebitda` (number), `fcf_margin_pct` (number), `share_count_change_1y_pct` (number), `eps_current_fy` (number), `current_fy_end` (string), `eps_next_fy` (number), `next_fy_end` (string), `current_fy_estimate_as_of` (string), `next_fy_estimate_as_of` (string), `forward_eps` (number), `analyst_count` (integer), `analyst_rank` (string), `value_grade` (string), `growth_grade` (string), `momentum_grade` (string), `vgm_grade` (string), `annual_dividend` (number), `dividend_yield_pct` (number), `dividend_years_10y` (integer), `dividend_increase_streak_years` (integer), `last_ex_dividend_date` (string), `insider_buys` (integer), `insider_sells` (integer), `insider_latest_date` (string), `insider_data_through_date` (string), `insider_window_end` (string), `insider_coverage` (string), `employees` (integer), `etf_asset_class` (string), `backing_type` (string), `fund_category` (string), `category_basis` (string), `daily_target_multiple` (number), `multiple_basis` (string), `direction` (string), `corroboration_status` (string), `weighted_maturity_years` (number), `credit_quality` (string), `benchmark_index` (string), `benchmark_instrument_id` (string), `underlying_instrument_id` (string), `expense_ratio_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/snapshots?ticker=us:NVDA' -H 'X-API-Key: mw_demo'
```

#### Stock screener

`GET /api/v1/screener` · `get_screener` · eligible API key

Filter and cursor-paginate companies across size, EV/EBITDA, P/E, P/B, ROIC, FCF margin, net-buyback share change and dividend yield.

- `format` (json | csv, optional, default json) Response format: json or csv.
- `namespace` (us | global | crypto, optional, default us)
- `country` (string, optional)
- `exchange` (string, optional)
- `sector` (string, optional) Exact canonical warehouse sector, case-insensitive
- `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified, optional)
- `legacy_sector` (string, optional) Substring of a legacy sector or industry label
- `asset_type` (string, optional)
- `has_fundamentals` (boolean, optional) Filter to companies with reported TTM/FY revenue
- `max_stale_days` (integer, optional)
- `min_market_cap_b` (number, optional)
- `max_pe_ttm` (number, optional)
- `max_pe_forward` (number, optional)
- `max_pb_ratio` (number, optional)
- `max_ev_to_ebitda` (number, optional) Maximum enterprise value to EBITDA multiple.
- `max_ev_to_fcf` (number, optional) Maximum enterprise value to free cash flow multiple.
- `max_net_debt_to_ebitda` (number, optional) Maximum net debt to EBITDA multiple.
- `min_rev_growth_yoy` (number, optional)
- `min_rev_growth_qoq` (number, optional)
- `min_roic` (number, optional)
- `min_roe` (number, optional)
- `min_net_margin` (number, optional)
- `min_fcf_margin` (number, optional) Minimum annual free cash flow margin, in percent.
- `max_debt_to_equity` (number, optional)
- `min_dividend_yield` (number, optional)
- `max_share_count_change_1y` (number, optional) Maximum 1Y share-count change % (negative values screen for net buyback cannibals)
- `analyst_rank` (string, optional)
- `as_of` (string, optional) Point-in-time backtest date (YYYY-MM-DD); uses strictly prices <= as_of and filings with source_filed <= as_of
- `sort_by` (string, optional, default market_cap_b)
- `sort_dir` (string, optional, default DESC)
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `sector` (string), `sector_as_of` (string), `sector_funds` (array), `directory_sector` (string), `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified), `sector_asset_type` (string), `sector_isin` (string), `sector_link_venue` (string), `sector_link_ticker` (string), `directory_link_venue` (string), `directory_link_ticker` (string), `industry_label` (string), `sic_code` (string), `sic_description` (string), `instrument_id` (string), `namespace` (us | global | crypto | index), `symbol` (string), `name` (string), `country` (string), `exchange` (string), `security_type` (string), `asset_type` (string), `cik` (string), `sic` (string), `industry` (string), `sec_sector` (string), `gics_sector` (string), `latest_date` (string), `stale_days` (integer), `is_active` (boolean), `has_financials` (boolean), `quote_currency` (string), `native_close` (number), `usd_rate` (number), `fx_date` (string), `price` (number), `daily_open` (number), `daily_high` (number), `daily_low` (number), `volume` (number), `shares_out` (number), `price_adjustment` (string), `last_share_change` (string), `change_1d_pct` (number), `change_5d_pct` (number), `change_1m_pct` (number), `change_6m_pct` (number), `change_1y_pct` (number), `ytd_pct` (number), `total_return_start_date` (string), `total_return_1y_pct` (number), `dividend_basis` (string), `dividend_price_observation` (string), `sma_50` (number), `sma_50_days` (integer), `sma_200` (number), `sma_200_days` (integer), `ema_15` (number), `rsi14` (number), `mfi14` (number), `realized_volatility` (number), `beta` (number), `high_52w` (number), `low_52w` (number), `range_52w_days` (integer), `weekly_high` (number), `weekly_low` (number), `monthly_high` (number), `monthly_low` (number), `market_cap_b` (number), `quote_market_cap_b` (number), `market_cap_basis` (string), `market_cap_shares_as_of` (string), `market_cap_filed` (string), `market_cap_accession` (string), `market_cap_ordinary_per_us_share` (number), `financial_currency` (string), `valuation_eligible` (boolean), `fundamentals_basis` (string), `fundamentals_as_of` (string), `latest_fy_date` (string), `revenue_ttm` (number), `revenue_prev` (number), `rev_growth_yoy_pct` (number), `rev_growth_qoq_pct` (number), `rev_growth_qyoy_pct` (number), `gross_profit_ttm` (number), `operating_income_ttm` (number), `net_income_ttm` (number), `ebitda_ttm` (number), `eps_ttm` (number), `eps_ttm_basis` (string), `eps_fy` (number), `eps_growth_yoy_pct` (number), `eps_growth_3y_cagr_pct` (number), `eps_growth_5y_cagr_pct` (number), `gross_margin_pct` (number), `operating_margin_pct` (number), `net_margin_pct` (number), `roe_pct` (number), `roic_pct` (number), `debt_to_equity` (number), `current_ratio` (number), `interest_coverage` (number), `balance_sheet_as_of` (string), `balance_equation_consistent` (boolean), `cash` (number), `total_assets` (number), `long_term_debt` (number), `total_debt` (number), `total_liabilities` (number), `total_equity` (number), `book_value_per_share` (number), `operating_cash_flow` (number), `capex` (number), `free_cash_flow` (number), `cash_flow_as_of` (string), `cash_flow_currency` (string), `cash_flow_basis` (string), `fcf_shares_used` (number), `fcf_share_basis` (string), `fcf_per_share` (number), `fcf_yield_pct` (number), `pe_ttm` (number), `pe_forward` (number), `pb_ratio` (number), `ffo_ttm` (number), `price_to_ffo` (number), `enterprise_value_b` (number), `ev_to_ebitda` (number), `ev_to_fcf` (number), `net_debt_to_ebitda` (number), `fcf_margin_pct` (number), `share_count_change_1y_pct` (number), `eps_current_fy` (number), `current_fy_end` (string), `eps_next_fy` (number), `next_fy_end` (string), `current_fy_estimate_as_of` (string), `next_fy_estimate_as_of` (string), `forward_eps` (number), `analyst_count` (integer), `analyst_rank` (string), `value_grade` (string), `growth_grade` (string), `momentum_grade` (string), `vgm_grade` (string), `annual_dividend` (number), `dividend_yield_pct` (number), `dividend_years_10y` (integer), `dividend_increase_streak_years` (integer), `last_ex_dividend_date` (string), `insider_buys` (integer), `insider_sells` (integer), `insider_latest_date` (string), `insider_data_through_date` (string), `insider_window_end` (string), `insider_coverage` (string), `employees` (integer), `etf_asset_class` (string), `backing_type` (string), `fund_category` (string), `category_basis` (string), `daily_target_multiple` (number), `multiple_basis` (string), `direction` (string), `corroboration_status` (string), `weighted_maturity_years` (number), `credit_quality` (string), `benchmark_index` (string), `benchmark_instrument_id` (string), `underlying_instrument_id` (string), `expense_ratio_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/screener?has_fundamentals=true&max_ev_to_ebitda=30&min_roic=15&limit=20' -H 'X-API-Key: YOUR_API_KEY'
```

#### Industry peers

`GET /api/v1/peers` · `get_peers` · sandbox sample key

Peer companies matched by canonical sector or 4-digit SIC industry, ordered by market cap.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 15) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `sector` (string), `sector_as_of` (string), `sector_funds` (array), `directory_sector` (string), `sector_coverage` (direct | linked_isin | directory_only | industry_only | not_applicable | unclassified), `sector_asset_type` (string), `sector_isin` (string), `sector_link_venue` (string), `sector_link_ticker` (string), `directory_link_venue` (string), `directory_link_ticker` (string), `industry_label` (string), `sic_code` (string), `sic_description` (string), `group_basis` (sector | sic_industry | sec_division | industry), `instrument_id` (string), `symbol` (string), `peer_group` (string), `name` (string), `industry` (string), `sec_sector` (string), `price` (number), `change_1y_pct` (number), `market_cap_b` (number), `rev_growth_yoy_pct` (number), `net_margin_pct` (number), `roe_pct` (number), `roic_pct` (number), `debt_to_equity` (number), `pe_ttm` (number), `pe_forward` (number), `fcf_yield_pct` (number), `dividend_yield_pct` (number), `analyst_rank` (string), `vgm_grade` (string)

```sh
curl 'https://api.quantset.dev/api/v1/peers?ticker=us:NVDA&limit=10' -H 'X-API-Key: mw_demo'
```

#### Financial statements

`GET /api/v1/financial-statements/{kind}` · `get_financial_statements` · sandbox sample key

Income statements, balance sheets or cash flow statements for up to 100 US or global companies (us:* and global:*), annual or quarterly.

- `kind` (income | balance_sheet | cash_flow, required) Which statement to return: income, balance_sheet, or cash_flow.
- `tickers` (array, required) Comma-separated distinct listing selectors, 1–100.
- `period` (annual | quarterly, optional, default annual) Reporting period.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit_per_instrument` (integer, optional, default 8) Number of periods to return for each company, newest first.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `as_of` (string, optional) Point-in-time date, YYYY-MM-DD. Returns only statements that were publicly filed on or before this date. Rows without a known filing date are excluded.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `period_end` (string), `period_start` (string), `available_at` (string), `period` (annual | quarterly), `period_basis` (annual | discrete_quarter | instant | mixed_fiscal_ytd_and_discrete), `currency` (string), `values` (string), `eps_method` (string), `accession` (string), `form` (string), `concepts` (object), `quality_issues` (array)

```sh
curl 'https://api.quantset.dev/api/v1/financial-statements/income?tickers=NVDA&period=annual&limit_per_instrument=2' -H 'X-API-Key: mw_demo'
```

#### Fundamentals summary

`GET /api/v1/fundamentals` · `get_fundamentals` · eligible API key

Standardized TTM or fiscal-year income summary and growth rates across covered US companies.

- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `basis` (ttm | fiscal_year), `period_end` (string), `currency` (string), `revenue` (number), `gross_profit` (number), `operating_income` (number), `net_income` (number), `eps` (number), `eps_method` (string), `revenue_growth_yoy_pct` (number), `revenue_growth_qoq_pct` (number), `revenue_growth_quarter_yoy_pct` (number), `eps_growth_yoy_pct` (number), `eps_growth_5y_cagr_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/fundamentals?limit=20' -H 'X-API-Key: YOUR_API_KEY'
```

### Estimates, ratings and calendars

Analyst consensus forecasts, factor grades, reported earnings surprises and market-wide event calendars.

#### Live earnings filing feed

`GET /api/v1/earnings/feed` · `get_earnings_feed` · eligible API key

Real-time stream of SEC Form 8-K Item 2.02 earnings releases and 10-Q/10-K reports across the market, newest first. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `accession_number` (string), `cik` (string), `instrument_id` (string), `symbol` (string), `company_name` (string), `filer_name` (string), `form_type` (string), `filing_date` (string), `report_date` (string), `items` (array), `primary_document` (string), `filing_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/earnings/feed?limit=25' -H 'X-API-Key: YOUR_API_KEY'
```

#### Earnings release guidance, non-GAAP & KPIs

`GET /api/v1/earnings-releases` · `get_earnings_releases` · eligible API key

Verbatim forward guidance, non-GAAP reconciliations and operating KPI citations extracted from Form 8-K Item 2.02 and Exhibit 99.1. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 2) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `accession_number` (string), `filing_date` (string), `report_date` (string), `filing_url` (string), `guidance` (array), `non_gaap` (array), `kpis` (array)

```sh
curl 'https://api.quantset.dev/api/v1/earnings-releases?ticker=us:NVDA&limit=2' -H 'X-API-Key: YOUR_API_KEY'
```

#### Company and market news

`GET /api/v1/news` · `get_market_news` · eligible API key

Read live financial headlines by ticker or market topic, with original article citations. The result reports the retrieval time. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `q` (string, optional) Topic or search query when ticker is omitted
- `limit` (integer, optional, default 20) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `title` (string), `publisher` (string), `published_at` (string), `url` (string), `related_instrument_ids` (array)

```sh
curl 'https://api.quantset.dev/api/v1/news?ticker=us:NVDA&limit=10' -H 'X-API-Key: YOUR_API_KEY'
```

#### Analyst price targets, buy/hold/sell counts & profile

`GET /api/v1/analyst-consensus` · `get_analyst_consensus` · eligible API key

Read price targets, current recommendation counts and available company profile fields for one US or global equity listing. Pin snapshot_id for an archived observation. An unpinned read can fall back to live data.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `name` (string), `quote_currency` (string), `financial_currency` (string), `current_price` (number), `target_mean_price` (number), `target_median_price` (number), `target_high_price` (number), `target_low_price` (number), `upside_pct` (number), `analyst_count` (integer), `recommendation_key` (string), `strong_buy` (integer), `buy` (integer), `hold` (integer), `sell` (integer), `strong_sell` (integer), `forward_pe` (number), `peg_ratio` (number), `beta` (number), `shares_short` (number), `short_pct_of_float` (number), `held_pct_insiders` (number), `held_pct_institutions` (number), `next_earnings_date` (string), `website` (string), `employees` (integer), `business_summary` (string), `observed_on` (string)

```sh
curl 'https://api.quantset.dev/api/v1/analyst-consensus?ticker=us:NVDA' -H 'X-API-Key: YOUR_API_KEY'
```

#### Analyst estimates

`GET /api/v1/estimates` · `get_estimates` · sandbox sample key

EPS and revenue forecasts for US and global equity listings, with contributor counts and ranges by forecast period. Check provenance.currency and scale_verified before comparing revenue.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `metric` (eps | revenue, optional, default eps) Which estimate to return: eps or revenue.
- `as_of` (string, optional) Only return estimates recorded on or before this date, YYYY-MM-DD.
- `history` (boolean, optional, default False) Include historical forecast periods in addition to active named buckets
- `limit` (integer, optional, default 20) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `as_of` (string), `period_end` (string), `period` (string), `consensus` (number), `recent` (number), `analyst_count` (integer), `high` (number), `low` (number), `year_ago` (number), `scale_verified` (boolean)

```sh
curl 'https://api.quantset.dev/api/v1/estimates?ticker=us:NVDA&metric=eps&limit=4' -H 'X-API-Key: mw_demo'
```

#### Analyst ratings and factor grades

`GET /api/v1/analyst-ratings` · `get_analyst_ratings` · sandbox sample key

Historical rank and Value, Growth, Momentum and VGM grades.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 20) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `date` (string), `rank` (string), `value_grade` (string), `growth_grade` (string), `momentum_grade` (string), `vgm_grade` (string)

```sh
curl 'https://api.quantset.dev/api/v1/analyst-ratings?ticker=us:NVDA&limit=12' -H 'X-API-Key: mw_demo'
```

#### Earnings history

`GET /api/v1/earnings` · `get_earnings` · sandbox sample key

Reported EPS against consensus estimate, with percentage surprise.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 8) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `period_end` (string), `actual_eps` (number), `estimated_eps` (number), `surprise_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/earnings?ticker=us:NVDA&limit=8' -H 'X-API-Key: mw_demo'
```

#### Market-wide earnings calendar

`GET /api/v1/calendar/earnings` · `get_earnings_calendar` · sandbox sample key

Upcoming or historical earnings releases across all covered US companies over a date window. Supply ticker to read one listing, including its published history.

- `ticker` (string, optional) Narrow the calendar to a US listing and read newest events first.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `timing` (string, optional) Exact case-insensitive session, such as BMO or AMC.
- `min_market_cap_b` (number, optional) Minimum market capitalization in billions of USD.
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `name` (string), `date` (string), `timing` (string), `market_cap_b` (number)

```sh
curl 'https://api.quantset.dev/api/v1/calendar/earnings?ticker=NVDA&start=2024-01-01&limit=5' -H 'X-API-Key: mw_demo'
```

#### Market-wide dividends and splits calendar

`GET /api/v1/calendar/corporate-actions` · `get_corporate_actions_calendar` · sandbox sample key

Ex-dividend and stock-split events across all covered US listings over a date window. Supply ticker to read one listing, including its published history.

- `ticker` (string, optional) Narrow to a US or supported India listing and read newest events first.
- `kind` (dividends | splits | shareholder_returns | exchange_actions, optional) Defaults to exchange_actions for an India listing and dividends otherwise. Exchange actions and annual shareholder returns require a listing selector.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `min_market_cap_b` (number, optional) Minimum USD billions, for dividends and splits.
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `name` (string), `market_cap_b` (number), `action_kind` (dividend | split | shareholder_return | india_exchange_action), `ex_date` (string), `year` (integer), `amount` (number), `buybacks` (number), `to_factor` (number), `for_factor` (number), `split_ratio` (number), `exchange` (string), `isin` (string), `record_date` (string), `action_type` (string), `ratio_num` (integer), `ratio_den` (integer), `cash_amount` (number), `face_value_from` (number), `face_value_to` (number), `raw_subject` (string)

```sh
curl 'https://api.quantset.dev/api/v1/calendar/corporate-actions?ticker=AAPL&start=2024-01-01&limit=5' -H 'X-API-Key: mw_demo'
```

### Actions, ownership and SEC disclosures

Dividends, splits, buybacks, 13F institutional holders, share counts, segments, debt maturities, 10b5-1 insider filings and XBRL facts.

#### Event webhooks

`GET /api/v1/webhooks` · `list_webhooks` · eligible API key

Manage HMAC-SHA256 signed outbound webhook subscriptions for real-time earnings, filings, insider and activist events.


Response fields: `id` (string), `url` (string), `events` (array), `description` (string), `created_at` (string)

```sh
curl 'https://api.quantset.dev/api/v1/webhooks' -H 'X-API-Key: YOUR_API_KEY'
```

#### SEC filings index

`GET /api/v1/sec/filings` · `get_sec_filings` · eligible API key

Live and historical SEC filings (10-K, 10-Q, 8-K, Form 4, Form 144, 13D/13G, S-1) by ticker, issuer CIK or market-wide. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `issuer_cik` (string, optional) SEC Central Index Key for the issuer, as one to ten decimal digits.
- `form_type` (string, optional) Comma-separated SEC forms, e.g. 10-K,10-Q,8-K,4,144,SC 13D
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `accession_number` (string), `cik` (string), `instrument_id` (string), `symbol` (string), `company_name` (string), `filer_name` (string), `form_type` (string), `filing_date` (string), `report_date` (string), `items` (array), `primary_document` (string), `filing_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/filings?ticker=us:NVDA&limit=20' -H 'X-API-Key: YOUR_API_KEY'
```

#### Institutional portfolio by manager

`GET /api/v1/institutional-holders` · `get_institutional_holders` · eligible API key

Every reported US equity position held by an institutional manager (e.g. Berkshire or Vanguard), ordered by position value.

- `holder` (string, optional) Manager name substring, e.g. Berkshire or Vanguard
- `holder_cik` (string, optional) SEC CIK of the institutional investment manager, e.g. 0001067983
- `as_of` (string, optional) Point-in-time date YYYY-MM-DD (uses filings with filing_date <= as_of)
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `holder` (string), `manager_cik` (string), `instrument_id` (string), `symbol` (string), `issuer_name` (string), `cusip` (string), `put_call` (string), `shares` (number), `market_value_usd` (number), `portfolio_weight_pct` (number), `prior_shares` (number), `shares_change_qoq` (number), `shares_change_qoq_pct` (number), `position_change` (string), `report_date` (string), `filing_date` (string), `accession_number` (string)

```sh
curl 'https://api.quantset.dev/api/v1/institutional-holders?holder=Berkshire&limit=25' -H 'X-API-Key: YOUR_API_KEY'
```

#### SEC filing item catalog

`GET /api/v1/sec/filing-items` · `get_sec_filing_items` · keyless

Zero-auth taxonomy of all 10-K, 10-Q, 8-K and DEF 14A item codes and plain-English descriptions.

- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.

```sh
curl 'https://api.quantset.dev/api/v1/sec/filing-items'
```

#### SEC form type catalog

`GET /api/v1/sec/filing-types` · `get_sec_filing_types` · keyless

Zero-auth list of supported SEC EDGAR form types (10-K, 10-Q, 8-K, DEF 14A, S-1, 13F-HR, Form 4, Form 144, 13D/13G, N-PORT).

- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.

```sh
curl 'https://api.quantset.dev/api/v1/sec/filing-types'
```

#### SEC 10-K, 10-Q & 8-K section text

`GET /api/v1/sec/filing-sections` · `get_sec_filing_sections` · eligible API key

Clean text of specific SEC filing sections such as Item 1A Risk Factors, Item 7 MD&A, or 8-K Item 2.02. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `form` (10-K | 10-Q | 8-K, optional, default 10-K)
- `item` (string, optional) Specific item code, e.g. 1, 1A, 7, 7A, 2.02
- `accession_number` (string, optional)
- `include_exhibits` (boolean, optional, default False) Include Exhibit 99.1 earnings release on 8-K filings
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `cik` (string), `accession_number` (string), `form_type` (string), `filing_date` (string), `item` (string), `title` (string), `text` (string), `filing_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/filing-sections?ticker=us:NVDA&form=10-K&item=1A' -H 'X-API-Key: YOUR_API_KEY'
```

#### Cited SEC filing & proxy search

`GET /api/v1/sec/filing-search` · `search_filing_text` · eligible API key

Search recent 10-K, 10-Q, 8-K, DEF 14A proxy and 20-F filings for verbatim paragraph excerpts with W3C #:~:text= deep-link SEC citations. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `q` (string, required) Search verbatim filing paragraphs. Results prioritize relevance.
- `forms` (array, optional) Comma-separated SEC forms. Accepts one to ten forms.
- `limit` (integer, optional, default 10) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `accession_number` (string), `form_type` (string), `filing_date` (string), `item` (string), `excerpt` (string), `filing_url` (string), `citation_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/filing-search?ticker=us:NVDA&q=data+center&forms=10-K&limit=5' -H 'X-API-Key: YOUR_API_KEY'
```

#### Structured forward earnings guidance

`GET /api/v1/kpi/guidance` · `get_kpi_guidance` · eligible API key

Numeric forward guidance ranges (low, high, midpoint, unit, period) extracted from 8-K earnings releases with #:~:text= SEC deep links. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 3) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `accession_number` (string), `filing_date` (string), `period` (string), `metric_name` (string), `low` (number), `high` (number), `midpoint` (number), `unit` (string), `excerpt` (string), `citation_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/kpi/guidance?ticker=us:NVDA&limit=2' -H 'X-API-Key: YOUR_API_KEY'
```

#### Structured non-GAAP metrics

`GET /api/v1/kpi/non-gaap` · `get_kpi_non_gaap` · eligible API key

Adjusted EPS, Adjusted EBITDA, Adjusted Operating Income and Free Cash Flow extracted from 8-K earnings releases with #:~:text= SEC deep links. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 3) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `accession_number` (string), `filing_date` (string), `period` (string), `metric_name` (string), `value` (number), `unit` (string), `excerpt` (string), `citation_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/kpi/non-gaap?ticker=us:NVDA&limit=2' -H 'X-API-Key: YOUR_API_KEY'
```

#### Sector operational KPIs

`GET /api/v1/kpi/metrics` · `get_kpi_metrics` · eligible API key

Operating KPIs not in GAAP statements (data center revenue, ARR, RPO, backlog, load factor, CET1, NIM, comp sales) with #:~:text= SEC deep links. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 3) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `symbol` (string), `accession_number` (string), `filing_date` (string), `period` (string), `metric_name` (string), `value` (number), `unit` (string), `excerpt` (string), `citation_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/kpi/metrics?ticker=us:NVDA&limit=2' -H 'X-API-Key: YOUR_API_KEY'
```

#### Schedule 13D & 13G beneficial and activist ownership

`GET /api/v1/sec/beneficial-ownership` · `get_beneficial_ownership` · eligible API key

5%+ activist (13D) and passive (13G) beneficial ownership filings across US public companies. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `activist_only` (boolean, optional, default False) When true, return only Schedule 13D / 13D/A activist stakes
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `accession_number` (string), `cik` (string), `instrument_id` (string), `symbol` (string), `company_name` (string), `filer_name` (string), `form_type` (string), `filing_date` (string), `report_date` (string), `items` (array), `primary_document` (string), `filing_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/beneficial-ownership?activist_only=true&limit=20' -H 'X-API-Key: YOUR_API_KEY'
```

#### SEC Form 144 proposed insider sales

`GET /api/v1/sec/form-144` · `get_form_144_notices` · eligible API key

Parsed SEC Form 144 XML notices of proposed insider stock sales, with seller, share count, market value and broker. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 25) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `accession_number` (string), `cik` (string), `instrument_id` (string), `symbol` (string), `issuer_name` (string), `seller_name` (string), `security_title` (string), `shares_to_be_sold` (number), `aggregate_market_value_usd` (number), `approx_sale_date` (string), `broker_name` (string), `filing_date` (string), `filing_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/form-144?ticker=us:NVDA&limit=10' -H 'X-API-Key: YOUR_API_KEY'
```

#### IPO filings (S-1, F-1 & 424B4)

`GET /api/v1/ipos` · `get_ipo_filings` · eligible API key

Live SEC IPO registration statements and final prospectuses. This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `classification` (ipo | spac | shell_company | resale | other, optional)
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `accession_number` (string), `cik` (string), `instrument_id` (string), `symbol` (string), `company_name` (string), `filer_name` (string), `form_type` (string), `filing_date` (string), `report_date` (string), `items` (array), `primary_document` (string), `filing_url` (string), `classification` (ipo | spac | shell_company | resale | other), `proposed_symbol` (string), `proposed_exchange` (string), `price_range_low` (number), `price_range_high` (number)

```sh
curl 'https://api.quantset.dev/api/v1/ipos?limit=20' -H 'X-API-Key: YOUR_API_KEY'
```

#### US Congressional stock disclosures

`GET /api/v1/politician-trades` · `get_politician_trades` · eligible API key

Public STOCK Act Periodic Transaction Reports disclosed by members of Congress.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `politician` (string, optional)
- `chamber` (House | Senate, optional)
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `politician` (string), `chamber` (string), `party` (string), `state` (string), `instrument_id` (string), `symbol` (string), `transaction_date` (string), `disclosure_date` (string), `transaction_type` (string), `amount_range` (string), `amount_low` (integer), `amount_high` (integer), `disclosure_url` (string)

```sh
curl 'https://api.quantset.dev/api/v1/politician-trades?limit=25' -H 'X-API-Key: YOUR_API_KEY'
```

#### Insider activity summary

`GET /api/v1/insider-activity` · `get_insider_activity` · sandbox sample key

Observed insider buys and sells over a date window anchored to the snapshot.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `window_start` (string), `window_end` (string), `data_through_date` (string), `instrument_latest_date` (string), `observed_buys` (integer), `observed_sells` (integer), `coverage` (partial | unavailable), `latest_available_filing_date` (string), `stale` (boolean)

```sh
curl 'https://api.quantset.dev/api/v1/insider-activity?ticker=us:NVDA' -H 'X-API-Key: mw_demo'
```

#### Institutional ownership

`GET /api/v1/institutional-ownership` · `get_institutional_ownership` · sandbox sample key

Reported institutional holders and ownership percentages.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `year` (integer, optional)
- `as_of` (string, optional) Point-in-time date YYYY-MM-DD (uses filings with filing_date <= as_of)
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `holder` (string), `manager_cik` (string), `year` (integer), `report_date` (string), `filing_date` (string), `shares` (number), `market_value_usd` (number), `portfolio_weight_pct` (number), `prior_shares` (number), `shares_change_qoq` (number), `shares_change_qoq_pct` (number), `position_change` (string), `pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/institutional-ownership?ticker=us:NVDA&limit=25' -H 'X-API-Key: mw_demo'
```

#### Shares outstanding history

`GET /api/v1/shares-outstanding` · `get_shares_outstanding` · sandbox sample key

Reported share counts with both period-end and public filing dates.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 50) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `cik` (string), `as_of_date` (string), `knowledge_date` (string), `shares_outstanding` (number), `form` (string), `accession` (string)

```sh
curl 'https://api.quantset.dev/api/v1/shares-outstanding?ticker=us:NVDA&limit=20' -H 'X-API-Key: mw_demo'
```

#### Revenue segments

`GET /api/v1/segments` · `get_revenue_segments` · sandbox sample key

Product and geographic revenue segment disclosures.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `year` (integer, optional)
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `year` (integer), `quarter` (integer), `revenue` (number)

```sh
curl 'https://api.quantset.dev/api/v1/segments?ticker=us:NVDA&limit=20' -H 'X-API-Key: mw_demo'
```

#### Debt maturities

`GET /api/v1/debt-maturities` · `get_debt_maturities` · sandbox sample key

Reported debt maturity schedules.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 20) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `year` (integer)

```sh
curl 'https://api.quantset.dev/api/v1/debt-maturities?ticker=us:NVDA&limit=10' -H 'X-API-Key: mw_demo'
```

#### Executive compensation

`GET /api/v1/executive-compensation` · `get_executive_compensation` · sandbox sample key

Reported proxy-statement executive compensation.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 20) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `year` (integer)

```sh
curl 'https://api.quantset.dev/api/v1/executive-compensation?ticker=us:NVDA&limit=10' -H 'X-API-Key: mw_demo'
```

#### Employees

`GET /api/v1/employees` · `get_employees` · sandbox sample key

Annual reported employee headcount.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `limit` (integer, optional, default 20) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `year` (integer), `employee_count` (integer)

```sh
curl 'https://api.quantset.dev/api/v1/employees?ticker=us:NVDA&limit=10' -H 'X-API-Key: mw_demo'
```

#### EDGAR filing scans

`GET /api/v1/filing-scans` · `get_filing_scans` · sandbox sample key

Annual filing financial and valuation scan summaries.

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `kind` (all | finance | valuation, optional, default all)
- `limit` (integer, optional, default 10) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `dataset` (string), `title` (string), `basis` (string), `records` (array)

```sh
curl 'https://api.quantset.dev/api/v1/filing-scans?ticker=us:NVDA' -H 'X-API-Key: mw_demo'
```

#### SEC XBRL company facts

`GET /api/v1/sec/company-facts` · `get_sec_facts` · sandbox sample key

Read as-filed XBRL facts using exactly one of ticker or issuer_cik. Use filed_before for an inclusive end-of-day UTC cutoff.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `issuer_cik` (string, optional) SEC Central Index Key for the issuer, as one to ten decimal digits.
- `taxonomy` (string, optional) Limit results to one taxonomy, such as us-gaap.
- `concept` (string, optional) Limit results to one concept, such as Revenues.
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `filed_before` (string, optional) Only return facts filed on or before this date, YYYY-MM-DD.
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `fact_id` (string), `cik` (string), `entity_name` (string), `taxonomy` (string), `concept` (string), `unit` (string), `period_start` (string), `period_end` (string), `value` (number), `value_text` (string), `accession` (string), `filed` (string), `form` (string), `filing_fiscal_year` (integer), `filing_fiscal_period` (string), `frame` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/company-facts?ticker=us:NVDA&limit=20' -H 'X-API-Key: mw_demo'
```

#### SEC Form 3/4/5 insider transactions

`GET /api/v1/sec/insider-transactions` · `get_sec_transactions` · sandbox sample key

Individual as-filed insider trades with Rule 10b5-1 plan flags and post-trade balances, queryable per issuer or market-wide.

- `issuer_cik` (string, optional) Optional SEC Central Index Key of the issuer.
- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `owner_cik` (string, optional) Filter to filings by a specific reporting-owner CIK
- `transaction_code` (string, optional) SEC Form 4 transaction code, e.g. P (open-market buy) or S (sale)
- `min_value` (number, optional) Minimum reported transaction_value
- `exclude_10b5_1` (boolean, optional, default False) Exclude trades reported under a Rule 10b5-1 trading plan
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `filed_before` (string, optional) Only return transactions filed on or before this date, YYYY-MM-DD.
- `include_amendments` (boolean, optional, default False) Include amended filings.
- `limit` (integer, optional, default 500) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `transaction_id` (string), `accession` (string), `transaction_kind` (non_derivative | derivative), `instrument_id` (string), `issuer_cik` (string), `ticker` (string), `filing_date` (string), `transaction_date` (string), `form` (string), `is_amendment` (boolean), `is_10b5_1` (boolean), `transaction_code` (string), `acquired_disposed` (string), `is_buy` (boolean), `security_title` (string), `shares` (number), `price_per_share` (number), `transaction_value` (number), `shares_after` (number), `ownership_type` (string), `owner_count` (integer), `owners` (array), `footnotes` (array), `disclosure_quarter` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/insider-transactions?ticker=us:NVDA&limit=20' -H 'X-API-Key: mw_demo'
```

#### SEC Form 3/4/5 insider holdings

`GET /api/v1/sec/insider-holdings` · `get_sec_holdings` · sandbox sample key

Reported non-transaction share and derivative ownership balances from Form 3/4/5.

- `ticker` (string, optional) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `issuer_cik` (string, optional) SEC Central Index Key for the issuer, as one to ten decimal digits.
- `owner_cik` (string, optional) SEC Central Index Key for the reporting owner, as one to ten decimal digits.
- `filed_before` (string, optional)
- `include_amendments` (boolean, optional, default False)
- `limit` (integer, optional, default 200) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `holding_id` (string), `accession` (string), `holding_kind` (string), `instrument_id` (string), `issuer_cik` (string), `ticker` (string), `filing_date` (string), `form` (string), `is_amendment` (boolean), `is_10b5_1` (boolean), `security_title` (string), `shares_owned` (number), `value_owned` (number), `ownership_type` (string), `owners` (array), `disclosure_quarter` (string)

```sh
curl 'https://api.quantset.dev/api/v1/sec/insider-holdings?ticker=us:NVDA&limit=20' -H 'X-API-Key: mw_demo'
```

#### Cross-company insider profile

`GET /api/v1/sec/insiders` · `get_sec_insider_owner` · eligible API key

Every public issuer where a given executive, director, or 10% owner has filed Form 3/4/5, with buy/sell totals.

- `owner_cik` (string, required) SEC Central Index Key for the reporting owner, as one to ten decimal digits.
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `owner_cik` (string), `owner_name` (string), `instrument_id` (string), `issuer_cik` (string), `issuer_name` (string), `ticker` (string), `relationship` (string), `title` (string), `filings_count` (integer), `first_filing_date` (string), `latest_filing_date` (string), `buy_transactions` (integer), `sell_transactions` (integer), `buy_value` (number), `sell_value` (number)

```sh
curl 'https://api.quantset.dev/api/v1/sec/insiders?owner_cik=0001197649' -H 'X-API-Key: YOUR_API_KEY'
```

### Regional filings and reference series

Local statutory disclosures across China, Hong Kong, Korea, Europe and India, plus market reference series.

#### Regional filings and disclosures

`GET /api/v1/regional-filings` · `get_regional_filings` · sandbox sample key

Local exchange and statutory disclosures for global:* listings (KRX DART, China A-Shares, HKEX, Europe/UK, India).

- `ticker` (string, required) Catalog selector, such as NVDA, 7203.T, or a canonical ID such as us:NVDA.
- `dataset` (string, optional) Optional published dataset identifier, e.g. financial-indicators.
- `limit` (integer, optional, default 30) Maximum number of rows to return.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `instrument_id` (string), `dataset` (string), `title` (string), `basis` (string), `records` (array)

```sh
curl 'https://api.quantset.dev/api/v1/regional-filings?ticker=global:SHEL.L' -H 'X-API-Key: mw_demo'
```

#### List reference series

`GET /api/v1/reference/series` · `get_reference_series` · eligible API key

Browse daily and 5-minute market reference series for Japan, the UK, Hong Kong and world markets. Use reference prices to retrieve observations for a selected series.

- `market` (jp | uk | hk | world, required)
- `interval` (1d | 5m, optional, default 1d)
- `q` (string, optional) Search text, matched against ticker, exchange, country and name.
- `series_group` (string, optional)
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `market` (string), `series_group` (string), `series_symbol` (string), `first_date` (string), `last_date` (string), `observations` (integer)

```sh
curl 'https://api.quantset.dev/api/v1/reference/series?market=jp&limit=10' -H 'X-API-Key: YOUR_API_KEY'
```

#### Reference series prices

`GET /api/v1/reference/prices` · `get_reference_prices` · eligible API key

Read historical bars for one market reference series. Use the reference series catalog to discover its market, group, symbol and interval.

- `market` (jp | uk | hk | world, required)
- `series_group` (string, required)
- `symbol` (string, required) Ticker symbol.
- `interval` (1d | 5m, optional, default 1d)
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 1000) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `market` (string), `series_group` (string), `symbol` (string), `interval` (1d | 5m), `date` (string), `open` (number), `high` (number), `low` (number), `close` (number), `volume` (number), `open_interest` (number), `reported_timestamp` (string)

```sh
curl 'https://api.quantset.dev/api/v1/reference/prices?market=jp&series_group=jp%2Ftse+indices&symbol=TOPIX.JP' -H 'X-API-Key: YOUR_API_KEY'
```

### Macro and FX

US Treasury yields, cataloged economic series and USD exchange rates.

#### US inflation pack (CPI, Core CPI, PCE, PPI & breakevens)

`GET /api/v1/macro/inflation` · `get_macro_inflation` · eligible API key

Headline & Core CPI, Headline & Core PCE, PPI, and 5Y/10Y breakeven inflation with pre-computed MoM and YoY percent changes in one call.

- `mode` (snapshot | historical, optional, default snapshot)
- `series_id` (string, optional)
- `limit` (integer, optional) Historical mode only. Defaults to 50 observations.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `series_id` (string), `name` (string), `category` (string), `frequency` (string), `unit` (string), `latest_date` (string), `latest_value` (number), `prior_value` (number), `period_change` (number), `mom_change_pct` (number), `qoq_change_pct` (number), `yoy_change_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/macro/inflation' -H 'X-API-Key: YOUR_API_KEY'
```

#### US labor market pack (Payrolls, Unemployment, JOLTS & Claims)

`GET /api/v1/macro/labor` · `get_macro_labor` · eligible API key

Nonfarm payrolls, U-3 & U-6 unemployment, participation rate, hourly earnings, weekly hours, JOLTS job openings, and weekly jobless claims with period and YoY changes.

- `mode` (snapshot | historical, optional, default snapshot)
- `series_id` (string, optional)
- `limit` (integer, optional) Historical mode only. Defaults to 50 observations.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `series_id` (string), `name` (string), `category` (string), `frequency` (string), `unit` (string), `latest_date` (string), `latest_value` (number), `prior_value` (number), `period_change` (number), `mom_change_pct` (number), `qoq_change_pct` (number), `yoy_change_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/macro/labor' -H 'X-API-Key: YOUR_API_KEY'
```

#### US GDP, corporate profits & activity pack

`GET /api/v1/macro/gdp` · `get_macro_gdp` · eligible API key

Real & Nominal GDP, QoQ SAAR GDP growth, private investment, corporate profits after tax, retail sales, industrial production, and consumer sentiment.

- `mode` (snapshot | historical, optional, default snapshot)
- `series_id` (string, optional)
- `limit` (integer, optional) Historical mode only. Defaults to 50 observations.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `series_id` (string), `name` (string), `category` (string), `frequency` (string), `unit` (string), `latest_date` (string), `latest_value` (number), `prior_value` (number), `period_change` (number), `mom_change_pct` (number), `qoq_change_pct` (number), `yoy_change_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/macro/gdp' -H 'X-API-Key: YOUR_API_KEY'
```

#### Global central bank policy rates (10 central banks)

`GET /api/v1/macro/central-bank-rates` · `get_macro_central_bank_rates` · eligible API key

Official daily policy rates, prior rate, and last rate move in bps across 10 major central banks (Fed, ECB, BoE, BoJ, BoC, RBA, SNB, RBNZ, Riksbank, Norges Bank). This operation uses live observations and reports provenance.observed_at in UTC. Historical generation replay is unavailable.

- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `bank_code` (string), `central_bank` (string), `currency` (string), `date` (string), `policy_rate_pct` (number), `prior_rate_pct` (number), `last_change_bps` (number), `last_change_date` (string)

```sh
curl 'https://api.quantset.dev/api/v1/macro/central-bank-rates' -H 'X-API-Key: YOUR_API_KEY'
```

#### Treasury rates

`GET /api/v1/treasury` · `get_treasury` · eligible API key

Daily US Treasury yields across maturities from 1M to 30Y.

- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 252) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `date` (string), `rates_pct` (object)

```sh
curl 'https://api.quantset.dev/api/v1/treasury?limit=30' -H 'X-API-Key: YOUR_API_KEY'
```

#### H.15 Treasury curve, real yields & spreads

`GET /api/v1/macro/treasury-yields` · `get_macro_treasury_yields` · eligible API key

Daily Federal Reserve H.15 constant-maturity yields (1Y to 30Y), effective Fed Funds rate, 10Y-2Y and 10Y-3M curve spreads, 10Y TIPS real yield and 10Y breakeven inflation.

- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 60) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `date` (string), `fed_funds_pct` (number), `yield_1y_pct` (number), `yield_2y_pct` (number), `yield_3y_pct` (number), `yield_5y_pct` (number), `yield_7y_pct` (number), `yield_10y_pct` (number), `yield_20y_pct` (number), `yield_30y_pct` (number), `spread_10y_2y_pct` (number), `spread_10y_3m_pct` (number), `real_yield_10y_pct` (number), `breakeven_10y_pct` (number)

```sh
curl 'https://api.quantset.dev/api/v1/macro/treasury-yields?limit=10' -H 'X-API-Key: YOUR_API_KEY'
```

#### List macro series

`GET /api/v1/macro/series` · `get_macro_series_catalog` · keyless

Browse all macro economic series in the warehouse with titles, categories, date ranges and latest values.

- `q` (string, optional) Filter by series code, title, or category
- `category` (string, optional)
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.

Response fields: `series_id` (string), `title` (string), `category` (string), `first_date` (string), `last_date` (string), `observations` (integer), `latest_value` (number)

```sh
curl 'https://api.quantset.dev/api/v1/macro/series?q=rate'
```

#### Economic indicators

`GET /api/v1/macro/indicators` · `get_macro_indicators` · eligible API key

Dated macro observations such as UNRATE, FEDFUNDS, CPIAUCSL, high-yield spreads and real GDP growth.

- `series_ids` (string, optional) Comma-separated macroeconomic series IDs (e.g. UNRATE,FEDFUNDS,CPIAUCSL,A191RL1Q225SBEA)
- `latest_only` (boolean, optional, default False) Return only the latest observation per series
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 100) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `series_id` (string), `date` (string), `value` (number), `title` (string)

```sh
curl 'https://api.quantset.dev/api/v1/macro/indicators?series_ids=UNRATE,FEDFUNDS,CPIAUCSL&latest_only=true' -H 'X-API-Key: YOUR_API_KEY'
```

#### FX reference rates

`GET /api/v1/fx/rates` · `get_fx_rates` · eligible API key

Daily and historical USD exchange rates per unit of base currency.

- `base_currency` (string, optional) Comma-separated 3-letter currency codes (e.g. GBP,EUR,JPY)
- `latest_only` (boolean, optional, default False) Return only the most recent rate per currency
- `start` (string, optional) First date to include, as an ISO date (YYYY-MM-DD).
- `end` (string, optional) Last date to include, as an ISO date (YYYY-MM-DD).
- `limit` (integer, optional, default 250) Maximum number of rows to return.
- `cursor` (string, optional) Opaque continuation. Pass it unchanged with the original filters and snapshot_id.
- `snapshot_id` (string, optional) Pin the request to one immutable snapshot so a read across several pages stays consistent.
- `format` (json | csv, optional, default json) Return a JSON page or UTF-8 CSV rows.
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `date` (string), `base_currency` (string), `quote_currency` (string), `usd_per_unit` (number)

```sh
curl 'https://api.quantset.dev/api/v1/fx/rates?base_currency=EUR,GBP,JPY&latest_only=true' -H 'X-API-Key: YOUR_API_KEY'
```

### Account and integration

Manage account webhooks, provision an agent credential and report a data issue.

#### Create a webhook

`POST /api/v1/webhooks` · `create_webhook` · eligible API key

Create a subscription and save its signing secret. Before retrying a timed-out create, list your subscriptions to check its result.


Response fields: `id` (string), `url` (string), `events` (array), `description` (string), `created_at` (string), `secret` (string)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/webhooks' -H 'X-API-Key: YOUR_API_KEY' -H 'Content-Type: application/json' --data '{"url":"https://example.com/webhooks","events":["filing.created"]}'
```

#### Delete a webhook

`DELETE /api/v1/webhooks/{webhook_id}` · `delete_webhook` · eligible API key

Delete an account webhook by ID. List webhooks after a timeout to reconcile the result.

- `webhook_id` (string, required)

Response fields: `deleted` (boolean), `id` (string)

```sh
curl -X DELETE 'https://api.quantset.dev/api/v1/webhooks/YOUR_WEBHOOK_ID' -H 'X-API-Key: YOUR_API_KEY'
```

#### Test a webhook

`POST /api/v1/webhooks/{webhook_id}/test` · `test_webhook` · eligible API key

Attempt a delivery to an existing webhook. Check delivery state after a timeout before sending another test.

- `webhook_id` (string, required)
- `X-Max-Credits` (integer, optional) Refuse the request if its maximum charge exceeds this ceiling.
- `X-Workflow-Id` (string, optional) Optional printable identifier for grouping charges in a research workflow.

Response fields: `webhook_id` (string), `event_id` (string), `status_code` (integer), `delivered` (boolean)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/webhooks/YOUR_WEBHOOK_ID/test' -H 'X-API-Key: YOUR_API_KEY'
```

#### Published credit rate card

`GET /api/v1/billing/rate-card` · `get_rate_card` · keyless

Read the effective tariff version and billable units for each operation. This is a free discovery operation.


Response fields: `rate_card_version` (string), `rules` (object)

```sh
curl 'https://api.quantset.dev/api/v1/billing/rate-card'
```

#### Estimate request credits

`POST /api/v1/billing/estimate` · `estimate_credit_cost` · keyless

Calculate a request's maximum charge at the current published rate without executing the data query. Eligible sandbox reads and discovery operations can cost zero.


Response fields: `operation` (string), `rate_card_version` (string), `maximum_credits` (integer), `exact` (boolean), `units` (object)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/billing/estimate' -H 'Content-Type: application/json' --data '{"method":"GET","path":"/prices","params":{"ticker":"NVDA","limit":251}}'
```

#### Partner catalog

`GET /api/v1/partner-catalog` · `get_partner_catalog` · keyless

Discover the public integration URLs and plans for QuantSet.


Response fields: `provider` (string), `homepage` (string), `docs_url` (string), `llms_txt` (string), `agent_onboarding_skill` (string), `openapi_url` (string), `mcp` (object), `coverage` (object), `citation_and_provenance` (object), `plans` (object), `contact` (object)

```sh
curl 'https://api.quantset.dev/api/v1/partner-catalog'
```

#### Create an agent sandbox key

`POST /api/v1/agent/signup` · `create_agent_sandbox_key` · keyless

Create an account (201) or rotate an unconfirmed, unfunded account key (200). Confirmed or funded accounts return 409. Save the returned key immediately.


Response fields: `api_key` (string), `email` (string), `agent_name` (string), `plan` (string), `status` (string), `trial_credits_remaining` (integer), `checkout_link_endpoint` (string), `feedback_endpoint` (string), `docs_url` (string), `message` (string)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/agent/signup' -H 'Content-Type: application/json' --data '{"email":"YOUR_ACCOUNT_EMAIL","agent_name":"Research agent"}'
```

#### Create an agent checkout link

`POST /api/v1/agent/checkout-link` · `create_agent_checkout_link` · eligible API key

Create a checkout link for a personal key. Share the link with the account owner for payment.


Response fields: `checkout_url` (string), `plan` (credits | growth | scale | developer | pro | commercial | developer_annual | pro_annual | commercial_annual), `amount_usd` (integer), `included_credits` (integer), `mode` (stripe | console), `message` (string)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/agent/checkout-link' -H 'X-API-Key: YOUR_API_KEY' -H 'Content-Type: application/json' --data '{"plan":"credits"}'
```

#### Submit API feedback

`POST /api/v1/feedback` · `submit_feedback` · sandbox sample key

Submit a data note with any valid key, including sandbox and unfunded keys. A successful submission returns 201. Each subject can send six notes per 24 hours.


Response fields: `status` (string), `notes_left_today` (integer)

```sh
curl -X POST 'https://api.quantset.dev/api/v1/feedback' -H 'X-API-Key: mw_demo' -H 'Content-Type: application/json' --data '{"note":"Check the filing date for this observation.","endpoint":"/api/v1/financial-statements/income","symbol":"NVDA"}'
```

## MCP server

- https://api.quantset.dev/mcp uses Streamable HTTP. Connect with OAuth (S256 PKCE) or an API key in the Bearer header.
- The `warehouse://contract` resource contains this operation guide.
- The sandbox aliases qs_demo and mw_demo share the same sample allowance.

### Read-only tools

- `get_rate_card` Get the published credit rate card
- `get_capabilities` Get market coverage and status
- `list_instruments` Find market instruments
- `get_quotes` Get latest quotes
- `get_price_history` Get daily price history
- `get_intraday_bars` Get hourly price bars
- `get_company_snapshot` Get a company snapshot
- `get_peers` Get comparable companies
- `get_market_status` Get current US market status
- `get_screener_filters` Discover structured screener filters
- `get_financial_statements` Get financial statements
- `get_financial_metrics` Get historical financial ratios and efficiency metrics
- `get_fundamentals` Get reported fundamentals
- `get_estimates_and_earnings` Get analyst estimates and earnings
- `get_corporate_actions` Get dividends, splits and shareholder returns
- `get_sec_filings` Get SEC facts and ownership disclosures
- `get_etf_data` Get fund profiles, holdings and exposures
- `get_macro_and_fx` Get economic indicators and exchange rates
- `screen_stocks` Screen stocks
- `search_screener` Screen stocks with arbitrary statement & ratio DSL filters

## Documentation

- Quickstart https://quantset.dev/docs/quickstart
- AI agents https://quantset.dev/docs/agents
- Agent signup and checkout https://api.quantset.dev/skill.md
- All operations https://quantset.dev/docs/api
- OpenAPI 3.1 https://api.quantset.dev/openapi.json
