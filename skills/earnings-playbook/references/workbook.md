# Earnings Workbook Layout

One workbook per company: `earnings/[SYMBOL]_earnings.xlsx`. It is the checkable record behind the note, and it grows by one quarter each time the skill runs. If the file exists, open it, add the new rows and keep every earlier row. Never rewrite history: a restated figure goes in as a new row with its own `available_at`.

Build it with whatever spreadsheet library the environment already has (for example `openpyxl` in Python); do not install one. If there is none, write one CSV per sheet into `earnings/[SYMBOL]_earnings/`, named after the sheet, with each formula written out as text in its cell.

## Rules

- Row 1 of every sheet is the header exactly as listed below.
- Raw values come straight from QuantSet responses, unrounded, in the company's reporting currency. The `Sources` sheet names that currency on the statement rows.
- Every derived column is a spreadsheet formula over the same row (or the row it names), never a pasted number, so the reader can trace it.
- An unknown value stays an empty cell. Never write `0` for `null`.
- Every sheet carries a `source_call` column (the call that returned the row) and a `pulled_on` column (the date of this run).

## Sheets

### `Bar`
One row per run, per metric, per estimate row. Source: `estimates` view.

| pulled_on | metric | period | period_end | consensus | low | high | analyst_count | year_ago | implied_growth | estimates_as_of | source_call |
|---|---|---|---|---|---|---|---|---|---|---|---|

`implied_growth` is the formula `consensus / year_ago - 1`.

### `History`
One row per reported quarter. Source: `earnings` view. Add only quarters not already present; keep rows sorted by `period_end`.

| period_end | estimated_eps | actual_eps | surprise_pct | beat | source_call | pulled_on |
|---|---|---|---|---|---|---|

`beat` is the formula `actual_eps > estimated_eps`. The beat rate and the median surprise go in the note, not in this sheet.

### `Quarterly`
One row per fiscal quarter, sorted by `period_end`. Source: quarterly `income` and `cash_flow` statements, one row per quarter after removing duplicates.

| period_end | revenue | cost_of_revenue | gross_profit | operating_income | net_income | reported_diluted_eps | gross_margin | operating_margin | revenue_yoy | operating_cash_flow | free_cash_flow | cash_flow_basis | available_at | accession | source_call | pulled_on |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- When the response has no `gross_profit`, the cell is the formula `revenue - cost_of_revenue`. `gross_margin` and `operating_margin` are formulas over the same row; `revenue_yoy` is a formula against the row four quarters earlier, empty when that row is absent.
- Income figures are single quarters. `cash_flow_basis` holds the cash-flow row's `period_basis`: a value other than `discrete_quarter` means the two cash-flow cells are year-to-date. Do not compute a margin from year-to-date cash flow.
- `period_end` is as the statement row gives it. The `Bar` and `History` sheets use month-end labels for the same quarters, so match the sheets by year and month.

### `Segments`
One row per segment per period. Source: `segments` view.

| period | flow | segment | revenue | share_of_total | derived | source_call | pulled_on |
|---|---|---|---|---|---|---|---|

`share_of_total` is a formula over the rows of the same `period` and `flow`. Mark `derived` as `yes` on a fourth-quarter row computed as the fiscal year minus the three quarters before it.

### `Reaction`
The matrix from the note, one row per case, kept across quarters so a later run can be scored against what was expected.

| pulled_on | period_end | case | what_prints | why_it_matters | outcome | source_call |
|---|---|---|---|---|---|---|

Leave `outcome` empty in a preview. The post-earnings update fills it for the matching `period_end`. `source_call` names the calls the thresholds came from.

### `Sources`
The same rows as the note's Sources table, closing with a row that reads `Data: QuantSet (https://quantset.dev)`.

| pulled_on | supplied | source_call | describes_date | filed_or_published | accession | currency |
|---|---|---|---|---|---|---|
