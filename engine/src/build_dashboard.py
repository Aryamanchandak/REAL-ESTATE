"""
build_dashboard.py — Excel → window.DASH JSON → dashboard.html

Usage:
    python3 src/build_dashboard.py
    python3 src/build_dashboard.py INPUT.xlsx TEMPLATE.html OUTPUT.html
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from ingest import FUND_ID, annual_period, ingest, month_label, quarter_label

PROJECT_ROOT  = Path(__file__).resolve().parents[1]
EXCEL_PATH    = PROJECT_ROOT / "data" / "real_estate_fund_data.xlsx"
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "dashboard.template.html"
OUTPUT_PATH   = PROJECT_ROOT / "output" / "dashboard.html"

VENDOR_LIBRARIES = {
    "__REACT_LIBRARY__": "react.production.min.js",
    "__REACT_DOM_LIBRARY__": "react-dom.production.min.js",
    "__BABEL_LIBRARY__": "babel.min.js",
}

# One muted hex value per possible asset slot, in asset-list order
ASSET_PALETTE = [
    "#6B7A4A", "#4E6577", "#A39C8C", "#B4930F", "#8B4A4A",
    "#9B7A3A", "#6A5A8C", "#4A5A8C", "#787878", "#8C7A3A",
    "#3D7A72", "#3A6F7A", "#7A3A4A", "#3A4A6E", "#8C5A4A",
]
FUND_COLOR = "#17181C"

STACK_LEGEND = [
    {"key": "outsourcing", "label": "Outsourcing",    "color": "var(--cat-outsourcing)"},
    {"key": "other",       "label": "Other Services", "color": "#8C8678"},
    {"key": "it",          "label": "IT Services",    "color": "#B8960C"},
    {"key": "healthcare",  "label": "Healthcare",     "color": "#6E5A2E"},
    {"key": "vacant",      "label": "Vacant",         "color": "var(--vacant)"},
]

COMPLIANCE_RAG_MAP = {
    "In Progress":    "inProgress",
    "Ongoing":        "inProgress",
    "Due Soon":       "dueSoon",
    "OK":             "ok",
    "Not Due":        "notDue",
    "Not Applicable": "na",
}

MONTHLY_KEYS = (
    "leasable", "leased", "vacant", "occupancy", "psf", "monthlyRent", "monthlyCam",
    "grossBilling", "rentalCollections", "camCollections", "otherCollections", "collections",
    "openingBalance", "overdraftOpening", "redemptionFd", "otherInflow", "totalInflow",
    "statutory", "camExpense", "debtService", "opex", "totalExpense", "netSurplus",
    "investmentMf", "creationFd", "capex", "otherOutflow", "bankCharges", "totalOutflow",
    "outflowComponents", "outflowGap", "closingBalance", "rentToBeBilled", "actualBilled",
    "plannedCollection", "tdsReceivable",
)


# ── formatting helpers ────────────────────────────────────────────────────────

def _r(value, decimals: int = 4):
    return None if value is None else round(float(value), decimals)


def _date_label(value):
    """Human-readable date for Excel date cells; free text ('5 years', 'Jun-25') passes through."""
    if value is None:
        return None
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    if isinstance(value, (int, float)) and 20000 < value < 80000:
        from openpyxl.utils.datetime import from_excel
        return from_excel(value).strftime("%d %b %Y")
    return str(value)


def _month_key(month: date) -> str:
    return month.strftime("%Y-%m")


def _years_between(start: date, end: date) -> float:
    return (end - start).days / 365.25


def _descending(rows: list, key: str) -> list:
    return sorted(rows, key=lambda row: (row.get(key) is not None, row.get(key) or 0), reverse=True)


# ── section builders ──────────────────────────────────────────────────────────

def _build_monthly(book) -> dict:
    result = {}
    for asset_id, series in book.monthly.items():
        rows = []
        for row in series:
            out = {
                "key": _month_key(row["month"]),
                "label": month_label(row["month"]),
                "period": annual_period(row["month"]),
                "hasData": row["hasData"],
                "openingSource": row.get("openingSource"),
                "note": row.get("note"),
            }
            for key in MONTHLY_KEYS:
                out[key] = _r(row.get(key), 2 if key in ("occupancy", "psf") else (0 if key in ("leasable", "leased", "vacant") else 4))
            if asset_id == FUND_ID:
                out["psfExcluded"] = row.get("psfExcluded", [])
            rows.append(out)
        result[asset_id] = rows
    return result


def _build_annual(book) -> dict:
    result = {}
    for asset_id, periods in book.annual.items():
        result[asset_id] = [
            {
                "period": p["period"],
                "monthsReported": p["monthsReported"],
                "from": month_label(p["firstMonth"]),
                "to": month_label(p["lastMonth"]),
                **{k: _r(p.get(k), 2 if k in ("occupancy", "psf") else 4) for k in (
                    "leasable", "leased", "occupancy", "psf", "monthlyRent", "monthlyCam",
                    "grossBilling", "collections", "totalInflow", "statutory", "totalExpense",
                    "netSurplus", "capex", "investmentMf", "totalOutflow", "outflowGap",
                    "openingBalance", "closingBalance", "rentToBeBilled", "actualBilled",
                    "plannedCollection",
                )},
            }
            for p in periods
        ]
    return result


def _wale(tenants: list, as_of: date):
    weighted = [(t["area"], _years_between(as_of, t["end"])) for t in tenants if t["area"] and t["end"] and t["end"] > as_of]
    area = sum(a for a, _ in weighted)
    return (sum(a * years for a, years in weighted) / area if area else None), area


def _build_tenants(book, asset_ids: list) -> dict:
    as_of = book.as_of
    window_start = book.report_month
    next_year = as_of + timedelta(days=365)
    result = {}
    for scope in [FUND_ID, *asset_ids]:
        tenants = [t for t in book.tenants if scope == FUND_ID or t["assetId"] == scope]
        wale, wale_area = _wale(tenants, as_of)

        by_name = {}
        for tenant in tenants:
            entry = by_name.setdefault(tenant["name"].lower(), {"name": tenant["name"], "rent": 0.0, "area": 0.0, "assets": []})
            entry["rent"] += tenant["monthlyRent"] or 0
            entry["area"] += tenant["area"] or 0
            if tenant["assetId"] not in entry["assets"]:
                entry["assets"].append(tenant["assetId"])
        top = _descending([{**e, "rent": _r(e["rent"]), "area": _r(e["area"], 0)} for e in by_name.values()], "rent")

        expiry = {}
        for tenant in tenants:
            if tenant["end"] and tenant["end"] >= window_start:
                bucket = expiry.setdefault(quarter_label(tenant["end"]), {"sft": 0, "tenants": [], "unknownArea": 0, "sort": (tenant["end"].year, (tenant["end"].month - 1) // 3)})
                bucket["sft"] += tenant["area"] or 0
                bucket["unknownArea"] += 0 if tenant["area"] else 1
                bucket["tenants"].append(tenant["name"])
        lease_expiry = [
            {"q": q, "sft": round(b["sft"]), "tenants": b["tenants"], "unknownArea": b["unknownArea"]}
            for q, b in sorted(expiry.items(), key=lambda item: item[1]["sort"])
        ]

        rows = [
            {
                "assetId": t["assetId"],
                "name": t["name"],
                "monthlyRent": _r(t["monthlyRent"]),
                "psf": _r(t["psf"], 2),
                "area": _r(t["area"], 0),
                "start": _date_label(t["start"]),
                "end": _date_label(t["end"]),
                "endKey": t["end"].isoformat() if t["end"] else None,
                "remainingYears": _r(_years_between(as_of, t["end"]), 2) if t["end"] else None,
                "expired": bool(t["end"] and t["end"] < as_of),
                "areaStatus": t["areaStatus"],
                "notes": t["notes"],
                "recordAsOf": _date_label(t["recordAsOf"]),
            }
            for t in tenants
        ]
        result[scope] = {
            "asset": scope,
            "rows": rows,
            "count": len(rows),
            "wale": _r(wale, 2),
            "waleArea": _r(wale_area, 0),
            "totalRent": _r(sum(t["monthlyRent"] or 0 for t in tenants)),
            "totalArea": _r(sum(t["area"] or 0 for t in tenants), 0),
            "needsArea": sum(1 for t in tenants if not t["area"]),
            "expiredCount": sum(1 for r in rows if r["expired"]),
            "expiring12m": _r(sum(t["area"] or 0 for t in tenants if t["end"] and as_of < t["end"] <= next_year), 0),
            "topTenants": top,
            "leaseExpiry": lease_expiry,
        }
    return result


def _build_assets(book, tenants: dict) -> tuple:
    assets = []
    for asset in book.assets:
        assets.append({
            "id": asset["id"],
            "name": asset["name"],
            "city": asset["city"],
            "address": asset["address"],
            "leasable": _r(asset["leasable"], 0),
            "imageUrl": asset["imageUrl"],
            "imageAlt": asset["imageAlt"],
            "mapEmbedUrl": asset["mapEmbedUrl"],
            "mapLinkUrl": asset["mapLinkUrl"],
            "latitude": asset["latitude"],
            "longitude": asset["longitude"],
            "notes": asset["notes"],
            "capexTillDate": _r(asset["capexTillDate"]),
            "wale": tenants[asset["id"]]["wale"],
        })
    colors = {a["id"]: ASSET_PALETTE[i % len(ASSET_PALETTE)] for i, a in enumerate(assets)}
    colors[FUND_ID] = FUND_COLOR
    return assets, colors


def _build_stack_plan(book, asset_ids: list) -> dict:
    """
    Floor-by-floor stack. Each unit carries `own` ("Fund" | "Others"). `k` may be 0
    when a floor's area is unknown — `kKnown` distinguishes that from a zero-area unit.
    """
    result = {}
    for aid in asset_ids:
        floors_map: dict = {}
        for row in (r for r in book.stack_plan if r["assetId"] == aid):
            own = row["ownership"] if row["ownership"] in ("Fund", "Others") else "Fund"
            floors_map.setdefault(row["floor"], []).append({
                "t":      row["tenant"] or "—",
                "k":      _r(row["areaK"], 3) or 0,
                "kKnown": row["areaK"] is not None,
                "cat":    row["category"] or "other",
                "own":    own,
                "notes":  row["notes"],
            })

        def floor_sort(item):
            try:
                return (1, float(item[0]))
            except (TypeError, ValueError):
                return (0, str(item[0]))

        floors = [{"floor": f, "units": u} for f, u in sorted(floors_map.items(), key=floor_sort, reverse=True)]
        units_all = [u for f in floors for u in f["units"]]

        def totals(scope):
            units = [u for u in units_all if scope is None or u["own"] == scope]
            known = [u for u in units if u["kKnown"]]
            return {
                "areaK":   round(sum(u["k"] for u in known), 2),
                "vacantK": round(sum(u["k"] for u in known if u["cat"] == "vacant"), 2),
                "floors":  len({f["floor"] for f in floors if any(scope is None or u["own"] == scope for u in f["units"])}),
                "units":   len(units),
                "unknownArea": sum(1 for u in units if not u["kKnown"]),
            }

        result[aid] = {
            "asset": aid,
            "legend": STACK_LEGEND,
            "floors": floors,
            "totals": {"Fund": totals("Fund"), "Others": totals("Others"), "All": totals(None)},
        }
    return result


def _build_approvals(book, asset_ids: list) -> dict:
    result = {}
    for scope in [FUND_ID, *asset_ids]:
        rows, counts = [], {"complied": 0, "inProgress": 0, "revisionRequired": 0, "unclassified": 0}
        for r in book.approvals:
            if scope != FUND_ID and r["Asset ID"] != scope:
                continue
            status = r.get("Status") or "Unclassified"
            if status == "Complied":
                counts["complied"] += 1
            elif status in ("In Progress", "Ongoing"):
                counts["inProgress"] += 1
            elif status == "Revision Required":
                counts["revisionRequired"] += 1
            else:
                counts["unclassified"] += 1
            rows.append({
                "assetId":     r["Asset ID"],
                "desc":        r.get("Approval Description"),
                "authority":   r.get("Issuing Authority"),
                "issued":      _date_label(r.get("Date Issued")),
                "validity":    _date_label(r.get("Validity")),
                "timeline":    _date_label(r.get("Target Timeline")),
                "risk":        r.get("Risk Level"),
                "status":      status,
                "lastUpdated": _date_label(r.get("Last Updated")),
                "owner":       r.get("Owner / SPOC"),
                "remarks":     r.get("Remarks"),
            })
        result[scope] = {"asset": scope, "rows": rows, "summary": {"total": len(rows), **counts}}
    return result


def _build_compliance(book, asset_ids: list) -> dict:
    result = {}
    for scope in [FUND_ID, *asset_ids]:
        rows = []
        counts = {k: 0 for k in COMPLIANCE_RAG_MAP.values()}
        counts["unclassified"] = 0
        for r in book.compliance:
            if scope != FUND_ID and r["Asset ID"] != scope:
                continue
            rag = r.get("RAG Status") or "Unclassified"
            counts[COMPLIANCE_RAG_MAP.get(rag, "unclassified")] += 1
            rows.append({
                "assetId":     r["Asset ID"],
                "item":        r.get("Compliance Item"),
                "cat":         r.get("Category"),
                "freq":        r.get("Frequency"),
                "due":         _date_label(r.get("Due Date")),
                "filed":       _date_label(r.get("Date Filed")),
                "who":         r.get("Responsible Party"),
                "risk":        r.get("Consequence of Non-Compliance"),
                "rag":         rag,
                "lastUpdated": _date_label(r.get("Last Updated")),
                "owner":       r.get("Owner / SPOC"),
                "remarks":     r.get("Remarks"),
            })
        result[scope] = {"asset": scope, "rows": rows, "summary": counts}
    return result


def _build_data(book) -> dict:
    """Convert the ingested workbook into the dashboard data contract (window.DASH)."""
    asset_ids = [a["id"] for a in book.assets]
    tenants = _build_tenants(book, asset_ids)
    assets, colors = _build_assets(book, tenants)
    spread = book.rent_spread
    return {
        "meta": {
            "fund":        book.meta.get("fund") or "Real Estate Fund",
            "currency":    book.meta.get("currency") or "INR",
            "unit":        book.meta.get("unit"),
            "frequency":   book.meta.get("frequency"),
            "annualConvention": book.meta.get("annualConvention"),
            "reportMonth": _month_key(book.report_month),
            "reportMonthLabel": month_label(book.report_month),
            "asOf":        book.as_of.strftime("%d %b %Y"),
            "months": [
                {"key": _month_key(m), "label": month_label(m), "period": annual_period(m)}
                for m in book.months
            ],
        },
        "fundId":      FUND_ID,
        "assets":      assets,
        "assetColors": colors,
        "monthly":     _build_monthly(book),
        "annual":      _build_annual(book),
        "rentSpread": {
            "asOf":    month_label(spread["asOf"]) if spread["asOf"] else None,
            "fund":    [{"band": b["band"], "sft": _r(b["sft"], 0)} for b in spread["fund"]],
            "byAsset": {aid: [{"band": b["band"], "sft": _r(b["sft"], 0)} for b in bands] for aid, bands in spread["byAsset"].items()},
        },
        "revenueMix": [
            {"key": _month_key(r["month"]), "assetId": r["assetId"], "line": r["line"], "value": _r(r["amount"])}
            for r in book.revenue_mix
        ],
        "tenants":     tenants,
        "stackPlan":   _build_stack_plan(book, asset_ids),
        "approvals":   _build_approvals(book, asset_ids),
        "compliance":  _build_compliance(book, asset_ids),
        "dataQuality": {
            "overall":  book.data_quality.get("overall"),
            "checks":   book.data_quality.get("checks", []),
            "warnings": list(book.report.warnings),
        },
    }


# ── HTML assembly ─────────────────────────────────────────────────────────────

def _json_for_script(data: dict) -> str:
    """Serialize JSON without allowing workbook text to break out of <script>."""
    payload = json.dumps(data, ensure_ascii=False)
    return payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


def _embed_browser_libraries(template: str, template_path: Path) -> str:
    """Inline pinned browser libraries so the output has no runtime CDN dependency."""
    vendor_dir = template_path.resolve().parent / "vendor"
    for placeholder, filename in VENDOR_LIBRARIES.items():
        if placeholder not in template:
            raise ValueError(f"Placeholder {placeholder} not found in {template_path}")
        library_path = vendor_dir / filename
        if not library_path.is_file():
            raise FileNotFoundError(
                f"Browser library not found: {library_path}. "
                "Restore the pinned files in the vendor directory."
            )
        source = library_path.read_text(encoding="utf-8")
        if not source.strip():
            raise ValueError(f"Browser library is empty: {library_path}")
        # HTML parsers terminate a script element at a literal closing tag even
        # when it appears inside JavaScript text.
        source = source.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")
        template = template.replace(placeholder, source)
    return template


def build(
    excel_path: Path = EXCEL_PATH,
    template_path: Path = TEMPLATE_PATH,
    output_path: Path = OUTPUT_PATH,
) -> dict:
    print(f"[build] ingesting {excel_path} …")
    book = ingest(excel_path)
    data = _build_data(book)

    for name, count in sorted(book.report.dropped_rows.items()):
        print(f"[build] dropped {count} row(s) from {name}")
    for warning in book.report.warnings:
        print(f"[build][warn] {warning}")
    print(f"[build] {len(data['assets'])} assets: {[a['id'] for a in data['assets']]}")
    print(f"[build] months: {[m['label'] for m in data['meta']['months']]} (report month {data['meta']['reportMonthLabel']})")

    template = template_path.read_text(encoding="utf-8")
    if "__DASH_DATA__" not in template:
        raise ValueError(f"Placeholder __DASH_DATA__ not found in {template_path}")
    template = _embed_browser_libraries(template, template_path)

    # A workbook cell containing ``</script>`` must not be able to terminate
    # the data script and inject markup into the generated dashboard.
    html = template.replace("__DASH_DATA__", _json_for_script(data))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"[build] wrote {output_path} ({output_path.stat().st_size // 1024} KB)")
    return data


if __name__ == "__main__":
    excel    = Path(sys.argv[1]) if len(sys.argv) > 1 else EXCEL_PATH
    template = Path(sys.argv[2]) if len(sys.argv) > 2 else TEMPLATE_PATH
    output   = Path(sys.argv[3]) if len(sys.argv) > 3 else OUTPUT_PATH
    build(excel, template, output)
