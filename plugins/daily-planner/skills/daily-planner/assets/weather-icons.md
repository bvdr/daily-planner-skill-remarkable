# Weather icons (inline SVG)

Drop the matching `<svg>` into the weather module. Icons use two classes from
`planner.css`: `.sun` (filled with `--sun`) and `.cloud` (white fill, ink outline).
On a colour device set `<body class="color">` and the sun renders warm; on a mono
device it renders as a filled black disc behind the cloud. Pick by condition:

| condition                | icon key            |
|--------------------------|---------------------|
| clear / sunny (day)      | `clear-day`         |
| clear (night)            | `clear-night`       |
| partly / mostly cloudy   | `partly-cloudy-day` |
| overcast / cloudy        | `cloudy`            |
| rain / showers / drizzle | `rain`              |
| thunderstorm             | `storm`             |
| snow / sleet             | `snow`              |
| fog / mist / haze        | `fog`               |

Common cloud shape used below: `M78 82 H38 a17 17 0 0 1 -3 -33 a22 22 0 0 1 43 5 a14 14 0 0 1 0 28 Z`

### clear-day
```html
<svg class="wx" viewBox="0 0 100 100"><g class="sun">
<circle cx="50" cy="50" r="18" fill="var(--sun)" stroke="none"/>
<g stroke="var(--sun)" stroke-width="3" stroke-linecap="round">
<line x1="50" y1="10" x2="50" y2="20"/><line x1="50" y1="80" x2="50" y2="90"/>
<line x1="10" y1="50" x2="20" y2="50"/><line x1="80" y1="50" x2="90" y2="50"/>
<line x1="22" y1="22" x2="29" y2="29"/><line x1="71" y1="71" x2="78" y2="78"/>
<line x1="22" y1="78" x2="29" y2="71"/><line x1="71" y1="29" x2="78" y2="22"/></g></g></svg>
```

### partly-cloudy-day
```html
<svg class="wx" viewBox="0 0 100 100">
<g class="sun"><circle cx="37" cy="36" r="14" fill="var(--sun)" stroke="none"/>
<g stroke="var(--sun)" stroke-width="3" stroke-linecap="round">
<line x1="37" y1="8" x2="37" y2="16"/><line x1="37" y1="56" x2="37" y2="64"/>
<line x1="9" y1="36" x2="17" y2="36"/><line x1="57" y1="36" x2="65" y2="36"/>
<line x1="17" y1="16" x2="23" y2="22"/><line x1="51" y1="50" x2="57" y2="56"/>
<line x1="17" y1="56" x2="23" y2="50"/><line x1="51" y1="22" x2="57" y2="16"/></g></g>
<path class="cloud" d="M78 82 H38 a17 17 0 0 1 -3 -33 a22 22 0 0 1 43 5 a14 14 0 0 1 0 28 Z"/></svg>
```

### cloudy
```html
<svg class="wx" viewBox="0 0 100 100">
<path class="cloud" d="M80 78 H34 a18 18 0 0 1 -3 -35 a23 23 0 0 1 45 5 a15 15 0 0 1 4 30 Z"/></svg>
```

### rain
```html
<svg class="wx" viewBox="0 0 100 100">
<path class="cloud" d="M78 62 H38 a17 17 0 0 1 -3 -33 a22 22 0 0 1 43 5 a14 14 0 0 1 0 28 Z"/>
<g stroke="var(--ink)" stroke-width="3" stroke-linecap="round">
<line x1="40" y1="72" x2="35" y2="88"/><line x1="55" y1="72" x2="50" y2="88"/>
<line x1="70" y1="72" x2="65" y2="88"/></g></svg>
```

### storm
```html
<svg class="wx" viewBox="0 0 100 100">
<path class="cloud" d="M78 60 H38 a17 17 0 0 1 -3 -33 a22 22 0 0 1 43 5 a14 14 0 0 1 0 28 Z"/>
<path d="M54 60 L44 82 H52 L46 96 L68 72 H58 L64 60 Z" fill="var(--sun)" stroke="none"/></svg>
```

### snow
```html
<svg class="wx" viewBox="0 0 100 100">
<path class="cloud" d="M78 62 H38 a17 17 0 0 1 -3 -33 a22 22 0 0 1 43 5 a14 14 0 0 1 0 28 Z"/>
<g fill="var(--ink)"><circle cx="40" cy="80" r="3"/><circle cx="56" cy="86" r="3"/>
<circle cx="70" cy="80" r="3"/></g></svg>
```

### fog
```html
<svg class="wx" viewBox="0 0 100 100">
<path class="cloud" d="M78 58 H38 a17 17 0 0 1 -3 -33 a22 22 0 0 1 43 5 a14 14 0 0 1 0 28 Z"/>
<g stroke="var(--ink)" stroke-width="3" stroke-linecap="round">
<line x1="30" y1="74" x2="78" y2="74"/><line x1="34" y1="86" x2="74" y2="86"/></g></svg>
```

### clear-night
```html
<svg class="wx" viewBox="0 0 100 100">
<path d="M64 20 a34 34 0 1 0 24 60 a28 28 0 0 1 -24 -60 Z"
 fill="var(--sun)" stroke="none"/></svg>
```
