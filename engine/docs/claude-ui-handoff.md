# ICICI Prudential Alternate Investments — Claude UI Handoff

## Purpose and scope

This is the implementation brief for carrying the **production Real Estate
Fund dashboard visual language** into another project. It is deliberately more
prescriptive than a mood board: treat the values and component recipes below as
the reference implementation unless the target project's requirements make a
specific exception necessary.

The intended character is **quiet, institutional, and editorial**. It should
feel like a well-produced investment committee report that happens to be
interactive—not a consumer app, generic SaaS dashboard, or a colourful
presentation. The cues that create that feeling are:

- warm paper neutrals rather than pure/cool greys;
- one restrained attention colour (antique gold) rather than an all-purpose
  brand colour;
- almost-flat surfaces with fine warm rules instead of rounded, shadowy cards;
- a high-contrast serif reserved for hierarchy and important numbers; and
- very compact, carefully spaced sans-serif UI typography.

Do **not** copy the older Streamlit prototype in `src/app.py` or `src/theme.py`.
It is a separate navy/orange/Mulish design and is not the visual language in
the production dashboard.

The executable source of truth is
`templates/dashboard.template.html`. The generated `output/dashboard.html`, if
present, is a build product and must not be treated as the editable source.

---

## 1. Firm logo: exact source, extraction, and placement

### Where the logo actually lives

There is currently **no standalone PNG, JPG, or SVG file** in this repository.
The exact firm wordmark used by the production dashboard is an SVG embedded as
a Base64 data URI in:

```text
templates/dashboard.template.html
TopBar() → <img className="brand-logo" ...>
approximately line 631 (search for: alt="ICICI Prudential Alternate Investments")
```

This is the asset Claude must use. It is not an approximation, text recreation,
or a logo that needs to be fetched from the web. The image has this accessible
name:

```html
alt="ICICI Prudential Alternate Investments"
```

The embedded data URI begins with:

```text
data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEi...
```

and ends immediately before the `alt` attribute on that same `<img>` element.
It decodes to a vector logo with `viewBox="24 25 184 86"`, including its white
rectangular field and the full ICICI Prudential Alternate Investments lockup.
Use the complete asset unchanged. Do not redraw its lettering, replace it with
plain text, recolour it, crop it to the symbol, or apply a CSS filter.

### Recommended extraction into the target project

For a normal web project, extract it once into a real asset and reference that
file. This avoids a giant data URI being duplicated through components. From a
checkout that contains this repository, Claude can run the following exact
one-off command (the output directory must exist first):

```bash
python3 -c 'import base64,re,pathlib; p=pathlib.Path("templates/dashboard.template.html"); s=p.read_text(); m=re.search(r"<img className=\"brand-logo\" src=\"data:image/svg\+xml;base64,([^\"]+)\"", s); assert m, "Brand SVG not found"; pathlib.Path("assets/icici-prudential-alternate-investments.svg").write_bytes(base64.b64decode(m.group(1)))'
```

After extraction, the target project should reference the resulting file—not a
screenshot and not a raster export:

```html
<img
  src="/assets/icici-prudential-alternate-investments.svg"
  alt="ICICI Prudential Alternate Investments"
  class="brand-logo"
/>
```

If the target cannot host a static file, retaining the original data URI is
acceptable. SVG is strongly preferred because the lockup remains sharp at all
screen densities.

### Logo sizing and container geometry

The logo is part of the masthead, not a floating badge or content illustration.

| Context | Required treatment |
| --- | --- |
| Desktop image | `height: 90px; width: auto; display: block; flex-shrink: 0` |
| Mobile image (≤700px) | reduce only to `height: 64px` |
| Image rounding | `border-radius: 6px` because the supplied white logo field is a rectangular asset |
| Light masthead | no logo shadow |
| Dark masthead | only a fine outline and restrained lift: `0 0 0 1px rgba(255,255,255,.10), 0 1px 6px rgba(0,0,0,.35)` |
| Desktop logo bay | left side of the masthead; `padding: 8px 40px 8px 56px`; 1px right divider |
| Narrow desktop (≤1100px) | horizontal padding becomes 24px |
| Mobile (≤700px) | masthead stacks vertically; centre the logo; remove right divider; add bottom divider; padding `6px 16px` |

