# CLAUDE.md

Guidance for Claude Code sessions working in this repository.

## 1. Project summary

**PyGoDevOps-guide** (the code and the README call the app **`roadmap-site`** —
both names are in use, see §7) is a personal, self-hosted Flask site that tracks
one person's progress through a "Python + Go → DevOps" learning plan.

- The plan is 12 phases / 77 lessons (`data/lessons_data.py`), covering Python
  basics → Python for automation → Project 1 (Homelab Monitoring & Alerting API)
  → Go basics → Go concurrency/CLI → Project 2 (Metrics Exporter + Health-check
  CLI) → CI/CD and portfolio packaging → and, as a continuation, the DevOps
  tooling track: Ansible (`a1`) → CI/CD + Terraform (`a2`) → Kubernetes/k3s
  (`a3`), 7 lessons each.
- The index page (`/`) lists phases as collapsible blocks with a checkbox per
  lesson, per-phase counters and an overall progress bar.
- Each lesson also has its own page (`/lesson/<lesson_id>`) with a long-form
  Markdown write-up, a "mark as done" toggle, related links, personal notes and
  prev/next navigation through the whole course (Stepik-style).
- A lesson is modelled as up to three steps — **Theory → Practice → Verify**
  (§4a). Theory is the Markdown write-up and is always there; Practice and
  Verify come from optional fields on the lesson dict, so their sections simply
  don't render when those fields are absent — which is the case for all 56
  lessons of the original course. All 21 lessons of the devops track do have
  both fields (one `verify` criterion each, as the source roadmap was written).

**Audience: a single user, personal use.** There is no login, no accounts, no
per-user data — one shared progress table. Do not add multi-tenancy, user
models, or sessions unless explicitly asked. (README §4 notes that if the site is
exposed to the internet, protection is HTTP basic auth at the reverse proxy, not
in the app.)

**Language: everything user-facing and every comment is Russian.** UI strings,
templates, docstrings, code comments, the README, and all lesson text are in
Russian. New lessons, templates, and comments must be written in Russian too.

## 2. Stack

- **Flask 3.1.3** — server-rendered Jinja2 templates.
- **SQLite** (stdlib `sqlite3`) — progress state only.
- **Markdown 3.10.3** — renders lesson bodies to HTML server-side.
- **gunicorn 26.2.0** — the process manager used inside the Docker image.
- **Vanilla JS + hand-written CSS** — `static/app.js`, `static/style.css`.

**No frontend framework, no build step, no bundler, no package.json.** This is
intentional for a small personal site on a modest home server. Do **not**
introduce React, Vue, Svelte, Tailwind, webpack, vite, npm, or a CSS
preprocessor unless explicitly asked. Likewise there is no ORM — plain `sqlite3`
and plain SQL.

There are no tests, no linter/formatter config, and no `.github/` workflows in
this repo. Don't go looking for them.

## 3. File structure

```
app.py                    Flask app: all routes, DB helpers, Markdown rendering
requirements.txt          Flask, gunicorn, Markdown (pinned)
Dockerfile                python:3.13-slim, non-root appuser, healthcheck, gunicorn
docker-compose.yml        service "roadmap" (container "roadmap-site"), 8080:5000
.dockerignore/.gitignore  both exclude venv/, __pycache__/, *.pyc, progress.db
README.md                 Russian setup/deploy guide (see §7 about drift)
data/
  __init__.py             empty — makes data/ an importable package
  lessons_data.py         ~740 lines: PHASES list + all_lesson_ids()
  lesson_content.py       ~7350 lines: CONTENT dict of long-form Markdown
templates/
  base.html               shell: inline theme script in <head>, sticky header,
                          theme toggle button, per-track progress bars, phase nav, reset form
  index.html              phase <details> blocks + lesson checkboxes + "continue" card
  lesson_detail.html      single lesson page: theory/practice/verify, notes, prev/next
static/
  style.css               the entire visual design, both themes (see §5)
  app.js                  progressive enhancement for checkbox toggling + the theme toggle click
  notes.js                debounced autosave for the per-lesson note
```

