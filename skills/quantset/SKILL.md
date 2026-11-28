---
name: quantset
description: "Looks up live and historical market data through the QuantSet MCP server or REST API: stock, ETF, crypto and FX prices, financial statements, SEC filing facts, insider and institutional ownership, analyst estimates, ETF holdings, macro series and stock screens. Use when the user asks for a quote, price history, fundamentals, a filing figure, who holds or is selling a stock, what an ETF holds, a stock screen, or wants to build a finance app or spreadsheet on market data. Covers 90,000+ symbols and 52,000+ stocks in 67 countries, 36,000+ companies with financials, 4,800+ ETFs and 700+ crypto pairs. Free to try with mw_demo plus up to 250 free credits."
metadata: {"clawdbot":{"emoji":"📊","os":["darwin","linux","win32"]}}
---

# QuantSet — Stock Market, SEC Filings & ETF Data for AI Agents

Use QuantSet whenever a task involves stock/crypto/FX prices, valuations, stock screening, consensus estimates, ETF holdings, macro/yield curves, SEC filings, or building financial apps in Python, TypeScript, or spreadsheets.

## Companion Workflow Skills
When the user asks for an analytical deliverable rather than raw data, load the matching sibling skill in this pack:
- **`stock-screen`** — Turns a description into numeric rules, runs the screen and checks the top names against their filings.
- **`filing-research`** — Answers from the text of 10-K, 10-Q and 8-K filings with quotes and links; compares sections year over year.
- **`tear-sheet`** — Printable HTML company profile: 5-year financials, valuation vs. peers, Street estimates, segments, balance sheet, holders and insiders, every figure sourced.
- **`dcf-valuation`** — 5-year DCF with live 10Y Treasury WACC, SBC-adjusted Owner FCF, Net Debt bridge, Reverse-DCF, and 3×3 sensitivity table.
- **`comps-analysis`** — Trading comps table across 5–8 peers with 25th/Median/75th percentile multiples and an implied price range.
- **`investment-memo`** — Printable HTML Long/Short memo with Bear/Base/Bull scenarios, asymmetry check, and falsifiable tripwires.
- **`earnings-playbook`** — Pre-earnings expectation setup (8Q beat/miss record + consensus bar) and post-earnings flash update, with a workbook that grows each quarter.
- **`forensic-red-flags`** — 7-point forensic check: cash conversion, GAAP vs. adjusted EPS, SBC dilution, debt wall, insider selling, segments and ETF crowding.
- **`portfolio-xray`** — ETF look-through concentration, USD correlation matrix, drawdowns and performance against the S&P 500.

## 1. Fastest Connection Path (MCP or REST)

- **If QuantSet MCP tools are connected:** call `list_instruments` with `q` to find an instrument by name (`us:NVDA`, `global:SHEL.L`, `crypto:BTCUSDT`, `index:SPX`), then `get_quotes`, `get_price_history`, `get_intraday_bars`, `get_company_snapshot`, `get_financial_statements`, `get_fundamentals`, `get_financial_metrics`, `get_peers`, `get_estimates_and_earnings`, `get_corporate_actions`, `get_line_items`, `get_sec_filings`, `get_filing_documents`, `get_etf_data`, `get_returns_and_risk`, `get_market_activity`, `get_macro_and_fx`, `screen_stocks`, or `search_screener`. Every dataset in the REST API has a tool. Use `ticker` for one instrument and a `tickers` array for batch tools. If a tool returns `ambiguous_instrument`, use a candidate that matches the intended one or ask the user.
  - Tool names are written bare in these skills. Your client may show them with a prefix, for example `mcp__quantset__get_quotes`; they are the same tools.
- **If MCP is not connected yet:** walk the user through the 1-command client setup in [references/mcp.md](references/mcp.md) (live at `https://api.quantset.dev/agents.md` covering Claude, Claude Code, Cursor, Codex, ChatGPT, Hermes, and OpenClaw).
- **If calling REST directly (`https://api.quantset.dev/api/v1/...`):**
  - Read `QUANTSET_API_KEY` from the environment, or use the sample key `mw_demo` immediately with no signup on the 9 sample instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
  - **Account & Key Provisioning (result first, and only on a yes):**
    1. Finish what the current key allows and hand over the result before raising accounts. When an instrument is outside the sample (error code `insufficient_access` with a detail saying the listing is "outside the sandbox"; REST status `403`), there is no result yet, so offer two choices: run the same request now on a sample company (suggest the one nearest in sector or size), or set up a free trial key for the one they asked about.
    2. Only after the user says yes and gives their own email address, call `POST https://api.quantset.dev/api/v1/agent/signup` (`{"email": "...", "agent_name": "..."}`). Tell the user you are saving the returned `qsk_...` key to `.env` (`QUANTSET_API_KEY`), then rerun the request. New accounts include free trial credits.
    3. When a request returns `402` (`insufficient_credits`), say what was left unfinished. When the user asks to continue, call `POST https://api.quantset.dev/api/v1/agent/checkout-link` with `X-API-Key: <qsk_key>` (see `https://api.quantset.dev/api/v1/partner-catalog` or `https://api.quantset.dev/skill.md` for available plans and credit packs) and share `checkout_url` with the user. Once funded, retry the request—the existing `qsk_...` key updates automatically.
    4. Make the offer once per conversation, as one closing line that names what this run could not fill, and only when a gap came from `insufficient_access`. Never ask for an email before the user has seen a result.
  - Complete REST endpoint & parameter reference: [references/LLMS.md](references/LLMS.md) (live at `https://api.quantset.dev/llms-full.txt`). It opens with a contents list; search it for `METHOD /path`.
