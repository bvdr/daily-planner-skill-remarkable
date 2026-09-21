# Module catalog

The sheet is assembled from modules the user picks, using the classes in
`assets/planner.css`. It reproduces the reference "Daily One Sheet": a header, a
full-width weather strip, a two-column body (schedule left; priorities / follow-up
right), and a full-width notes box above the footer.

Build the final HTML like this:

1. Write the **page setup** head (below) with the chosen device's page size + toolbar side.
2. Header, then weather strip.
3. `.cols` with `.col.col--left` (schedule) and `.col` (priorities, follow-up).
4. Full-width notes module, then footer.

Only render a section with real content, or a blank write-on section the user asked for.
Blank ruled/boxed space is the point of a planner; fabricated events or tasks are not.

The reference module set fits one page at the sizes in `planner.css`. If the user picks
many long modules and it spills to a second page, drop a module, shorten items, or
narrow the schedule hour range rather than shrinking type below the sizes given.

---

## Page setup (write this per device)

`@page` size cannot read a CSS variable, so write it literally from the device
`page_mm`. Put `<body class="color">` for a colour device (reMarkable Paper Pro) so the
sun icon renders warm; omit the class on mono devices. Set the toolbar padding from
`devices.json` (`toolbar_side` + `toolbar_mm`) so the tool rail never covers content.

```html
<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: 179.7mm 239.5mm; margin: 12mm 12mm 12mm 18mm; }  /* top right bottom left */
/* paste the full contents of assets/planner.css here */
</style></head>
<body class="color">
  <div class="sheet"><!-- header, weather, .cols, notes, footer --></div>
  <!-- optional extra lined page(s) go here, see "lined page" below -->
</body></html>
```

Margins live in the **`@page` rule** so every printed page (including an extra lined page)
gets them. The **toolbar side gets the wider margin**: reMarkable's rail is on the left,
so `margin: 12mm 12mm 12mm 18mm`. Supernote's is on the right, so flip it to
`margin: 12mm 18mm 12mm 12mm`. Kindle Scribe has no rail: `margin: 12mm`.

Deliver: render with `scripts/render.py`, then Folio `create_upload` + `send_file`
(reMarkable / Kindle) or Dropbox / Drive (Supernote). Name the file
`DD.MM.YYYY - Daily Plan - <Device label>.pdf` in the user's local date.

---

## Core modules (match the reference sheet)

### header  (always on)
Date on one line (serif). Right side: week number + day-of-year.
```html
<div class="head">
  <div><div class="head__date">Thursday, 10 September</div>
       <div class="head__sub">Daily One Sheet &middot; Bucharest</div></div>
  <div class="head__meta">Week <b>37</b> Day 253 / 365</div>
</div>
```

### weather  — source: a weather API keyed on the confirmed location
Pick the icon from `assets/weather-icons.md` by condition. Every degree mark is wrapped
in `<span class="deg">&deg;</span>` so it stays in the serif and superscripts correctly.
```html
<div class="weather">
  <!-- paste the chosen icon svg from weather-icons.md here -->
  <div class="weather__now">
    <span class="weather__temp">24<span class="deg">&deg;</span></span>
    <span class="weather__cond">Partly cloudy</span>
  </div>
  <div class="weather__div"></div>
  <div class="weather__stats"><b>H 27<span class="deg">&deg;</span> &nbsp; L 14<span class="deg">&deg;</span></b><br>
    Rain 10% &middot; Wind 12 km/h<br>Sunset 19:42</div>
  <div class="weather__hours">
    <div class="hour">09<b>19<span class="deg">&deg;</span></b></div>
    <div class="hour">12<b>23<span class="deg">&deg;</span></b></div>
    <div class="hour">15<b>27<span class="deg">&deg;</span></b></div>
    <div class="hour">18<b>24<span class="deg">&deg;</span></b></div>
    <div class="hour">21<b>17<span class="deg">&deg;</span></b></div>
  </div>
</div>
```

**Week outlook (alternative to the hourly strip).** Swap `.weather__hours` for
`.weather__week` to show the next 7 days instead: each day gets its label, a mini icon
(the same SVGs from `weather-icons.md`, they scale to the 7mm `.wday .wx`), a bold high
and a lighter low. Drop the H/L from `.weather__stats` (or the whole stats block) when
you use this, since the week already carries highs and lows. Ask the user which they want.
```html
  <div class="weather__week">
    <div class="wday">Mon <!-- icon svg --><b>26<span class="deg">&deg;</span></b><span class="lo">13<span class="deg">&deg;</span></span></div>
    <div class="wday">Tue <!-- icon svg --><b>24<span class="deg">&deg;</span></b><span class="lo">12<span class="deg">&deg;</span></span></div>
    <!-- ...through Sun (7 cells) -->
  </div>
</div>
```

