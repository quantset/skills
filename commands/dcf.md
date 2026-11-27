---
description: Run a 5-year unlevered free-cash-flow DCF valuation and 3x3 WACC vs. terminal growth sensitivity matrix for any US or global stock ticker.
argument-hint: "<ticker or company name, e.g. us:NVDA>"
---

Follow the `dcf-valuation` skill to value the requested company (`$ARGUMENTS`). The skill holds the exact calls; this is the order of work:

1. Resolve the listing with `list_instruments` if a name was given, then pull the inputs in Step 1 of the skill: the snapshot (`get_company_snapshot`), annual and quarterly cash flows and the latest quarterly income statement (`get_financial_statements`, one `kind` per call), stock-based compensation (`get_sec_filings` with `view="company_facts"`), consensus revenue (`get_estimates_and_earnings` with `view="estimates"`), the latest U.S. 10-Year Treasury yield (`get_macro_and_fx` with `view="treasury_yields"`) and peers (`get_peers`).
2. Build the Enterprise Value to Equity Value bridge from the snapshot (`total_debt`, `cash`) and the latest `weighted_average_diluted_shares`.
3. Project 5 years of unlevered Free Cash Flow, discount at WACC, run the skill's four sanity checks, and render the 3x3 WACC vs. Terminal Growth implied share-price table (centre cell = base case) alongside the current market price and the Sources table.
