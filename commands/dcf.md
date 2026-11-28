---
description: Run a 5-year unlevered free-cash-flow DCF valuation and 3x3 WACC vs. terminal growth sensitivity matrix for any US or global stock ticker.
argument-hint: "<ticker or company name, e.g. us:NVDA>"
---

Follow the `dcf-valuation` skill to value the requested company (`$ARGUMENTS`). The skill holds the exact calls and rules; this is the order of work:

1. Resolve the instrument with `list_instruments` if a name was given, then pull the inputs in Step 1 of the skill: the snapshot (`get_company_snapshot`), fiscal-year cash flows and income, the latest balance sheet and diluted shares (`get_financial_statements`, one `kind` per call), stock-based compensation (`get_sec_filings` with `view="company_facts"`), consensus revenue (`get_estimates_and_earnings` with `view="estimates"`), the U.S. 10-Year Treasury yield (`get_macro_and_fx` with `view="treasury_yields"`) and peers (`get_peers`).
2. Check that a cash-flow DCF fits the company (Step 2). If it does not, say why and stop without a value.
3. Run `scripts/dcf_math.py` on the inputs, or do Steps 3 to 5 by hand: base cash flow and its normal-year check, growth path, discount rate, bridge to a share price, sanity checks, the 3x3 WACC vs. Terminal Growth table (centre cell = base case) and the reverse DCF.
4. Report as the skill's Output Structure describes, ending with the Sources table.
