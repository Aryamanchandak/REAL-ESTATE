# `data/real_estate_fund_data.xlsx` — what changed, and what the HTML needs

> **Status: implemented.** Everything in §0-§2 is fixed and verified;
> `output/dashboard.html` is rebuilt from `data/real_estate_fund_data.xlsx`.
> §3 is still open — those are data-entry items
> only the RE team can resolve. See §5 for what shipped.

Compared cell-by-cell against `tests/fixtures/sparse_fund_data.xlsx`.
All 11 sheets diffed. Sheets with **zero** changes: `Instructions`, `1 · META`, `8 · TENANT`.

---

## 0. Headline: the build does not run at all right now

```
ValueError: financial_usage: missing required column(s):
  ['Creation of FD', 'Transfer to Projects', 'Other Outflow', 'Bank Charges']
```

`5 · FINANCIAL` section C renamed its four spend categories. This is a hard crash in
`ingest.py`, before anything else is reached. Nothing else can be assessed until it's fixed.

| Old label | New label |
|---|---|
| Creation of FD | **Creation of MF/FD** |
| Transfer to Projects | **Capex** |
| Other Outflow | **Operational Expenses** |
| Bank Charges | **Others** |

Still four categories, so it's a rename, not a structural change. Two places to update:
`ingest.py:126` (`_REQUIRED_COLUMNS["financial_usage"]`) and `build_dashboard.py:277-280`,
where the old labels are **hardcoded as display strings**. If only the ingest side is fixed,
the dashboard renders the *old* category names against the *new* numbers — correct values,
wrong labels, no error. That's the most dangerous failure mode in this changeset.

> Note: `5 · FINANCIAL` also reports `max_col=7` now vs 6 before. Column G is **entirely
> empty** — stray formatting only, no data implication.

---

## 1. The stack plan change

`7 · STACK PLAN` gained column F, **`Ownership`**, with values `Fund` / `Others`.
The sheet now lists *every floor in each building*, not just the fund's floors.

Row counts went 27 → 44 real rows. Examples: `blue` 1 → 4 rows, `white` 1 → 7,
`red` 9 → 12, `green` 2 → 6. `yellow` is unchanged at 15.

### What `Ownership` means — reconciled against `2 · ASSETS`

Summing stack-plan area for `Ownership = Fund` per asset, versus the asset's reported
Leasable area:

| Asset | Fund rows | Others rows | Fund total | ASSETS Leasable | Match |
|---|---|---|---|---|---|
| green  | 127.0K | 105.0K | 127.0K | 120K | ~ |
| blue   | 172.0K |  88.0K | 172.0K | 170K | ✓ |
| white  |  40.0K |   0.0K |  40.0K |  40K | ✓ |
| yellow |   —    |   —    | *(blank)* 223.6K | 223K | ✓ |
| red    | 388.0K | 141.0K | 388.0K | 380K | ✓ |

So `Fund` = the floors we own (exactly what the old sheet contained), `Others` = the rest
of the building, newly added.

> **Assumption to confirm with the RE team:** `yellow`'s Ownership column is *entirely
> blank*, and its total (223.6K) matches its leasable area (223K). That reads as "the whole
> building is ours." I'm treating **blank → Fund**. This is load-bearing — every KPI number
> below depends on it. If blank were treated as `Others`, yellow's stack would show as 0%
> fund-owned.

---

## 2. What has to change in the HTML

### 2a. The four KPIs silently change meaning — this is the real breakage

`StackSection` (`dashboard.template.html:1096`) computes `totalK`, `vacantK` and
`S.floors.length` across **every unit in the sheet**. Those were fund-scoped only by
accident of the old data. With the new sheet, the same code reports the whole building
under labels that say "Total Floor Area" and "Vacant Area".

The damage is split across two moments, because 10 rows are dropped today (§3a) and will
stop being dropped once the ingest filter is relaxed:

| Asset | ASSETS Leasable | Area KPI **today** | Area KPI **after §4 step 2** | Floors KPI |
|---|---|---|---|---|
| green  | 120K | **232K** ✗ | 232K ✗ | 2 → 5 |
| red    | 380K | **529K** ✗ | 529K ✗ | 9 → 11 |
| blue   | 170K | 172K ✓ | **260K** ✗ | 1 → 4 |
| white  |  40K | 40K ✓ | 40K ✓ | **1 → 7** |
| yellow | 223K | 223.6K ✓ | 223.6K ✓ | unchanged |

Read that carefully: **green and red are already wrong today.** `blue` and `white` look
right only because the rows that would inflate them are the very rows the filter is
currently suppressing.