### Routes in `app.py`

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Index: phases + lessons + progress counters/percent |
| `/lesson/<lesson_id>` | GET | Lesson page; plain-text 404 if the id is unknown |
| `/toggle/<lesson_id>` | POST | Flip the lesson's own done/not-done (= "theory done"); JSON or redirect (see below) |
| `/step/<lesson_id>/<step>` | POST | Flip one extra step: `practice` or `verify-<n>`; JSON or redirect |
| `/reset` | POST | Set every lesson back to not-done, then redirect to `/` |
| `/healthz` | GET | `{"status": "ok"}` — used by the Docker HEALTHCHECK |

`FLAT_LESSONS` is built once at import time from `PHASES` and backs the
prev/next navigation on lesson pages.

### `lessons_data.py` vs `lesson_content.py` — the split

Both are plain Python, not a database. Content lives in code; only *state* lives
in SQLite.

- **`data/lessons_data.py` — the lightweight index/metadata.** `PHASES` is a list
  of dicts: `code` (anchor id, e.g. `"p1"`), `track` (`"py"` / `"go"` /
  `"devops"` / `"project"` — this drives the accent colour, see §5), `title`,
  `meta` (e.g. `"Недели 1–3 · ~18 ч"`), `why`, and `lessons`. Each lesson dict
  has a unique `id` (e.g. `"p1-4"`), `title`, a short `text`, an optional `task`,
  and optional `links` (`[{"title": ..., "url": ...}]`). `all_lesson_ids()`
  returns the flat list of ids used to seed the DB.
  Two more optional lesson fields drive the Practice/Verify sections (§4a):
  `practice` — `list[str]`, ordered hands-on steps; `verify` — `list[str]`,
  "done when…" criteria. Present on the 21 devops lessons (`a1-*`/`a2-*`/`a3-*`),
  absent on all 56 lessons of the original course. A `practice` step may contain
  newlines (a1-1 embeds an `inventory.ini` snippet), so `.practice-list li` is
  `white-space: pre-wrap`.
- **`data/lesson_content.py` — the long-form lesson text.** A single `CONTENT`
  dict keyed by the same lesson `id`; values are raw Markdown strings
  (`r'''...'''`). Rendered with the `fenced_code`, `tables` and `sane_lists`
  extensions. All 77 lessons currently have content. A missing key is not an
  error: the lesson page falls back to the short `text` from `lessons_data.py`.

**When adding a lesson:** add the dict to the right phase in `lessons_data.py`
with a new unique `id`, optionally add a matching `CONTENT[id]` entry, and
restart. `init_db()` inserts a row for the new id on startup
(`INSERT OR IGNORE`), so existing progress is untouched — progress is keyed by
`id`, not by position in the list.

## 4. Data architecture

- **Content** (phases, lessons, Markdown) lives in the Python files above, in git.
- **State** lives in SQLite — three tables, all created by `init_db()` with
  `CREATE TABLE IF NOT EXISTS`:
  - `progress` (`lesson_id TEXT PRIMARY KEY`, `done INTEGER NOT NULL DEFAULT 0`,
    `updated_at TEXT`) — the lesson's own checkbox. Seeded with one row per
    lesson id via `INSERT OR IGNORE`.
  - `notes` (`lesson_id TEXT PRIMARY KEY`, `content TEXT NOT NULL DEFAULT ''`,
    `updated_at TEXT`) — personal notes. Not seeded: no row = no note.
  - `lesson_steps` (`lesson_id TEXT`, `step TEXT`, `done INTEGER`,
    `updated_at TEXT`, PK `(lesson_id, step)`) — the extra steps, `step` being
    `"practice"` or `"verify-<n>"`. Not seeded either: no row = not done.
- **The schema only ever grows.** Never drop or rewrite an existing table or
  column; add a new table (or a new `step` key) next to what's there, so a
  `progress.db` that has been running on the server since the first version
  keeps opening. Anything new must be safe to create on every startup.
- **`progress.db` is NOT in the repo** — it is in both `.gitignore` and
  `.dockerignore`. Never commit it.
