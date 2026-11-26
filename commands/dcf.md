---
description: Run a 5-year unlevered free-cash-flow DCF valuation and 5x5 WACC vs. terminal growth sensitivity matrix for any US or global stock ticker.
---

Follow the `dcf-valuation` skill to value the requested company (`$ARGUMENTS`):

1. Resolve the ticker and pull its current snapshot (`get_company_snapshot`), 5-year annual and 4-quarter financial statements (`get_financial_statements` with `kind="all"`), consensus forward estimates (`get_estimates_and_earnings`), and the latest U.S. 10-Year Treasury yield (`get_macro_and_fx` with `view="treasury_yields"`).
2. Build the Enterprise Value to Equity Value bridge from the latest balance sheet (`total_debt`, `cash_and_short_term_investments`, `diluted_shares`).
3. Project 5 years of unlevered Free Cash Flow across Bear, Base, and Bull cases, discount at WACC, and render a 5x5 WACC vs. Terminal Growth implied share-price sensitivity table alongside the current market price.
