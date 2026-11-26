---
description: Screen US or global equities across 67 countries by valuation multiples, revenue growth, margins, ROIC, buyback yield, and leverage.
---

Translate the user's screening criteria (`$ARGUMENTS`) into a structured QuantSet stock screen:

1. Call `screen_stocks` (or `get_screener_filters` + `search_screener` for custom multi-condition filters) with the requested `namespace` (`us` or `global`), `country`, `sector`, valuation caps (`max_pe_ttm`, `max_ev_to_ebitda`, `max_ev_to_fcf`), growth floors (`min_rev_growth_yoy`), quality floors (`min_roic`, `min_fcf_margin`), or net share-cannibal filters (`max_share_count_change_1y`).
2. Present the matching companies in a ranked Markdown table with ticker, name, country/exchange, market cap, valuation multiples, growth, margins, and capital return metrics.