- **Persistence in Docker is a named volume**, not a bind mount:
  `progress-data:/app/db` in `docker-compose.yml`. It survives
  `docker compose down` and image rebuilds. Backup:
  `docker compose cp roadmap:/app/db/progress.db ./progress-backup.db`.
- **`DB_PATH` environment variable pattern** (`app.py`):
  ```python
  DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "progress.db"))
  ```
  Default = `progress.db` next to `app.py` (local dev). The Dockerfile sets
  `ENV DB_PATH=/app/db/progress.db` so the file lands on the mounted volume.
  Keep this pattern: any new file-backed state should be configurable the same
  way and live under `/app/db`.
- `get_db()` opens a connection per call with `check_same_thread=False`
  (gunicorn threads) and `row_factory = sqlite3.Row`. `init_db()` is called at
  import time, so it runs under both `python app.py` and gunicorn.

### 4a. The three-step lesson model — Theory / Practice / Verify

A lesson can show up to three sections on its page, each rendered only if the
lesson has data for it:

| Step | Icon | Source | Checkbox |
|---|---|---|---|
| Theory | 📖 | `CONTENT[lesson_id]` in `lesson_content.py` | the lesson's own toggle (`/toggle`, table `progress`) |
| Practice | 🔧 | optional `practice: list[str]` on the lesson dict | one toggle for the whole list (`step = "practice"`) |
| Verify | ✅ | optional `verify: list[str]` on the lesson dict | one per criterion (`step = "verify-<n>"`) |

**"Done" still means "theory done".** The top-level checkbox — on the index, on
the lesson page, in the phase counters, in the overall/per-track percent and in
the "continue learning" card — keeps exactly the meaning it always had: the row
in `progress`. Practice and Verify are *additional, independent* signals; they
are shown on the lesson page and stored in `lesson_steps`, and they deliberately
do **not** feed any counter. This was a conscious choice: redefining "done" as
"all three steps done" would have silently changed every existing number and
would leave a lesson with no practice section permanently un-completable.

Rules that keep this honest:

- **The read path is driven by the code, not by the DB.** `get_lesson_steps()`
  builds the verify list from `lesson["verify"]` and looks each index up, so if
  a `verify` list later shrinks from 3 items to 2, the stale `verify-2` row is
  simply never read. No migration, no cleanup.
- **The write path validates against `lessons_data.py`.** `_step_exists()` is
  the gate in `/step`: a POST for a step the lesson doesn't have returns 404
  instead of inserting a junk row.
- **A lesson with neither field renders exactly as before** — the "📖 Теория"
  heading itself only appears when the lesson has `practice` or `verify`. That
  is what keeps the 56 existing lessons free of empty boxes and stray labels.
- `/reset` clears `progress` **and** `lesson_steps` (notes survive).

### Progressive enhancement — preserve it