The logo's white field is intentional. Keep it intact even on the dark theme;
that small white rectangle gives the official mark a stable, legible field.
Do not place the logo directly on a coloured panel, on a patterned image, or
inside a circular avatar.

### Brand-use guardrails

The visual asset is a company mark. Use it only where the target project is
authorised to represent ICICI Prudential Alternate Investments. Preserve its
proportions and clear space; do not animate, skew, mask, add gradients, or use
the logo as an icon/button. For a different firm, retain the **layout role and
sizing** but substitute only that firm's approved asset.

---

## 2. The system in one sentence

**Warm off-white canvas + paper-white ruled panels + near-black ink + antique
gold for interaction + vermilion for primary data + Playfair Display for
editorial hierarchy + Inter for all operational UI.**

The following hierarchy is important: gold is a navigation and emphasis signal;
vermilion is primarily a data-series signal. Do not turn every primary button,
heading, chart, and status into gold or vermilion.

---

## 3. Design tokens — copy these before styling components

### Core CSS token block (light mode)

```css
:root {
  /* Canvas and surfaces */
  --bg: #F4F2EC;
  --bg-grad-a: #F6F4EE;
  --bg-grad-b: #EFEDE5;
  --surface: #FCFBF8;
  --surface-2: #F4F2EB;
  --surface-3: #EDEAE1;

  /* Text and rules */
  --ink: #17181C;
  --ink-2: #5C584E;
  --ink-3: #948F82;
  --line: #E2DDD1;
  --line-2: #ECE8DE;
  --grid: rgba(60,55,40,.10);

  /* Intentional accents */
  --vermilion: #E34234;
  --vermilion-dark: #C0392B;
  --gold: #B8960C;
  --gold-dark: #9C7E08;

  /* Data ramp */
  --data-ink: #17181C;
  --data-warm-grey: #8C8678;
  --data-light-grey: #C2BCAD;
  --data-dark-grey: #56524A;
  --data-light-gold: #D0AE3A;
  --vacant: #E0DBCE;

  /* Status only */
  --ok: #4F7A52;
  --warn: #B8860B;
  --danger: #AE4A3C;
  --info: #4E6577;

  /* Geometry */
  --radius: 5px;
  --radius-small: 4px;
  --radius-large: 6px;
  --gutter: 56px;
  --content-max: 1440px;
  --elevated-shadow: 0 1px 2px rgba(30,25,15,.08), 0 18px 44px rgba(30,25,15,.12);
}
```

Use the aliases in the template (`--brand-maroon` for vermilion and
`--brand-orange` for gold) only when carrying code directly. In a new project,
the clearer names above are preferable; the colour values and their roles must
not change.

### Dark-mode overrides

Dark mode is a warm charcoal reading room, **not navy/slate**. Keep the same
information hierarchy and make body text weight 500 for legibility.

```css
[data-theme="dark"] {
  --bg: #15171E;
  --bg-grad-a: #181B23;
  --bg-grad-b: #131520;
  --surface: #16181F;
  --surface-2: #1B1E26;
  --surface-3: #22252F;
  --ink: #F2F0E8;
  --ink-2: #C9C4B6;
  --ink-3: #948E7F;
  --line: rgba(255,255,255,.09);
  --line-2: rgba(255,255,255,.05);
  --vacant: #2A2D36;
  --vermilion: #DAD5C8;
  --gold: #C9A52A;
  --data-ink: #E2DDD0;
  --data-light-grey: #5E5A50;
  --data-dark-grey: #B4AE9F;
  --grid: rgba(255,250,235,.07);
}
[data-theme="dark"] body { font-weight: 500; }
```

### Colour allocation rules

1. **Gold**: active-tab underline, page kicker, 18px section rule, selected
   sort affordance, a small check/attention detail, and a secondary focal
   series. It is not a full-page background.
2. **Vermilion**: leading data series, selected data contribution, or a
   deliberate financial emphasis. It is not the default UI brand colour.
3. **Ink and warm greys**: most charts, copy, dividers, and control states.
4. **Status colours**: only meaning-bearing feedback—success, warning, error,
   information. They must not be used as decorative chart palettes.
5. **Vacancy**: pale warm neutral (or charcoal in dark mode); distinguish it
   with a dashed/hatch treatment when it represents spatial inventory.

Asset-specific chart colours, if the new project needs a long categorical
sequence, are intentionally muted:

