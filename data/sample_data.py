"""
sample_data.py
==============
All dashboard data lives here as pandas DataFrames.
Replace the hardcoded values with real data sources (CSV, DB, API)
while keeping the exact column names — the charts will work without
any other changes.

Naming convention:
  df_<tab>_<dataset>   e.g.  df_investment_summary, df_exec_rent_billed
"""

import pandas as pd

# ─────────────────────────────────────────────
# SHARED LOOKUP DATA
# ─────────────────────────────────────────────

ASSETS = ["All", "Blue", "Green", "White", "Yellow"]
MONTHS = ["Aug-23", "Sep-23", "Oct-23", "Nov-23", "Dec-23", "Jan-24"]

# ─────────────────────────────────────────────
# TAB 1 — INVESTMENT SUMMARY
# ─────────────────────────────────────────────

# Top-level KPI cards
df_investment_kpis = pd.DataFrame([{
    "monthly_rental_amount_cr": 83.5,
    "cam_charges_psf":          12.6,
    "occupied_pct":             90.2,
    "gross_billing_cr":         75.0,
    "collections_cr":           75.0,
}])

# Per-asset summary table
df_investment_summary = pd.DataFrame([
    {"asset": "Blue",   "leasable_area_msft": 0.46, "leased_area_msft": 0.43,
     "vacant_area_msft": 0.02, "occupancy_pct": 95.1, "monthly_rent_cr": 4.3},
    {"asset": "Green",  "leasable_area_msft": 0.52, "leased_area_msft": 0.39,
     "vacant_area_msft": 0.13, "occupancy_pct": 74.8, "monthly_rent_cr": 3.1},
    {"asset": "White",  "leasable_area_msft": 6.78, "leased_area_msft": 6.14,
     "vacant_area_msft": 0.64, "occupancy_pct": 90.6, "monthly_rent_cr": 60.9},
    {"asset": "Yellow", "leasable_area_msft": 1.57, "leased_area_msft": 1.45,
     "vacant_area_msft": 0.12, "occupancy_pct": 92.2, "monthly_rent_cr": 15.3},
    {"asset": "Total",  "leasable_area_msft": 9.34, "leased_area_msft": 8.42,
     "vacant_area_msft": 0.92, "occupancy_pct": 90.2, "monthly_rent_cr": 83.5},
])

# Rent spread by PSF band
df_rent_spread = pd.DataFrame([
    {"band": "0–60 INR/sft",   "area_msft": 1.1},
    {"band": "60–90 INR/sft",  "area_msft": 4.2},
    {"band": "90–120 INR/sft", "area_msft": 2.9},
    {"band": ">120 INR/sft",   "area_msft": 0.3},
])

# Area summary (leasable / leased / vacant)
df_area_summary = pd.DataFrame([
    {"category": "Leasable Area", "area_msft": 9.3},
    {"category": "Leased Area",   "area_msft": 8.4},
    {"category": "Vacant Area",   "area_msft": 0.9},
])

# Revenue composition (excl. taxes)
df_revenue_composition = pd.DataFrame([
    {"component": "Base Rental",  "amount_cr": 67},
    {"component": "CAM Rent",     "amount_cr": 13},
    {"component": "Parking Rent", "amount_cr":  3},
    {"component": "Other Rent",   "amount_cr":  1},
])

# ─────────────────────────────────────────────
# TAB 2 — EXECUTIVE SUMMARY
# ─────────────────────────────────────────────

df_exec_kpis = pd.DataFrame([{
    "asset":              "Green",
    "month":              "Jan-24",
    "leasable_area_sft":  523532,
    "wale_yrs":           2.9,
    "total_area_msft":    0.52,
    "leased_area_msft":   0.39,
    "vacant_area_msft":   0.13,
    "rent_to_be_billed_cr": 2.5,
    "actual_billed_cr":   2.9,
    "gross_billing_cr":   3.4,
    "collections_cr":     3.4,
}])

