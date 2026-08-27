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
  base.html               shell: sticky header, per-track progress bars, phase nav, reset form
  index.html              phase <details> blocks + lesson checkboxes + "continue" card
  lesson_detail.html      single lesson page: theory/practice/verify, notes, prev/next
static/
  style.css               the entire visual design (see §5)
  app.js                  progressive enhancement for checkbox toggling
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

The look is deliberate. `static/style.css` is the single source of truth and
opens with a comment saying the site is personal, hence no animations and no
extra effects.

- **Pure black background** — `--bg: #000000`, and `--panel: #000000` too:
  panels are the *same* colour as the page and are visible only by their border.
  Content sits in bordered "frame" boxes (`--border: #332d55`, a muted purple
  outline) — phases, lessons, lesson pages, buttons, link chips. **No filled
  panel backgrounds.** The only darker fills are inside rendered Markdown (code
  `#14121f`, `pre` `#0a0912`, blockquote/table headers `#0e0c18`).
- **Track colour-coding is meaningful — preserve it.** The `track` field on each
  phase maps to a `track-*` CSS class:
  - `track-py` → **purple** `--purple: #a78bfa` — Python track
  - `track-go` → **blue** `--blue: #5b9dff` — Go track
  - `track-project` → **white** `--white: #f3f2fa` — project phases
  - `track-devops` → **a purple→blue gradient**, not a colour of its own —
    phases `a1` / `a2` / `a3` (Ansible, CI/CD + Terraform, Kubernetes)

  It drives the phase-nav border, the phase left border, checkbox
  `accent-color`, link and heading colours, and hover states. Don't collapse it
  to a single accent colour and don't reassign the colours.
- **The devops track has no hue of its own, on purpose.** Ansible is Python,
  the Kubernetes ecosystem is Go — so the track is painted as a transition from
  `--purple` to `--blue` instead of a fourth colour. **Do not add a devops
  colour variable.** The technique is the same everywhere: make the border (or
  just its left edge) `transparent` and paint the gradient as a *background*
  underneath it — `linear-gradient(...) left / 4px 100% no-repeat` for the left
  strips, and the two-layer `padding-box` / `border-box` trick for full borders.
  `border-image` is deliberately not used: it kills `border-radius`.
  Where a gradient is technically impossible — `accent-color` on checkboxes,
  `outline-color` on focus — the devops track just inherits the default purple.
  That is the intended fallback, not an oversight.
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
  for body text. No web fonts are loaded.
- **Animations: there are none.** No `transition` and no `@keyframes` anywhere in
  the stylesheet — state changes are instant, hovers simply swap colour. Keep it
  that way; if something genuinely needs motion, ask first.
- Layout is a single `.wrap` column, `max-width: 860px`, mobile-friendly — the
  point of the site is ticking lessons off from a phone or a laptop.

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
