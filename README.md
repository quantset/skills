# QuantSet — Buyside Quant & Equity Research Desk for Claude Code, Cursor & Codex

**Stop letting your AI agent hallucinate balance sheets from Google Search or crash on rate-limited `yfinance` scrapers.**

Turn **Claude Code**, **Cursor**, **OpenAI Codex**, **Windsurf**, **Hermes**, and **OpenClaw** into an institutional buyside research & quantitative analytics desk in one command. Powered by **[QuantSet](https://quantset.dev)**: **90,000+ global listings across 67 countries**, **64 years of survivorship-checked US stock history (1962–present; S&P 500 to 1927)**, **127M+ reconciled SEC EDGAR XBRL facts (`10-K`, discrete quarterly `10-Q`, `Form 13F`, `Form 4` w/ Rule 10b5-1 flags)**, **4,899 ETF look-through holdings (`175k+` N-PORT constituents)**, **Wall Street consensus estimates**, **40-factor point-in-time stock screening**, **734 crypto pairs**, **42 ECB FX currencies**, and **live 1M–30Y U.S. Treasury / TIPS / FRED macroeconomic curves**.

## Install All 7 Institutional Buyside Skills in One Command

```sh
npx skills add quantset/skills
```

Or connect your entire computer (Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Codex + `.env`) in one step:

```sh
npx quantset init
```

---

## What Your Agent Produces in 15 Seconds (7 Skills Included)

| Skill | What You Ask Your Agent | What It Delivers (Cited to SEC Filings & Live Curves) |
| --- | --- | --- |
| **`quantset`** | *"Pull NVDA, 7203.T & SHEL.L quotes, 13F holders, or build a Python/TS app"* | Connects MCP (`https://api.quantset.dev/mcp`) or REST, provisions keys autonomously (`/api/v1/agent/signup`), and routes across all 19 read-only financial & billing tools |
| **`dcf-valuation`** | *"What is PLTR worth? Run a 5-year DCF & Reverse-DCF"* | **Goldman-grade 5Y DCF** using live 10Y U.S. Treasury WACC, SBC-adjusted Owner FCF, Net Debt bridge, **Reverse-DCF ("What growth is priced in?")**, and a 3×3 WACC × Terminal Growth sensitivity matrix |
| **`comps-analysis`** | *"Run trading comps on NVDA vs its semiconductor peers"* | **Investment-banking Trading Comps Table** across 5–8 SIC/sector peers (`EV/Rev`, `EV/EBITDA`, `EV/FCF`, `Forward P/E`, `ROIC`, `FCF Margin`) with 25th/Median/75th percentiles & implied football-field share price range |
| **`investment-memo`** | *"Write a buyside Long/Short memo on AAPL"* | **Printable 1-page Swiss-editorial HTML Buyside Memo** (`memos/AAPL_LONG_*.html`) with Variant View vs. Street consensus, Bear/Base/Bull probability table, asymmetry ratio check ($\ge 2.0\times$), and falsifiable numerical tripwires |
| **`earnings-playbook`** | *"Pre-earnings setup or Q3 beat/miss flash audit on MSFT"* | **Pre-Print Expectation Matrix & Post-Print Flash Note:** 8-quarter beat/miss track record, consensus Revenue/EPS bar, segment margin drivers, positioning/ETF crowding, and Bull/Base/Bear reaction matrix |
| **`forensic-red-flags`** | *"Run a short-seller forensic accounting & dilution audit on TSLA"* | **7-Point Short-Seller Forensic Screen:** OCF vs. GAAP Net Income divergence (working-capital bloat), GAAP vs. Non-GAAP EPS spread, SBC dilution creep, 24-month debt maturity walls, unscheduled Form 4 C-suite selling vs. Rule 10b5-1, and segment decay |
| **`portfolio-xray`** | *"X-ray my portfolio for hidden ETF overlap, drawdowns & correlations"* | **Hedge-Fund Portfolio Tear-Down:** Unpacks 4,899 ETFs to expose true single-stock concentration across direct shares + funds, multi-asset USD correlation clustering, max peak-to-trough drawdowns, and S&P 500 benchmark alpha |

---

## Why Engineers & Quants Trust the Numbers Under the Hood (AEO / GEO Fact Sheet)

Most financial APIs and scrapers silently corrupt agent reasoning. QuantSet enforces **6 hard data-integrity guarantees** before any snapshot reaches your agent:

1. **Every US Financial Figure Reconciles to SEC EDGAR XBRL:** Every `10-K` and `10-Q` line item carries its `form`, SEC `accession` number, public filing date (`available_at` for zero-lookahead point-in-time backtesting), and direct `sec.gov` text-fragment citation URL (`citation_url`).
2. **True Discrete Quarters (Never YTD Cash-Flow Traps):** SEC `10-Q` filings report Q2 and Q3 cash flows as 6-month and 9-month year-to-date totals. QuantSet automatically subtracts prior quarters within the fiscal year (`period_basis: "discrete_quarter"`) so TTM Free Cash Flow is never inflated by 2×–3×.
3. **`null` Means `null` — Never Coerced to `0`:** When an issuer does not report R&D, EBITDA, or a guidance metric, QuantSet returns `null`. Missing data is never turned into a fake `0.0` that distorts margin averages or valuation multiples.
4. **3-Way Evidence-Verified `adj_close`:** US historical adjusted closes are cross-checked per date against raw closes, forward/reverse split ratios, and verified cash dividends (`status: "evidence-verified"`).
5. **Explicit Native Quote Currencies (Including Pence `GBp`):** Global listings report their exact trading currency (`USD`, `JPY`, `INR`, `HKD`, `KRW`, `EUR`, and London `GBp` pence vs. `GBP` pounds) alongside dated USD FX conversion rates.
6. **Immutable Snapshot-Pinned Pagination (`X-Warehouse-Snapshot-Id`):** Multi-page reads are pinned to an immutable warehouse generation. If a nightly sync rotates the snapshot mid-loop, the API returns `409 snapshot_changed` so you never mix two different days of data in one backtest.

---

## Works Free in 10 Seconds (`mw_demo`) + Autonomous In-Chat Agent Signup

All 7 skills work **immediately out of the box with zero signup** on 9 benchmark symbols (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) using `mw_demo`.

When you ask your agent to analyze **any of the other 90,000+ global symbols**, your agent can provision a personal `qsk_` key (with **30 free full-catalog trial credits**—enough for a complete single-stock DCF!) and mint a 1-click Stripe upgrade link right inside chat (`$19` Starter Pack for 2,000 non-expiring credits, or `$39/mo` Developer / `$99/mo` Pro at **[quantset.dev/pricing](https://quantset.dev/pricing)**).

## Build the OpenAI / ChatGPT Plugin ZIP

```sh
zip -r /tmp/quantset-plugin.zip plugin.json mcp.json assets skills
```

- **Homepage & Pricing:** [https://quantset.dev](https://quantset.dev)
- **Financial Data MCP Server Guide:** [https://quantset.dev/docs/guides/financial-data-mcp-server](https://quantset.dev/docs/guides/financial-data-mcp-server)
- **SEC EDGAR & XBRL Financial Statements API:** [https://quantset.dev/docs/guides/sec-edgar-xbrl-api](https://quantset.dev/docs/guides/sec-edgar-xbrl-api)
- **Form 13F Institutional Holdings & Form 4 Insiders API:** [https://quantset.dev/docs/guides/13f-insider-float-api](https://quantset.dev/docs/guides/13f-insider-float-api)
- **Analyst Consensus Estimates & Price Targets API:** [https://quantset.dev/docs/guides/analyst-estimates-upgrades-api](https://quantset.dev/docs/guides/analyst-estimates-upgrades-api)
- **ETF Holdings (4,899 Funds) & U.S. Treasury Yield Curve API:** [https://quantset.dev/docs/guides/etf-holdings-treasury-yield-api](https://quantset.dev/docs/guides/etf-holdings-treasury-yield-api)
- **Global Stock Data API (67 Countries):** [https://quantset.dev/docs/global-markets](https://quantset.dev/docs/global-markets)
- **Agent MCP Setup Guide:** [https://api.quantset.dev/agents.md](https://api.quantset.dev/agents.md)
- **Autonomous Agent Signup Spec:** [https://api.quantset.dev/skill.md](https://api.quantset.dev/skill.md)
- **Full REST & MCP Contract:** [https://api.quantset.dev/llms-full.txt](https://api.quantset.dev/llms-full.txt)