```text
#6B7A4A #4E6577 #A39C8C #B4930F #8B4A4A
#9B7A3A #6A5A8C #4A5A8C #787878 #8C7A3A
#3D7A72 #3A6F7A #7A3A4A #3A4A6E #8C5A4A
```

---

## 4. Typography and numeric language

Load only these two font families:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
```

| Content | Font, size, weight | Exact character |
| --- | --- | --- |
| Page title | Playfair Display, 32px, 600, `line-height: 1`, `letter-spacing: -.02em` | Editorial and authoritative; never all caps |
| KPI value | Playfair Display, `clamp(24px, 2.1vw, 33px)`, 600 | Prominent but compact; unit is smaller sans text |
| Panel title | Playfair Display, 17px, 600, `-.01em` tracking | Quiet hierarchy, not a huge heading |
| Body/table cells | Inter, 13px, normally 500 | Neutral and dense enough for data |
| Metadata | Inter, 12–13px, 500 | `ink-2`, never competing with the title |
| Uppercase label | Inter, 10.5–11.5px, 500–600 | uppercase with `.10em`–`.18em` tracking |
| Chart axis/legend | Inter, 8.5–11px, 500 | muted `ink-3` / `ink-2` |

All monetary, percentage, area, and tabular values should use tabular figures:

```css
.tnum { font-variant-numeric: tabular-nums; }
```

Use an Indian number formatting locale when values are full numbers
(`toLocaleString('en-IN')`). For the existing financial dashboard, currency is
stored and shown in crore (`₹Cr`) and areas in million square feet (`M sft`) or
thousand square feet (`K sft`). The target project may use different units, but
must retain the same unit/value hierarchy: large serif number, small muted
sans-serif unit.

Do not substitute the older **Mulish** font or a generic system/Arial stack if
the intention is to reproduce this production UI.

---

## 5. Global layout and responsive contract

### Desktop frame

```text
sticky masthead
├── fixed/auto-width logo bay
└── right masthead area
    ├── 64px control row
    └── horizontally scrollable tab bar

