# Rawan · Portfolio

> كلما ظننت أنني فهمت وجدت ما يستحق أن أتعلّمه
> *Every time I think I understand I find something worth learning.*

A bilingual **single-page** personal portfolio in English and Arabic, built with **Python + FastAPI**.
All the text, links and images come from JSON files, so updating the content never means touching HTML.

---

## Run it

```bash
# 1. create & activate a virtual environment (you already have .venv)
python3 -m venv .venv
source .venv/bin/activate

# 2. install
pip install -e ".[dev]"

# 3. start the server (--reload picks up Python changes automatically)
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. English is the default. Use the toggle button or `/?lang=ar` for Arabic.
The browser remembers the last language a visitor chose, so if you switched before, press the toggle once to go back.
The auto-generated API docs are at <http://127.0.0.1:8000/docs>.

If the page ever looks out of date, press **⌘ + Shift + R** in the browser, or stop the server (Ctrl + C) and start it again.

Run the tests:

```bash
pytest
```

---

## Deploy (Render Static Site)

The live site is a **static build**: FastAPI renders the page once at build time and `freeze.py`
writes everything into `dist/`. No server runs in production, so the site never sleeps.

```bash
python freeze.py      # builds dist/ locally if you want to check it
```

`dist/` contains `index.html`, `static/`, `favicon.ico` and `api/learning-ideas.json`
(the ideas card reads this file on the static site, and `/api/learning-ideas` when running with uvicorn).
`dist/` is in `.gitignore`; Render builds it on every push.

| Render setting | Value |
|---|---|
| Service type | Static Site |
| Branch | `main` |
| Root Directory | *(empty)* |
| Build Command | `pip install ".[dev]" && python freeze.py` |
| Publish Directory | `dist` |
| Environment variable | `PYTHON_VERSION` = `3.14.8` |

---

## Page sections (top to bottom)

| # | Section | Template | Text key |
|---|---|---|---|
| 1 | Hero | `sections/hero.html` | `hero` |
| 2 | Professional experience (Musaned, systems, architecture) | `sections/experience.html` | `experience` + `experience.json` |
| 3 | Projects · من الأفكار إلى الأنظمة | `sections/projects.html` | `projects` + `projects.json` |
| 4 | Production troubleshooting | `sections/troubleshooting.html` | `troubleshooting` |
| 5 | Skills | `sections/learning.html` | `learning` |
| 6 | Learning & certifications | `sections/credentials.html` | `credentials` + `credentials.json` |
| 7 | What should I explore today? (ideas generator) | `sections/ideas.html` | `ideas` + `learning_ideas.json` |
| 8 | روان الرسّامة (drawings) | `sections/creative.html` | `creative` + `site.json → artworks` |
| 9 | حين حاولتُ أن أشرح (teaching story) | `sections/teaching.html` | `teaching` |
| 10 | Contact & «باختصار عنّي» | `sections/contact.html` | `contact` |

The order lives in `app/routers/pages.py` (`SECTIONS`) and the top menu in `NAV`.
"Text key" is the key in `ar.json` / `en.json`.

---

## Project structure

```
my-portfolio/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── routers/
│   │   ├── pages.py         # the single page ( / ) + section order
│   │   └── api.py           # /api/... content, projects, learning ideas
│   ├── templates/
│   │   ├── index.html       # page skeleton (nav, footer)
│   │   ├── macros.html      # icons + shared section header
│   │   └── sections/        # one file per section
│   ├── static/
│   │   ├── css/style.css    # colours, fonts, layout
│   │   ├── js/main.js       # language switch, reveals, filters, ideas generator, copy email
│   │   ├── files/           # ⬅ CV (PDF)
│   │   └── images/          # ⬅ character, drawings, icons
│   └── content/
│       ├── site.json        # ⬅ name, email, links, image paths, drawings
│       ├── ar.json          # ⬅ all Arabic text
│       ├── en.json          # ⬅ all English text
│       ├── experience.json  # ⬅ Musaned: job title, period, stack, systems list
│       ├── credentials.json # ⬅ earned + in-progress certifications
│       ├── projects.json    # ⬅ project cards (status, stack, links)
│       ├── learning_ideas.json # ⬅ the 30 ideas for the ideas card
│       └── loader.py        # reads the JSON (auto-reloads on change)
├── tests/
│   └── test_app.py
├── pyproject.toml
├── README.md
└── .gitignore
```

---

## ✏️ How to edit

### Personal details · `app/content/site.json`

| Field | What it is |
|---|---|
| `default_language` | The language a first-time visitor sees: `"en"` (current) or `"ar"` |
| `name.ar` / `name.en` | Your name in each language |
| `email` | Used by "Write to me" and "Copy email" |
| `links.linkedin` / `links.github` | Professional links |
| `links.teaching_video` | The YouTube video for the teaching story |
| `links.cv` | Your CV, currently `/static/files/Rawan_Alsofyani_CV.pdf` (replace the file to update it) |
| `images.profile` | The character illustration (`roro.png`) |
| `artworks[]` | The drawings in «روان الرسّامة» |

**Leave a link empty (`""`) and its button disappears.**

### Text

- Arabic lives in `ar.json`, English in `en.json`. Both files must have **the same keys**.
  The test `test_arabic_and_english_have_the_same_keys` tells you if one is missing.
- The Arabic hero title uses `\n` for its line break.
- Blocks shown as separate paragraphs are lists: `creative.paragraphs`, `teaching.paragraphs`, `experience.arch_text`.
- Changes show up on refresh. No restart needed for JSON.

**Writing style:** natural Saudi Arabic mixed with simple polished Arabic, few commas, no semicolons,
no periods on headings, buttons or labels. English stays natural with only the punctuation grammar needs.

### Section headings

All main section headings share one style: the `section-title` class. Its size, weight, line height and
spacing are tokens at the top of `style.css` (`--section-title-*`). Change them there and every heading follows.
The hero headline is intentionally larger.

### Experience · `experience.json` + `ar.json`/`en.json → experience`

- `title` (official job title) and `period` (e.g. `"2023 — present"`) are hidden while empty.
- `areas[]` is the simple list of systems you worked on, in display order, with no status labels.
  Their titles live in `experience.areas.<id>.title`.
- `experience.highlights` (both languages): confirmed, public-safe achievements. Hidden while empty.

### Projects · `projects.json` + `ar.json`/`en.json → projects.items`

1. Add an entry to `projects.json`:
   ```json
   { "id": "my-new-thing", "status": "in_progress", "image": "",
     "stack": ["Python"], "stack_learning": [], "links": { "live": "", "code": "" } }
   ```
2. Add its text under `projects.items` in **both** language files:
   ```json
   "my-new-thing": { "category": "…", "title": "…", "context": "…", "contribution": "", "challenge": "" }
   ```

- Statuses: `professional` · `analysis` · `in_progress` · `experiment` · `finished`.
  Their labels (e.g. «قيد التطوير») are in `projects.filters`.
- `contribution` and `challenge` are optional. Leave them empty and those lines are hidden.
- `stack_learning` shows a technology with a small "learning" tag.
- Filter chips only appear for statuses that have at least one project.

### Certifications · `credentials.json`

- `earned`: certificates you've actually earned, newest first:
  ```json
  { "name": "Certificate name", "issuer": "Issuer", "date": "2025", "url": "https://verify-link" }
  ```
  Fill `url` to show a «تحقّق» (Verify) button.
- `preparing`: currently AWS Certified Machine Learning Engineer – Associate, shown under «الآن».

### Drawings · «روان الرسّامة»

1. Put the image in `app/static/images/artwork/` (portrait photos at 9:16, about 900×1600, work best).
2. Add or edit an entry in `site.json → artworks` (`id` + `image`).
3. Add its caption in **both** language files under `creative.artworks.<id>.title`.

### "What should I explore today?" (ideas generator)

- The 30 ideas live in `app/content/learning_ideas.json`, each with `id`, `topic`, and `ar` / `en` (`title`, `text`).
- FastAPI serves them at `GET /api/learning-ideas` (both languages) or `GET /api/learning-ideas?lang=ar|en`.
- The browser fetches the list once and shuffles locally. It goes through all ideas before repeating,
  never shows the same idea twice in a row, and remembers its place in `localStorage`.
- The test `test_learning_ideas_endpoint_returns_30_bilingual_ideas` expects exactly 30. Update it if you change the count.

---

## Design notes

- **Palette:** sky blue `#83CFFF`, clear blue `#39A9E8`, icy white `#F5FBFF`, powder blue `#E3F4FF`,
  midnight blue `#193B58`, butter yellow `#FFE7A3`. All are CSS variables at the top of `style.css`.
