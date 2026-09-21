import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_dashboard import _build_data, _json_for_script, build
from ingest import FUND_ID, ingest

LATEST_BOOK = ROOT / "data" / "real_estate_fund_data.xlsx"
TEMPLATE = ROOT / "templates" / "dashboard.template.html"


def extract_dash(html: str) -> dict:
    match = re.search(r"window\.DASH = (\{.*?\});\s*</script>", html, re.S)
    if not match:
        raise AssertionError("window.DASH payload not found")
    return json.loads(match.group(1))


class WorkbookIngestTests(unittest.TestCase):
    """Figures checked by hand against the Aug-2026 workbook."""

    @classmethod
    def setUpClass(cls):
        if not LATEST_BOOK.exists():
            raise unittest.SkipTest(f"{LATEST_BOOK.name} not present")
        cls.book = ingest(LATEST_BOOK)
        cls.data = _build_data(cls.book)

    def row(self, asset_id, key):
        return next(r for r in self.data["monthly"][asset_id] if r["key"] == key)

    def warnings(self):
        return "\n".join(self.book.report.warnings)

    def test_active_assets_skip_unused_slots(self):
        self.assertEqual([a["id"] for a in self.book.assets], ["green", "blue", "white", "yellow", "red"])

    def test_report_month_ignores_rolled_forward_months(self):
        # Sep-26 onward only carry the Opening Balance formula, not entered figures.
        self.assertEqual(self.book.report_month, date(2026, 8, 1))
        self.assertEqual([m["label"] for m in self.data["meta"]["months"]], ["Jun-26", "Jul-26", "Aug-26"])

    def test_fund_rollup_matches_monthly_input(self):
        aug = self.row(FUND_ID, "2026-08")
        self.assertEqual(aug["leasable"], 964591)
        self.assertEqual(aug["leased"], 887604)
        self.assertAlmostEqual(aug["occupancy"], 92.02, places=2)
        self.assertAlmostEqual(aug["monthlyRent"], 9.2011, places=4)
        self.assertAlmostEqual(aug["closingBalance"], 8.2506, places=4)

    def test_fund_psf_leaves_out_blank_assets(self):
        aug = self.row(FUND_ID, "2026-08")
        self.assertEqual(aug["psfExcluded"], ["yellow"])
        self.assertAlmostEqual(aug["psf"], 81.62, places=2)
        self.assertIn("counts blank PSF as 0", self.warnings())

    def test_overdraft_opening_balance_is_used_when_opening_is_blank(self):
        white_jul = self.row("white", "2026-07")
        self.assertEqual(white_jul["openingSource"], "Over Draft Opening Balance")
        self.assertAlmostEqual(white_jul["openingBalance"], -3.348, places=3)

    def test_net_surplus_is_collections_less_expense(self):
        yellow_jul = self.row("yellow", "2026-07")
        self.assertAlmostEqual(yellow_jul["netSurplus"], yellow_jul["collections"] - yellow_jul["totalExpense"], places=3)
        self.assertIn("workbook Net Surplus", self.warnings())

    def test_investment_in_mf_missing_from_total_outflow_is_surfaced(self):
        yellow_jul = self.row("yellow", "2026-07")
        self.assertAlmostEqual(yellow_jul["outflowGap"], 4.5, places=4)
        self.assertAlmostEqual(yellow_jul["totalOutflow"], 37.8, places=4)   # workbook value kept
        self.assertEqual(self.row("red", "2026-08")["outflowGap"], 0)          # this row's formula includes MF

    def test_wale_is_recalculated_from_tenant_leases(self):
        wale = {a["id"]: a["wale"] for a in self.data["assets"]}
        self.assertEqual(wale, {"green": 1.08, "blue": 3.39, "white": 4.0, "yellow": 7.96, "red": 8.21})
        self.assertIn("1.3-year fallback", self.warnings())

    def test_tenant_sheet_is_split_into_three_blocks(self):
        self.assertEqual(len(self.book.tenants), 21)
        self.assertTrue(self.book.lease_schedule)
        red_floors = {row["floor"] for row in self.book.stack_plan if row["assetId"] == "red"}
        self.assertEqual(red_floors, {"G", 4, 5, 6, 7, 8, 9, 10, 11})
        self.assertIn("Lease Expiry Schedule block does not match", self.warnings())

    def test_lease_expiry_is_derived_from_lease_end_dates(self):
        red = {row["q"]: row["sft"] for row in self.data["tenants"]["red"]["leaseExpiry"]}
        self.assertEqual(red, {"30 Q3": 50000, "35 Q3": 291362})

    def test_stack_plan_fund_area_reconciles_with_leasable(self):
        leasable = {a["id"]: a["leasable"] for a in self.data["assets"]}
        for aid, plan in self.data["stackPlan"].items():
            fund_k = plan["totals"]["Fund"]["areaK"]
            self.assertLess(abs(fund_k * 1000 - leasable[aid]) / leasable[aid], 0.10, aid)

    def test_rent_spread_reads_fund_table_and_asset_matrix(self):
        spread = self.data["rentSpread"]
        self.assertEqual([b["sft"] for b in spread["fund"]], [0, 460000, 296000, 140000])
        self.assertEqual([b["sft"] for b in spread["byAsset"]["yellow"]], [0, 30000, 56000, 140000])

    def test_registers_are_split_side_by_side(self):
        self.assertEqual(self.data["approvals"][FUND_ID]["summary"]["total"], 22)
        self.assertEqual(len(self.data["compliance"][FUND_ID]["rows"]), 51)
        for scope, register in self.data["compliance"].items():
            self.assertEqual(sum(register["summary"].values()), len(register["rows"]), scope)

    def test_register_dates_are_human_readable(self):
        values = [r[k] for r in self.data["approvals"][FUND_ID]["rows"] for k in ("issued", "validity", "timeline") if r[k]]
        self.assertFalse(any("00:00:00" in v for v in values))
        self.assertIn("31 Dec 2028", values)

    def test_map_embed_is_built_from_coordinates(self):
        green = self.data["assets"][0]
        self.assertTrue(green["mapEmbedUrl"].startswith("https://maps.google.com/maps?q=12.97"))
        self.assertIn("output=embed", green["mapEmbedUrl"])
        self.assertIn("/maps/place/", green["mapLinkUrl"])

    def test_workbook_data_quality_checks_are_carried(self):
        self.assertEqual(self.data["dataQuality"]["overall"], "ACTION REQUIRED")
        self.assertEqual(len(self.data["dataQuality"]["checks"]), 8)