# Top-5 tenants bar
df_exec_top5_tenants = pd.DataFrame([
    {"tenant": "Nagravision", "monthly_rent_cr": 0.5},
    {"tenant": "Tyco",        "monthly_rent_cr": 0.4},
    {"tenant": "Ekaterra",    "monthly_rent_cr": 0.4},
    {"tenant": "Agilent",     "monthly_rent_cr": 0.3},
    {"tenant": "Atos",        "monthly_rent_cr": 0.3},
])

# Current & future average rental PSF
df_exec_rental_psf = pd.DataFrame([
    {"period": "2023 Q2", "rent_to_be_billed_psf": 52, "actual_billed_psf": 52},
    {"period": "2023 Q4", "rent_to_be_billed_psf": 55, "actual_billed_psf": 54},
    {"period": "2024 Q2", "rent_to_be_billed_psf": 65, "actual_billed_psf": 65},
    {"period": "2024 Q4", "rent_to_be_billed_psf": 66, "actual_billed_psf": 65},
    {"period": "2025 Q2", "rent_to_be_billed_psf": 72, "actual_billed_psf": 70},
    {"period": "2025 Q4", "rent_to_be_billed_psf": 90, "actual_billed_psf": 88},
])

# 6-month rent billed vs actual
df_exec_rent_trend = pd.DataFrame([
    {"month": "Aug-23", "rent_to_be_billed_cr": 2.3, "actual_billed_cr": 2.3},
    {"month": "Sep-23", "rent_to_be_billed_cr": 2.4, "actual_billed_cr": 2.3},
    {"month": "Oct-23", "rent_to_be_billed_cr": 2.4, "actual_billed_cr": 2.5},
    {"month": "Nov-23", "rent_to_be_billed_cr": 2.6, "actual_billed_cr": 2.5},
    {"month": "Dec-23", "rent_to_be_billed_cr": 2.3, "actual_billed_cr": 2.5},
    {"month": "Jan-24", "rent_to_be_billed_cr": 2.5, "actual_billed_cr": 2.9},
])

# ─────────────────────────────────────────────
# TAB 3 — TENANT PROFILE
# ─────────────────────────────────────────────

# Blue asset top-5
df_tenant_top5 = pd.DataFrame([
    {"tenant": "Alcon Labs",     "monthly_rent_cr": 2.0, "revenue_psf": 110},
    {"tenant": "Boeing",         "monthly_rent_cr": 1.2, "revenue_psf":  90},
    {"tenant": "Excality",       "monthly_rent_cr": 0.5, "revenue_psf":  75},
    {"tenant": "Mott Macdonald", "monthly_rent_cr": 0.2, "revenue_psf":  65},
    {"tenant": "Roofs",          "monthly_rent_cr": 0.2, "revenue_psf":  60},
])

# Upcoming lease expiry (quarterly buckets)
df_tenant_lease_expiry = pd.DataFrame([
    {"quarter": "2024 Q3", "area_sft": 42190, "tenant_group": "Group A"},
    {"quarter": "2025 Q1", "area_sft": 16770, "tenant_group": "Group B"},
    {"quarter": "2026 Q2", "area_sft": 27445, "tenant_group": "Group C"},
    {"quarter": "2026 Q3", "area_sft": 27445, "tenant_group": "Group C"},
    {"quarter": "2027 Q3", "area_sft": 19252, "tenant_group": "Group A"},
    {"quarter": "2027 Q4", "area_sft": 16770, "tenant_group": "Group B"},
    {"quarter": "2028 Q2", "area_sft": 27445, "tenant_group": "Group C"},
    {"quarter": "2028 Q4", "area_sft": 20432, "tenant_group": "Group A"},
    {"quarter": "2029 Q1", "area_sft": 18180, "tenant_group": "Group B"},
])

# ─────────────────────────────────────────────
# TAB 4 — STACKING PLAN
# ─────────────────────────────────────────────

