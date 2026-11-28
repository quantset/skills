---
description: Build a public comparable companies (trading comps) valuation table with NTM & TTM multiples, peer quartiles, and implied share price range for a stock ticker.
argument-hint: "<ticker or company name, e.g. us:NVDA>"
---

Follow the `comps-analysis` skill for the target company (`$ARGUMENTS`). The skill holds the exact calls and rules; this is the order of work:

1. Pull the candidate peers with `get_peers` and keep 5 to 8 by the skill's rules, listing the ones dropped.
2. Pull `get_company_snapshot` for the target and each peer, then one batched `get_financial_statements` call each for fiscal-year income (`kind="income"`), cash flow (`kind="cash_flow"`) and the balance sheet (`kind="balance_sheet"`).
3. Run `scripts/comps_stats.py` on those figures, or apply the same rules by hand: one enterprise value per company, multiples on one fiscal-year basis, forward P/E as price over forward EPS, 25th/median/75th benchmarks and the implied share price range.
4. Render the peer table, the benchmarks, the implied range, what limits the table, and the Sources table.
