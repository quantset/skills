---
description: Build a public comparable companies (trading comps) table leading with peer-quartile positioning, NTM & TTM multiples, and relative growth/return drivers.
argument-hint: "<ticker or company name, e.g. us:NVDA>"
---

Follow the `comps-analysis` skill for the target company (`$ARGUMENTS`). The skill holds the exact calls and rules; this is the order of work:

1. Pull the candidate peers with `get_peers` and keep 5 to 8 by the skill's rules, listing the ones dropped.
2. Pull `get_company_snapshot` for the target and each peer, then one batched `get_financial_statements` call each for fiscal-year income (`kind="income"`), cash flow (`kind="cash_flow"`) and the balance sheet (`kind="balance_sheet"`).
3. Run `scripts/comps_stats.py` on those figures, or apply the same rules by hand: one enterprise value per company, multiples on one fiscal-year basis, forward P/E as price over forward EPS, 25th/median/75th benchmarks and the implied share price range.
4. Lead with the Top 3 peer-positioning takeaways, then render the peer table + quartile benchmarks, the illustrative multiple translation, and a compact Sources footer.
