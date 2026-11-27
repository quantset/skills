# Earnings Workbook Layout

One workbook per company: `earnings/[TICKER]_earnings.xlsx`. It is the checkable record behind the note, and it grows by one quarter each time the skill runs. If the file exists, open it, add the new rows and keep every earlier row. Never rewrite history: a restated figure goes in as a new row with its own `available_at`.

Build it with whatever spreadsheet library the environment has (for example `openpyxl` in Python). If none is available, write one CSV per sheet into `earnings/[TICKER]_earnings/` using the sheet names below as file names.

## Rules

- Row 1 of every sheet is the header exactly as listed. Freeze it.
- Raw values come straight from QuantSet responses, unrounded. Put units in the header, not in the cells.
- Every derived cell is a spreadsheet formula, never a pasted number, so the reader can trace it.
- An unknown value stays an empty cell. Never write `0` for `null`.
- Every data row ends with `source_call` (the call that returned it) and the date it was pulled.

## Sheets

### `Bar`
One row per run, per metric, per estimate period. Source: `estimates` view.

| run_date | fiscal_period | metric | period | period_end | consensus | low | high | analyst_count | year_ago | implied_growth | estimates_as_of | source_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

`implied_growth` is the formula `consensus / year_ago - 1`.

### `History`
One row per reported quarter. Source: `earnings` view. Add only quarters not already present.

| period_end | estimated_eps | actual_eps | surprise_pct | beat | source_call | pulled_on |
|---|---|---|---|---|---|---|

`beat` is the formula `actual_eps > estimated_eps`. Under the table: beat rate over the last 8 rows and the average `surprise_pct`, both as formulas.

### `Quarterly`
One row per fiscal quarter. Source: quarterly `income` and `cash_flow` statements. Keep `period_basis`, and compare only rows that share it.

| period_end | period_basis | revenue | gross_profit | operating_income | net_income | reported_diluted_eps | operating_cash_flow | free_cash_flow | gross_margin | operating_margin | fcf_margin | revenue_yoy | available_at | accession | source_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

The three margins and `revenue_yoy` are formulas over the same row and the row four quarters earlier.

### `Segments`
One row per segment per period. Source: `segments` view.

| period | flow | segment | revenue | share_of_total | yoy | source_call | pulled_on |
|---|---|---|---|---|---|---|---|

`share_of_total` and `yoy` are formulas.

### `Reaction`
The matrix from the note, one row per case, kept across quarters so a later run can be scored against what was expected.

| run_date | fiscal_period | case | what_prints | why_it_matters | outcome |
|---|---|---|---|---|---|

Leave `outcome` empty in a preview. The post-earnings update fills it for the matching `fiscal_period`.

### `Sources`
The same rows as the note's Sources table, closing with a row that reads `Data: QuantSet (https://quantset.dev)`.

| run_date | supplied | source_call | describes_date | filed_or_published | accession |
|---|---|---|---|---|---|
