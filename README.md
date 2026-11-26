# QuantSet Skills: put the global stock market inside your agent

Seven research skills and three slash commands for Claude, Cursor and Codex: DCF, comps, earnings, forensics, memos and portfolio x-ray, on live data.

**Free to start: 250 credits on signup, no card.** Sample tickers work with no signup at all.

## Ask it

- "Which fast-growing companies are still cheap?"
- "How much of my portfolio is secretly one stock? I hold IVV, QQQ and SMH."
- "Which carmaker is cheapest once you put them in one currency?"
- "Which companies are growing revenue 20%+ with 15%+ free cash flow margins and still trade under 15x EV/FCF?"
- "Are Nvidia insiders selling into the rally, and is it on a pre-arranged 10b5-1 plan?"
- "Who is buying back the most stock while trading at the cheapest multiples?"
- "Where in the AI supply chain is free cash flow growing fastest?"

## Connect in One Command

```sh
npx skills add quantset/skills
npx quantset init
```

- **`npx skills add quantset/skills`** installs all 7 research skills (`quantset`, `dcf-valuation`, `comps-analysis`, `investment-memo`, `earnings-playbook`, `forensic-red-flags`, `portfolio-xray`), 3 slash commands (`/dcf`, `/comps`, `/screen`), and the Cursor market-data routing rule.
- **`npx quantset init`** approves your computer in the browser, connects the QuantSet MCP server (`https://api.quantset.dev/mcp`) to the AI tools it finds, saves `QUANTSET_API_KEY` to `.env`, and verifies a first call.
- **Claude Code Plugin Marketplace:** `claude plugin marketplace add quantset/skills` then `claude plugin install quantset@quantset`
- **Cursor Marketplace Plugin:** Install from `quantset/skills` (includes `mcp.json`, 7 skills, `/dcf`, `/comps`, `/screen` commands, and `rules/quantset-market-data.mdc`).

---

## What is Inside the Warehouse

| Figure | Coverage |
| --- | --- |
| **`90,000+`** | Symbols covered across US, international, ETF, index, and crypto markets |
| **`67`** | Countries normalized into one schema and one set of canonical IDs (`us:NVDA`, `global:7203.T`, `global:SHEL.L`) |
| **`36,000+`** | Companies with standardized financial statements |
| **`127M+`** | Facts from SEC EDGAR filings since 2000 (`10-K`, discrete `10-Q`, `Form 13F`, `Form 4`, `8-K` guidance) |
| **`4,899`** | ETFs you can look through, with **`175,000+`** fund holdings mapped to tickers |
| **`42`** | Currencies with dated FX rates, plus daily 1M–30Y U.S. Treasury/TIPS curves and 82 macro series |

---

## Seven Research Skills Included

| Skill | Prompt Example | What Your Agent Delivers |
| --- | --- | --- |
| **`quantset`** | *"Pull NVDA, 7203.T & SHEL.L quotes, 13F holders, or build a Python/TS integration"* | Connects MCP (`https://api.quantset.dev/mcp`) or REST, provisions keys autonomously (`/api/v1/agent/signup`), and queries every dataset |
| **`dcf-valuation`** | *"What is NVDA worth? Run a 5-year DCF & Reverse-DCF"* | 5-year DCF using live 10Y U.S. Treasury WACC, SBC-adjusted Owner FCF, Net Debt bridge, Reverse-DCF ("What's priced in"), and a 3×3 sensitivity table |
| **`comps-analysis`** | *"Run trading comps on NVDA vs its semiconductor peers"* | Peer trading multiples table (`EV/Rev`, `EV/EBITDA`, `EV/FCF`, `Forward P/E`, `ROIC`, `FCF Margin`) with 25th/Median/75th percentiles & football-field range |
| **`investment-memo`** | *"Write a buyside Long/Short memo on AAPL"* | Printable 1-page HTML memo (`memos/AAPL_LONG_*.html`) with Variant View vs. consensus, Bear/Base/Bull scenarios, asymmetry check, and falsifiable tripwires |
| **`earnings-playbook`** | *"Pre-earnings setup or Q3 beat/miss update on MSFT"* | 8-quarter surprise streak, consensus Revenue/EPS bar, segment swing drivers, and a Bull/Base/Bear reaction matrix |
| **`forensic-red-flags`** | *"Audit accounting red flags, dilution & insider selling on TSLA"* | 7-point forensic check: cash conversion vs. net income, GAAP vs. non-GAAP EPS spread, SBC dilution, 24-month debt walls, and Form 4 Rule 10b5-1 insider trades |
| **`portfolio-xray`** | *"Check my portfolio for hidden ETF overlap, correlations & drawdowns"* | Unpacks 4,899 ETFs to expose true single-stock concentration across direct shares + funds, USD correlation clusters, max drawdowns, and S&P 500 alpha |

