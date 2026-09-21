"""
theme.py
========
Single source of truth for ICICI Prudential colours and Mulish typography.
Import this in app.py and every component module.

Provenance
----------
The values marked "brand" below were read out of the live ICICI Prudential AMC
stylesheet (https://www.icicipruamc.com/static/css/index.CmJaN2Ir.css) rather
than eyeballed: navy #133359 is the single most-used colour on the site, orange
#DC6009 the second, and every font rule on that sheet is `font-family: Mulish`.
Values marked "derived" are tints/shades mixed from those brand hues so that
cards, badges and charts have somewhere to sit — they are not official.

Typography
----------
One weight only: Mulish SemiBold (600). Nothing here should ask for 700+, or
the browser will synthesise a fake bold next to the real 600 face.
"""

# ─────────────────────────────────────────────
# ICICI PRUDENTIAL COLOUR PALETTE
# ─────────────────────────────────────────────

# Primary brand
ORANGE        = "#DC6009"   # brand — signature burnt orange
BRIGHT_ORANGE = "#F97000"   # brand — brighter orange used for emphasis
DARK_ORANGE   = "#C55608"   # brand — hover / pressed
LIGHT_ORANGE  = "#FFF1E5"   # brand — tinted background chips

# Secondary brand
NAVY          = "#133359"   # brand — headers, ink, primary series
DARK_NAVY     = "#0D2440"   # derived — deeper variant for gradients
MID_NAVY      = "#2A4C74"   # derived — secondary nav elements
SLATE         = "#5A718B"   # brand — muted blue-grey series colour
MAROON        = "#96191F"   # brand — ICICI maroon, used sparingly

# Neutrals
WHITE         = "#FFFFFF"
OFF_WHITE     = "#FCFCFA"   # brand — page background
LIGHT_GREY    = "#E0E6EE"   # derived — card borders, dividers
MID_GREY      = "#BDC4C9"   # brand — muted labels
DARK_GREY     = "#75838E"   # brand — secondary body text
CHARCOAL      = "#1B2A3D"   # derived — primary body text (navy-tinted ink)

# Status / RAG
GREEN_OK      = "#267D00"   # brand
GREEN_BG      = "#E9F3E4"   # derived
AMBER_DUE     = "#FFA217"   # brand
AMBER_BG      = "#FFF4E0"   # derived
RED_PROGRESS  = "#C8190A"   # brand
RED_BG        = "#FCEAE8"   # derived
GREY_NOTDUE   = "#75838E"   # brand
GREY_BG       = "#F1F4F8"   # derived
PURPLE_NA     = "#6E5A8E"   # harmonised — the brand has no violet, but
PURPLE_BG     = "#F0ECF6"   # "Not Applicable" needs its own hue

# Chart colour sequence (ICICI Pru themed)
CHART_COLORS  = [
    NAVY,            # navy
    ORANGE,          # orange
    SLATE,           # slate
    GREEN_OK,        # green
    AMBER_DUE,       # amber
    MAROON,          # maroon
    "#8FA3B8",       # pale slate
]

# Stack plan industry colours
INDUSTRY_COLORS = {
    "Outsourcing":    NAVY,
    "IT Services":    SLATE,
    "Other Services": "#8FA3B8",
    "Healthcare":     GREEN_OK,
    "Vacant":         "#E8EAED",
}

# ─────────────────────────────────────────────
# TYPOGRAPHY
# ─────────────────────────────────────────────

FONT_FAMILY = "Mulish, sans-serif"
FONT_WEIGHT = 600                    # semi-bold, the only weight we ship
FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?family=Mulish:wght@600&display=swap"
)

# ─────────────────────────────────────────────
# PLOTLY LAYOUT TEMPLATE
# ─────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family=FONT_FAMILY, color=DARK_GREY, size=12),
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
        font=dict(family=FONT_FAMILY, size=12, color=CHARCOAL),
    ),
    legend=dict(
        font=dict(family=FONT_FAMILY, size=11),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
    ),
    # Plotly renders SVG text, which has no access to the CSS weight rules —
    # the family alone is enough because Mulish 600 is the only face loaded.
    title_font=dict(family=FONT_FAMILY, size=14, color=NAVY),
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
        f'font-weight:{FONT_WEIGHT};'
        f'font-family:{FONT_FAMILY};'
        f'white-space:nowrap;'
        f'">{status}</span>'
    )
