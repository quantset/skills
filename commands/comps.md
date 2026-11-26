---
description: Build a public comparable companies (trading comps) valuation table with NTM & TTM multiples, peer quartiles, and implied share price range for a stock ticker.
---

Follow the `comps-analysis` skill for the target company (`$ARGUMENTS`):

1. Pull the target's snapshot and sector/industry peers using `get_company_snapshot` and `get_peers` (or `screen_stocks` within the same sector and market-cap band).
2. Fetch batch quotes (`get_quotes`), TTM income/balance/cash-flow statements (`get_financial_statements`), and forward consensus estimates (`get_estimates_and_earnings`) for the target and 5-10 peers.
3. Render the side-by-side peer table (`EV/Sales`, `EV/EBITDA`, `EV/FCF`, `P/E`, revenue growth, EBITDA margin, FCF margin, Rule of 40) with 25th/Median/75th percentile benchmarks and implied share-price football field.