---

## Checked Before It Reaches Your Code

Models break when a feed turns a missing line into a zero, folds year-to-date cash flows into a quarter, or drifts across a stock split. Every QuantSet snapshot clears six quality gates before it is published:

1. **Filings you can cite:** US statements reconcile to SEC XBRL filings and carry `form`, `accession`, `available_at` (public filing date), and a `citation_url` that opens `sec.gov` with the exact sentence highlighted.
2. **Null means null, never zero:** When a company does not report a line, or a figure cannot be verified, you get `null`—never a silent `0` that bends a margin or an average.
3. **Adjustments with evidence:** Adjusted closes pass a three-way check against raw closes, split continuity, and verified cash dividends (`status: "evidence-verified"`).
4. **True quarters and native units:** Quarterly cash flows are separated from fiscal year-to-date figures (`period_basis: "discrete_quarter"`), and every price states its currency, pence (`GBp`) included.
5. **Snapshots that hold still:** Every response is pinned to `X-Warehouse-Snapshot-Id`, returning `409 Conflict` if rotated mid-read so paginated scans never shift underneath you.
6. **One ID per instrument:** Market namespaces (`us:BRK.B`, `global:1301.T`, `crypto:BTCUSDT`, `index:SPX`) keep tickers from colliding across exchanges.

---

## Start Free in Seconds (`mw_demo` + Up to 250 Free Credits)

Run calls right now with `mw_demo` across 9 sample listings (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) with **zero signup**.

When you ask your agent to analyze any other listing across all 67 markets, it can provision a personal `qsk_` key in chat (`POST https://api.quantset.dev/api/v1/agent/signup`) with **30 free credits** right inside the conversation—or you can run `npx quantset init` / sign in at **[quantset.dev/signup](https://quantset.dev/signup)** to get **up to 250 free credits** (~10 full DCF valuations, 16 research context bundles, or 250 stock/price queries) with no credit card required.

## Links

- **Homepage & Pricing:** [https://quantset.dev](https://quantset.dev)
- **Quickstart:** [https://quantset.dev/docs/quickstart](https://quantset.dev/docs/quickstart)
- **All Endpoints (Interactive Reference):** [https://quantset.dev/docs/api](https://quantset.dev/docs/api)
- **How We Verify Data:** [https://quantset.dev/docs/data-quality](https://quantset.dev/docs/data-quality)
- **Global Markets (67 Countries):** [https://quantset.dev/docs/global-markets](https://quantset.dev/docs/global-markets)
- **Google Sheets (`=QUANTSET()`), Excel & Notion Templates:** [`spreadsheets/`](spreadsheets/README.md) · [https://quantset.dev/docs/guides/google-sheets-excel-notion-stock-templates](https://quantset.dev/docs/guides/google-sheets-excel-notion-stock-templates)
- **AI Agents & MCP Guide:** [https://quantset.dev/docs/agents](https://quantset.dev/docs/agents)
- **Autonomous Agent Signup (`skill.md`):** [https://api.quantset.dev/skill.md](https://api.quantset.dev/skill.md)
- **Full LLM Contract (`llms-full.txt`):** [https://api.quantset.dev/llms-full.txt](https://api.quantset.dev/llms-full.txt)