# Each row = one block on a floor
# industry: Outsourcing | IT Services | Other Services | Healthcare | Vacant
df_stack_plan = pd.DataFrame([
    # Floor 7
    {"floor": 7, "tenant": "Tyco",          "area_ksft": 18, "industry": "Outsourcing"},
    {"floor": 7, "tenant": "Yash",          "area_ksft": 17, "industry": "Other Services"},
    {"floor": 7, "tenant": "Vacant",        "area_ksft":105, "industry": "Vacant"},
    # Floor 6
    {"floor": 6, "tenant": "Tyco",          "area_ksft": 41, "industry": "Outsourcing"},
    {"floor": 6, "tenant": "Johnson Controls","area_ksft":17, "industry": "Other Services"},
    {"floor": 6, "tenant": "Atos",          "area_ksft": 39, "industry": "IT Services"},
    {"floor": 6, "tenant": "Vacant",        "area_ksft": 43, "industry": "Vacant"},
    # Floor 5
    {"floor": 5, "tenant": "Walmart",       "area_ksft": 27, "industry": "Outsourcing"},
    {"floor": 5, "tenant": "Ekaterra",      "area_ksft": 20, "industry": "Other Services"},
    {"floor": 5, "tenant": "Zitro",         "area_ksft": 23, "industry": "IT Services"},
    {"floor": 5, "tenant": "Atos",          "area_ksft": 46, "industry": "IT Services"},
    {"floor": 5, "tenant": "Vacant",        "area_ksft": 23, "industry": "Vacant"},
    # Floor 4
    {"floor": 4, "tenant": "IP Infusion",   "area_ksft": 27, "industry": "IT Services"},
    {"floor": 4, "tenant": "Agilent",       "area_ksft": 46, "industry": "Healthcare"},
    {"floor": 4, "tenant": "Vacant",        "area_ksft": 66, "industry": "Vacant"},
    # Floor 3
    {"floor": 3, "tenant": "Nagravision",   "area_ksft": 70, "industry": "IT Services"},
    {"floor": 3, "tenant": "Vacant",        "area_ksft": 70, "industry": "Vacant"},
    # Floor 2
    {"floor": 2, "tenant": "Vacant",        "area_ksft":140, "industry": "Vacant"},
])

# ─────────────────────────────────────────────
# TAB 5 — EXPENSE VS COLLECTION
# ─────────────────────────────────────────────

df_expense_vs_collection = pd.DataFrame([
    {"month": "Aug-23", "collections_cr": 398.6, "expense_cam_cr": 280.4,
     "expense_debt_cr":  60.1, "expense_opex_cr":  60.1},
    {"month": "Sep-23", "collections_cr": 318.7, "expense_cam_cr": 206.9,
     "expense_debt_cr":  54.1, "expense_opex_cr":  57.3},
    {"month": "Oct-23", "collections_cr": 445.4, "expense_cam_cr": 286.3,
     "expense_debt_cr":  88.1, "expense_opex_cr":  66.1},
    {"month": "Nov-23", "collections_cr": 357.1, "expense_cam_cr": 216.1,
     "expense_debt_cr":  54.0, "expense_opex_cr":  90.0},
    {"month": "Dec-23", "collections_cr": 198.3, "expense_cam_cr": 144.7,
     "expense_debt_cr":   0.0, "expense_opex_cr":   0.0},
    {"month": "Jan-24", "collections_cr": 187.6, "expense_cam_cr": 103.7,
     "expense_debt_cr":   0.0, "expense_opex_cr":   0.0},
])

df_rent_billed_trend = pd.DataFrame([
    {"month": "Aug-23", "rent_to_be_billed_cr": 68.7, "actual_billed_cr": 65.3},
    {"month": "Sep-23", "rent_to_be_billed_cr": 68.9, "actual_billed_cr": 67.0},
    {"month": "Oct-23", "rent_to_be_billed_cr": 69.1, "actual_billed_cr": 65.9},
    {"month": "Nov-23", "rent_to_be_billed_cr": 69.3, "actual_billed_cr": 65.7},
    {"month": "Dec-23", "rent_to_be_billed_cr": 70.2, "actual_billed_cr": 65.9},
    {"month": "Jan-24", "rent_to_be_billed_cr": 70.5, "actual_billed_cr": 67.6},
])

