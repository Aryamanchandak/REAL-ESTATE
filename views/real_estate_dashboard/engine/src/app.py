"""
app.py — ICICI Prudential Real Estate Dashboard
================================================
Run:  streamlit run src/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── local imports ──────────────────────────────────────────────────────────────
from theme import (
    ORANGE, DARK_ORANGE, LIGHT_ORANGE, NAVY, DARK_NAVY, MID_NAVY,
    WHITE, OFF_WHITE, LIGHT_GREY, MID_GREY, DARK_GREY, CHARCOAL,
    GREEN_OK, GREEN_BG, AMBER_DUE, AMBER_BG, RED_PROGRESS, RED_BG,
    GREY_BG, GREY_NOTDUE, PURPLE_NA, PURPLE_BG,
    CHART_COLORS, INDUSTRY_COLORS, PLOTLY_LAYOUT, STATUS_STYLES,
    status_badge_html,
)
from sample_data import (
    ASSETS, MONTHS,
    df_investment_kpis, df_investment_summary, df_rent_spread,
    df_area_summary, df_revenue_composition,
    df_exec_kpis, df_exec_top5_tenants, df_exec_rental_psf, df_exec_rent_trend,
    df_tenant_top5, df_tenant_lease_expiry,
    df_stack_plan,
    df_expense_vs_collection, df_rent_billed_trend,
    df_approvals,
    df_compliance,
    df_financial_kpis, df_financial_cashflow, df_financial_sources,
    df_financial_usage, df_financial_collections_trend,
)

# ── page config — MUST be first ───────────────────────────────────────────────
st.set_page_config(
    page_title="ICICI Pru Real Estate Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Google Fonts + global CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mulish:wght@600&display=swap');

/* ── Reset / Global ── */
*, *::before, *::after { box-sizing: border-box; }
/* Mulish SemiBold (600) is the only face loaded — no synthesised bolds. */
* { font-synthesis-weight: none; font-synthesis: none; }
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #FCFCFA !important;
    font-family: 'Mulish', sans-serif !important;
    color: #1B2A3D;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Mulish', sans-serif !important;
    font-weight: 600 !important;
    color: #133359 !important;
    letter-spacing: -0.01em;
}
p, span, div, label, td, th {
    font-family: 'Mulish', sans-serif !important;
}
/* Streamlit's Material icons are ligature spans — the rule above would catch
   them and print the literal glyph name. Give them their own font back. */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
span[class*="material-symbols"],
span[class*="material-icons"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    font-weight: 400 !important;
}

/* ── Top header bar ── */
.dash-header {
    background: linear-gradient(135deg, #133359 0%, #2A4C74 100%);
    padding: 18px 32px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.dash-header-title {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 22px;
    color: #FFFFFF;
    letter-spacing: -0.01em;
}
.dash-header-sub {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 13px;
    color: rgba(255,255,255,0.65);
    margin-top: 2px;
}
.dash-header-badge {
    background: #DC6009;
    color: #fff;
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 12px;
    padding: 4px 14px;
    border-radius: 20px;
}

/* ── Tab bar ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 4px 6px;
    gap: 2px;
    border: 1px solid #E0E6EE;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Mulish', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #75838E !important;
    padding: 8px 18px !important;
    border-radius: 7px !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.18s ease;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #DC6009 !important;
    color: #FFFFFF !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

/* ── KPI Cards ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E0E6EE;
    border-radius: 12px;
    padding: 18px 20px;
    min-height: 90px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: #DC6009;
    border-radius: 12px 0 0 12px;
}
.kpi-label {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 11px;
    color: #BDC4C9;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 26px;
    color: #133359;
    line-height: 1.1;
}
.kpi-sub {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 11px;
    color: #75838E;
    margin-top: 4px;
}

/* ── Section cards ── */
.section-card {
    background: #FFFFFF;
    border: 1px solid #E0E6EE;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 16px;
}
.section-title {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 14px;
    color: #133359;
    margin-bottom: 14px;
    letter-spacing: -0.01em;
}

/* ── Status chip row ── */
.chip-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
.chip {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 12px;
    padding: 5px 14px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.chip-count {
    background: rgba(255,255,255,0.35);
    border-radius: 10px;
    padding: 1px 7px;
    font-size: 11px;
    font-weight: 600;
}

/* ── Table styling ── */
.dash-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Mulish', sans-serif;
    font-size: 13px;
}
.dash-table th {
    background: #133359;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 10px 14px;
    text-align: left;
    white-space: nowrap;
}
.dash-table td {
    padding: 9px 14px;
    color: #1B2A3D;
    font-weight: 600;
    border-bottom: 1px solid #E0E6EE;
    vertical-align: middle;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: #FCFCFA; }
.dash-table tr.total-row td {
    background: #F1F4F8;
    font-weight: 600;
    color: #133359;
}

/* ── Flow bar (Financial) ── */
.flow-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #FFFFFF;
    border: 1px solid #E0E6EE;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.flow-item { text-align: center; min-width: 100px; }
.flow-item-label {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 11px;
    color: #BDC4C9;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.flow-item-value {
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 22px;
    color: #133359;
}
.flow-op {
    font-size: 26px;
    font-weight: 600;
    color: #BDC4C9;
}

/* ── WALE badge ── */
.wale-badge {
    background: linear-gradient(135deg, #FFF1E5, #FED9B7);
    border: 1px solid #DC6009;
    border-radius: 8px;
    padding: 10px 16px;
    font-family: 'Mulish', sans-serif;
    font-weight: 600;
    font-size: 13px;
    color: #C55608;
    display: inline-block;
}

/* ── Plotly chart containers ── */
[data-testid="stPlotlyChart"] { border-radius: 10px; overflow: hidden; }

/* ── Metric overrides ── */
[data-testid="metric-container"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="metric-container"] label {
    font-family: 'Mulish', sans-serif !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    color: #BDC4C9 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    font-family: 'Mulish', sans-serif !important;
    font-weight: 600 !important;
    color: #133359 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {
    font-family: 'Mulish', sans-serif !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    color: #75838E !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #E0E6EE; margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = "All"
if "selected_month" not in st.session_state:
    st.session_state.selected_month = "Jan-24"


# ══════════════════════════════════════════════════════════════════════════════
# HELPER UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def kpi_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {sub_html}
    </div>"""