centred content container (max 1440px)
├── page kicker + title
└── purpose-built grids of panels/KPIs
```

- The viewport canvas uses `--bg`; content is centred with
  `max-width: 1440px; width: 100%; margin: 0 auto`.
- Content padding is `40px 56px 80px` on desktop.
- Default grid gap is 22px. A subsequent major grid normally has 18px top
  margin. These two nearby values create the actual vertical rhythm; do not
  replace both with an arbitrary framework spacing value.
- Panels are `--surface`, a 1px `--line` border, and 5px radius. They are not
  lifted with card shadows.
- The masthead is `position: sticky; top: 0; z-index: 40`, with translucent
  `rgba(252,251,248,.86)` light background, 16px backdrop blur and a 1px
  lower rule. It must remain visually lighter than the content canvas.

### Breakpoints

| Viewport | Required changes |
| --- | --- |
| >1100px | 56px gutter and purpose-specific desktop grids (often 5, 4, 3, or 2 columns) |
| ≤1100px | gutter 24px; force grids to two equal `minmax(0,1fr)` columns; masthead side padding 24px |
| ≤700px | gutter 16px; masthead becomes non-sticky and vertical; logo bay centres; control row wraps; content begins at 28px; every grid is one column |

Tabs and tables deliberately retain horizontal scrolling where needed. Never
squeeze tab labels, truncate financial table headers without a strategy, or
turn this into a hamburger-only information architecture on mobile.

### Spacing reference

| Element | Measurement |
| --- | --- |
| Panel header | `22px 24px 0` |
| Panel body | `20px 24px 24px` |
| KPI shell | `22px 22px 20px` |
| Panel/card radius | 5px |
| Compact control radius | 4px |
| Section-label top/bottom margin | `38px 0 16px` |
| Page header bottom margin | 34px |
| Kicker bottom margin | 11px |
| Table cell | `13px 16px` |

---

## 6. Component recipes

### Masthead, controls, and navigation

- Use the official logo in the separate left bay as described above.
- The top right control row is 64px high, horizontally aligned, and spaced by
  24px. The fund/project descriptor is an uppercase Inter 13px/500 label with
  `.06em` tracking and `ink-2` colour.
- The tab bar is centred on desktop and left-scrollable on narrow screens. Tabs
  are transparent, borderless, Inter 13px/500, 15px top / 14px bottom padding,
  and 18px horizontal padding.
- An active tab uses normal `ink` text plus a **2px gold underline** inset 18px
  from each end. It does not become an orange/gold pill.
- Selects, theme toggles, and inputs have transparent backgrounds, 1px warm
  borders, 4px corners, 11–12.5px Inter/500, and a quiet 160ms border/colour
  hover. A selected option in a segmented control inverts to ink fill and
  surface-coloured label text.
- Dropdowns alone may use the elevated shadow. They use a 5px outer radius,
  5px internal padding, and 9px × 11px menu items.

### Page title and section label

- Page kicker: gold, uppercase, 11.5px/500, `.18em` tracking.
- Title: Playfair 32px/600 directly beneath it.
- Do not put the title in a card or use a hero gradient.
- A sectional divider is an 18×2px gold bar followed by an uppercase Inter
  11px/600 heading in `ink-2` with `.16em` tracking.

### Panel and KPI shell

- Panels use no heavy header fill. Their title/subtitle live in the same
  surface, set with a deliberately generous top/side inset.
- Panel subtitle is uppercase Inter 10.5px/500, `.12em` tracking, `ink-3`, and
  7px below the title.
- KPI label: uppercase Inter 11px/500, `.13em` tracking, `ink-3`.
- KPI value: 14px below its label. Optional footnote begins 12px later, behind a
  fine top rule, and is Inter 12.5px in `ink-2`.
- Do not add icon circles, left accent rails, oversized trend arrows, strong
  shadows, or gradient fills. This design achieves emphasis through type,
  whitespace, and one fine divider.

### Tables

- Table headers are not filled blocks. They are uppercase Inter 10.5px/600,
  `.10em` tracking, `ink-3`, with a 1px bottom border.
- Body rows: 13px, `ink`, 13px × 16px padding, subtle `line-2` divider.
- Hover only changes a row to `surface-2` over 140ms.
- Numeric headings and cells are right-aligned; numbers use tabular figures.
- A total row uses Inter 600 and a 1px top border; do not introduce a dark,
  coloured grand-total band.
- Search controls, if included, are a thin outlined shell rather than a filled
  oversized field.

### Badges and status

- Badge: inline flex, dot + uppercase label, Inter 10.5px/500, `.04em`
  tracking, `padding: 3px 9px`, 4px radius.
- Fill is only ~13% semantic tint (15% warning); the text/dot use the solid
  semantic colour.
- A badge conveys status. It is not a generic category tag and should not be
  the main visual focus of a card.

### Charts and spatial visualisations

- Plot backgrounds are transparent; panel/canvas shows through.
- Use a minimal custom SVG/chart style: faint warm horizontal grid lines,
  compact labels, no default chart container, no gradients, no 3D, no thick
  axes, no legend box.
- Bars have gently rounded tops (about 4px) where appropriate. Donuts are
  spare (around 14px ring thickness) with a clear centre label.
- Leading series: vermilion. Selected/secondary focal: gold. Other series use
  ink/warm grey ramp. Do not use the entire rainbow palette unless distinct
  asset identity genuinely needs it.
- Legends: 10×10px square swatch (2px corner radius), uppercase Inter 11px/500,
  `.06em` tracking, 16px gaps.
- Tooltips invert: `ink` background, `bg` text, 4px radius, 10px × 12px
  padding, 11.5px text; use tabular bold values and small muted uppercase keys.
- Animate chart reveal once: bars grow / lines draw in over ~320–600ms with a
  gentle `cubic-bezier(.2,.8,.2,1)` stagger. Do not add continuous motion.

For stacking/floor visuals specifically, preserve the production semantics:
units use proportional flex widths; vacant units are light and hatched/dashed;
third-party holdings are transparent with a dashed category outline. These
encoding choices are more meaningful than merely copying the colours.

---

## 7. Interaction, motion, and accessibility

### Motion

- Hover, colour, border, and background transitions: **140–180ms**.
- Dropdown/tooltip opacity: **120ms**.
- Chart entrance: **320ms** per mark family, with small 40–80ms stagger.
- Do not use bouncy springs, parallax, shimmers, continuous animations, or
  large scale transforms. The dashboard should feel composed and stable.

### Feedback and focus

- Every interactive control needs a visible keyboard focus treatment. A good
  compatible treatment is a 2px gold outline with 2px offset; do not remove
  outlines without replacement.
- Do not rely on gold/vermilion alone to express financial condition or status;
  keep labels, values, and badge text.
- Ensure ordinary body copy remains at least AA contrast. In particular, use
  `ink`/`ink-2` for text, not `ink-3`, when the text must be read rather than
  merely scanned.
- Retain the supplied logo `alt` text exactly. Decorative chart SVGs should be
  labelled or hidden from assistive technology depending on whether the data is
  also available in adjacent text/table form.

### Browser details worth retaining

```css
* { box-sizing: border-box; }
body { -webkit-font-smoothing: antialiased; font-feature-settings: "cv05", "ss01"; }
::selection { background: color-mix(in srgb, var(--gold) 26%, transparent); }
*::-webkit-scrollbar { width: 9px; height: 9px; }
*::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--ink-3) 38%, transparent);
  border: 3px solid transparent;
  border-radius: 20px;
  background-clip: padding-box;
}
```

---

## 8. What must not be carried over

Avoid these changes even if a component library makes them easy:

- cool white/blue-grey canvases, navy app shells, or the legacy bright orange;
- generic 10–16px-radius cards with omnipresent soft shadows;
- filled coloured tab pills for the active navigation item;
- blue primary buttons, purple gradients, glassmorphism, or rainbow charts;
- sans-serif-only headlines or oversized bold all-caps headings;
- hero images, stock building photography, or decorative icons in every KPI;
- strong chart backgrounds, heavy axes, thick grids, or large legends;
- changing the official firm logo's colours/proportions or rebuilding it in text.

The target project may have new information architecture and new content; it
does not need to mimic every dashboard section. It should, however, preserve
the **hierarchy, colour discipline, density, typography roles, panel treatment,
and logo placement** documented here.

---

## 9. Implementation order for Claude

1. Extract/copy the official SVG from `templates/dashboard.template.html` into
   the target project's asset folder; insert it in a masthead logo bay.
2. Load Playfair Display and Inter, then define the light tokens and dark-mode
   overrides before creating any page-specific component styles.
3. Build the frame: sticky masthead, logo bay, control row, understated tab
   navigation, centred 1440px content column.
4. Build reusable `PageHeading`, `Panel`, `Kpi`, `DataTable`, `Badge`, and
   chart-tooltip primitives to the recipes above. Use tokens—do not scatter
   raw hex values.
5. Compose the target application's screens using its actual data and workflow.
   Use 5/4/3/2-column grids only when their content supports it; avoid empty
   KPI cards simply to reproduce a row count.
6. Implement the two responsive breakpoints and test at 320px, 700px, 1100px,
   1440px, and a wide desktop viewport.
7. Review both themes: the logo stays unchanged, the gold remains restrained,
   numbers align, text does not become too faint, and only overlays receive
   elevation shadows.

### Acceptance checklist

- [ ] The official SVG came from the embedded `<img className="brand-logo">`
      source, not from a web search or recreated lettering.
- [ ] Logo is 90px high on desktop and 64px on mobile, in its own masthead bay.
- [ ] Canvas is warm `#F4F2EC`, not cool white; cards are `#FCFBF8` with warm
      1px rules and ~5px corners.
- [ ] Playfair is used for page/KPI/panel hierarchy; Inter is used for UI/data.
- [ ] Gold is limited to attention/navigation; vermilion leads primary data.
- [ ] Cards are largely flat; only menus/tooltips have the elevated shadow.
- [ ] Tables are quiet, right-align numeric values, and have no solid header
      band.
- [ ] Light and dark themes are both warm and readable.
- [ ] At ≤1100px grids have two columns; at ≤700px they have one and masthead
      stacks.
- [ ] No default component-library blue, radius, shadow, typography, or chart
      style leaks into the finished interface.

## Related repository references

- `templates/dashboard.template.html` — authoritative CSS, JSX components,
  embedded firm logo, motion, and responsive rules.
- `src/build_dashboard.py` — muted asset palette and stack-plan category
  colours.
- `docs/ui-recreation-guide.md` — shorter companion reference with production
  palette and layout values.
- `src/app.py` and `src/theme.py` — legacy prototype only; intentionally not
  part of this handoff's style target.
