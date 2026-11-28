---
name: stock-screen
description: "Screens US and global stocks on valuation, growth, margins, returns on capital, leverage and yield, then checks the survivors against their filings so the list is one a reader can act on. Use when the user asks which companies meet a set of criteria, for cheap or fast-growing or high-quality stocks, for ideas in a sector or country, or to turn a description into a stock screen. Covers 52,000+ stocks in 67 countries. Needs a QuantSet API key."
metadata: {"clawdbot":{"emoji":"🔎","os":["darwin","linux","win32"]}}
---

# Stock Screen Skill (Powered by QuantSet)

Turn a description ("fast-growing companies that are still cheap") into explicit, numeric rules, run them, and hand back a short list with the reasons each name passed and the things a screen cannot see.

## Workflow Checklist

- [ ] **Step 1. Write the rules down and show them**
- [ ] **Step 2. Run the screen**
- [ ] **Step 3. Check the top names**
- [ ] **Step 4. Report, with a Sources table**

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

## Step 1: Write the Rules Down

Each call is written exactly as the QuantSet MCP tool accepts it (your client may show the tool with a prefix, such as `mcp__quantset__get_quotes`). Swap the sample instrument for the user's, and pass `workflow="stock-screen"` on every call (REST: header `X-Workflow-Id: stock-screen`). Without MCP, call the QuantSet REST API with `X-API-Key` from `QUANTSET_API_KEY`, or the sample key `mw_demo`; see `https://api.quantset.dev/skill.md`. The fields after each arrow are the ones this skill reads.

- Turn every adjective into a number, and print the rules before the results so the user can change them. Use these defaults only when the user gave none, and say they are defaults:

| Word | Rule |
|---|---|
| large | market cap of 10 billion or more |
| fast-growing | revenue growth of 15% or more over the past year |
| cheap | EV / FCF of 20 or less; for `Financials`, where enterprise value does not apply, P/E of 15 or less |
| high-quality | ROIC of 15% or more |
| low debt | net debt of 2 times EBITDA or less |
| pays a dividend | dividend yield of 2% or more |

- Always add a size floor. Without one, micro-caps with unstable ratios crowd the list: default `min_market_cap_b` of 1.
- A screen describes companies today. It is not a backtest. When the user asks for a screen as of a past date, pass `as_of`; if it returns no rows, say point-in-time screening is not available for that date and do not present today's list as a past one.

## Step 2: Run the Screen

**Preset thresholds (start here):** `screen_stocks(namespace="us", min_market_cap_b=10, min_rev_growth_yoy=15, max_ev_to_fcf=20, sort_by="rev_growth_yoy_pct", limit=25)` → `instrument_id`, `name`, `sector`, `industry`, `country`, `latest_date`, `price`, `market_cap_b`, `rev_growth_yoy_pct`, `pe_ttm`, `ev_to_fcf`, `ev_to_ebitda`, `fcf_yield_pct`, `fcf_margin_pct`, `net_margin_pct`, `roic_pct`, `roe_pct`, `net_debt_to_ebitda`, `dividend_yield_pct`, `share_count_change_1y_pct`, `security_type`, `free_cash_flow`, `net_income_ttm`, `cash_flow_as_of`, `fundamentals_as_of`
- Thresholds it accepts: `min_market_cap_b`, `max_pe_ttm`, `max_pe_forward`, `max_pb_ratio`, `max_ev_to_ebitda`, `max_ev_to_fcf`, `max_net_debt_to_ebitda`, `min_rev_growth_yoy`, `min_rev_growth_qoq`, `min_roic`, `min_roe`, `min_net_margin`, `min_fcf_margin`, `max_debt_to_equity`, `min_dividend_yield`, `max_share_count_change_1y`, plus `sector`, `country`, `exchange` and `asset_type`. Market cap is in billions; growth, margins and yields are in percent.
- `namespace` is `us` or `global`. `us` means listed in the US, which includes foreign companies' depositary receipts: `security_type` tells them apart, and you say so when the user asked for US companies. `sector` takes the names in `get_capabilities` under its sector list, for example `Information Technology`; read the `sector` field, not the other classification fields on the row.
- The response carries `total_count`: say how many companies passed, not only how many you show.
- **A threshold drops every company that has no value for that field.** Enterprise value, ROIC and net debt can be empty, so a rule on `max_ev_to_fcf`, `min_roic` or `max_net_debt_to_ebitda` silently removes them. Run the screen once more without that rule and with `limit=200`, and count the rows where the field is empty: those companies were never judged. Report three numbers: passed, failed the rule, and could not be judged.