def section_card_open(title: str = "") -> str:
    title_html = f'<div class="section-title">{title}</div>' if title else ""
    return f'<div class="section-card">{title_html}'


def section_card_close() -> str:
    return "</div>"


def chip_row_html(chips: list[dict]) -> str:
    """chips: [{"label":"In Progress","count":1,"bg":"#FCEAE8","color":"#C8190A"}]"""
    items = ""
    for c in chips:
        count = f'<span class="chip-count">{c["count"]}</span>' if "count" in c else ""
        items += (
            f'<span class="chip" style="background:{c["bg"]};color:{c["color"]};'
            f'border:1px solid {c["color"]};">'
            f'{c["label"]}{count}</span>'
        )
    return f'<div class="chip-row">{items}</div>'


def apply_plotly_theme(fig: go.Figure, title: str = "") -> go.Figure:
    layout = dict(PLOTLY_LAYOUT)
    if title:
        layout["title"] = dict(text=title, font=dict(
            family="Mulish, sans-serif", size=13, color=NAVY), x=0, xanchor="left")
    fig.update_layout(**layout)
    return fig


def render_status_table(df: pd.DataFrame, status_col: str, columns: list[str], col_labels: list[str]):
    """Render a HTML table with coloured status badges."""
    thead = "".join(f"<th>{l}</th>" for l in col_labels)
    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for col in columns:
            if col == status_col:
                cells += f"<td>{status_badge_html(row[col])}</td>"
            else:
                cells += f"<td>{row[col]}</td>"
        rows += f"<tr>{cells}</tr>"
    html = f"""
    <div style="overflow-x:auto;">
    <table class="dash-table">
      <thead><tr>{thead}</tr></thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="dash-header">
  <div>
    <div class="dash-header-title">🏢 Real Estate Asset Dashboard</div>
    <div class="dash-header-sub">ICICI Prudential Asset Management · Commercial Portfolio</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Global filters row
f1, f2, f3 = st.columns([1, 1, 6])
with f1:
    selected_asset = st.selectbox("Asset", ASSETS, key="asset_filter")
with f2:
    selected_month = st.selectbox("Month", MONTHS, index=len(MONTHS)-1, key="month_filter")


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

(tab_inv, tab_exec, tab_tenant, tab_stack,
 tab_exp, tab_approvals, tab_compliance, tab_fin) = st.tabs([
    "📊 Investment Summary",
    "📋 Executive Summary",
    "👥 Tenant Profile",
    "🏗️ Stacking Plan",
    "💰 Expense vs Collection",
    "✅ Approvals",
    "📑 Compliance Register",
    "🏦 Financial Summary",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — INVESTMENT SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

with tab_inv:
    kpis = df_investment_kpis.iloc[0]

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, sub in [
        (c1, "Monthly Rental",    f"₹{kpis['monthly_rental_amount_cr']} Cr", ""),
        (c2, "CAM Charges",       f"₹{kpis['cam_charges_psf']}/sf",          "Per sq ft"),
        (c3, "Occupancy",         f"{kpis['occupied_pct']}%",                "Overall Portfolio"),
        (c4, "Gross Billing",     f"₹{kpis['gross_billing_cr']} Cr",         "Incl. Taxes"),
        (c5, "Collections",       f"₹{kpis['collections_cr']} Cr",           "Incl. Taxes"),
    ]:
        with col:
            st.markdown(kpi_card(label, val, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Investment summary table
    st.markdown('<div class="section-card"><div class="section-title">Investment Summary — Asset Breakdown</div>', unsafe_allow_html=True)
    tbl = df_investment_summary.copy()
    thead = "<tr>" + "".join(f"<th>{h}</th>" for h in [
        "Asset", "Leasable Area (Msft)", "Leased Area (Msft)",
        "Vacant Area (Msft)", "Occupancy %", "Monthly Rent (Cr)"]) + "</tr>"
    rows = ""
    for _, row in tbl.iterrows():
        tr_class = ' class="total-row"' if row["asset"] == "Total" else ""
        rows += (
            f"<tr{tr_class}>"
            f"<td><b>{row['asset']}</b></td>"
            f"<td>{row['leasable_area_msft']:.2f}</td>"
            f"<td>{row['leased_area_msft']:.2f}</td>"
            f"<td>{row['vacant_area_msft']:.2f}</td>"
            f"<td>{row['occupancy_pct']:.1f}%</td>"
            f"<td>₹{row['monthly_rent_cr']:.1f}</td>"
            "</tr>"
        )
    st.markdown(f'<div style="overflow-x:auto;"><table class="dash-table"><thead>{thead}</thead><tbody>{rows}</tbody></table></div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_mid, col_right = st.columns([1, 1, 1])

    # Rent spread bar
    with col_left:
        st.markdown('<div class="section-card"><div class="section-title">Rent Spread Rate PSF Area</div>', unsafe_allow_html=True)
        if not df_rent_spread.empty:
            fig = px.bar(df_rent_spread, y="band", x="area_msft", orientation="h",
                         color_discrete_sequence=[ORANGE])
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "xaxis_title": "Area (Msft)", "yaxis_title": "",
                "margin": dict(l=0, r=0, t=8, b=0), "height": 220})
            fig.update_traces(marker_cornerradius=3)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Area summary bars
    with col_mid:
        st.markdown('<div class="section-card"><div class="section-title">Area Summary</div>', unsafe_allow_html=True)
        if not df_area_summary.empty:
            colors = [NAVY, ORANGE, LIGHT_GREY]
            fig = px.bar(df_area_summary, y="category", x="area_msft", orientation="h",
                         color="category",
                         color_discrete_map={
                             "Leasable Area": NAVY,
                             "Leased Area": ORANGE,
                             "Vacant Area": "#BDC4C9"})
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "showlegend": False, "xaxis_title": "Area (Msft)", "yaxis_title": "",
                "margin": dict(l=0, r=0, t=8, b=0), "height": 220})
            fig.update_traces(marker_cornerradius=3)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Revenue composition donut
    with col_right:
        st.markdown('<div class="section-card"><div class="section-title">Revenue Composition (Excl. Taxes)</div>', unsafe_allow_html=True)
        if not df_revenue_composition.empty:
            fig = px.pie(df_revenue_composition, names="component", values="amount_cr",
                         color_discrete_sequence=CHART_COLORS, hole=0.55)
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "margin": dict(l=0, r=0, t=8, b=0), "height": 220,
                "legend": dict(orientation="v", font=dict(size=11))})
            fig.update_traces(textinfo="percent", textfont_size=11)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

with tab_exec:
    ex = df_exec_kpis.iloc[0]

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, sub in [
        (c1, "WALE",             f"{ex['wale_yrs']} Yrs",           "Weighted Avg. Lease Expiry"),
        (c2, "Rent to be Billed",f"₹{ex['rent_to_be_billed_cr']} Cr","Without Tax"),
        (c3, "Actual Billed",    f"₹{ex['actual_billed_cr']} Cr",   "Without Tax"),
        (c4, "Gross Billing",    f"₹{ex['gross_billing_cr']} Cr",    "Incl. Tax"),
        (c5, "Collections",      f"₹{ex['collections_cr']} Cr",     "Incl. Tax"),
    ]:
        with col:
            st.markdown(kpi_card(label, val, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Area donut + top-5 + PSF chart
    col_a, col_b, col_c = st.columns([1, 1.2, 1.5])

    # Status-wise area donut
    with col_a:
        st.markdown('<div class="section-card"><div class="section-title">Status-wise Area</div>', unsafe_allow_html=True)
        area_data = pd.DataFrame([
            {"status": "Leased", "area_msft": ex["leased_area_msft"]},
            {"status": "Vacant", "area_msft": ex["vacant_area_msft"]},
        ])
        fig = px.pie(area_data, names="status", values="area_msft",
                     color_discrete_map={"Leased": NAVY, "Vacant": "#E8EAED"}, hole=0.6)
        fig.update_layout(**{**PLOTLY_LAYOUT,
            "margin": dict(l=0, r=0, t=8, b=0), "height": 200,
            "annotations": [dict(text=f"{ex['total_area_msft']}M<br>Total", x=0.5, y=0.5,
                                 showarrow=False, font=dict(size=13, color=NAVY, family="Mulish"),
                                 xref="paper", yref="paper")]})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Top 5 tenants
    with col_b:
        st.markdown('<div class="section-card"><div class="section-title">Top 5 Tenants by Monthly Rent</div>', unsafe_allow_html=True)
        if not df_exec_top5_tenants.empty:
            fig = px.bar(df_exec_top5_tenants.sort_values("monthly_rent_cr"),
                         y="tenant", x="monthly_rent_cr", orientation="h",
                         color_discrete_sequence=[ORANGE],
                         text="monthly_rent_cr")
            fig.update_traces(texttemplate="₹%{text:.1f}Cr", textposition="outside",
                              marker_cornerradius=3)
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "xaxis_title": "₹ Cr", "yaxis_title": "",
                "margin": dict(l=0, r=40, t=8, b=0), "height": 200})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Current & future rental PSF
    with col_c:
        st.markdown('<div class="section-card"><div class="section-title">Current & Future Avg Rental PSF</div>', unsafe_allow_html=True)
        if not df_exec_rental_psf.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_exec_rental_psf["period"], y=df_exec_rental_psf["rent_to_be_billed_psf"],
                name="Rent to be Billed", line=dict(color=ORANGE, width=2.5),
                fill="tonexty", fillcolor="rgba(242,101,34,0.08)"))
            fig.add_trace(go.Scatter(
                x=df_exec_rental_psf["period"], y=df_exec_rental_psf["actual_billed_psf"],
                name="Actual Billed", line=dict(color=NAVY, width=2.5, dash="dot")))
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "yaxis_title": "₹/sf", "height": 200,
                "margin": dict(l=0, r=0, t=8, b=0)})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 6-month trend bar
    st.markdown('<div class="section-card"><div class="section-title">Rent to be Billed vs Actual Billed — 6 Month Trend (₹ Cr, Without Tax)</div>', unsafe_allow_html=True)
    if not df_exec_rent_trend.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_exec_rent_trend["month"], y=df_exec_rent_trend["rent_to_be_billed_cr"],
                             name="Rent to be Billed", marker_color=NAVY, marker_cornerradius=4))
        fig.add_trace(go.Bar(x=df_exec_rent_trend["month"], y=df_exec_rent_trend["actual_billed_cr"],
                             name="Actual Billed", marker_color=ORANGE, marker_cornerradius=4))
        fig.update_layout(**{**PLOTLY_LAYOUT, "barmode": "group", "height": 240,
            "yaxis_title": "₹ Cr", "margin": dict(l=0, r=0, t=8, b=0)})
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TENANT PROFILE
# ══════════════════════════════════════════════════════════════════════════════

with tab_tenant:
    toggle_col, _ = st.columns([1, 4])
    with toggle_col:
        metric_toggle = st.radio("View by", ["Monthly Rent", "Revenue PSF"],
                                 horizontal=True, label_visibility="collapsed")

    col_l, col_r = st.columns([1, 1.6])

    with col_l:
        st.markdown('<div class="section-card"><div class="section-title">Top 5 Tenants</div>', unsafe_allow_html=True)
        if not df_tenant_top5.empty:
            y_col = "monthly_rent_cr" if metric_toggle == "Monthly Rent" else "revenue_psf"
            label = "₹ Cr" if metric_toggle == "Monthly Rent" else "₹/sf"
            fig = px.bar(df_tenant_top5.sort_values(y_col),
                         y="tenant", x=y_col, orientation="h",
                         color_discrete_sequence=[ORANGE], text=y_col)
            prefix = "₹" if metric_toggle == "Monthly Rent" else "₹"
            suffix = " Cr" if metric_toggle == "Monthly Rent" else "/sf"
            fig.update_traces(texttemplate=f"{prefix}%{{text:.1f}}{suffix}",
                              textposition="outside", marker_cornerradius=3)
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "xaxis_title": label, "yaxis_title": "",
                "margin": dict(l=0, r=50, t=8, b=0), "height": 260})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-card"><div class="section-title">Upcoming Lease Expiry (by Quarter)</div>', unsafe_allow_html=True)
        if not df_tenant_lease_expiry.empty:
            fig = px.bar(df_tenant_lease_expiry, x="quarter", y="area_sft",
                         color="tenant_group",
                         color_discrete_sequence=CHART_COLORS,
                         text="area_sft")
            fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                              marker_cornerradius=3)
            fig.update_layout(**{**PLOTLY_LAYOUT,
                "xaxis_title": "Lease Expiry Quarter", "yaxis_title": "Area (sft)",
                "barmode": "group", "height": 280,
                "margin": dict(l=0, r=0, t=8, b=0)})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — STACKING PLAN
# ══════════════════════════════════════════════════════════════════════════════

with tab_stack:
    st.markdown('<div class="section-card"><div class="section-title">Stack Plan — Floor by Floor</div>', unsafe_allow_html=True)

    if not df_stack_plan.empty:
        floors = sorted(df_stack_plan["floor"].unique(), reverse=True)
        fig = go.Figure()

        for industry, color in INDUSTRY_COLORS.items():
            ind_df = df_stack_plan[df_stack_plan["industry"] == industry]
            for floor in floors:
                floor_ind = ind_df[ind_df["floor"] == floor]
                for _, row in floor_ind.iterrows():
                    fig.add_trace(go.Bar(
                        y=[f"Floor {row['floor']}"],
                        x=[row["area_ksft"]],
                        orientation="h",
                        name=industry,
                        marker_color=color,
                        marker_line_color=WHITE,
                        marker_line_width=1.5,
                        text=f"{row['tenant']}<br>{row['area_ksft']}K",
                        textposition="inside",
                        insidetextanchor="middle",
                        textfont=dict(size=10, color=WHITE if industry != "Vacant" else DARK_GREY,
                                      family="Mulish"),
                        hovertemplate=(f"<b>{row['tenant']}</b><br>"
                                       f"Floor {row['floor']}<br>"
                                       f"Area: {row['area_ksft']}K sft<br>"
                                       f"Industry: {industry}<extra></extra>"),
                        showlegend=False,
                        legendgroup=industry,
                    ))

        # Legend entries (one per industry)
        for industry, color in INDUSTRY_COLORS.items():
            fig.add_trace(go.Bar(
                y=[None], x=[None], orientation="h",
                name=industry,
                marker_color=color,
                showlegend=True,
                legendgroup=industry,
            ))

        fig.update_layout(**{**PLOTLY_LAYOUT,
            "barmode": "stack",
            "height": 380,
            "xaxis_title": "Area (K sft)",
            "yaxis_title": "",
            "xaxis": dict(gridcolor=LIGHT_GREY),
            "yaxis": dict(categoryorder="array",
                          categoryarray=[f"Floor {f}" for f in sorted(floors)]),
            "legend": dict(orientation="h", yanchor="bottom", y=-0.22,
                           xanchor="left", x=0,
                           font=dict(size=12, family="Mulish")),
            "margin": dict(l=0, r=0, t=8, b=60),
        })
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — EXPENSE VS COLLECTION
# ══════════════════════════════════════════════════════════════════════════════

with tab_exp:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-card"><div class="section-title">Expense vs Collection (₹ Cr)</div>', unsafe_allow_html=True)
        if not df_expense_vs_collection.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_expense_vs_collection["month"],
                                 y=df_expense_vs_collection["collections_cr"],
                                 name="Collections", marker_color=ORANGE, marker_cornerradius=3))
            fig.add_trace(go.Bar(x=df_expense_vs_collection["month"],
                                 y=df_expense_vs_collection["expense_cam_cr"],
                                 name="Expense (CAM)", marker_color="#BDC4C9", marker_cornerradius=3))
            fig.add_trace(go.Bar(x=df_expense_vs_collection["month"],
                                 y=df_expense_vs_collection["expense_debt_cr"],
                                 name="Expense (Debt)", marker_color=NAVY, marker_cornerradius=3))
            fig.add_trace(go.Bar(x=df_expense_vs_collection["month"],
                                 y=df_expense_vs_collection["expense_opex_cr"],
                                 name="Expense (OPEX)", marker_color="#FFA217", marker_cornerradius=3))
            fig.update_layout(**{**PLOTLY_LAYOUT, "barmode": "group",
                "yaxis_title": "₹ Cr", "height": 300,
                "margin": dict(l=0, r=0, t=8, b=0)})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-card"><div class="section-title">Rent to be Billed vs Actual Billed (₹ Cr, Without Tax)</div>', unsafe_allow_html=True)
        if not df_rent_billed_trend.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_rent_billed_trend["month"],
                                 y=df_rent_billed_trend["rent_to_be_billed_cr"],
                                 name="Rent to be Billed", marker_color=NAVY, marker_cornerradius=3))
            fig.add_trace(go.Bar(x=df_rent_billed_trend["month"],
                                 y=df_rent_billed_trend["actual_billed_cr"],
                                 name="Actual Billed", marker_color=ORANGE, marker_cornerradius=3))
            fig.update_layout(**{**PLOTLY_LAYOUT, "barmode": "group",
                "yaxis_title": "₹ Cr", "height": 300,
                "margin": dict(l=0, r=0, t=8, b=0)})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — APPROVALS
# ══════════════════════════════════════════════════════════════════════════════

with tab_approvals:
    complied_count  = int((df_approvals["status"] == "Complied").sum())
    revision_count  = int((df_approvals["status"] == "Revision Required").sum())

    st.markdown(chip_row_html([
        {"label": "Complied",          "count": complied_count,
         "bg": GREEN_BG,  "color": GREEN_OK},
        {"label": "Revision Required", "count": revision_count,
         "bg": AMBER_BG, "color": DARK_ORANGE},
    ]), unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    render_status_table(
        df_approvals, "status",
        ["description", "issuing_authority", "issue_date", "validity",
         "expected_timelines", "associated_risk", "status"],
        ["Approval Description", "Issuing Authority", "Issue Date", "Validity",
         "Expected Timelines", "Associated Risk", "Status"],
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — COMPLIANCE REGISTER
# ══════════════════════════════════════════════════════════════════════════════

with tab_compliance:
    in_progress_count = int((df_compliance["rag_status"] == "In Progress").sum())
    due_soon_count    = int((df_compliance["rag_status"] == "Due Soon").sum())
    ok_count          = int((df_compliance["rag_status"] == "OK").sum())

    st.markdown(chip_row_html([
        {"label": "In Progress", "count": in_progress_count,
         "bg": RED_BG,    "color": RED_PROGRESS},
        {"label": "Due Soon",    "count": due_soon_count,
         "bg": AMBER_BG,  "color": DARK_ORANGE},
        {"label": "OK",          "count": ok_count,
         "bg": GREEN_BG,  "color": GREEN_OK},
    ]), unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    render_status_table(
        df_compliance, "rag_status",
        ["item", "category", "frequency", "due_date", "filed_done",
         "responsible", "consequence", "rag_status"],
        ["Compliance Item", "Category", "Frequency", "Due Date", "Filed / Done",
         "Responsible", "Consequence of Non-Compliance", "RAG Status"],
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — FINANCIAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

with tab_fin:
    fin = df_financial_kpis.iloc[0]

    # Cash flow bridge bar
    st.markdown(f"""
    <div class="flow-bar">
      <div class="flow-item">
        <div class="flow-item-label">Opening Balance</div>
        <div class="flow-item-value" style="color:{NAVY};">₹{fin['opening_balance_cr']} Cr</div>
      </div>
      <div class="flow-op" style="color:{GREEN_OK};">+</div>
      <div class="flow-item">
        <div class="flow-item-label">Total Inflow</div>
        <div class="flow-item-value" style="color:{GREEN_OK};">₹{fin['total_inflow_cr']} Cr</div>
      </div>
      <div class="flow-op" style="color:{RED_PROGRESS};">−</div>
      <div class="flow-item">
        <div class="flow-item-label">Total Outflow</div>
        <div class="flow-item-value" style="color:{RED_PROGRESS};">₹{fin['total_outflow_cr']} Cr</div>
      </div>
      <div class="flow-op">=</div>
      <div class="flow-item">
        <div class="flow-item-label">Closing Balance</div>
        <div class="flow-item-value" style="color:{ORANGE};">₹{fin['closing_balance_cr']} Cr</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.8, 1])

    # Cashflow table
    with col_l:
        st.markdown('<div class="section-card"><div class="section-title">Cash Flow Details — By Bank Account</div>', unsafe_allow_html=True)
        if not df_financial_cashflow.empty:
            bank_cols = [c for c in df_financial_cashflow.columns if c.startswith("PNB")]
            headers = ["Tag"] + bank_cols + ["Grand Total"]
            thead = "".join(f"<th>{h}</th>" for h in headers)
            rows_html = ""
            for _, row in df_financial_cashflow.iterrows():
                tr_class = ' class="total-row"' if row["tag"] in ("Opening Balance", "Closing Balance") else ""
                cells = f"<td><b>{row['tag']}</b></td>"
                for bc in bank_cols:
                    val = row[bc]
                    color = RED_PROGRESS if val < 0 else (GREEN_OK if val > 0 else GREY_NOTDUE)
                    cells += f'<td style="color:{color};font-weight: 600;">₹{val:.1f}</td>'
                gt = row["grand_total"]
                gt_color = RED_PROGRESS if gt < 0 else (GREEN_OK if gt > 0 else GREY_NOTDUE)
                cells += f'<td style="color:{gt_color};font-weight: 600;">₹{gt:.1f}</td>'
                rows_html += f"<tr{tr_class}>{cells}</tr>"
            st.markdown(
                f'<div style="overflow-x:auto;">'
                f'<table class="dash-table"><thead><tr>{thead}</tr></thead><tbody>{rows_html}</tbody></table>'
                f'</div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Sources & usage
    with col_r:
        st.markdown('<div class="section-card"><div class="section-title">Sources & Usage Summary</div>', unsafe_allow_html=True)

        if not df_financial_sources.empty:
            st.markdown(f'<div style="font-family:Mulish;font-weight: 600;font-size:12px;color:{NAVY};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">Sources of Funds</div>', unsafe_allow_html=True)
            for _, row in df_financial_sources.iterrows():
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:6px 0;border-bottom:1px solid {LIGHT_GREY};'
                    f'font-family:Mulish;font-size:13px;font-weight:600;">'
                    f'<span style="color:{CHARCOAL};">{row["source"]}</span>'
                    f'<span style="color:{GREEN_OK};font-weight: 600;">₹{row["amount_cr"]:.1f} Cr</span>'
                    f'</div>',
                    unsafe_allow_html=True)
            total_sources = df_financial_sources["amount_cr"].sum()
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
                f'font-family:Mulish;font-size:13px;font-weight: 600;color:{NAVY};">'
                f'<span>Grand Total</span><span>₹{total_sources:.1f} Cr</span></div>',
                unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        if not df_financial_usage.empty:
            st.markdown(f'<div style="font-family:Mulish;font-weight: 600;font-size:12px;color:{NAVY};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">Usage of Funds</div>', unsafe_allow_html=True)
            for _, row in df_financial_usage.iterrows():
                val = row["amount_cr"]
                color = RED_PROGRESS if val > 0 else GREY_NOTDUE
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:6px 0;border-bottom:1px solid {LIGHT_GREY};'
                    f'font-family:Mulish;font-size:13px;font-weight:600;">'
                    f'<span style="color:{CHARCOAL};">{row["usage"]}</span>'
                    f'<span style="color:{color};font-weight: 600;">−₹{val:.1f} Cr</span>'
                    f'</div>',
                    unsafe_allow_html=True)
            total_usage = df_financial_usage["amount_cr"].sum()
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
                f'font-family:Mulish;font-size:13px;font-weight: 600;color:{RED_PROGRESS};">'
                f'<span>Grand Total</span><span>−₹{total_usage:.1f} Cr</span></div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Business plan vs actual
    st.markdown('<div class="section-card"><div class="section-title">Business Plan vs Actual Collections (₹ Cr)</div>', unsafe_allow_html=True)
    if not df_financial_collections_trend.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_financial_collections_trend["month"],
            y=df_financial_collections_trend["actual_cr"],
            name="Actual", line=dict(color=ORANGE, width=2.5),
            mode="lines+markers", marker=dict(size=6, color=ORANGE)))
        fig.add_trace(go.Scatter(
            x=df_financial_collections_trend["month"],
            y=df_financial_collections_trend["planned_cr"],
            name="Planned", line=dict(color=NAVY, width=2.5, dash="dash"),
            mode="lines+markers", marker=dict(size=6, color=NAVY)))
        fig.update_layout(**{**PLOTLY_LAYOUT,
            "yaxis_title": "₹ Cr", "height": 280,
            "margin": dict(l=0, r=0, t=8, b=0)})
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