# ─────────────────────────────────────────────
# TAB 6 — APPROVALS
# ─────────────────────────────────────────────

df_approvals = pd.DataFrame([
    {"description": "Environment Clearance",
     "issuing_authority": "State Environment Impact Assessment Authority",
     "issue_date": "Aug-22", "validity": "31/08/2032",
     "expected_timelines": "Mar-27", "associated_risk": "Low",
     "status": "Revision Required"},
    {"description": "Consent to Establish",
     "issuing_authority": "Maharashtra Pollution Control Board",
     "issue_date": "Aug-22", "validity": "15/08/2027",
     "expected_timelines": "Mar-27", "associated_risk": "Low",
     "status": "Revision Required"},
    {"description": "Commencement Certificate – Building no. 1",
     "issuing_authority": "Municipal Corporation of Greater Mumbai",
     "issue_date": "Oct-24", "validity": "09/03/2025",
     "expected_timelines": "Mar-25", "associated_risk": "Low",
     "status": "Revision Required"},
    {"description": "IOD Approved Plan – Building no. 1",
     "issuing_authority": "Municipal Corporation of Greater Mumbai",
     "issue_date": "Sept-24", "validity": "Not Applicable",
     "expected_timelines": "Mar-25", "associated_risk": "Low",
     "status": "Revision Required"},
    {"description": "Archaeological NOC",
     "issuing_authority": "Archaeological Survey of India",
     "issue_date": "Mar-14", "validity": "Not Applicable",
     "expected_timelines": "Not Applicable", "associated_risk": "Not Applicable",
     "status": "Complied"},
    {"description": "Hydraulic Engineer's Remarks – Building no. 1 & 2",
     "issuing_authority": "Municipal Corporation of Greater Mumbai",
     "issue_date": "Jan-22", "validity": "Not Applicable",
     "expected_timelines": "Not Applicable", "associated_risk": "Not Applicable",
     "status": "Complied"},
    {"description": "I to R/C Conversion Letter",
     "issuing_authority": "Municipal Corporation of Greater Mumbai",
     "issue_date": "Jun-14", "validity": "Not Applicable",
     "expected_timelines": "Not Applicable", "associated_risk": "Not Applicable",
     "status": "Complied"},
    {"description": "Labour Commissioner NOC",
     "issuing_authority": "Labour Commissioner, Government of Maharashtra",
     "issue_date": "Jan-14", "validity": "Not Applicable",
     "expected_timelines": "Not Applicable", "associated_risk": "Not Applicable",
     "status": "Complied"},
    {"description": "Provisional CFO NOC (Building no. 1)",
     "issuing_authority": "MCGM, Mumbai Fire Brigade",
     "issue_date": "Dec-21", "validity": "Not Applicable",
     "expected_timelines": "Not Applicable", "associated_risk": "Not Applicable",
     "status": "Complied"},
    {"description": "Provisional CFO NOC (Building no. 2)",
     "issuing_authority": "MCGM, Mumbai Fire Brigade",
     "issue_date": "Jan-24", "validity": "Not Applicable",
     "expected_timelines": "Not Applicable", "associated_risk": "Not Applicable",
     "status": "Complied"},
])

# ─────────────────────────────────────────────
# TAB 7 — COMPLIANCE REGISTER
# ─────────────────────────────────────────────

