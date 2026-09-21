# Real Estate Dashboard — UI Recreation Guide

## Scope and visual direction

This guide documents the **production dashboard** built from
`templates/dashboard.template.html` by `src/build_dashboard.py`. It is the
interface to reproduce when recreating this project elsewhere.

The look is a restrained, editorial **“warm boardroom”** dashboard:

- warm, paper-like neutrals rather than cool white and grey;
- near-black typography, thin warm borders, and square-to-slightly-rounded cards;
- muted antique gold is the principal interactive accent;
- deep vermilion is reserved for the primary data series;
- Playfair Display creates the executive/editorial hierarchy and Inter carries
  all interface, tables, labels, and data.

Do not blend it with the Streamlit prototype, which is a separate navy-and-orange
visual system (documented at the end of this guide).

## Design tokens

### Typography

Load these Google Fonts:

```text
Playfair Display: 500, 600, 700
Inter: 300, 400, 500, 600, 700
```

| Purpose | Family | Weight | Typical size | Treatment |
| --- | --- | ---: | ---: | --- |
| Page title / KPI value / panel title | Playfair Display | 600 | 17–33px | Tight tracking (`-0.01em` to `-0.02em`), compact line-height |
| UI controls, body, data tables | Inter | 500 | 11–13px | Neutral, legible; use tabular figures for numeric values |
| Uppercase labels / kicker | Inter | 500–600 | 10.5–11.5px | Uppercase, spacious tracking (`0.10em`–`0.18em`) |
| Secondary body text | Inter | 500 | 12–13px | `ink-2` colour |

### Light theme palette (default)

| Token | Hex / value | Use |
| --- | --- | --- |
| `bg` | `#F4F2EC` | Main canvas |
| `bg-grad-a` | `#F6F4EE` | Warm background gradient start, where used |
| `bg-grad-b` | `#EFEDE5` | Warm background gradient end, where used |
| `surface` | `#FCFBF8` | Cards, popovers, app bar base |
| `surface-2` | `#F4F2EB` | Table-row hover / subdued surface |
| `surface-3` | `#EDEAE1` | Selected or muted surface |
| `ink` | `#17181C` | Primary text, active controls, primary data series |
| `ink-2` | `#5C584E` | Secondary text |
| `ink-3` | `#948F82` | Labels, placeholders, muted metadata |
| `line` | `#E2DDD1` | Card, control, and strong divider borders |
| `line-2` | `#ECE8DE` | Subtle row dividers |
| `grid` | `rgba(60,55,40,.10)` | Chart grid lines |
| `appbar-bg` | `rgba(252,251,248,.86)` | Sticky translucent header |
| `vacant` | `#E0DBCE` | Vacant area/data segment |

### Brand, chart, and semantic palette

| Role | Token | Hex | Rule |
| --- | --- | --- | --- |
| Primary chart series / category | `brand-maroon` | `#E34234` | Use sparingly as the leading data colour; it is vermilion, despite the legacy name. |
| Dark vermilion | `brand-maroon-d` | `#C0392B` | Hover, selected, or darker data state. |
| Primary UI accent | `brand-orange` | `#B8960C` | Antique/muted gold: active tab underline, kicker, sorted column, checkmarks, highlights. |
| Dark gold | `brand-orange-d` | `#9C7E08` | Darker gold interaction state. |
| Chart ink | `d1` | `#17181C` | Main dark series. |
| Chart gold | `d2` | `#B8960C` | Accent series. |
| Warm grey | `d3` | `#8C8678` | Secondary series. |
| Light warm grey | `d4` | `#C2BCAD` | Low-emphasis series. |
| Dark warm grey | `d5` | `#56524A` | Supporting series. |
| Light gold | `d6` | `#D0AE3A` | Supporting accent series. |
| Positive | `ok` | `#4F7A52` | Positive trend and success badge. |
| Warning | `warn` | `#B8860B` | Warning badge. |
| Negative | `danger` | `#AE4A3C` | Negative trend and alert badge. |
| Informational | `info` | `#4E6577` | Informational badge. |

Use translucent semantic badge fills: approximately 13% of the semantic colour
over transparent (15% for warning), with the solid semantic colour for text and
the badge dot.

### Dark theme palette

Dark mode retains the warm character; it is charcoal, not blue-grey.

| Token | Value |
| --- | --- |
| `bg` / gradient | `#15171E`, `#181B23`, `#131520` |
| surfaces | `#16181F`, `#1B1E26`, `#22252F` |
| text hierarchy | `#F2F0E8`, `#C9C4B6`, `#948E7F` |
| borders | `rgba(255,255,255,.09)` and `rgba(255,255,255,.05)` |
| vacant segment | `#2A2D36` |
| leading data colour | `#DAD5C8` |
| gold accent | `#C9A52A` |
| dark-mode supporting ramp | `#E2DDD0`, `#8C8678`, `#5E5A50`, `#B4AE9F` |

In dark mode, increase normal body copy to weight 500; this is intentional to
keep light text from appearing too thin.

## Layout and geometry