Nothing errors. The numbers just quietly stop meaning what the label says, on the tab
whose whole job is showing what we hold. This needs either a Fund/Building split in the
KPI row, explicit relabelling, or — cleanest — a **Fund-only / Whole-building toggle** on
the panel, with the KPIs following the toggle.

**Bounding the blast radius (good news):** `stack_plan` feeds only `_build_stack_plan` →
`StackSection`. No other tab consumes it. The whole-building rows therefore cannot move
any number on Portfolio, Executive, Financial or Expenses — this change is contained to
the Stack Plan tab.

### 2b. Ownership should be a second visual dimension, not a new column

Category already owns the fill colour (`catColor`). Ownership is orthogonal, so it should
be *treatment*, not hue:

- `Fund` → solid, as today
- `Others` → desaturated / outlined / reduced opacity
- one extra legend entry, and Fund/Others added to the hover tooltip

This is the "room" the change actually calls for. It does not need extra horizontal space —
which matters, because the existing layout has no room to spare.

### 2c. Area-less units need a fallback block

`_z(row["Area (K sft)"], 2)` maps a missing area to `0`, and the unit renders with
`flex: 0`. `white` would draw six floors as **empty rows with just a floor label**. Needs a
fixed-width neutral block for unknown area, or those floors look broken.

Related, same fix: `maxFloor = Math.max(...floorTotals)` is `0` if every floor on an asset
has a blank area, making `ft/maxFloor` render `width: NaN%`. Not reachable today (white
still has floor 10 at 40K), but it is one blank cell away once the filter is relaxed.

### 2d. (Pre-existing) proportional floor width appears to be inert

`dashboard.template.html:1134`:

```jsx
<div style={{flex:1, display:'flex', gap:5, height:54, width:`${ft/maxFloor*100}%`}}>
```

`flex: 1` expands to `flex-basis: 0%`; for a flex item, a non-`auto` flex-basis takes
precedence over `width` for main-size. So every floor bar should render full-width and
`ft/maxFloor` never applies. That would mean floors have never been scaled by area.

This predates the current change, but it starts to matter now: whole-building data creates
much wider disparity (blue `G` with no area sitting beside `3rd to 7th` at 172K).

*Confirmed empirically during the fix: the old build rendered `width:100%` on every floor
bar regardless of area; after moving the sizing onto `flex-basis` the same asset renders
`28.3%` / `100%`. Floor bars really had never been scaled by area.*

---

## 3. Data-quality items for the RE team

### 3a. 10 stack-plan rows are silently dropped

`_ROW_KEYS["stack_plan"] = ("Floor No.", "Area (K sft)", "Category")` keeps a row only if
**all three** are populated. Most of the newly added building rows fail:

| Row | Asset | Floor | Tenant | Missing |
|---|---|---|---|---|
| 21 | blue | G | Tata EXL | Area, Category |
| 22 | blue | 1 | Tata EXL | Category |
| 23 | blue | 2 | Yash Technologies | Category |
| 30 | white | G | Hafele India | Area, Category |
| 31 | white | 1 | Aker Powergas | Area, Category |
| 32 | white | 2 | HDFC Bank Limited | Area, Category |
| 33 | white | 3rd to 7th | Aker Powergas | Area, Category |
| 34 | white | 8 | Orange Business Services | Area, Category |
| 35 | white | 9 | Indian Regsiter of Shipping | Area, Category |
| 54 | red | G | Lobby and Retail Area | Area |

Net effect: `blue` and `white` lose almost the entire whole-building view that this change
was made to add. `red`'s ground-floor lobby also disappears — it *was* rendering before
(it had area 10 in the old sheet). The build prints `dropped 28 empty template row(s)`,
which reads as harmless template padding; 10 of those are real data.

### 3b. `IT` vs `it` casing — a new regression

`Category` now contains **both** `IT` and `it`. The legend key is lowercase `it`, so
`catColor('IT')` returns `undefined` and those units render with `background: undefined`.
Affects `blue` / WNS and `white` / Mirae Asset Sharekhan — **both were lowercase `it` in the
old file**, so this is newly introduced. Cheapest fix is case-folding Category on ingest,
which also hardens against it recurring.

### 3c. `9 · APPROVALS` — Excel date serials leaking as raw numbers

`yellow`'s approvals block (rows 33-38) was replaced with real Maharashtra data. Four
`Validity` cells are unformatted date serials and will render literally as
**`46326`, `46203`, `46331`, `46290`** (rows 34, 36, 37, 38). Row 35 also has
`Risk Level = "NO"`, which isn't a valid risk level.