### schedule  — source: Google Calendar / dictation
One `.slot` per time step. Ask the user for the range and granularity; a **half-hour**
grid (e.g. 09:00-17:00) is a good work-day default and fills the column well. Add `has`
to `.slot__event` when it holds an event (draws the short left tick); leave empty ones
blank to write in. Add `half` to the `.slot` on every `:30` row so its rule is dotted and
its time smaller, which keeps the whole hours reading as the strong lines. `.dur` is an
optional duration chip.
```html
<div class="module sched">
  <div class="module__head">Schedule <span class="module__count">5 events</span></div>
  <div class="slot"><div class="slot__time">08:00</div><div class="slot__event"></div></div>
  <div class="slot"><div class="slot__time">09:00</div><div class="slot__event has">Standup <span class="dur">15m</span></div></div>
  <div class="slot"><div class="slot__time">10:00</div><div class="slot__event"></div></div>
  <!-- one .slot per step -->
</div>
```
Half-hour rows just add `half` and a `:30` time:
```html
<div class="slot half"><div class="slot__time">09:30</div><div class="slot__event"></div></div>
```

### priorities  — source: user, Notion/Todoist tasks, GitHub issues assigned
Every item has an empty `.prio__check` box to tick by hand. A carried item just prefixes
`&rarr;` and tags `Carried N days`.
```html
<div class="module">
  <div class="module__head">Priorities <span class="module__count">3 of 6</span></div>
  <div class="prio__item"><div class="prio__check"></div>
    <div><div class="prio__text">Ship reMarkable send-file spine</div>
         <span class="prio__tag">Folio &middot; due today</span></div></div>
  <div class="prio__item"><div class="prio__check"></div>
    <div><div class="prio__text">&rarr; Draft Q3 retro notes</div>
         <span class="prio__tag">Carried 2 days</span></div></div>
</div>
```

### follow-up  — source: GitHub PRs/issues, Slack, Gmail threads owed a reply
Repo/ref line is monospace with the age on the right.
```html
<div class="module">
  <div class="module__head">Follow up <span class="module__count">GitHub &middot; 3</span></div>
  <div class="fu__item">
    <div class="fu__top"><span>bvdr/folio #412</span><span class="fu__age">3d</span></div>
    <div class="fu__title">Tables dropped in MCP read path (turndown, no GFM)</div>
    <div class="fu__meta">Awaiting your review</div>
  </div>
</div>
```

### notes  — full-width box to write in (place after `.cols`)
```html
<div class="module"><div class="module__head">Notes <span class="module__count">&mdash;</span></div>
  <div class="notes__box"></div></div>
```

### footer
```html
<div class="foot"><span>10 September 2026 &middot; Folio</span><span>reMarkable Paper Pro</span></div>
```

### lined page  (optional extra page after the sheet)
A full ruled page for longer notes. Put it **after** `</div>` of `.sheet`, still inside
`<body>`. `.page2` forces a page break and fills the page with ruled lines; it inherits
the same `@page` margins (so the toolbar side stays clear). Add more `.page2` blocks for
more pages. Use `dotted` on `.lines` for a dot grid instead of rules.
```html
<div class="page2">
  <div class="p2head"><span>Notes</span><span>Thursday, 10 September</span></div>
  <div class="lines">
    <div class="ln"></div><!-- ~22 lines fill the page -->
  </div>
</div>
```

---

## Extra modules (offer these when asking "what to include")

Reuse the same classes.

- **top-3** — three big `.box` squares with a label, for the day's most-important tasks.
- **habit-tracker** — `.grid__row` per habit with a `.box` to tick.
- **time-block** — `sched` with 30-min rows and empty events, a pure planning grid.
- **water-health** — a row of 8 `.box` cups plus a steps / sleep line.
- **meals** — Breakfast / Lunch / Dinner over `.lines`.
- **workout** — a movement plan line with a done `.box`.
- **gratitude** — a `.prompt` ("Three things...") over `.dotted .ln` lines.
- **reading** — the user's Folio queue: `mcp__folio__list_articles`, list a few titles + source.
- **quote** — a single centered serif line.
- **mood-energy** — two rows of five `.box` (a 1-5 scale) for mood and energy.
- **sleep** — hours slept + a 1-5 quality row of `.box`.
- **expenses** — 3-4 `.lines` with room for an amount.
- **daylight** — sunrise / sunset / daylight length (pairs well when weather is off).
- **brain-dump** — a large `.dotted` ruled block, or a second `.notes__box`.

Compact devices (Kindle, Supernote Nomad) should carry 3-4 modules max.
