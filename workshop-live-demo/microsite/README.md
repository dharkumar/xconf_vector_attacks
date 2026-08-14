# ShopBot Workshop Microsite

An offline, self-contained slide deck (reveal.js) for the 2.5-hour "The Lethal Trifecta: Breaking
and Defending AI Agents" workshop. Looks and presents like slides; is actually a website — no
build step, no internet required during the talk.

## Presenting it

Just open `index.html` in a browser (Chrome or Firefox recommended):

```bash
open index.html          # macOS
# or
python3 -m http.server   # then visit http://localhost:8000
```

Use the local-server option if the Speaker Notes popup window has trouble communicating over
`file://` in your browser — some browsers restrict `postMessage`/`localStorage` between a `file://`
page and its popup window.

**Controls:**
- Arrow keys / space / click to navigate
- `S` — open Speaker View (shows current + next slide, your notes, and a clock)
- `F` — fullscreen
- `ESC` — slide overview grid
- Click any code block to zoom it (zoom plugin)

**Lab timers:** the two hands-on lab slides (Lab 1: Red Team, Lab 2: Blue Team) have a built-in
countdown with ▶ start / ⏸ pause / ↺ reset controls, set to 30:00 and 35:00 respectively.

## Printing to PDF

Open with the `print-pdf` query string and use your browser's print dialog (destination: Save as
PDF, layout: landscape, margins: none, enable background graphics):

```
index.html?print-pdf
```

## Offline / no-wifi guarantee

Everything the deck needs — reveal.js itself, the theme, and all illustrations — is vendored inside
this folder (`vendor/reveal.js/`, `assets/`). Nothing is fetched from a CDN. To double-check before
a live session: open devtools → Network tab → set to "Offline" → reload the page. Nothing should
404.

## Structure

```
microsite/
├── index.html                          # the whole deck, one file
├── vendor/reveal.js/                   # vendored reveal.js 6.0.1 (see VENDORED.txt)
├── assets/
│   ├── css/theme.css                   # "hacker terminal meets flat cartoon" theme
│   └── js/deck.js                      # Reveal.initialize() + countdown timer component
└── labs/
    ├── lab1-red-team-challenges.md     # printable/shareable Lab 1 worksheet
    └── lab2-blue-team-checklist.md     # printable/shareable Lab 2 worksheet
```

Both hands-on labs run against the real code in `../workshop-live-demo/` — an 8-attack red-team
suite plus a Streamlit chat UI, run against a local Ollama model (`llama3`). No API key needed;
just `ollama serve` running with the model pulled.
