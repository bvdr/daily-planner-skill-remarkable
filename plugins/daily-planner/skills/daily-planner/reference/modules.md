# Module catalog

The sheet is assembled from modules the user picks. Each module is a self-contained
block of HTML that uses the classes in `assets/planner.css`. Build the final HTML by:

1. Writing the **page setup** head (below) with the chosen device's size + toolbar side.
2. Dropping in the header + weather strip (if chosen).
3. Placing the remaining modules across the two `.col` columns, longest first
   (schedule usually fills the left column; priorities / follow-up / notes fill the right).
4. Footer.

Keep every module honest: only render a section if there is real content or the user
wants blank space to write on. Empty ruled space is fine (that is the point of a planner);
fake data is not.

---

## Page setup (write this per device)

`@page` size cannot read a CSS variable, so write it literally. `--toolbar-side-pad-left`
/ `-right` keeps the device's tool rail from covering content (see `devices.json`
`toolbar_side` + `toolbar_mm`). On a mono device set `--accent: #000`.

```html
<!doctype html><html><head><meta charset="utf-8">
<style>
@page { size: 179.7mm 239.5mm; margin: 0; }   /* <- chosen device page_mm */
:root { --toolbar-side-pad-left: 14mm; }        /* <- toolbar_mm on toolbar_side */
/* paste the full contents of assets/planner.css here */
</style></head>
<body><div class="sheet">
  <!-- header, weather, .cols, footer -->
</div></body></html>
```

Deliver via Folio: render to PDF with `scripts/render.py`, then `create_upload` +
`send_file` (reMarkable/Kindle), or Dropbox/Drive for Supernote. Name the file
`DD.MM.YYYY - Daily Plan - <Device label>.pdf` in the user's local date.

---

## Core modules (these match the reference one-sheet)

### header  (always on)
Data: date, city (from location), ISO week number, day-of-year.
```html
<div class="head">
  <div><div class="head__date">Thursday, 10 September</div>
       <div class="head__sub">Daily One Sheet &middot; Bucharest</div></div>
  <div class="head__meta">Week <b>37</b> Day 253 / 365</div>
</div>
```

### weather  — source: a weather API / connected tool, keyed on the user's location
Data: current temp + condition, high/low, rain %, wind, sunset, a few hourly points.
```html
<div class="weather">
  <div class="weather__now"><span class="weather__temp">24&deg;</span>
       <span class="weather__cond">Partly cloudy</span></div>
  <div class="weather__stats">H 27&deg; &nbsp; L 14&deg;<br>Rain 10% &middot; Wind 12 km/h<br>Sunset 19:42</div>
  <div class="weather__hours">
    <div class="hour">09<b>19&deg;</b></div><div class="hour">12<b>23&deg;</b></div>
    <div class="hour">15<b>27&deg;</b></div><div class="hour">18<b>24&deg;</b></div>
    <div class="hour">21<b>17&deg;</b></div>
  </div>
</div>
```

### schedule  — source: Google Calendar / user's dictation
Hour rows from the user's day start to end; events sit in the right cell. Leave empty
hours blank to write in. `.dur` is an optional duration chip.
```html
<div class="module sched">
  <div class="module__head">Schedule <span class="module__count">5 events</span></div>
  <div class="slot"><div class="slot__time">08:00</div><div class="slot__event"></div></div>
  <div class="slot"><div class="slot__time">09:00</div><div class="slot__event">Standup <span class="dur">15m</span></div></div>
  <div class="slot"><div class="slot__time">10:00</div><div class="slot__event"></div></div>
  <!-- one .slot per hour -->
</div>
```

### priorities  — source: user, Notion/Todoist tasks, GitHub issues assigned
Tick boxes to check off by hand. Add `prio__done` to `prio__check` to pre-tick.
Carried-over items use `.prio__carry`.
```html
<div class="module">
  <div class="module__head">Priorities <span class="module__count">3 of 6</span></div>
  <div class="prio__item"><div class="prio__check"></div>
    <div><div class="prio__text">Ship reMarkable send-file spine</div>
         <span class="prio__tag">Folio &middot; due today</span></div></div>
  <div class="prio__carry">&rarr; Draft Q3 retro notes <span class="prio__tag">carried 2 days</span></div>
</div>
```

### follow-up  — source: GitHub (PRs/issues), Slack, Gmail threads owed a reply
```html
<div class="module">
  <div class="module__head">Follow up <span class="module__count">GitHub &middot; 3</span></div>
  <div class="fu__item">
    <div class="fu__top"><span>bvdr/folio #412</span><span>3d</span></div>
    <div class="fu__title">Tables dropped in MCP read path</div>
    <div class="fu__meta">Awaiting your review</div>
  </div>
</div>
```

### notes  — blank ruled space to write on
```html
<div class="module lines">
  <div class="module__head">Notes</div>
  <div class="ln"></div><div class="ln"></div><div class="ln"></div><div class="ln"></div>
</div>
```

---

## Extra modules (offer these when asking "what to include")

- **top-3** — three big empty boxes for the day's most-important tasks (`.box` + label).
- **habit-tracker** — `.grid__row` per habit with a `.box` to tick.
- **time-block** — like `schedule` but 30-min rows and no event text, pure planning grid.
- **water-health** — a row of 8 `.box` cups + a steps/sleep line.
- **meals** — Breakfast / Lunch / Dinner ruled lines (`.lines`).
- **workout** — movement plan + a done box.
- **gratitude** — a `.prompt` line ("Three things...") over `.dotted` ruled lines.
- **reading** — the user's Folio reading queue: call `list_articles` and list a few titles with source.
- **quote** — a single centered line, quote of the day.
- **mood-energy** — a 1-5 scale row (five `.box`) for mood and for energy.
- **sleep** — last night hours + a quality 1-5 row.
- **expenses** — 3-4 ruled lines with an amount column to jot spend.
- **daylight** — sunrise / sunset / daylight length (from location); pairs well without full weather.
- **brain-dump** — a large `.dotted` ruled block for free writing.

All extras reuse the same classes (`.module`, `.lines`, `.box`, `.grid__row`). Compact
devices (Kindle, Supernote Nomad) should carry 3-4 modules max.
