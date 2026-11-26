# QuantSet for Google Sheets, Excel & Notion (`=QUANTSET()`)

Put **`90,000+` symbols** and **`52,000+` stocks across `67` countries**, **`734` crypto pairs**, **`42` FX currencies**, **`36,000+` companies with standardized financial statements**, **`127M+` SEC EDGAR XBRL facts**, and **`4,899` ETF look-through holdings** directly inside Google Sheets, Excel, and Notion—without `=GOOGLEFINANCE()` `#N/A` timeouts.

> **Full Guide & Copyable Templates:** **[quantset.dev/docs/guides/google-sheets-excel-notion-stock-templates](https://quantset.dev/docs/guides/google-sheets-excel-notion-stock-templates)**

---

## 1. Custom `=QUANTSET()` Function for Google Sheets (`google-sheets/Code.gs`)

1. In Google Sheets, open **Extensions → Apps Script** and paste [`google-sheets/Code.gs`](google-sheets/Code.gs).
2. Use `=QUANTSET()` in any cell (works immediately with zero signup via `mw_demo`, or reads your personal `qsk_...` key from `Config!B1` for all `90,000+` symbols):

```excel
=QUANTSET("quotes", "us:NVDA,us:AAPL,global:SHEL.L,global:1301.T,crypto:BTCUSDT")
=QUANTSET("income", "us:NVDA", "period=annual&limit_per_instrument=5")
=QUANTSET("cash-flow", "us:NVDA", "period=quarterly&limit_per_instrument=8")
=QUANTSET("balance-sheet", "us:NVDA", "period=quarterly&limit_per_instrument=4")
=QUANTSET("etf-holdings", "us:IVV", "limit=25")
=QUANTSET("etf-exposures", "us:NVDA", "limit=25")
=QUANTSET("screener", "", "min_roic=20&max_pe_ttm=25&limit=25")
```

## 2. Zero-Script `=IMPORTDATA()` Formulas for Google Sheets

```excel
=IMPORTDATA("https://api.quantset.dev/api/v1/quotes?tickers=us:NVDA,us:AAPL,us:MSFT,global:SHEL.L,crypto:BTCUSDT&format=csv&apikey=mw_demo")
=IMPORTDATA("https://api.quantset.dev/api/v1/financial-statements/income?tickers=us:NVDA&period=annual&limit_per_instrument=5&format=csv&apikey=mw_demo")
=IMPORTDATA("https://api.quantset.dev/api/v1/etf-holdings?ticker=us:IVV&limit=50&format=csv&apikey=mw_demo")
```

## 3. Excel Power Query (`excel/QuantSet.pq`)

In Excel (Windows or Mac), open **Data → Get Data → From Other Sources → Blank Query → Advanced Editor** and paste [`excel/QuantSet.pq`](excel/QuantSet.pq). Keeps your `X-API-Key` in the HTTP header and refreshes with `Ctrl+Alt+F5`.

## 4. Notion Investment Memos & Portfolio Databases

- **Claude / Cursor + Notion MCP:** Pair QuantSet MCP (`https://api.quantset.dev/mcp`) with the Notion MCP server to write DCF models, peer comps tables, and 7-point forensic audits straight into Notion databases.
- **Live Sheet Embeds in Notion:** Publish any Google Sheet using `=QUANTSET()` or `=IMPORTDATA()` and paste the URL into a Notion `/embed` block.
