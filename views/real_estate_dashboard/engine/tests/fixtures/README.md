# Local test fixtures

`sparse_fund_data.xlsx` is in the superseded workbook format and is no longer
read by the pipeline. The tests now run against the live workbook at
`data/real_estate_fund_data.xlsx` (simplified 9-asset format) and skip when it
is absent, so run them on a machine that has that file.

Excel workbooks are intentionally ignored by Git.