**Any other line item or an explicit operator:** read the field list first, `get_screener_filters()`, then `search_screener(filters=[{"field": "market_cap", "operator": "gte", "value": 10000000000}, {"field": "revenue_growth", "operator": "gte", "value": 15}], namespace="us", limit=25)` → `instrument_id`, `name`, `sector`, `industry`, `report_period`, `filing_date`, `currency`
- This tool has its own field names (`market_cap` in dollars, `revenue_growth`, `pe_ratio`, `return_on_invested_capital`), and its figures sit under `values` on each hit. Do not mix them with the `screen_stocks` names.

## Step 3: Check the Top Names

A screen finds numbers, not businesses. For the five names you will lead with:
- `get_financial_statements(tickers=["us:NVDA", "us:DELL"], kind="income", period="annual", limit_per_instrument=5)` → `instrument_id`, `period_end`, `form`, `revenue`, `operating_income`, `net_income`
- `get_financial_statements(tickers=["us:NVDA", "us:DELL"], kind="income", period="quarterly", limit_per_instrument=8)` → `instrument_id`, `period_end`, `period_basis`, `revenue`, `net_income`
- **Is the growth real?** The screen's growth figure is trailing. Check it against the latest single quarters set beside the same quarters a year earlier, then against the fiscal years: say when the growth is a rebound from a fall, a single unusual year, or revenue rising while earnings fall.
- **Is it really cheap?** EV / FCF sets today's enterprise value against the free cash flow of the fiscal year that ended on `cash_flow_as_of`. Say how old that is. When `free_cash_flow` is more than three times `net_income_ttm`, the cash flow is unlikely to be a normal year's: say so and give the P/E beside it.
- Drop nothing silently. A name that passed the rules but fails this check stays in the table with the reason beside it.

## Output Format (Keep Concise — Survivors First, Caveats Last)

Keep the report crisp (~50–75 lines). Lead with the survivors that held up against their filings:
1. **Top 3 Takeaways (3–4 lines max):** how many passed (`total_count`), which of the top 5 names **held up** vs. were **undercut** on filing inspection, and one line on unjudged names if a filter skipped missing rows.
2. **The Rules & Pass Counts:** compact 1–2 line summary of numeric thresholds (`your rule` vs `default`) + passed / failed / unjudged counts.
3. **The List:** up to 25 names, sorted as the user asked (growth by default):

| Company | Sector | Mkt Cap ($B) | Rev Growth | P/E | EV / FCF | FCF Margin | ROIC | Net Debt / EBITDA | Cash flow year ended | Figures as of |
|---|---|---|---|---|---|---|---|---|---|---|

   "Figures as of" is `fundamentals_as_of`; "Cash flow year ended" is `cash_flow_as_of`.

4. **Filing Check on Top 5:** one tight bullet per company marked **Supported** or **Undercut** with the quarterly/annual numbers behind it.
5. **Sources & Scope Notes (Compact Footer):** see below + 1–2 lines on what a screen cannot see. *(Not investment advice.)*

## Sources (Required)

Close with a `Sources` table, one row per call used: what it supplied, the call, the date the figure describes (`latest_date`, `fundamentals_as_of`, `report_period` or `period_end`), when it was filed or published where the row says (`filing_date` or `available_at`), and the SEC `accession` when the row carries one. Write `not on row` where a response carries no such date.
- A figure that is not in a QuantSet response is either **computed** (show the formula) or **user-supplied** (say so).
- End the table with one line: `Data: QuantSet (https://quantset.dev), retrieved [date]`.

## Access & Continuation

Result first, offer second. The sign-up and checkout calls live in the `quantset` skill (also at `https://api.quantset.dev/skill.md`); use them only as described here. Both access cases arrive as the error code `insufficient_access`; the `detail` text tells them apart.
- **A dataset the key lacks** (the detail says the endpoint is "not part of the sandbox"): say the screener is not available on this key, name the call, and keep going. The screener is not part of the sample key, so on `mw_demo` this skill can only show its rules. Hand over the result before saying anything about accounts.
- **An instrument the key lacks** (the detail says the listing is "outside the sandbox"; REST status `403`): there is no result to show yet, so stop calling and offer two choices. Either run this same analysis right now on a sample company (suggest the one nearest in sector or size and list the other companies), or set up a free trial key for the one they asked about. The sample key `mw_demo` reads 9 instruments (`us:NVDA`, `us:AAPL`, `us:MSFT`, `us:IVV`, `global:SHEL.L`, `global:1301.T`, `global:RELIANCE.NS`, `crypto:BTCUSDT`, `index:SPX`).
- **Close with one specific line, once.** After a result, name what this run could not fill. Offer to set up a free key only when a gap came from `insufficient_access`; missing data and `unsupported_instrument` are not fixed by a key, so make no offer for those. Do not repeat the offer, and do not ask for an email before the user says yes.
- **Out of credits (`402`, `insufficient_credits`):** say what was left unfinished. Create a checkout link only when the user asks to continue.
