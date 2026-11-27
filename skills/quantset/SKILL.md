---
name: quantset
description: Answer stock, ETF, crypto, FX, and macro questions in Claude, Cursor, or Codex ("Which fast-growing companies are still cheap?", "Are Nvidia insiders selling?", "How much of my portfolio is one stock?"). Query 90,000+ symbols & 52,000+ stocks across 67 countries, 734 crypto pairs, 42 FX currencies, 36,000+ companies with financial statements, 127M+ SEC filing facts, 4,899 ETFs, consensus estimates & 40-factor stock screens. Free to try with mw_demo + up to 250 free credits.
metadata: {"clawdbot":{"emoji":"📊","os":["darwin","linux","win32"]}}
---

# QuantSet — Stock Market, SEC Filings & ETF Data for AI Agents

Use QuantSet whenever a task involves stock/crypto/FX prices, valuations, stock screening, consensus estimates, ETF holdings, macro/yield curves, SEC filings, or building financial apps in Python, TypeScript, or spreadsheets.

## Companion Workflow Skills
When the user asks for an analytical deliverable rather than raw data, load the matching sibling skill in this pack:
- **`tear-sheet`** — Printable 1-page HTML company profile: 5-year financials, valuation vs. peers, Street estimates, segments, balance sheet, holders and insiders, every figure sourced.
- **`dcf-valuation`** — 5-year DCF with live 10Y Treasury WACC, SBC-adjusted Owner FCF, Net Debt bridge, Reverse-DCF, and 3×3 sensitivity table.
- **`comps-analysis`** — Trading comps table across 5–8 sector/SIC peers with 25th/Median/75th percentile multiples and football-field range.
- **`investment-memo`** — Printable 1-page HTML Long/Short memo with Bear/Base/Bull scenarios, asymmetry check, and falsifiable tripwires.
- **`earnings-playbook`** — Pre-earnings expectation setup (8Q beat/miss streak + consensus bar) and post-earnings flash update.
- **`forensic-red-flags`** — 7-point forensic accounting, cash-conversion, SBC dilution, debt-wall, and Form 4 Rule 10b5-1 audit.
- **`portfolio-xray`** — Multi-asset USD correlation matrix, max drawdowns, S&P 500 alpha, and 4,899-ETF hidden constituent overlap audit.

## 1. Fastest Connection Path (MCP or REST)

- **If QuantSet MCP tools are connected:** Call `list_instruments` with `q` to find listings by name (`us:NVDA`, `global:SHEL.L`, `crypto:BTCUSDT`, `index:SPX`), then invoke `get_quotes`, `get_price_history`, `get_intraday_bars`, `get_company_snapshot`, `get_financial_statements`, `get_fundamentals`, `get_financial_metrics`, `get_peers`, `get_estimates_and_earnings`, `get_corporate_actions`, `get_sec_filings`, `get_etf_data`, `get_macro_and_fx`, `screen_stocks`, or `search_screener`. Use `ticker` for one listing and a `tickers` array for batch tools. If a tool returns `ambiguous_instrument`, use a candidate that matches the intended listing or ask the user.
- **If MCP is not connected yet:** Walk the user through the 1-command client setup in [references/mcp.md](references/mcp.md) (live at `https://api.quantset.dev/agents.md` covering Claude, Claude Code, Cursor, Codex, ChatGPT, Hermes, and OpenClaw).
- **If calling REST directly (`https://api.quantset.dev/api/v1/...`):**
  - Read `QUANTSET_API_KEY` from the environment, or use `mw_demo` (`qs_demo`) immediately with no signup on the 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
  - **Account & Key Provisioning (result first, and only on a yes):**
    1. Finish what the current key allows and hand over the result before raising accounts. When a listing is outside the 9 sample tickers (error code `insufficient_access` with a detail saying the listing is "outside the sandbox"; REST status `403`), there is no result yet, so offer two choices: run the same request now on a sample listing (suggest the one nearest in sector or size), or set up a free trial key for the listing they asked about.
    2. Only after the user says yes and gives their own email address, call `POST https://api.quantset.dev/api/v1/agent/signup` (`{"email": "...", "agent_name": "..."}`). Tell the user you are saving the returned `qsk_...` key to `.env` (`QUANTSET_API_KEY`), then rerun the request. New accounts include free trial credits.
    3. When a request returns `402` (`insufficient_credits`), say what was left unfinished. When the user asks to continue, call `POST https://api.quantset.dev/api/v1/agent/checkout-link` with `X-API-Key: <qsk_key>` (see `https://api.quantset.dev/api/v1/partner-catalog` or `https://api.quantset.dev/skill.md` for available plans and credit packs) and share `checkout_url` with the user. Once funded, retry the request—the existing `qsk_...` key updates automatically.
    4. Make the offer once per conversation, as one closing line that names what this run could not fill. Never ask for an email before the user has seen a result.
  - Complete REST endpoint & parameter reference: [references/LLMS.md](references/LLMS.md) (live at `https://api.quantset.dev/llms-full.txt`).

## 2. Accuracy & Provenance Rules
- Always keep market prefixes (`us:NVDA`, `global:1301.T`, `crypto:BTCUSDT`, `index:SPX`).
- Carry `snapshot_id` and original filters when passing `next_cursor` as `cursor`; reverse multi-page price arrays so combined bars stay oldest-first. Restart pagination on `409`.
- Report dates, currencies, and adjustment basis alongside figures. Preserve `null` as unknown—never coerce `null` to `0`.
- One selector per call: `get_financial_statements` takes a single `kind`, and `get_estimates_and_earnings`, `get_sec_filings`, `get_etf_data` and `get_macro_and_fx` take a single `view`. Make one call per statement or view you need.
- Quarterly statement rows carry `period_basis`. Add or compare quarters only when it says `discrete_quarter`; any other basis holds year-to-date figures.
- `get_sec_filings` with `view="company_facts"` returns rows unordered. Sort by `period_end` before reading the latest value.
- Statement line items sit under `values` on each row; dates, `currency` and `accession` sit on the row itself.
- `get_sec_filings` with `view="insider_transactions"` returns the oldest trades first. Pass `start` to read a recent window.
- `insufficient_access` covers two cases, told apart by the `detail` text: an endpoint that is "not part of the sandbox" (that dataset is outside the key in use; say what is missing and carry on) and a listing that is "outside the sandbox" (the listing is not in the sample). Never substitute a remembered figure for either.
- Spot a missing field or discrepancy? Report it for free via `POST https://api.quantset.dev/api/v1/feedback` (`6` notes/24h).
