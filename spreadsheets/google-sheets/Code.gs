/**
 * QuantSet for Google Sheets — =QUANTSET() Custom Function & Scheduled Refresh
 *
 * 90,000+ symbols & 52,000+ stocks across 67 countries, 734 crypto pairs,
 * 42 FX currencies, 36,000+ companies with standardized financial statements,
 * 127M+ SEC EDGAR XBRL facts, 4,899 ETF look-through holdings & 40-factor screens.
 *
 * Works immediately with the free `mw_demo` sandbox key.
 * To unlock all 90,000+ symbols (250 free credits on signup, no credit card):
 *   1. Get your key at https://quantset.dev/signup
 *   2. Put your `qsk_...` key in cell `Config!B1` (or Script Properties `QUANTSET_API_KEY`).
 *
 * Examples in any Google Sheets cell:
 *   =QUANTSET("quotes", "us:NVDA,us:AAPL,global:SHEL.L,global:1301.T,crypto:BTCUSDT")
 *   =QUANTSET("income", "us:NVDA", "period=annual&limit_per_instrument=5")
 *   =QUANTSET("cash-flow", "us:NVDA", "period=quarterly&limit_per_instrument=8")
 *   =QUANTSET("balance-sheet", "us:NVDA", "period=quarterly&limit_per_instrument=4")
 *   =QUANTSET("etf-holdings", "us:IVV", "limit=25")
 *   =QUANTSET("etf-exposures", "us:NVDA", "limit=25")
 *   =QUANTSET("screener", "", "min_roic=20&max_pe_ttm=25&limit=25")
 *   =QUANTSET("treasury-yields", "", "limit=10")
 *
 * @param {string} dataset Dataset slug ("quotes", "prices", "snapshots", "income", "balance-sheet", "cash-flow", "etf-holdings", "etf-exposures", "screener", "dividends", "estimates", "insider-activity", "institutional-ownership", "treasury-yields", "fx-rates").
 * @param {string=} tickers Optional ticker or comma-separated tickers ("NVDA" or "us:NVDA,global:SHEL.L").
 * @param {string=} extraQuery Optional query string ("period=quarterly&limit_per_instrument=4").
 * @return {Array<Array<string>>} 2D table of headers and rows.
 * @customfunction
 */
function QUANTSET(dataset, tickers, extraQuery) {
  var routes = {
    "quotes": "/api/v1/quotes",
    "prices": "/api/v1/prices",
    "snapshots": "/api/v1/snapshots",
    "income": "/api/v1/financial-statements/income",
    "balance-sheet": "/api/v1/financial-statements/balance_sheet",
    "cash-flow": "/api/v1/financial-statements/cash_flow",
    "etf-holdings": "/api/v1/etf-holdings",
    "etf-exposures": "/api/v1/etf-exposures",
    "screener": "/api/v1/screener",
    "dividends": "/api/v1/dividends",
    "estimates": "/api/v1/estimates",
    "insider-activity": "/api/v1/insider-activity",
    "institutional-ownership": "/api/v1/institutional-ownership",
    "treasury-yields": "/api/v1/macro/treasury-yields",
    "fx-rates": "/api/v1/fx/rates"
  };
  var clean = String(dataset || "quotes").trim();
  var path = routes[clean] || ("/api/v1/" + clean.replace(/^\/+/, ""));
  var key = PropertiesService.getScriptProperties().getProperty("QUANTSET_API_KEY") || "mw_demo";
  try {
    var cfg = SpreadsheetApp.getActiveSpreadsheet().getRange("Config!B1").getValue();
    if (cfg && String(cfg).trim()) key = String(cfg).trim();
  } catch (e) {}

  var params = ["format=csv"];
  if (tickers && String(tickers).trim()) {
    var t = String(tickers).trim();
    var paramName = (path.indexOf("/quotes") !== -1 || path.indexOf("/financial-statements/") !== -1 || path.indexOf("/fundamentals") !== -1) ? "tickers" : "ticker";
    params.push(paramName + "=" + encodeURIComponent(t));
  }
  if (extraQuery && String(extraQuery).trim()) {
    params.push(String(extraQuery).trim().replace(/^[?&]+/, ""));
  }

  var url = "https://api.quantset.dev" + path + "?" + params.join("&");
  var res = UrlFetchApp.fetch(url, {
    headers: { "X-API-Key": key },
    muteHttpExceptions: true
  });
  if (res.getResponseCode() !== 200) {
    return [["QuantSet HTTP " + res.getResponseCode(), res.getContentText().slice(0, 240)]];
  }
  return Utilities.parseCsv(res.getContentText());
}
