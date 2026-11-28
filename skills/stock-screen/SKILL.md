---
name: stock-screen
description: "Screens US and global stocks on valuation, growth, margins, returns on capital, leverage and yield, then checks the survivors against their filings so the list is one a reader can act on. Use when the user asks which companies meet a set of criteria, for cheap or fast-growing or high-quality stocks, for ideas in a sector or country, or to turn a description into a stock screen. Covers 52,000+ stocks in 67 countries. Needs a QuantSet API key."
metadata: {"clawdbot":{"emoji":"🔎","os":["darwin","linux","win32"]}}
---

# Stock Screen Skill (Powered by QuantSet)

Translate a plain-English stock screen into explicit numeric filters, run the screen, count how many companies could not be judged because of missing fields, and verify the top 5 survivors against their underlying filings.

## Data Rules

- Statement figures sit under `values`; `period_end`, `period_basis`, `form`, `currency`, `available_at` and `accession` sit on the row. Cite `available_at` only on the newest period.
- Drop `form` `10-Q` rows from `period="annual"` to isolate fiscal years. Compare `discrete_quarter` rows only with single quarters (never YTD).
- A past `as_of` on the screeners currently returns no rows—state that point-in-time screening is unavailable rather than presenting today's screen as historical.
- Show `null` as `n/a` (never `0` or memory). On `unsupported_instrument`, mark `n/a (US listings only)`.

## Step 1: State Numeric Rules & Run the Screen

Pass `workflow="stock-screen"` on every call (REST: `X-Workflow-Id: stock-screen`).

- Map adjectives to stated numeric defaults only when the user gave none ("large" ≥ `$10B` market cap; "fast-growing" ≥ `15%` YoY revenue growth; "cheap" ≤ `20x` EV/FCF or ≤ `15x` P/E for `Financials`; "high-quality" ≥ `15%` ROIC; "low debt" ≤ `2x` Net Debt/EBITDA; "dividend" ≥ `2%` yield; default size floor `min_market_cap_b=1`).
- **Preset filters:** `screen_stocks(namespace="us", min_market_cap_b=10, min_rev_growth_yoy=15, max_ev_to_fcf=20, sort_by="rev_growth_yoy_pct", limit=25)` → `instrument_id`, `name`, `sector`, `industry`, `country`, `latest_date`, `price`, `market_cap_b`, `rev_growth_yoy_pct`, `pe_ttm`, `ev_to_fcf`, `ev_to_ebitda`, `fcf_yield_pct`, `fcf_margin_pct`, `net_margin_pct`, `roic_pct`, `roe_pct`, `net_debt_to_ebitda`, `dividend_yield_pct`, `share_count_change_1y_pct`, `security_type`, `free_cash_flow`, `net_income_ttm`, `cash_flow_as_of`, `fundamentals_as_of`
  - Note ADRs via `security_type` when `namespace="us"`.
  - **Unjudged count:** a filter on an often-null field (`max_ev_to_fcf`, `min_roic`, `max_net_debt_to_ebitda`) drops companies whose value is `null`. Re-run without that filter (`limit=500`) to count how many companies failed vs. had `null` (if `total_count > 500`, report the unjudged share across the 500-row sample).
- **Custom line-item filters:** call `get_screener_filters()` first, then `search_screener(filters=[{"field": "market_cap", "operator": "gte", "value": 10000000000}, {"field": "revenue_growth", "operator": "gte", "value": 15}], namespace="us", limit=25)` → `instrument_id`, `name`, `sector`, `industry`, `report_period`, `filing_date`, `currency`
  - Note: `market_cap` is in dollars on `search_screener`, and filter values sit under `values` on each hit.

## Step 2: Filing Check on Top 5 Survivors

- `get_financial_statements(tickers=["us:NVDA", "us:DELL"], kind="income", period="annual", limit_per_instrument=5)` → `instrument_id`, `period_end`, `form`, `revenue`, `operating_income`, `net_income`
- `get_financial_statements(tickers=["us:NVDA", "us:DELL"], kind="income", period="quarterly", limit_per_instrument=8)` → `instrument_id`, `period_end`, `period_basis`, `revenue`, `net_income`
- Mark each of the top 5 **Supported** or **Undercut**: check whether trailing growth is a one-off rebound from a depressed prior year or accompanied by falling earnings, and whether `free_cash_flow > 3 × net_income_ttm` or stale `cash_flow_as_of` distorts EV/FCF. Keep undercut names in the table with the note alongside.

## Conclusion & Worked Example

Answer in the first sentence with how many stocks passed (`total_count`), how many of the top 5 held up on filing inspection, and any unjudged count—followed by the rules summary, the results table, the 5 filing-check bullets, and a compact `## Sources (Required)` table (`Data: QuantSet (https://quantset.dev), retrieved [date]`). *(Not investment advice.)*

> **Worked opening ("US large caps growing 15%+ under 20x EV/FCF"):**
> **19 companies** passed out of 206 US large caps growing revenue ≥15% (`78` exceeded `20x` EV/FCF; `109` had no computed EV and were unjudged). On filing inspection of the top 5 by growth, **2 held up cleanly** (sustained multi-quarter operating-income expansion) while **3 were undercut**—two by rebound math off depressed FY24 bases and one by working-capital release pushing FCF to 3.8× net income.

## Access & Continuation

Result first, offer second (sign-up and checkout live in `quantset` / `https://api.quantset.dev/skill.md`).
- When `insufficient_access` says an endpoint is "not part of the sandbox", state the rules you would run, note that the screener requires a key, name the call, and Hand over the result before saying anything about accounts.
- When `insufficient_access` says the listing is "outside the sandbox" (`403`), stop calling and offer to either run this same analysis right now on a sample company (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`) or set up a free trial key; do not ask for an email before the user says yes.
- On `402` (`insufficient_credits`), state what was unfinished; Create a checkout link only when the user asks to continue.