class BuildTests(unittest.TestCase):
    def test_build_embeds_payload_and_runtime(self):
        if not LATEST_BOOK.exists():
            self.skipTest(f"{LATEST_BOOK.name} not present")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dashboard.html"
            build(LATEST_BOOK, TEMPLATE, output)
            html = output.read_text(encoding="utf-8")
        data = extract_dash(html)
        self.assertEqual(data["meta"]["reportMonthLabel"], "Aug-26")
        self.assertEqual(len(data["assets"]), 5)
        for placeholder in ("__REACT_LIBRARY__", "__REACT_DOM_LIBRARY__", "__BABEL_LIBRARY__", "__DASH_DATA__"):
            self.assertNotIn(placeholder, html)
        self.assertNotRegex(html, r'<script[^>]+src=["\']https?://')

    def test_missing_required_sheet_fails_with_clear_error(self):
        if not LATEST_BOOK.exists():
            self.skipTest(f"{LATEST_BOOK.name} not present")
        with tempfile.TemporaryDirectory() as tmp:
            malformed = Path(tmp) / "missing-registers.xlsx"
            workbook = openpyxl.load_workbook(LATEST_BOOK)
            del workbook["6_APPROVALS_COMPLIANCE"]
            workbook.save(malformed)
            with self.assertRaisesRegex(ValueError, "missing required sheet"):
                ingest(malformed)

    def test_all_dashboard_jsx_compiles_with_embedded_babel(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        jsx_blocks = re.findall(r'<script type="text/babel">(.*?)</script>', template, re.S)
        self.assertTrue(jsx_blocks)
        babel_path = ROOT / "templates" / "vendor" / "babel.min.js"
        compiler = (
            "const fs=require('fs');"
            f"const Babel=require({json.dumps(str(babel_path))});"
            "Babel.transform(fs.readFileSync(0,'utf8'),{presets:['react']});"
        )
        subprocess.run(["node", "-e", compiler], input="\n".join(jsx_blocks), text=True, capture_output=True, check=True)

    def test_chart_scales_follow_small_large_and_narrow_data(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        helpers = re.search(r"(const num = .*?)(?=const cssVar =)", template, re.S)
        self.assertIsNotNone(helpers)
        script = helpers.group(1) + """
console.log(JSON.stringify({
  small: niceScale([0.58, 0.67]),
  large: niceScale([14.12, 15.08]),
  narrow: niceScale([10.13, 10.34], {includeZero:false, tickCount:4, padRatio:.12}),
  zero: niceScale([0, 0, 0]),
  cr: [fmtCr(0.6902), fmtCr(12.158), fmtCr(-3.348), fmtCr(null)]
}));
"""
        result = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
        scales = json.loads(result.stdout)
        self.assertLess(scales["small"]["max"], 2)
        self.assertGreaterEqual(scales["large"]["max"], 15.08)
        self.assertGreater(scales["narrow"]["min"], 0)
        self.assertEqual(scales["zero"]["min"], 0)
        self.assertEqual(scales["cr"], ["₹0.69Cr", "₹12.2Cr", "-₹3.35Cr", "—"])

    def test_embedded_json_cannot_close_its_script_tag(self):
        payload = _json_for_script({"name": "</script><script>alert(1)</script>"})
        self.assertNotIn("</script>", payload.lower())
        self.assertEqual(json.loads(payload)["name"], "</script><script>alert(1)</script>")


if __name__ == "__main__":
    unittest.main()
