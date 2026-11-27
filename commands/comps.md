---
description: Build a public comparable companies (trading comps) valuation table with NTM & TTM multiples, peer quartiles, and implied share price range for a stock ticker.
argument-hint: "<ticker or company name, e.g. us:NVDA>"
---

Follow the `comps-analysis` skill for the target company (`$ARGUMENTS`). The skill holds the exact calls; this is the order of work:

1. Pull the target's sector/industry peers using `get_peers` (or `screen_stocks` within the same sector and market-cap band) and keep 5-8 true economic peers.
2. Pull `get_company_snapshot` for the target and each peer (enterprise value, TTM revenue, EBITDA and FCF, trailing and forward multiples), plus the target's latest quarterly income statement (`get_financial_statements` with `kind="income"`) for diluted shares.
3. Render the side-by-side peer table (`EV/Sales`, `EV/EBITDA`, `EV/FCF`, `P/E`, revenue growth, EBITDA margin, FCF margin, Rule of 40) with 25th/Median/75th percentile benchmarks, the implied share-price football field and the Sources table. EBITDA margin is `ebitda_ttm / revenue_ttm`; Rule of 40 is `rev_growth_yoy_pct + fcf_margin_pct`.
