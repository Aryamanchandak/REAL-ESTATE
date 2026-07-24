"""
build_dashboard.py — Excel → window.DASH JSON → dashboard.html

Usage:
    python3 build_dashboard.py
    python3 build_dashboard.py IPRU_RE_Fund_DataEntry_ver_3_final.xlsx dashboard.html
"""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from ingest import ingest

# ── constants ─────────────────────────────────────────────────────────────────

EXCEL_PATH    = Path("Copy of IPRU_RE_Fund_DataEntry_ver_3_final.xlsx")
TEMPLATE_PATH = Path("dashboard.template.html")
OUTPUT_PATH   = Path("dashboard.html")

# 15 muted hex values — one per possible asset slot, in asset-list order
ASSET_PALETTE = [
    "#6B7A4A", "#4E6577", "#A39C8C", "#B4930F", "#8B4A4A",
    "#9B7A3A", "#6A5A8C", "#4A5A8C", "#787878", "#8C7A3A",
    "#3D7A72", "#3A6F7A", "#7A3A4A", "#3A4A6E", "#8C5A4A",
]

STACK_LEGEND = [
    {"key": "outsourcing", "label": "Outsourcing",    "color": "var(--cat-outsourcing)"},
    {"key": "other",       "label": "Other Services", "color": "#8C8678"},
    {"key": "it",          "label": "IT Services",    "color": "#B8960C"},
    {"key": "healthcare",  "label": "Healthcare",     "color": "#6E5A2E"},
    {"key": "vacant",      "label": "Vacant",         "color": "var(--vacant)"},
]

# portfolio_kpis: KPI label → DASH field path
PORTFOLIO_KPI_MAP = {
    "Monthly Rent":   "monthlyRent",
    "CAM Charge":     "camCharge",
    "Occupancy":      "occupancy",
    "Gross Billing":  "grossBilling",
    "Collections":    "collections",
    "Leasable Area":  "area.leasable",
    "Leased Area":    "area.leased",
    "Vacant Area":    "area.vacant",
}

# approvals status column
APPROVAL_STATUS_COL  = "Status"
APPROVAL_COMPLIED    = "Complied"