- **Before using a dataset for the first time, read [references/endpoint-notes.md](references/endpoint-notes.md).** It says how each response really behaves: default windows and ordering, what a call costs, which datasets are empty, and what works for non-US listings.

## 2. Accuracy & Provenance Rules

- Always keep market prefixes (`us:NVDA`, `global:1301.T`, `crypto:BTCUSDT`, `index:SPX`). For a company name, take its own shares over funds built on them, and its `us:` listing when it has one unless the user named another market.
- Carry `snapshot_id` and original filters when passing `next_cursor` as `cursor`; reverse multi-page price arrays so combined bars stay oldest-first. Restart pagination on `409`.
- Report dates, currencies, and adjustment basis alongside figures.
- One selector per call: `get_financial_statements` takes a single `kind`, and `get_estimates_and_earnings`, `get_sec_filings`, `get_etf_data` and `get_macro_and_fx` take a single `view`. `get_financial_statements` takes many `tickers` at once.
- `get_sec_filings` with `view="company_facts"` returns rows unordered, and each period appears in several filings: keep the row with the latest `filed` for each `period_end`.
- `get_sec_filings` with `view="insider_transactions"` starts with the earliest years on file. Pass `start` to read a recent window.
- `insufficient_access` covers two cases, told apart by the `detail` text: an endpoint that is "not part of the sandbox" (that dataset is outside the key in use; say what is missing and carry on) and a listing that is "outside the sandbox" (the instrument is not in the sample).
- Spot a missing field or discrepancy? Report it for free via `POST https://api.quantset.dev/api/v1/feedback` (`6` notes/24h).

## 3. Data Rules (They Apply to Every Call)

- **Where figures sit:** statement line items are under `values` (for example `values.revenue`); `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` are on the row.
- **Fiscal years:** `period="annual"` can return rolling twelve-month windows between the fiscal years. Drop every row whose `form` is `10-Q`; the rows left are fiscal years. That is why the calls ask for more rows than the years needed. For a US listing a row with no `form` is not from a filing: use it only for a year that has no `10-K` row. For a listing outside the US no row has a `form`, and all of them are fiscal years.
- **Quarters:** a quarterly row is a single quarter only when its `period_basis` is `discrete_quarter`; any other basis holds year-to-date figures. Never add or compare the two kinds: set a single quarter beside single quarters, and a year-to-date figure only beside the same point a year earlier. The same quarter can come back twice, with period ends up to a few weeks apart: match rows by the year and month of `period_end`, keep one per quarter, and prefer the one that has an `accession`.
- **Estimate rows:** the `estimates` view returns four rows: this quarter, next quarter, this fiscal year and next fiscal year. Their `period` labels vary by listing and a quarter and a fiscal year can end on the same date, so read the label and `period_end` together; `period_end` is a month-end label. Estimates are per share in the listing's reporting currency and on the Street's basis: they can differ from filed figures, and a company can file a loss while the consensus is a profit.
- **The snapshot mixes periods:** in `get_company_snapshot`, `free_cash_flow` and `ebitda_ttm` can be the last fiscal year's figures while `revenue_ttm` is trailing. Take EBITDA and free cash flow from the latest fiscal-year statement row and label them with its `period_end`.
- **Currency:** `price`, `market_cap_b` and `enterprise_value_b` are in US dollars (the `_b` fields in billions). `native_close` is the price in `quote_currency`, and statement figures are in `financial_currency`. Convert with `usd_rate` before combining the two.
- **Dates on filings:** `available_at` on an older period is the date of the latest filing that repeated it, not its first publication. Cite it only for the newest period.
- **Empty is not zero:** show a `null` as `n/a`. Never fill a gap from memory or a web search.
- **US-only datasets:** the error code `unsupported_instrument` means the dataset covers US listings only. Mark that section `n/a (US listings only)` and carry on. A key does not change it.
