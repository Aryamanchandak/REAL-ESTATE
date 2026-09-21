# Real Estate Dashboard

This repository contains two dashboard implementations:

- `src/build_dashboard.py` builds the production, self-contained HTML dashboard from an Excel workbook.
- `src/app.py` runs the Streamlit prototype with the sample data in `src/sample_data.py`.

## Project layout

```text
src/                 Python application and build pipeline
templates/           HTML source template and pinned browser libraries
data/                Local input workbook (ignored by Git)
output/              Generated dashboard HTML (ignored by Git)
tests/fixtures/       Local test workbooks (ignored by Git)
tests/                Pipeline regression tests
docs/                 Implementation notes
archive/              Superseded workbooks and exports (ignored by Git)
```

## Setup

Use Python 3.9 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r views/real_estate_dashboard/engine/requirements.txt
```

Place the current workbook at `views/real_estate_dashboard/engine/data/real_estate_fund_data.xlsx`. Workbooks are
ignored because they may contain confidential data.

The reader (`src/ingest.py`) expects the simplified 9-asset workbook: it reads
`1_ASSET_MASTER`, `2_MONTHLY_INPUT`, `3_REVENUE_RENT`, `3A_REVENUE_MIX`,
`4_TENANT_STACK_LEASE`, `6_APPROVALS_COMPLIANCE` and `DATA_QUALITY_CHECKS`.
Fund totals, annual (June–May) roll-ups, WALE and lease expiry are calculated
from those input rows. The latest month with entered figures becomes the report
month. Anything in the workbook that does not reconcile is printed during the
build and listed on the dashboard's Data Quality tab.

## Build the static dashboard

```bash
python3 views/real_estate_dashboard/engine/src/build_dashboard.py
```

The generated file is written to `engine/output/dashboard.html`. Custom paths may be
supplied as positional arguments:

```bash
python3 views/real_estate_dashboard/engine/src/build_dashboard.py INPUT.xlsx TEMPLATE.html OUTPUT.html
```

## Run the Streamlit prototype

```bash
streamlit run views/real_estate_dashboard/engine/src/app.py
```

## Run the dashboard builder app

```bash
streamlit run views/real_estate_dashboard/app.py
```

## Test

The regression suite requires the local workbooks under `data/` and
`tests/fixtures/`, plus Node.js for the embedded JSX compilation check.

```bash
python3 -m unittest discover -s views/real_estate_dashboard/engine/tests
```
