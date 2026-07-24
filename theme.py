"""
theme.py
========
Single source of truth for ICICI Prudential AMC colours and Mulish typography.
Import this in app.py and every component module.
"""

# ─────────────────────────────────────────────
# ICICI PRUDENTIAL AMC COLOUR PALETTE
# ─────────────────────────────────────────────

# Primary brand
ORANGE        = "#F26522"   # ICICI Pru signature orange
DARK_ORANGE   = "#C84E0E"   # hover / pressed orange
LIGHT_ORANGE  = "#FDE9D8"   # tinted background chips

# Secondary brand
NAVY          = "#1B2A5E"   # deep navy — headers, sidebars
DARK_NAVY     = "#111C40"   # deeper variant
MID_NAVY      = "#2C3E7A"   # secondary nav elements

# Neutrals
WHITE         = "#FFFFFF"
OFF_WHITE     = "#F7F8FA"   # page background
LIGHT_GREY    = "#EEF0F4"   # card borders, dividers
MID_GREY      = "#C2C7D4"   # muted labels
DARK_GREY     = "#4A4F63"   # body text secondary
CHARCOAL      = "#1E2235"   # primary body text

# Status / RAG
GREEN_OK      = "#1AAF5D"
GREEN_BG      = "#E6F7EE"
AMBER_DUE     = "#F5A623"
AMBER_BG      = "#FEF3DC"
RED_PROGRESS  = "#D0021B"
RED_BG        = "#FDEAEA"
GREY_NOTDUE   = "#6B7280"
GREY_BG       = "#F3F4F6"
PURPLE_NA     = "#7C5CBF"
PURPLE_BG     = "#EFE9F9"

# Chart colour sequence (ICICI Pru themed)
CHART_COLORS  = [
    "#F26522",   # orange
    "#1B2A5E",   # navy
    "#1AAF5D",   # green
    "#F5A623",   # amber
    "#7C5CBF",   # purple
    "#2196F3",   # blue
    "#E91E63",   # pink
]

# Stack plan industry colours
INDUSTRY_COLORS = {
    "Outsourcing":    "#1B2A5E",
    "IT Services":    "#2196F3",
    "Other Services": "#90A4AE",
    "Healthcare":     "#1AAF5D",
    "Vacant":         "#E8EAED",
}

# ─────────────────────────────────────────────
# PLOTLY LAYOUT TEMPLATE
# ─────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Mulish, sans-serif", color=DARK_GREY, size=12),
    xaxis=dict(
        gridcolor=LIGHT_GREY,
        linecolor=LIGHT_GREY,
        tickcolor=LIGHT_GREY,
        tickfont=dict(size=11),
        title_font=dict(size=12),
    ),
    yaxis=dict(
        gridcolor=LIGHT_GREY,
        linecolor="rgba(0,0,0,0)",
        tickcolor="rgba(0,0,0,0)",
        tickfont=dict(size=11),
        title_font=dict(size=12),
    ),
    colorway=CHART_COLORS,
    margin=dict(l=8, r=8, t=36, b=8),
    hoverlabel=dict(
        bgcolor=WHITE,
        bordercolor=LIGHT_GREY,
        font=dict(family="Mulish, sans-serif", size=12, color=CHARCOAL),
    ),
    legend=dict(
        font=dict(family="Mulish, sans-serif", size=11),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
    ),
    title_font=dict(family="Mulish ExtraBold, Mulish, sans-serif", size=14, color=NAVY),
)

# ─────────────────────────────────────────────
# STATUS BADGE CONFIG
# ─────────────────────────────────────────────

STATUS_STYLES = {
    "In Progress":    {"bg": RED_BG,     "color": RED_PROGRESS, "border": RED_PROGRESS},
    "Due Soon":       {"bg": AMBER_BG,   "color": DARK_ORANGE,  "border": AMBER_DUE},
    "OK":             {"bg": GREEN_BG,   "color": GREEN_OK,     "border": GREEN_OK},
    "Not Due":        {"bg": GREY_BG,    "color": GREY_NOTDUE,  "border": MID_GREY},
    "Not Applicable": {"bg": PURPLE_BG,  "color": PURPLE_NA,    "border": PURPLE_NA},
    "Revision Required": {"bg": AMBER_BG, "color": DARK_ORANGE, "border": AMBER_DUE},
    "Complied":       {"bg": GREEN_BG,   "color": GREEN_OK,     "border": GREEN_OK},
}


def status_badge_html(status: str) -> str:
    """Return an inline HTML badge for a given status string."""
    style = STATUS_STYLES.get(status, STATUS_STYLES["Not Due"])
    return (
        f'<span style="'
        f'background:{style["bg"]};'
        f'color:{style["color"]};'
        f'border:1px solid {style["border"]};'
        f'border-radius:4px;'
        f'padding:2px 10px;'
        f'font-size:11px;'
        f'font-weight:700;'
        f'font-family:Mulish,sans-serif;'
        f'white-space:nowrap;'
        f'">{status}</span>'
    )