df_compliance = pd.DataFrame([
    {"item": "Statutory Audit – FY 2024-25",      "category": "Statutory",  "frequency": "Annual",
     "due_date": "30-Sept-26", "filed_done": "",          "responsible": "Statutory Auditor",
     "consequence": "Delay in ITR",                         "rag_status": "In Progress"},
    {"item": "Property Tax (BBMP) – Annual",       "category": "Statutory",  "frequency": "Annual",
     "due_date": "30-Jun-26",  "filed_done": "",          "responsible": "Consulting Edge",
     "consequence": "Penalty 2% per month",                 "rag_status": "Due Soon"},
    {"item": "Asset Valuation (External)",          "category": "SPV/Legal",  "frequency": "Monthly",
     "due_date": "30-Apr-26",  "filed_done": "",          "responsible": "IPru",
     "consequence": "Lender covenant breach / Fund NAV",    "rag_status": "Due Soon"},
    {"item": "TDS Payment",                        "category": "Statutory",  "frequency": "Monthly",
     "due_date": "7th / 30th Apr for Mar", "filed_done": "20-Apr-25", "responsible": "Consulting Edge",
     "consequence": "Penalty + interest",                   "rag_status": "OK"},
    {"item": "GST Return – GSTR-3B",               "category": "Statutory",  "frequency": "Monthly",
     "due_date": "20th of every month",    "filed_done": "17-Apr-25", "responsible": "Consulting Edge",
     "consequence": "Penalty + interest",                   "rag_status": "OK"},
    {"item": "Financial Statements – AOC-4",       "category": "Statutory",  "frequency": "Annual",
     "due_date": "30-Oct-26",  "filed_done": "",          "responsible": "Company Secretary",
     "consequence": "Penalty on directors",                 "rag_status": "Not Due"},
    {"item": "Advance Tax – Q1 Instalment",        "category": "Statutory",  "frequency": "Quarterly",
     "due_date": "15-Jun-26",  "filed_done": "",          "responsible": "Consulting Edge",
     "consequence": "Interest u/s 234B/C",                  "rag_status": "Not Due"},
    {"item": "GST Annual Return – GSTR-9",         "category": "Statutory",  "frequency": "Annual",
     "due_date": "31-Dec-26",  "filed_done": "",          "responsible": "Consulting Edge",
     "consequence": "Late fee ₹200/day",                    "rag_status": "Not Due"},
    {"item": "Income Tax Return – ITR-6",          "category": "Statutory",  "frequency": "Annual",
     "due_date": "31-Oct-26",  "filed_done": "",          "responsible": "Consulting Edge",
     "consequence": "Penalty u/s 271F",                     "rag_status": "Not Due"},
    {"item": "Insurance Renewal – Property + LOP", "category": "SPV/Legal",  "frequency": "Annual",
     "due_date": "20-Feb-27",  "filed_done": "",          "responsible": "IPru",
     "consequence": "Uninsured loss",                       "rag_status": "Not Due"},
    {"item": "Professional Tax (Employer)",        "category": "Statutory",  "frequency": "Annual",
     "due_date": "15-Mar-27",  "filed_done": "",          "responsible": "Consulting Edge",
     "consequence": "Penalty",                              "rag_status": "Not Due"},
    {"item": "ROC Annual Return – MGT-7",          "category": "Statutory",  "frequency": "Annual",
     "due_date": "30-Oct-26",  "filed_done": "",          "responsible": "Company Secretary",
     "consequence": "Additional fee + penalty",             "rag_status": "Not Due"},
    {"item": "TDS Return – Form 26Q",              "category": "Statutory",  "frequency": "Quarterly",
     "due_date": "31-Jul-26",  "filed_done": "",          "responsible": "Consulting Edge",
     "consequence": "Interest + penalty",                   "rag_status": "Not Due"},
    {"item": "Internal Audit – Q4 FY25",           "category": "NA",         "frequency": "NA",
     "due_date": "NA",          "filed_done": "",          "responsible": "Internal Auditor",
     "consequence": "Governance lapse",                     "rag_status": "Not Applicable"},
])

# ─────────────────────────────────────────────
# TAB 8 — FINANCIAL SUMMARY
# ─────────────────────────────────────────────

