#!/usr/bin/env python3
"""Build the daily one-sheet HTML from a JSON data file.

Usage: build_sheet.py <data.json> <out.html>

This encodes the fixed design decisions (layout, fonts, e-ink rules, half-hour
schedule, week/hourly weather, blank write-on rows, notes box that fills, optional
lined pages, toolbar-clear margins). The caller supplies only the *data*, so the
same sheet can be recreated from live data any time. Render the HTML with render.py.

Data shape (all fields optional unless noted; see reference/modules.md for the look):

{
  "page_mm": [179.7, 239.5],          # required, device page_mm
  "toolbar_side": "left",             # left|right|none -> that side gets the wider margin
  "color": true,                      # colour e-ink -> warm weather icons
  "device_label": "reMarkable Paper Pro",
  "date_line": "Tuesday, 22 September",
  "location": "Bucharest",
  "week": 39, "day_of_year": 265,
  "weather": {
    "current": {"temp": 17, "cond": "Partly cloudy", "icon": "partly-cloudy-day"},
    "mode": "week",                   # "week" (7-day) or "hourly"
    "week": [{"day": "Tue", "icon": "cloudy", "hi": 20, "lo": 12}, ...7],
    "hourly": [{"label": "09", "temp": 19}, ...],
    "stats": {"hi": 27, "lo": 14, "rain": "10%", "wind": "12 km/h", "sunset": "19:13"}
  },
  "schedule": {"start": "09:00", "end": "17:00", "step_min": 30,
               "events": {"09:00": {"text": "Standup", "dur": "15m"}}},
  "priorities": {"count_label": "3 of 6", "blank": 6,
                 "items": [{"text": "...", "tag": "...", "done": false}]},
  "followup":   {"count_label": "GitHub · 3", "blank": 4,
                 "items": [{"ref": "bvdr/folio #412", "age": "3d", "title": "...", "meta": "..."}]},
  "notes": true,
  "lined_pages": 1,
  "footer_left": "Tuesday, 22 September · Folio"
}

For a blank write-on sheet, omit `items` and set `blank` (a row count). icon keys are
the ones in assets/weather-icons.md; `wmo_icon`/`wmo_cond` below map open-meteo codes.
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CSS = (SKILL / "assets" / "planner.css").read_text()


def load_icons():
    md = (SKILL / "assets" / "weather-icons.md").read_text()
    keys = re.findall(r'^### (.+)$', md, re.M)
    svgs = re.findall(r'```html\n(<svg.*?</svg>)\n```', md, re.S)
    return dict(zip(keys, svgs))


ICONS = load_icons()

# open-meteo WMO weather_code -> (icon key, condition text). Convenience for the skill.
WMO = {0: ("clear-day", "Clear"), 1: ("clear-day", "Mainly clear"),
       2: ("partly-cloudy-day", "Partly cloudy"), 3: ("cloudy", "Overcast"),
       45: ("fog", "Fog"), 48: ("fog", "Fog"),
       51: ("rain", "Drizzle"), 53: ("rain", "Drizzle"), 55: ("rain", "Drizzle"),
       61: ("rain", "Rain"), 63: ("rain", "Rain"), 65: ("rain", "Heavy rain"),
       71: ("snow", "Snow"), 73: ("snow", "Snow"), 75: ("snow", "Heavy snow"),
       80: ("rain", "Showers"), 81: ("rain", "Showers"), 82: ("rain", "Heavy showers"),
       95: ("storm", "Thunderstorm"), 96: ("storm", "Thunderstorm"), 99: ("storm", "Thunderstorm")}


def icon(key):
    return ICONS.get(key, ICONS.get("cloudy", ""))


def deg(t):
    return f'{t}<span class="deg">&deg;</span>'


def esc(s):
    return str(s) if s is not None else ""


def header(d):
    date = esc(d.get("date_line"))
    loc = d.get("location")
    sub = "Daily One Sheet" + (f" &middot; {esc(loc)}" if loc else "")
    week = esc(d.get("week"))
    doy = esc(d.get("day_of_year"))
    meta = f'Week <b>{week}</b> Day {doy} / 365' if (week or doy) else ""
    return (f'<div class="head"><div><div class="head__date">{date or "&nbsp;"}</div>'
            f'<div class="head__sub">{sub}</div></div>'
            f'<div class="head__meta">{meta}</div></div>')


def weather(w):
    if not w:
        return ""
    cur = w.get("current", {})
    big = icon(cur.get("icon", "cloudy")) if cur else '<div class="wx"></div>'
    now = (f'<div class="weather__now"><span class="weather__temp">'
           f'{deg(cur.get("temp","&nbsp;"))}</span>'
           f'<span class="weather__cond">{esc(cur.get("cond")) or "&nbsp;"}</span></div>')
    if w.get("mode") == "hourly":
        stats = ""
        st = w.get("stats")
        if st:
            stats = ('<div class="weather__div"></div><div class="weather__stats">'
                     f'<b>H {deg(st.get("hi",""))} &nbsp; L {deg(st.get("lo",""))}</b><br>'
                     f'Rain {esc(st.get("rain",""))} &middot; Wind {esc(st.get("wind",""))}<br>'
                     f'Sunset {esc(st.get("sunset",""))}</div>')
        cells = ''.join(f'<div class="hour">{esc(h.get("label"))}<b>{deg(h.get("temp",""))}</b></div>'
                        for h in w.get("hourly", []))
        strip = f'<div class="weather__hours">{cells}</div>'
        return f'<div class="weather">{big}{now}{stats}{strip}</div>'
    # default: week outlook
    cells = ''.join(
        f'<div class="wday">{esc(x.get("day"))} {icon(x.get("icon","cloudy"))}'
        f'<b>{deg(x.get("hi",""))}</b><span class="lo">{deg(x.get("lo",""))}</span></div>'
        for x in w.get("week", []))
    return f'<div class="weather">{big}{now}<div class="weather__week">{cells}</div></div>'


def _add_minutes(hhmm, step):
    h, m = int(hhmm[:2]), int(hhmm[3:])
    total = h * 60 + m + step
    return f'{total//60:02d}:{total%60:02d}'


def schedule(s):
    if not s:
        return ""
    start = s.get("start", "09:00")
    end = s.get("end", "17:00")
    step = int(s.get("step_min", 30))
    events = s.get("events", {})
    rows = []
    t = start
    guard = 0
    while guard < 200:
        half = " half" if int(t[3:]) != 0 else ""
        ev = events.get(t)
        if ev:
            dur = f' <span class="dur">{esc(ev.get("dur"))}</span>' if ev.get("dur") else ""
            cell = f'<div class="slot__event has">{esc(ev.get("text"))}{dur}</div>'
        else:
            cell = '<div class="slot__event"></div>'
        rows.append(f'<div class="slot{half}"><div class="slot__time">{t}</div>{cell}</div>')
        if t == end:
            break
        t = _add_minutes(t, step)
        guard += 1
    label = s.get("count_label", "&nbsp;")
    return (f'<div class="module sched"><div class="module__head">Schedule '
            f'<span class="module__count">{label}</span></div>{"".join(rows)}</div>')


def priorities(p):
    if not p:
        return ""
    label = p.get("count_label", "&nbsp;")
    items = p.get("items")
    if items:
        body = ''.join(
            f'<div class="prio__item"><div class="prio__check{" prio__done" if it.get("done") else ""}"></div>'
            f'<div><div class="prio__text">{esc(it.get("text"))}</div>'
            f'<span class="prio__tag">{esc(it.get("tag"))}</span></div></div>' for it in items)
    else:
        body = ''.join('<div class="blank-row prio__blank"><div class="prio__check"></div></div>'
                       for _ in range(int(p.get("blank", 6))))
    return (f'<div class="module"><div class="module__head">Priorities '
            f'<span class="module__count">{label}</span></div>{body}</div>')


def followup(fu):
    if not fu:
        return ""
    label = fu.get("count_label", "&nbsp;")
    items = fu.get("items")
    if items:
        body = ''.join(
            f'<div class="fu__item"><div class="fu__top"><span>{esc(it.get("ref"))}</span>'
            f'<span class="fu__age">{esc(it.get("age"))}</span></div>'
            f'<div class="fu__title">{esc(it.get("title"))}</div>'
            f'<div class="fu__meta">{esc(it.get("meta"))}</div></div>' for it in items)
    else:
        body = ''.join('<div class="blank-row"></div>' for _ in range(int(fu.get("blank", 4))))
    return (f'<div class="module"><div class="module__head">Follow up '
            f'<span class="module__count">{label}</span></div>{body}</div>')


def notes():
    return ('<div class="module notes-fill"><div class="module__head">Notes '
            '<span class="module__count">&mdash;</span></div><div class="notes__box"></div></div>')


def footer(d):
    return (f'<div class="foot"><span>{esc(d.get("footer_left"))}</span>'
            f'<span>{esc(d.get("device_label"))}</span></div>')


def lined_page(title, date_line):
    lns = ''.join('<div class="ln"></div>' for _ in range(22))
    return (f'<div class="page2"><div class="p2head"><span>{title}</span>'
            f'<span>{esc(date_line)}</span></div><div class="lines">{lns}</div></div>')


def margin_for(side):
    if side == "right":
        return "12mm 18mm 12mm 12mm"
    if side == "none":
        return "12mm"
    return "12mm 12mm 12mm 18mm"  # left (reMarkable default)


def build(d):
    w, h = d.get("page_mm", [179.7, 239.5])
    margin = d.get("margin") or margin_for(d.get("toolbar_side", "left"))
    body_class = "color" if d.get("color") else ""
    right = priorities(d.get("priorities")) + followup(d.get("followup"))
    sheet = ('<div class="sheet">' + header(d) + weather(d.get("weather"))
             + '<div class="cols"><div class="col col--left">' + schedule(d.get("schedule")) + '</div>'
             + '<div class="col">' + right + '</div></div>'
             + (notes() if d.get("notes", True) else "") + footer(d) + '</div>')
    pages = ''.join(lined_page("Notes", d.get("date_line")) for _ in range(int(d.get("lined_pages", 0))))
    return ('<!doctype html><html><head><meta charset="utf-8"><style>'
            f'@page {{ size: {w}mm {h}mm; margin: {margin}; }}'
            + CSS + '</style></head>'
            f'<body class="{body_class}">' + sheet + pages + '</body></html>')


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    data = json.loads(Path(sys.argv[1]).read_text())
    Path(sys.argv[2]).write_text(build(data))
    pm = data.get("page_mm", [179.7, 239.5])
    print(f"built {sys.argv[2]}  ({pm[0]}x{pm[1]}mm)  -> render with render.py {pm[0]} {pm[1]}")


if __name__ == "__main__":
    main()