Every checkbox is a real `<form method="post">` posting to `/toggle/<id>`, so the
site works with JavaScript disabled. `static/app.js` intercepts the submit,
re-posts with the header `X-Requested-With: fetch`, and `/toggle` branches on
that header: JSON for fetch, `redirect(request.referrer)` otherwise. If the fetch
fails, the JS falls back to `form.submit()`. Do not replace this with a JS-only
flow. The Practice/Verify checkboxes work the same way — real forms posting to
`/step/<id>/<step>`, marked `class="toggle-form step-form"`; `app.js` handles
them in a separate branch because their JSON response carries only that step's
state (they don't move the course counters).

## 5. Design constraints — do not change without being explicitly asked

The look is deliberate. `static/style.css` is the single source of truth: it
opens with a header comment describing the system, and every colour, spacing
step, radius, font size and transition in the file comes from a custom property
declared at the top. **There are no colour literals in the rules themselves** —
to change the palette you edit the two theme blocks, nothing else.

### The card system

Content sits on *elevated cards*, not in outline-only frames. There are four
surface levels and they always nest in this order:

| Token | What it is | Used by |
|---|---|---|
| `--bg` | page background | `body` |
| `--surface` | a card on the page | `details.phase`, `.lesson-page`, `.continue-card`, `.topbar`, `.sticky-nav`, `.nav-btn` |
| `--surface-sunken` | a recessed area *inside* a card | `.ph-body`, `pre`/`code`, blockquote, `th`, chips, buttons, `.note-area` |
| `--surface-raised` | a card inside the recessed area | `ul.lessons li`, `.verify-list li` |

Plus `--surface-hover` for hover fills. Cards get `--shadow-1` at rest and
`--shadow-2` on hover, and radii from `--r-lg` (14px, cards) → `--r-md` (10px,
nested cards) → `--r-sm` (7px, chips and buttons).

**In light mode the shadow carries the elevation.** In dark mode it cannot —
a shadow does not read against a near-black page — so there the card reads as
raised because *its surface is lighter than the page*, with the shadow only
supporting it (a dark halo below plus a barely-there `inset 0 1px 0` white
highlight along the top edge). If you change the dark surfaces, keep them
ordered lightest-on-top or the depth collapses.

The page background is `#08070e`, no longer literally pure black — a very
near-black that lets the cards sit above it. Don't push it back to `#000000`
without also rethinking the elevation.

### Two themes

- `:root` **is the dark theme**; `:root[data-theme="light"]` overrides the same
  tokens for the light one. There is deliberately **no `prefers-color-scheme`
  media query in the CSS** — duplicating the whole palette into one is exactly
  what the token layer exists to avoid.
- The theme is applied by a small inline script in `base.html`'s `<head>`,
  **before the page paints** (doing it from `app.js`, which loads at the end of
  `<body>`, makes the site flash the wrong colours). It reads `localStorage`
  first, falls back to `matchMedia("(prefers-color-scheme: light)")`, and stamps
  `data-theme` on `<html>` either way.
- **Nothing is written to `localStorage` until the toggle is clicked** (the
  click handler is `setupThemeToggle()` in `app.js`). That is what keeps the
  site following the OS setting until the user makes an explicit choice —
  writing the detected value on first visit would freeze it forever.
- Known trade-off: with JS disabled no `data-theme` is set, so `:root` applies
  and the visitor always gets the dark theme regardless of their OS.
- highlight.js: `<link id="hl-theme">` in `<head>` carries **no `href`** and two
  data attributes, `data-dark` / `data-light`, pointing at the cdnjs
  `github-dark` / `github` stylesheets. Both the head script and the toggle
  handler set `href` from them. An empty `href` fetches nothing, and without JS
  highlight.js does not run at all, so there is no fallback to add. The CDN file
  is only a skeleton anyway — the `--hl-*` variables at the bottom of
  `style.css` (a set per theme) are what actually colours the code, and they are
  what keeps highlighting correct when the CDN is unreachable on the home LAN.

### Track colour-coding is meaningful — preserve it

The `track` field on each phase maps to a `track-*` CSS class, which sets two
inherited custom properties, and everything inside picks them up:

- `--accent` — the track's single colour: link and heading colours, hover
  states, focus outline, `.note-status.ok`.
- `--strip` — the track's colour *as an image*, for the 4px edge and the
  checkbox fill.

| Class | `--accent` | Meaning |
|---|---|---|
| `track-py` | `--purple` | Python track |
| `track-go` | `--blue` | Go track |
| `track-project` | `--project` | project phases (a neutral, not a hue) |
| `track-devops` | `--purple` | phases `a1`/`a2`/`a3` — see below |

Each has different values per theme: `--purple` is `#a78bfa` in dark but
`#6d43c8` in light, `--blue` `#5b9dff` / `#2563eb`, `--project` a near-white
`#cbc7e2` in dark and a slate `#5b6478` in light. The dark values wash out on
white; that is why the light theme has its own. Don't collapse the tracks to a
single accent and don't reassign which track owns which colour.

**Since the redesign the track colour is a small accent detail, not the whole
outline of the block.** It shows up in exactly three places: a 4px strip down
the left edge of a card, a 7px dot before each phase link in the header, and the
fill of a ticked checkbox. Cards themselves have a neutral `--border`. Keep it
that way — colouring a whole card border again brings back the noise the
redesign removed.

### `--strip` must always be an image

Even for a solid colour, write it as `linear-gradient(c, c)` and never as a bare
colour. The rules draw it as

```css
background: var(--strip) left / var(--strip-w) 100% no-repeat, var(--surface);
```

and in that shorthand a bare colour is parsed as `background-color`, so the
"strip" floods the entire element. This costs a debugging round every time it is
forgotten.

### The devops track has no hue of its own, on purpose

Ansible is Python, the Kubernetes ecosystem is Go — so the track is painted as a
transition from `--purple` to `--blue` instead of a fourth colour. **Do not add
a devops colour variable.** Because `--strip` is a background image, the
gradient works unchanged for the left edge, the header dot, the progress bar and
the ticked checkbox. The only place it cannot go is `outline-color` on the focus
ring, where the track falls back to `--accent` (purple). That is the intended
fallback, not an oversight.

(The old two-layer `padding-box` / `border-box` trick that painted a gradient
*border* is gone along with the coloured outlines — the strip replaced it. If
you ever need a gradient border again, that trick is still the way: `border-image`
kills `border-radius`.)

### Checkboxes are drawn by us

`input[type=checkbox]` is `appearance: none` — a rounded square matching the
cards, filled with `var(--strip)` when checked and stamped with an SVG tick.
This is what lets the devops checkbox be gradient-filled, which `accent-color`
could never do. It is still a plain `<input type=checkbox>`, so the forms,
`requestSubmit()` and `app.js` are untouched — do not replace it with a
`<span>`-based fake.

The tick colour cannot be a variable inside a `data:` URI, so two ready-made
images live at `:root`: `--check-white` and `--check-dark`, selected through
`--check-img`. The one override is `.track-project` in dark mode, whose fill is
near-white and would swallow a white tick.

Two gotchas that are already handled and should stay handled:

- `details.phase` needs `overflow: hidden` (otherwise the strip and the sunken
  body escape the rounded corners), and that clips its `summary`'s focus ring —
  hence `details.phase > summary:focus-visible{ outline-offset: -3px; }`.
- On the two smaller checkboxes the size override must be
  `background-size: 12px 12px, auto`: without the `, auto` it applies to the
  fill layer too and tiles the devops gradient.

### Motion

Short transitions (`--t-fast` 150ms, `--t` 180ms) on hover and focus only —
border, background, shadow, colour, and the nudge of the "continue" arrow. The
progress bars animate their width because `app.js` changes it live. There are no
`@keyframes` and nothing animates on load. A `@media (prefers-reduced-motion:
reduce)` block turns all of it off. Keep motion at this level; if something
genuinely needs more, ask first.

### Everything else

- **Header progress is per skill track, not one bar.** `build_track_stats()`
  walks `PHASES` and emits one row per track *in order of first appearance*, so
  the markup is not tied to how many tracks exist — a new track shows up in the
  header on its own. The one exception is `NON_SKILL_TRACKS` (currently just
  `"project"`): a row shows progress through a skill being learned, and the
  project phases are hands-on work over material already covered, so they get
  no row. Their lessons still count in the combined number. Today that is three
  rows — Python 24, Go 13, DevOps 21 — over a combined 77. Keep this an
  *exclusion*, never an allowlist, so the next skill track needs no code change.
  The combined percent and `done/total` survive as a small monospace readout
  next to the title: with tracks of very different sizes it is a rough reference
  number, not the headline any more. Track labels are short on purpose
  (`Python` / `Go` / `DevOps`) — the name column is 54px (46px on mobile).
- **Typography:** monospace for headers/meta/code — the percent readout,
  counters, `.ph-meta`, `.task`, `.res-title`, `.done-toggle`, `.reset-btn`,
  code blocks; the system sans stack (`-apple-system, "Segoe UI", Roboto, …`)
  for body text. No web fonts are loaded. Sizes come from the `--fs-*` scale
  (`--fs-xs` 11px … `--fs-xl` 21px) and spacing from `--sp-1` … `--sp-8`
  (4/8/12/16/20/24/32) — use a step, don't invent a one-off pixel value.
- Layout is a single `.wrap` column, `max-width: 860px`, mobile-friendly — the
  point of the site is ticking lessons off from a phone or a laptop. Verify
  changes at ~380px: the phase nav scrolls sideways as one row, and wide tables
  and code blocks must scroll inside their own box rather than widen the page.

## 6. Commands

Run everything from the repo root (`data/` is a package, so the app must start
from the root).

### Local dev (no Docker)

```bash
python -m venv venv
venv\Scripts\activate          # Windows (this machine); Linux/macOS: . venv/bin/activate
pip install -r requirements.txt
python app.py                  # Flask dev server, debug=True, http://127.0.0.1:5000
```

`python app.py` is the local path: it binds `0.0.0.0:5000` with `debug=True`
(reachable from the LAN). `flask run` is not equivalent — it binds
`127.0.0.1:5000` and needs `--debug` for the reloader. gunicorn is the
*container* entrypoint (`gunicorn -w 2 -b 0.0.0.0:5000 app:app`) and is not used
for local dev on Windows.

### Docker

```bash
docker compose up -d --build       # build + start; also how code changes are applied
docker compose ps                  # container should report "healthy"
docker compose logs -f roadmap     # service is "roadmap", container is "roadmap-site"
curl http://127.0.0.1:8080/healthz # -> {"status": "ok"}
```

**The port differs between the two modes:** local dev is `:5000`; Docker
publishes host `8080` → container `5000`. On the LAN the site is
`http://<server-ip>:8080`.

### Deploy workflow

Target: the user's home **Debian server**, running the app under Docker Compose.
Remote is `git@github.com:Itegin/PyGoDevOps-guide.git`, branch `main`.

```bash
# once, on the server
git clone git@github.com:Itegin/PyGoDevOps-guide.git roadmap-site
cd roadmap-site

# every deploy
git pull
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8080/healthz
```

`restart: unless-stopped` plus `sudo systemctl enable docker` brings the site
back after a server reboot. README §4 documents the optional public-access
setup: a DuckDNS subdomain refreshed by cron, ports 80/443 forwarded on the
router, and a `caddy:2-alpine` service added to compose that terminates TLS
(Let's Encrypt, automatic) and reverse-proxies to `roadmap:5000` behind
`basic_auth`. In that configuration the app no longer publishes 8080 and only
`expose`s 5000. The `Caddyfile` and that extra compose service are **not** in
this repo — they live on the server.

Alternative without git: `scp -r roadmap-site your-user@server-ip:~/roadmap-site`,
then the same `docker compose up -d --build`.

**⚠ Because the deploy is git-based, anything uncommitted does not ship.**
Commit and push before deploying, and verify with `git status` and
`git ls-tree -r --name-only origin/main` rather than trusting notes in this file.

## 7. Notes / known drift

- **README §5 is out of date.** It says all guide content lives in
  `data/lessons_data.py`; that predates `data/lesson_content.py`. §3 above is
  authoritative on the split.
- The README calls the project `roadmap-site` (and uses that as the clone
  directory); the GitHub repo is `PyGoDevOps-guide`. Same project. The compose
  *service* name is `roadmap`, the container name is `roadmap-site`.
- The history starts with two commits both titled "Initial commit: roadmap
  tracker"; later commits have normal messages.
- An earlier version of this file warned that the lesson-detail feature was
  missing from `origin/main`. That is no longer true — it was pushed in
  `13c3794` / `b68bffb` / `3a81fc0`. Since the deploy is `git pull` on the
  server, the rule still stands: uncommitted work does not ship. Check with
  `git status` and `git ls-tree -r --name-only origin/main`, not with notes here.
- §5 used to describe a pure-black, outline-only, animation-free look with a
  single `--panel` colour and `accent-color` checkboxes. That was replaced in
  `1ee24f8` / `ce9a0c2` / `fe96952` by the light theme and the card system now
  documented above. If you find a stray comment anywhere still promising "no
  animations" or "no filled panel backgrounds", it is left over from then.