- **Type:** El Messiri + IBM Plex Sans Arabic for Arabic, Fraunces + DM Sans for English, JetBrains Mono for code.
- **Brand mark:** the sky-blue spark in `images/brand-mark.svg` (also the favicon).
- **RTL/LTR:** the layout uses CSS logical properties, so it mirrors when the language changes.
- **Motion:** floating gradient blobs, scroll reveals, tilted Polaroid drawings. Everything turns off
  for people who prefer reduced motion.
- **Caching:** CSS/JS links carry `?v=<timestamp>`, so browsers always load the latest version.
- The language switch is instant (no reload), remembers your choice and updates the URL (`?lang=en`).

## API

| Endpoint | Description |
|---|---|
| `GET /` | The page (`?lang=ar` or `?lang=en`) |
| `GET /api/health` | `{"status": "ok", "mood": "curious"}` |
| `GET /api/content/{lang}` | All text for one language |
| `GET /api/projects?status=&lang=` | Projects with their text |
| `GET /api/learning-ideas?lang=` | The 30 learning ideas (both languages, or one with `lang`) |

---

## Leftover files (safe to delete)

No longer used by the page:
`app/templates/sections/about.html`, `notebook.html`, `process.html`, `app/content/notebook.json`,
`app/static/images/youtube-thumbnail.svg`, `app/static/images/profile.svg`,
`app/static/images/artwork/artwork-*.svg`, `app/static/images/projects/*`, `notebooks/`.

---

*Always a work in progress, just like its owner* ♡