df_financial_kpis = pd.DataFrame([{
    "opening_balance_cr": 3.6,
    "total_inflow_cr":  428.4,
    "total_outflow_cr": 421.1,
    "closing_balance_cr": 10.9,
}])

# Per-account cashflow (8 PNB accounts)
df_financial_cashflow = pd.DataFrame([
    {"tag": "Opening Balance",          "PNB0051":  0.6, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431":  0.2, "PNB2444":  0.0, "PNB3238": -0.1, "PNB6853":  0.6, "PNB6863":  2.0, "grand_total":  3.6},
    {"tag": "Collections",              "PNB0051": 23.3, "PNB0951": 46.2, "PNB1619":  7.8, "PNB2431":  1.5, "PNB2444":  5.6, "PNB3238": 57.3, "PNB6853": 97.3, "PNB6863": -8.6, "grand_total": 187.6},
    {"tag": "Other Inflow",             "PNB0051":  0.0, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431":  0.0, "PNB2444":  0.0, "PNB3238":  0.0, "PNB6853":  0.1, "PNB6863":  0.0, "grand_total":   0.1},
    {"tag": "Redemption of Fixed Dep.", "PNB0051": 22.0, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431":  0.0, "PNB2444":  0.0, "PNB3238":130.0, "PNB6853":370.4, "PNB6863": 40.0, "grand_total": 162.5},
    {"tag": "Bank Charges",             "PNB0051":  0.0, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431":  0.0, "PNB2444":  0.0, "PNB3238":  0.0, "PNB6853":  0.0, "PNB6863":  0.0, "grand_total":   0.0},
    {"tag": "Creation of Fixed Dep.",   "PNB0051":-22.8, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431":  0.0, "PNB2444":  0.0, "PNB3238":-130.0,"PNB6853":-370.3,"PNB6863":-54.7, "grand_total":-183.4},
    {"tag": "Other Outflow",            "PNB0051":-21.9, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431": -1.7, "PNB2444": -5.6, "PNB3238":-20.9, "PNB6853":-108.1,"PNB6863":  7.6, "grand_total":-159.6},
    {"tag": "Transfer to Project Acc.", "PNB0051":-26.2, "PNB0951": -6.2, "PNB1619": -7.8, "PNB2431":  0.0, "PNB2444":  0.0, "PNB3238":-26.2, "PNB6853": 14.0, "PNB6863":  0.0, "grand_total":   0.0},
    {"tag": "Closing Balance",          "PNB0051": -1.8, "PNB0951":  0.0, "PNB1619":  0.0, "PNB2431":  0.0, "PNB2444":  0.0, "PNB3238":  1.3, "PNB6853":  4.0, "PNB6863":  1.6, "grand_total":  10.9},
])

# Sources & Usage
df_financial_sources = pd.DataFrame([
    {"source": "Collections",               "amount_cr": 187.6},
    {"source": "Other Inflow",              "amount_cr":   0.1},
    {"source": "Redemption of Fixed Dep.",  "amount_cr": 162.5},
])
df_financial_usage = pd.DataFrame([
    {"usage": "Bank Charges",               "amount_cr":   0.0},
    {"usage": "Creation of Fixed Dep.",     "amount_cr": 183.4},
    {"usage": "Other Outflow",              "amount_cr": 159.6},
    {"usage": "Transfer to Project Acc.",   "amount_cr":   0.0},
])

# Business plan vs actual collections
df_financial_collections_trend = pd.DataFrame([
    {"month": "Aug-23", "actual_cr": 123, "planned_cr": 130},
    {"month": "Sep-23", "actual_cr": 137, "planned_cr": 160},
    {"month": "Oct-23", "actual_cr": 188, "planned_cr": 150},
    {"month": "Nov-23", "actual_cr": 121, "planned_cr": 180},
    {"month": "Dec-23", "actual_cr": 156, "planned_cr": 140},
    {"month": "Jan-24", "actual_cr": 104, "planned_cr": 170},
])