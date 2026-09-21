"""
Upload the fund workbook, press Build, download the dashboard HTML.

Run:  streamlit run app.py

Colours and typography come from engine/src/theme.py (brand-sourced) and
.streamlit/config.toml (Streamlit's own chrome). Nothing is hardcoded twice.
"""

import sys
import tempfile
from pathlib import Path

import streamlit as st

ENGINE = Path(__file__).resolve().parent / "engine"
sys.path.insert(0, str(ENGINE / "src"))

from build_dashboard import build  # noqa: E402
from theme import (  # noqa: E402
    AMBER_BG, AMBER_DUE, CHARCOAL, DARK_GREY, DARK_NAVY, DARK_ORANGE,
    FONT_FAMILY, FONT_IMPORT, FONT_WEIGHT, GREEN_OK, LIGHT_GREY, LIGHT_ORANGE,
    MID_NAVY, NAVY, OFF_WHITE, ORANGE, WHITE,
)

st.set_page_config(
    page_title="Real Estate Dashboard Builder",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state — initialised unconditionally, before anything reads it ────
for key, default in (
    ("html", None),          # bytes of the built dashboard
    ("label", None),         # report month label
    ("as_of", None),         # as-of date from the workbook
    ("fund", None),          # fund name
    ("assets", 0),           # asset count
    ("warnings", []),        # data-quality warnings
    ("source", None),        # filename the result was built from
    ("signature", None),     # (name, size) the result was built from
):
    st.session_state.setdefault(key, default)


# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('{FONT_IMPORT}');

/* Mulish SemiBold is the only face we load. Pin every weight to it and turn
   off synthesis so Streamlit's own 700-weight rules can't fake a bolder cut. */
html, body, [class*="st-"], .stApp, .stApp *,
h1, h2, h3, h4, h5, h6, p, span, div, label, td, th, button, input, strong, b {{
    font-family: {FONT_FAMILY} !important;
    font-weight: {FONT_WEIGHT} !important;
    font-synthesis-weight: none;
    font-synthesis: none;
}}

/* Streamlit draws the upload cloud, expander chevron and download glyph as
   ligature spans in a Material icon font. The blanket rule above would catch
   them and render the literal words "cloud_upload" / "keyboard_arrow_down",
   so hand those elements their own font back. Glyphs aren't typography. */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
span[class*="material-symbols"],
span[class*="material-icons"] {{
    font-family: "Material Symbols Rounded", "Material Icons" !important;
    font-weight: 400 !important;
    font-synthesis: none;
}}

.stApp {{ background: {OFF_WHITE}; }}
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 780px; }}

h1, h2, h3 {{ color: {NAVY} !important; letter-spacing: -0.015em; }}