# compliance RAG column → DASH summary key
COMPLIANCE_RAG_MAP = {
    "In Progress":    "inProgress",
    "Due Soon":       "dueSoon",
    "OK":             "ok",
    "Not Due":        "notDue",
    "Not Applicable": "na",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _v(val):
    """JSON-safe Python value: NaN/NA/NaT → None; numpy scalars → Python."""
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(val, "item"):   # numpy int64 / float64 → Python int / float
        val = val.item()
    if isinstance(val, float) and math.isnan(val):
        return None
    return val


def _n(val, decimals: int = 2):
    """Numeric value rounded to `decimals` places, or None."""
    v = _v(val)
    if v is None:
        return None
    try:
        return round(float(v), decimals)
    except (TypeError, ValueError):
        return None


def _i(val):
    """Integer value, or None."""
    v = _v(val)
    if v is None:
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _s(val):
    """String value, or None."""
    v = _v(val)
    return str(v) if v is not None else None


def _month_label(val):
    """Month value as a 'Aug-23'-style label (matches the workbook's other
    month columns). Date/Timestamp values are formatted; existing strings pass
    through unchanged."""
    v = _v(val)
    if v is None:
        return None
    if isinstance(val, (pd.Timestamp, datetime, date)):
        return val.strftime("%b-%y")
    return str(v)


# ── section builders ──────────────────────────────────────────────────────────

def _build_meta(t: dict) -> dict:
    row = t["meta"].iloc[0]
    # Read every "Month N" column present (no fixed cap), in numeric order.
    month_cols = sorted(
        (c for c in t["meta"].columns if re.fullmatch(r"Month \d+", str(c))),
        key=lambda c: int(str(c).split()[1]),
    )
    months = [lbl for c in month_cols if (lbl := _month_label(row.get(c))) is not None]
    return {
        "fund":        _s(row["Fund Name"]),
        "reportMonth": _s(row["Report Month"]),
        "months":      months,
        "currency":    _s(row.get("Currency", "₹")),
    }


def _build_assets(t: dict) -> tuple[list, dict]:
    """Returns (assets list, assetColors dict)."""
    df = t["assets"]
    assets = []
    for _, row in df.iterrows():
        assets.append({
            "id":          _s(row["Asset ID"]),
            "name":        _s(row["Asset Name"]),
            "city":        _s(row["City, State"]),
            "leasable":    _n(row["Leasable (M sft)"], 2),
            "leased":      _n(row["Leased (M sft)"], 2),
            "vacant":      _n(row["Vacant (M sft)"], 2),
            "occupancy":   _n(row["Occupancy (%)"], 1),
            "monthlyRent": _n(row["Monthly Rent (₹Cr)"], 1),
            "wale":        _n(row["WALE (yrs)"], 1),
        })
    colors = {
        a["id"]: ASSET_PALETTE[i % len(ASSET_PALETTE)]
        for i, a in enumerate(assets) if a["id"] is not None
    }
    return assets, colors


def _build_portfolio(t: dict) -> dict:
    kpis_df = t["portfolio_kpis"]
    kpi = {}
    for _, row in kpis_df.iterrows():
        label = _s(row["KPI"])
        val   = _v(row["Value"])
        if label and label in PORTFOLIO_KPI_MAP:
            kpi[PORTFOLIO_KPI_MAP[label]] = val

    area = {
        "leasable": _n(kpi.get("area.leasable"), 2),
        "leased":   _n(kpi.get("area.leased"), 2),
        "vacant":   _n(kpi.get("area.vacant"), 2),
    }

    rent_spread = [
        {"band": _s(r["Rent Band"]), "area": _n(r["Area (M sft)"], 2)}
        for _, r in t["portfolio_rent_spread"].iterrows()
    ]

    rev_mix = [
        {"label": _s(r["Revenue Line"]), "value": _n(r["₹ Cr"], 2)}
        for _, r in t["portfolio_revenue_mix"].iterrows()
    ]

    return {
        "monthlyRent":       _n(kpi.get("monthlyRent"), 1),
        "camCharge":         _n(kpi.get("camCharge"), 2),
        "occupancy":         _n(kpi.get("occupancy"), 1),
        "grossBilling":      _n(kpi.get("grossBilling"), 1),
        "collections":       _n(kpi.get("collections"), 1),
        "area":              area,
        "rentSpread":        rent_spread,
        "revenueComposition": rev_mix,
    }


def _build_executive(t: dict, asset_ids: list[str]) -> dict:
    overview  = t["exec_asset_overview"].set_index("Asset ID")
    tenants   = t["exec_top_tenants"]
    psf       = t["exec_psf_trend"]
    bva       = t["exec_rent_billed_vs_actual"]

    result = {}
    for aid in asset_ids:
        # asset overview row
        ov = overview.loc[aid] if aid in overview.index else None

        top = [
            {"name": _s(r["Tenant Name"]), "rent": _n(r["Monthly Rent ₹Cr"], 2)}
            for _, r in tenants[tenants["Asset ID"] == aid].iterrows()
        ]

        psf_trend = [
            {"q": _s(r["Quarter"]), "psf": _n(r["Avg Rent ₹/sf"], 0)}
            for _, r in psf[psf["Asset ID"] == aid].iterrows()
        ]

        billed_actual = [
            {"m": _s(r["Month"]), "billed": _n(r["Rent to be Billed (₹Cr)"], 2), "actual": _n(r["Actual Billed (₹Cr)"], 2)}
            for _, r in bva[bva["Asset ID"] == aid].iterrows()
        ]

        result[aid] = {
            "address":      _s(ov["Address"])       if ov is not None else None,
            "leasableSft":  _i(ov["Leasable (sft)"]) if ov is not None else None,
            "wale":         _n(ov["WALE (yrs)"], 1)  if ov is not None else None,
            "leasedArea":   _n(ov["Leased Area (M sft)"], 2) if ov is not None else None,
            "vacantArea":   _n(ov["Vacant Area (M sft)"], 2) if ov is not None else None,
            "totalArea":    _n(ov["Total Area (M sft)"], 2)  if ov is not None else None,
            "grossBilling": _n(ov["Gross Billing (₹Cr)"], 2) if ov is not None else None,
            "collection":   _n(ov["Collection (₹Cr)"], 2)    if ov is not None else None,
            "topTenants":        top,
            "rentalPsfTrend":    psf_trend,
            "billedVsActual":    billed_actual,
        }
    return result


def _build_financial(t: dict, asset_ids: list[str]) -> dict:
    # Cash position, sources, usage, business-plan-vs-actual, and cash flow
    # are all reported per-asset — key the output by Asset ID (mirrors
    # _build_executive) instead of summing across assets into one
    # portfolio-level object.
    cash = t["financial_cash_position"].set_index("Asset ID")
    src  = t["financial_sources"].set_index("Asset ID")
    use  = t["financial_usage"].set_index("Asset ID")
    bp   = t["financial_bp_vs_actual"]
    cf   = t["financial_cash_flow_by_asset"].set_index("Asset ID")

    result = {}
    for aid in asset_ids:
        c = cash.loc[aid] if aid in cash.index else None
        s = src.loc[aid] if aid in src.index else None
        u = use.loc[aid] if aid in use.index else None
        f = cf.loc[aid] if aid in cf.index else None

        sources = [
            {"label": "Collections",      "value": _n(s["Collections"], 2) if s is not None else 0},
            {"label": "Redemption of FD", "value": _n(s["Redemption of FD"], 2) if s is not None else 0},
            {"label": "Other Inflow",     "value": _n(s["Other Inflow"], 2) if s is not None else 0},
        ]
        usage = [
            {"label": "Creation of FD",       "value": _n(u["Creation of FD"], 2) if u is not None else 0},
            {"label": "Transfer to Projects", "value": _n(u["Transfer to Projects"], 2) if u is not None else 0},
            {"label": "Other Outflow",        "value": _n(u["Other Outflow"], 2) if u is not None else 0},
            {"label": "Bank Charges",         "value": _n(u["Bank Charges"], 2) if u is not None else 0},
        ]
        businessPlan = [
            {"m": _s(r["Month"]), "planned": _n(r["Planned (₹Cr)"], 2), "actual": _n(r["Actual (₹Cr)"], 2)}
            for _, r in bp[bp["Asset ID"] == aid].iterrows()
        ]
        accounts = [{
            "acct":        aid,
            "open":        _n(f["Opening (₹Cr)"], 2) if f is not None else 0,
            "collections": _n(f["Collections (₹Cr)"], 2) if f is not None else 0,
            "inflow":      _n(f["Other Inflow (₹Cr)"], 2) if f is not None else 0,
            "close":       _n(f["Closing (₹Cr)"], 2) if f is not None else 0,
        }] if f is not None else []

        result[aid] = {
            "openingBalance": _n(c["Opening Balance"], 2) if c is not None else 0,
            "totalInflow":    _n(c["Total Inflow"], 2) if c is not None else 0,
            "totalOutflow":   _n(c["Total Outflow"], 2) if c is not None else 0,
            "closingBalance": _n(c["Closing Balance"], 2) if c is not None else 0,
            "sources":        sources,
            "usage":          usage,
            "businessPlan":   businessPlan,
            "accounts":       accounts,
        }
    return result


def _build_expenses(t: dict, asset_ids: list[str]) -> dict:
    # Both tables are asset × month — key the output by Asset ID (mirrors
    # _build_executive) instead of reading the portfolio "MONTHLY TOTALS"
    # sections.
    monthly_df = t["expenses_monthly"]
    bva_df     = t["expenses_rent_billed_vs_actual"]

    result = {}
    for aid in asset_ids:
        monthly = [
            {
                "m":          _s(r["Month"]),
                "collection": _n(r["Collection (₹Cr)"], 2),
                "cam":        _n(r["CAM (₹Cr)"], 2),
                "debt":       _n(r["Debt Service (₹Cr)"], 2),
                "opex":       _n(r["OPEX (₹Cr)"], 2),
            }
            for _, r in monthly_df[monthly_df["Asset ID"] == aid].iterrows()
        ]
        bva = [
            {"m": _s(r["Month"]), "billed": _n(r["Rent to be Billed (₹Cr)"], 2), "actual": _n(r["Actual Billed (₹Cr)"], 2)}
            for _, r in bva_df[bva_df["Asset ID"] == aid].iterrows()
        ]
        result[aid] = {"monthly": monthly, "billedVsActual": bva}
    return result


def _build_stack_plan(t: dict, asset_ids: list[str]) -> dict:
    df = t["stack_plan"]
    result = {}
    for aid in asset_ids:
        sub = df[df["Asset ID"] == aid]
        floors_map: dict[int, list] = {}
        for _, row in sub.iterrows():
            fno  = _i(row["Floor No."]) or 0
            unit = {
                "t":   _s(row["Tenant Name"]),
                "k":   _i(row["Area (K sft)"]) or 0,
                "cat": _s(row["Category"]) or "other",
            }
            floors_map.setdefault(fno, []).append(unit)
        floors = [
            {"floor": fno, "units": units}
            for fno, units in sorted(floors_map.items(), reverse=True)
        ]
        result[aid] = {"asset": aid, "legend": STACK_LEGEND, "floors": floors}
    return result


def _build_tenant(t: dict, asset_ids: list[str]) -> dict:
    prof   = t["tenant_profile"]
    expiry = t["tenant_lease_expiry"]

    # Surface silent data-entry failures: rows keyed to a non-existent asset
    # are dropped, and assets with no tenant rows render empty.
    known = set(asset_ids)
    orphans = sorted({_s(x) for x in prof["Asset ID"].dropna()} - known)
    if orphans:
        print(f"[build][warn] tenant_profile: rows for unknown asset id(s) dropped: {orphans}")
    empty = [aid for aid in asset_ids if not len(prof[prof["Asset ID"] == aid])]
    if empty:
        print(f"[build][warn] tenant_profile: no tenant rows for asset(s): {empty}")

    result = {}
    for aid in asset_ids:
        tp = prof[prof["Asset ID"] == aid]
        top = [
            {"name": _s(r["Tenant Name"]), "rent": _n(r["Monthly Rent (₹Cr)"], 2)}
            for _, r in tp.iterrows()
        ]
        # find first non-null effective LED
        led_series = tp["Effective LED"].dropna()
        eff_led = _s(led_series.iloc[0]) if len(led_series) else "—"

        ex = expiry[expiry["Asset ID"] == aid]
        lease_exp = [
            {"q": _s(r["Quarter"]), "sft": _i(r["Area Expiring (sft)"]) or 0}
            for _, r in ex.iterrows()
        ]
        result[aid] = {
            "asset":       aid,
            "topTenants":  top,
            "effectiveLed": eff_led,
            "leaseExpiry": lease_exp,
        }
    return result


def _build_approvals(t: dict, asset_ids: list[str]) -> dict:
    df = t["approvals"]
    # detect status column name
    status_col = APPROVAL_STATUS_COL if APPROVAL_STATUS_COL in df.columns else (df.columns[-1] if len(df.columns) else "Status")
    result = {}
    for aid in asset_ids:
        sub = df[df["Asset ID"] == aid]
        rows = []
        complied = rev_req = 0
        for _, r in sub.iterrows():
            st = _s(r[status_col]) or ""
            if st == APPROVAL_COMPLIED:
                complied += 1
            else:
                rev_req += 1
            rows.append({
                "desc":      _s(r.get("Approval Description")),
                "authority": _s(r.get("Issuing Authority")),
                "issued":    _s(r.get("Date Issued")),
                "validity":  _s(r.get("Validity")),
                "timeline":  _s(r.get("Target Timeline")),
                "risk":      _s(r.get("Risk Level")),
                "status":    st,
            })
        result[aid] = {
            "asset": aid,
            "asOf":  None,
            "rows":  rows,
            "summary": {"complied": complied, "revisionRequired": rev_req},
        }
    return result


def _build_compliance(t: dict, asset_ids: list[str]) -> dict:
    df = t["compliance"]
    # detect RAG column
    rag_col = "RAG Status" if "RAG Status" in df.columns else df.columns[-1]
    result = {}
    for aid in asset_ids:
        sub = df[df["Asset ID"] == aid]
        rows = []
        counts: dict[str, int] = {k: 0 for k in COMPLIANCE_RAG_MAP.values()}
        for _, r in sub.iterrows():
            rag = _s(r[rag_col]) or ""
            dash_key = COMPLIANCE_RAG_MAP.get(rag)
            if dash_key:
                counts[dash_key] += 1
            rows.append({
                "item":  _s(r.get("Compliance Item")),
                "cat":   _s(r.get("Category")),
                "freq":  _s(r.get("Frequency")),
                "due":   _s(r.get("Due Date")),
                "filed": _s(r.get("Date Filed")),
                "who":   _s(r.get("Responsible Party")),
                "risk":  _s(r.get("Consequence of Non-Compliance")),
                "rag":   rag,
            })
        result[aid] = {
            "asset":   aid,
            "asOf":    None,
            "rows":    rows,
            "summary": counts,
        }
    return result


# ── main builder ──────────────────────────────────────────────────────────────

def build(
    excel_path: Path = EXCEL_PATH,
    template_path: Path = TEMPLATE_PATH,
    output_path: Path = OUTPUT_PATH,
) -> None:
    print(f"[build] ingesting {excel_path} …")
    t = ingest(excel_path)

    assets_list, asset_colors = _build_assets(t)
    asset_ids = [a["id"] for a in assets_list if a["id"]]

    data = {
        "meta":        _build_meta(t),
        "assets":      assets_list,
        "assetColors": asset_colors,
        "portfolio":   _build_portfolio(t),
        "executive":   _build_executive(t, asset_ids),
        "financial":   _build_financial(t, asset_ids),
        "expenses":    _build_expenses(t, asset_ids),
        "stackPlan":   _build_stack_plan(t, asset_ids),
        "tenant":      _build_tenant(t, asset_ids),
        "approvals":   _build_approvals(t, asset_ids),
        "compliance":  _build_compliance(t, asset_ids),
    }

    print(f"[build] {len(asset_ids)} assets: {asset_ids}")

    template = template_path.read_text(encoding="utf-8")
    if "__DASH_DATA__" not in template:
        raise ValueError(f"Placeholder __DASH_DATA__ not found in {template_path}")

    html = template.replace("__DASH_DATA__", json.dumps(data, ensure_ascii=False))
    output_path.write_text(html, encoding="utf-8")
    print(f"[build] wrote {output_path} ({output_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    excel    = Path(sys.argv[1]) if len(sys.argv) > 1 else EXCEL_PATH
    template = Path(sys.argv[2]) if len(sys.argv) > 2 else TEMPLATE_PATH
    output   = Path(sys.argv[3]) if len(sys.argv) > 3 else OUTPUT_PATH
    build(excel, template, output)
