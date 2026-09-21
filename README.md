# Daily Planner for reMarkable (and other e-ink tablets)

A Claude Code plugin + skill that builds a modular **daily one-sheet** planner, sized and
styled for your e-ink tablet, and delivers it to the device with [Folio](https://myfolio.so).

It interviews you, pulls from whatever you have connected (calendar, tasks, GitHub,
weather), renders an e-ink-optimized PDF at the exact page size of your device, and sends
it through Folio.

## What it does

- **Delivers via Folio** - picks the device connected in your Folio account. Suggests
  installing the Folio MCP (`https://myfolio.so/mcp`) if it is missing.
- **Knows your device** - reMarkable Paper Pro / rM2, Kindle Scribe, Supernote A5X /
  Nomad, Kindle. Uses the live render spec from Folio when available, built-in profiles
  otherwise. Keeps the tool-rail side clear so the toolbar never covers your plan.
- **Figures out your location** - for the date, week/day number, weather and sunrise.
- **Modular** - pick which sections to include: header, weather, schedule, priorities,
  follow-up, notes, plus top-3, habit tracker, time-block grid, water, meals, workout,
  gratitude, your Folio reading queue, quote, mood, sleep, expenses, daylight, brain-dump.
- **E-ink correct** - pure-black text, 30-40% form lines, whole-pixel strokes, no
  hairlines / greys / gradients. Built to be written on.

## Install

Add this marketplace in Claude Code, then install the `daily-planner` plugin:

```
/plugin marketplace add bvdr/daily-planner-skill-remarkable
/plugin install daily-planner
```

You also need the **Folio MCP** for delivery: https://myfolio.so/mcp

Rendering uses headless Chrome/Chromium (already on most machines); it falls back to
WeasyPrint (`pip install weasyprint`) if no browser is found.

## Use

Just ask:

> make my daily plan and send it to my reMarkable

The skill takes it from there.

## Layout

```
.claude-plugin/marketplace.json        # the marketplace
plugins/daily-planner/
  .claude-plugin/plugin.json           # the plugin
  skills/daily-planner/
    SKILL.md                           # the workflow
    reference/devices.json             # e-ink device profiles
    reference/modules.md               # module catalog + HTML snippets
    assets/planner.css                 # the e-ink stylesheet
    scripts/render.py                  # HTML -> print-exact PDF (Chrome/WeasyPrint)
```

## License

MIT