| Item | Specification |
| --- | --- |
| Content maximum width | 1440px, centred |
| Desktop horizontal gutter | 56px |
| Page content padding | 40px top, 56px sides, 80px bottom |
| Desktop grid gap | 22px |
| Card radius | 5px (4px for compact controls; 6px only where needed) |
| Card treatment | `surface` fill, 1px `line` border, normally no shadow |
| Elevated popover/tooltip | `0 1px 2px rgba(30,25,15,.08), 0 18px 44px rgba(30,25,15,.12)` |
| Card internal padding | Head: 22px/24px; body: 20px 24px 24px; KPI: 22px 22px 20px |
| Sticky masthead | Translucent `appbar-bg`, 16px backdrop blur, 1px bottom border |

The masthead consists of a left logo block and a right area with a 64px control
row plus a tab bar. Keep the active tab understated: normal text colour plus a
2px gold underline, not a filled pill.

At 1100px and below, reduce the gutter to 24px and collapse content grids to two
columns. At 700px and below, use a 16px gutter, make the masthead vertical, use
one-column grids, and retain horizontal scrolling for tabs and tables.

## Component recipes

### Panels and KPI cards

- Panels: off-white surface, 1px warm border, 5px radius. Avoid generic drop
  shadows. Panel titles use Playfair Display 17px/600.
- KPI cards: same panel shell; label is an uppercase tracked Inter label; value is
  Playfair Display 24–33px/600; footnote is 12.5px Inter in `ink-2`, separated
  by a fine `line-2` rule.
- Page header: gold uppercase kicker above 32px Playfair Display title. Metadata
  is right-aligned Inter 12px in `ink-2`.
- Section labels: a 18×2px gold bar followed by an uppercase Inter heading with
  `0.16em` tracking.

### Controls, tables, and feedback

- Buttons, segmented controls, search, and selects are transparent or surface
  filled with a 1px `line` border and 4px radius. Use 11–12.5px Inter/500.
- A selected segmented-control option inverts to `ink` background and `surface`
  text. A selected tab does **not** invert.
- Tables have no heavy header fill: headers are uppercase, `ink-3`, 10.5px/600,
  with thin borders. Rows are 13px, with 13px × 16px cells and `surface-2` hover.
- Numeric columns are right aligned and use tabular numerals. Total rows have a
  1px top border and Inter 600.
- Badges are compact uppercase labels (10.5px/500), 3px × 9px padding, 4px
  radius, semantic text/dot, and a very light semantic tint.
- Tooltips invert: `ink` background, `bg` text, 4px radius, 10px × 12px padding.

### Chart language

- Keep plot backgrounds transparent so cards/canvas show through.
- Use the `d1`–`d6` ramp first. Vermilion should identify the primary series;
  gold should draw attention to selection or a secondary focal series.
- Use only faint warm grid lines, minimal axis decoration, compact Inter labels,
  and no gratuitous gradients.
- Asset-specific colours are deliberately muted: `#6B7A4A`, `#4E6577`,
  `#A39C8C`, `#B4930F`, `#8B4A4A`, `#9B7A3A`, `#6A5A8C`, `#4A5A8C`,
  `#787878`, `#8C7A3A`, `#3D7A72`, `#3A6F7A`, `#7A3A4A`, `#3A4A6E`, and
  `#8C5A4A`.
- Stack-plan categories: Outsourcing `#E34234`, Other Services `#8C8678`, IT
  Services `#B8960C`, Healthcare `#6E5A2E`, Vacant `#E0DBCE` (or `#2A2D36` in
  dark mode).

## Interaction and motion

- Use short, quiet transitions: 140–180ms for hover, colour, and background
  changes.
- Table rows transition their background over 140ms.
- Tabs and small controls transition colour over 160–180ms.
- Keep the header sticky and blurred. Dropdowns use the elevated shadow; cards do
  not float.
- Selection highlight: 26% gold mixed with transparency.
- Scrollbars are 9px, transparent track, muted rounded thumb with a 3px
  transparent border so it feels inset.

## Implementation starter tokens

```css
:root {
  --bg:#F4F2EC; --surface:#FCFBF8; --surface-2:#F4F2EB; --surface-3:#EDEAE1;
  --ink:#17181C; --ink-2:#5C584E; --ink-3:#948F82;
  --line:#E2DDD1; --line-2:#ECE8DE;
  --vermilion:#E34234; --vermilion-dark:#C0392B;
  --gold:#B8960C; --gold-dark:#9C7E08;
  --ok:#4F7A52; --warn:#B8860B; --danger:#AE4A3C; --info:#4E6577;
  --radius:5px; --radius-small:4px; --gutter:56px; --max-width:1440px;
  --ui-font:"Inter", sans-serif;
  --display-font:"Playfair Display", Georgia, serif;
}
```

## Important: legacy Streamlit prototype

`src/app.py` and `src/theme.py` use an earlier, different identity: Mulish font,
cool `#F7F8FA` background, `#1B2A5E` navy and `#F26522` orange. Its cards use
10–12px radii and an orange left rail. Do not use that system if the goal is to
match the production dashboard. Use it only when intentionally reproducing the
Streamlit prototype.

## Source of truth

- Production tokens, component CSS, responsive behaviour:
  `templates/dashboard.template.html`
- Asset and stack-plan chart colours:
  `src/build_dashboard.py`
- Legacy Streamlit-only palette:
  `src/theme.py` and `src/app.py`