/* ── Masthead ── */
.masthead {{
    background: linear-gradient(135deg, {DARK_NAVY} 0%, {NAVY} 55%, {MID_NAVY} 100%);
    border-radius: 14px;
    padding: 26px 30px 24px;
    margin-bottom: 26px;
    position: relative;
    overflow: hidden;
    animation: rise .38s ease-out both;
}}
.masthead::after {{
    content: "";
    position: absolute; left: 0; right: 0; bottom: 0; height: 4px;
    background: linear-gradient(90deg, {ORANGE} 0%, {AMBER_DUE} 100%);
}}
.masthead-eyebrow {{
    color: {LIGHT_ORANGE};
    font-size: 11px;
    letter-spacing: .16em;
    text-transform: uppercase;
    opacity: .85;
    margin-bottom: 9px;
}}
.masthead-title {{
    color: {WHITE};
    font-size: 27px;
    line-height: 1.18;
    letter-spacing: -0.02em;
    margin: 0 0 8px;
}}
.masthead-sub {{ color: #B9C6D8; font-size: 13.5px; line-height: 1.55; margin: 0; }}

/* ── Step labels ── */
.step {{
    display: flex; align-items: center; gap: 10px;
    margin: 26px 0 10px;
    color: {NAVY}; font-size: 15px;
}}
.step-num {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 23px; height: 23px; border-radius: 50%;
    background: {LIGHT_ORANGE}; color: {DARK_ORANGE};
    font-size: 12px; flex: 0 0 auto;
}}
.step-hint {{
    color: {DARK_GREY}; font-size: 12.5px;
    margin: -4px 0 10px 33px; line-height: 1.5;
}}

/* ── Result card ── */
.result {{
    background: {WHITE};
    border: 1px solid {LIGHT_GREY};
    border-left: 4px solid {GREEN_OK};
    border-radius: 12px;
    padding: 18px 22px;
    margin: 6px 0 18px;
    animation: rise .32s ease-out both;
}}
.result-head {{ color: {GREEN_OK}; font-size: 13px; letter-spacing: .04em;
                text-transform: uppercase; margin-bottom: 12px; }}
.result-grid {{ display: flex; flex-wrap: wrap; gap: 10px 34px; }}
.result-k {{ color: {DARK_GREY}; font-size: 10.5px; letter-spacing: .12em;
             text-transform: uppercase; margin-bottom: 3px; }}
.result-v {{ color: {CHARCOAL}; font-size: 17px; letter-spacing: -0.01em; }}

/* ── Stale-result notice ── */
.stale {{
    background: {AMBER_BG};
    border: 1px solid {AMBER_DUE};
    border-radius: 10px;
    padding: 11px 15px;
    margin-bottom: 14px;
    color: {DARK_ORANGE};
    font-size: 13px; line-height: 1.5;
}}

/* ── Buttons ── */
.stButton > button, .stDownloadButton > button {{
    transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}}
.stButton > button[kind="primary"] {{
    background: {ORANGE}; border-color: {ORANGE}; color: {WHITE};
    box-shadow: 0 1px 2px rgba(19,51,89,.14);
}}
.stButton > button[kind="primary"]:hover:not(:disabled) {{
    background: {DARK_ORANGE}; border-color: {DARK_ORANGE};
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(220,96,9,.28);
}}
.stDownloadButton > button:hover {{
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(19,51,89,.16);
}}

/* ── Dropzone ── */
[data-testid="stFileUploaderDropzone"] {{
    background: {WHITE};
    border: 1.5px dashed {LIGHT_GREY};
    transition: border-color .18s ease, background .18s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {ORANGE}; background: #FFFCF9;
}}

/* ── Footer ── */
.foot {{
    margin-top: 38px; padding-top: 14px;
    border-top: 1px solid {LIGHT_GREY};
    color: {DARK_GREY}; font-size: 11.5px; line-height: 1.6;
}}

@keyframes rise {{
    from {{ opacity: 0; transform: translateY(7px); }}
    to   {{ opacity: 1; transform: none; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="masthead">
  <div class="masthead-eyebrow">ICICI Prudential · Real Estate</div>
  <div class="masthead-title">Fund Dashboard Builder</div>
  <p class="masthead-sub">Upload the monthly fund workbook and get back a single,
  self-contained dashboard file you can email or open offline.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Step 1 — upload ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="step"><span class="step-num">1</span>Choose the fund workbook</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="step-hint">The 9-asset .xlsx — the reader expects the '
    '<code>1_ASSET_MASTER</code> / <code>2_MONTHLY_INPUT</code> sheet layout.</div>',
    unsafe_allow_html=True,
)
uploaded = st.file_uploader("Excel workbook", type=["xlsx"], label_visibility="collapsed")

signature = (uploaded.name, uploaded.size) if uploaded is not None else None

# A result on screen must always match the workbook currently in the uploader —
# otherwise the download button quietly hands over the *previous* file. Only
# warn while a file is actually loaded: with the uploader cleared, Build is
# disabled and telling someone to press it would be a dead end.
stale = (
    st.session_state["html"] is not None
    and uploaded is not None
    and signature != st.session_state["signature"]
)

# ── Step 2 — build ───────────────────────────────────────────────────────────
st.markdown(
    '<div class="step"><span class="step-num">2</span>Build the dashboard</div>',
    unsafe_allow_html=True,
)

run = st.button(
    "Build dashboard",
    type="primary",
    disabled=uploaded is None,
    use_container_width=True,
)

if uploaded is None:
    st.markdown(
        '<div class="step-hint">Waiting for a workbook.</div>',
        unsafe_allow_html=True,
    )

if run and uploaded is not None:
    with st.spinner("Reading the workbook and building the dashboard…"):
        with tempfile.TemporaryDirectory() as tmp:
            excel_path = Path(tmp) / "input.xlsx"
            output_path = Path(tmp) / "dashboard.html"
            excel_path.write_bytes(uploaded.getvalue())
            try:
                data = build(
                    excel_path,
                    ENGINE / "templates" / "dashboard.template.html",
                    output_path,
                )
            except Exception as exc:
                # Drop any earlier result so a failure can't leave a stale
                # download button sitting underneath the error.
                st.session_state.update(
                    html=None, label=None, as_of=None, fund=None,
                    assets=0, warnings=[], source=None, signature=None,
                )
                st.error(f"Could not build the dashboard: {exc}")
                st.stop()

            st.session_state.update(
                html=output_path.read_bytes(),
                label=data["meta"]["reportMonthLabel"],
                as_of=data["meta"].get("asOf"),
                fund=data["meta"].get("fund"),
                assets=len(data.get("assets", [])),
                warnings=data["dataQuality"]["warnings"],
                source=uploaded.name,
                signature=signature,
            )
    stale = False

# ── Step 3 — result ──────────────────────────────────────────────────────────
if st.session_state["html"] is not None:
    st.markdown(
        '<div class="step"><span class="step-num">3</span>Download</div>',
        unsafe_allow_html=True,
    )

    if stale:
        st.markdown(
            f'<div class="stale">The workbook in the uploader has changed. '
            f'The result below is still from <b>{st.session_state["source"]}</b> — '
            f'press <b>Build dashboard</b> to refresh it.</div>',
            unsafe_allow_html=True,
        )

    warnings = st.session_state["warnings"]
    st.markdown(
        f"""
<div class="result">
  <div class="result-head">Dashboard ready</div>
  <div class="result-grid">
    <div><div class="result-k">Fund</div>
         <div class="result-v">{st.session_state["fund"] or "—"}</div></div>
    <div><div class="result-k">Report month</div>
         <div class="result-v">{st.session_state["label"]}</div></div>
    <div><div class="result-k">As of</div>
         <div class="result-v">{st.session_state["as_of"] or "—"}</div></div>
    <div><div class="result-k">Assets</div>
         <div class="result-v">{st.session_state["assets"]}</div></div>
    <div><div class="result-k">Warnings</div>
         <div class="result-v">{len(warnings)}</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    month_slug = (st.session_state["label"] or "dashboard").replace(" ", "_")
    st.download_button(
        f"Download dashboard — {st.session_state['label']}",
        st.session_state["html"],
        file_name=f"dashboard_{month_slug}.html",
        mime="text/html",
        use_container_width=True,
    )

    if warnings:
        with st.expander(f"{len(warnings)} data warning(s) from this workbook"):
            for warning in warnings:
                st.markdown(f"- {warning}")
    else:
        st.markdown(
            '<div class="step-hint" style="margin-left:0">No data-quality '
            'warnings were raised.</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="foot">Anything in the workbook that does not reconcile is listed '
    'above and on the dashboard\'s Data Quality tab. The generated file is fully '
    'self-contained — no network access needed to open it.</div>',
    unsafe_allow_html=True,
)