### 3d. `green` fund-held area overshoots its leasable area

`green`'s Fund-owned stack rows total **127K sft** against a stated leasable of **120K**
(5.8% over). Every other asset lands within ~2%. Combined with 3e below — both point at
`green` — this looks like a floor area or an Ownership flag being wrong rather than
rounding. The regression test uses a 10% tolerance, so this passes today; tighten the
tolerance once the RE team confirms the correct figure.

### 3e. Occupancy figures don't reconcile

Ingest warns on both:
- `green`: stated 75.00% vs leased/leasable 83.33%
- `red`: stated 87.89% vs leased/leasable 89.47%

### 3f. `10 · COMPLIANCE` — blank RAG Status

Register was substantially rewritten (82 → 98 rows; `red`, `white`, `blue` expanded,
`violet` / `indigo` / `silver` / `teal` emptied out). Six rows have **blank RAG Status**
(red r29, white r79, blue r87/92/93/94). Checked: these do *not* crash and are not dropped
— they render with an empty RAG pill and are excluded from the summary counts. Cosmetic,
but the counts won't sum to the row count.

---

## 4. Suggested order of work

1. Fix the `financial_usage` rename — **both** `ingest.py` and the hardcoded labels in
   `build_dashboard.py:277-280`. Unblocks the build.
2. Relax `_ROW_KEYS["stack_plan"]` to `("Floor No.",)` so building rows survive; case-fold
   `Category`; read `Ownership` through `_build_stack_plan` (blank → `Fund`, pending
   confirmation).
3. HTML: ownership treatment + legend + tooltip; fallback block for unknown area.
4. HTML: resolve the KPI scoping — Fund/Building toggle or split KPIs.
5. Send §3 back to the RE team.

**Do not ship step 2 on its own.** Relaxing the row filter takes the area KPI from
wrong-on-two-assets to wrong-on-four (see §2a) — the suppressed rows are exactly what
inflates `blue`. Step 2 is a net regression unless step 4 lands with it. Steps 1-2 remain
prerequisites: the HTML work in 3-4 has nothing to render without them.


---

## 5. What shipped

**`ingest.py`**
- `financial_usage` required columns follow the renamed sheet labels, plus a
  `_COLUMN_ALIASES` shim so the superseded workbook still ingests instead of crashing.
- `_ROW_KEYS["stack_plan"]` relaxed from `(Floor, Area, Category)` to `(Floor,)`. Area and
  category are genuinely unknown on third-party floors; requiring them dropped 10 real rows.
- `Category` is lower-cased on ingest, fixing the `IT` vs `it` colour lookup.
- `Ownership` normalised, defaulting to `Fund` when blank or absent (older workbooks).

**`build_dashboard.py`**
- Usage category labels updated to match the sheet.
- `_build_stack_plan` emits `own` and `kKnown` per unit, plus a `totals` block scoped
  `Fund` / `Others` / `All`.
- Default workbook is now `data/real_estate_fund_data.xlsx`.

**`dashboard.template.html` — `StackSection`**
- **Fund / Building toggle** (reuses the existing `.seg` control). Defaults to **Fund**, so
  the headline numbers keep meaning what they always meant.
- KPIs are scope-aware and relabel themselves ("Fund Floor Area" vs "Building Floor Area").
- Third-party floors render dashed/outlined in their category colour; fund floors stay
  solid. One extra legend entry, and ownership in the tooltip.
- Unknown-area units draw at a nominal width showing "area n/a" instead of collapsing.
- Proportional floor width fixed: sizing moved off the inert `width` onto `flex-basis`
  (§2d confirmed — floor bars really were all rendering full-width).
- Toggle and third-party legend are hidden when an asset has no third-party floors, so the
  older workbook renders exactly as before.

### Verification

- `Fund` scope area reconciles with `2 · ASSETS` leasable on every asset: blue 172K/170K,
  white 40K/40K, yellow 223.6K/223K, green 127K/120K, red 388K/380K.
- All 7 JSX blocks transpile; `StackSection` renders headlessly for all 5 assets in both
  scopes with no `undefined` and no `NaN`.
- Hover tooltips exercised directly — they carry category, colour, area (or "area n/a")
  and Fund-held/Third-party.
- 8 new regression tests. Suite: 14/15 pass; the one failure
  (`test_filled_workbook_retains_all_assets`) is pre-existing and unrelated — it references
  `tests/fixtures/filled_fund_data.xlsx`, which is optional and not in the repo.
