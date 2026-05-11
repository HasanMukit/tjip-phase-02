# Site Structure & Extension Guide

This file is the operating manual for the site. Read it before adding a new class, topic, glossary entry, or case study. Conventions in §2 are durable — do not change them without explicit user approval.

---

## 1. Folder layout

```
.
├── STRUCTURE.md                  this file
├── styles.css                    shared stylesheet
├── index.html                    theme-first homepage (primary entry)
├── classes.html                  by-class view (secondary entry)
├── glossary.html                 alphabetical appendix, A–Z jumpbar
├── resources.html                standalone YouTube-video index per class (see §2.7)
│
├── hardware/        index.html + topic pages
├── execution/       index.html + topic pages
├── distribution/    index.html + topic pages
├── performance/     index.html + topic pages
├── reliability/     index.html + topic pages
├── craft/           index.html + topic pages   (interview-framework, BoE)
└── case-studies/    index.html + class-NN.html (one per class with cases)
```

Two views over the same content:
- **Theme** = primary taxonomy. Topics grouped by what they're *about*.
- **Class** = secondary taxonomy. Topics grouped by which session introduced them.

Every topic lives in exactly one theme. A topic's class assignment is metadata (a pill on the page + a row in `classes.html`), not a folder.

---

## 2. Durable conventions — do not change without user approval

### 2.1 Topic page anatomy
1. `<nav class="site-nav">` with five links — **Themes, Classes, Case Studies, Glossary, Resources** — plus the `.site-search` box on the right (input + hidden results panel). Every page carries the same nav block; mark the current page's link with `class="active"`.
2. `<header>` containing:
   - Eyebrow with breadcrumb back to theme: `<div class="eyebrow"><a href="index.html">← {Theme name}</a></div>`
   - `<h1>` with one word italicized via `<em>`.
   - `<p class="deck">` — one-sentence hook.
   - `<div class="meta">` with **only** a class pill and a "Theme · {Name}" tag. **Drop the read-time line.** (User feedback during M2.)
3. `<div class="toc">` — kept on every topic page.
4. `<p class="lede">` — opens the body, drop-cap on first letter.
5. Body sections (`<h2 id="...">` + `<span class="num">0N</span>` prefix). Inline-link **first occurrence** of any cross-topic term with `<a class="glink" href="../glossary.html#anchor">term</a>`.
6. **Terms used here** block at the bottom — compact link strip, no definitions:
   ```html
   <div class="terms-block">
     <div class="terms-block-label">Terms used here</div>
     <div class="terms-block-links">
       <a href="../glossary.html#term-a">term a</a><a href="../glossary.html#term-b">term b</a>...
     </div>
   </div>
   ```
   Separators between terms are inserted by CSS (`a:not(:last-child)::after`) on a flex-wrap container. No descriptions in markup.
7. **Related topics** block — three links is the standard:
   ```html
   <div class="related-topics">
     <div class="related-label">Related topics</div>
     <ul class="related-list">
       <li><a href="..."><span class="related-arrow">→</span><span>Title</span><span class="related-summary">— one-line gist.</span></a></li>
       <!-- two more -->
     </ul>
   </div>
   ```
8. `<footer class="site-footer">` — class pill + "Back to theme →" link + provenance/source.

### 2.2 Class pill
- Real class: `<span class="class-pill">Class 03</span>`.
- Meta page (cross-class, like the interview framework): `<span class="class-pill meta">Meta</span>`.
  Do not use a class number unless a class actually taught it.

### 2.3 Glossary
- One entry per term, alphabetically sectioned.
- **Strict scope: only terms referenced in topic or case-study pages.** Do not add adjacent terms a reader "might" search for.
- Each entry has:
  ```html
  <div class="glossary-entry" id="anchor-name">
    <div class="glossary-entry-term">Term Name <span class="glossary-entry-aliases">alias · alias</span></div>
    <div class="glossary-entry-def">2–3 sentence definition. Use <code>...</code> for code-shaped tokens.</div>
    <div class="glossary-entry-used">
      <span style="margin-right: 14px;">Used in:</span>
      <a href="theme/page.html#section">Page Title</a><a href="...">...</a>
    </div>
  </div>
  ```
- Anchor IDs: `lowercase-with-hyphens`. Multi-letter acronyms keep their spelling (`tlb`, `wal`, `mesi`, `gil`, `cdn`, `nic`, `numa`, `pacelc`, `c10k`, `pps`, `cow`, `pcb`, `smt`, `aof`, `ipc`, `iops`, `rps`, `hbm`, `hls`).
- Jumpbar letters with at least one entry get default class; empty letters get `class="empty"`.

### 2.4 Case-study page anatomy
Every case study has four blocks, in this order, with no exceptions:
1. **Scenario** — `<div class="callout">` setting up the situation in 2–4 concrete sentences.
2. **What's happening** — a `<p>` starting with `<strong>What's happening.</strong>` diagnosing the problem in plain language.
3. **Terms to know** — `<div class="terms"><dl>...</dl></div>` (the definition-list version, **not** the compact `terms-block`). 4–7 terms per case is the sweet spot.
4. **Solution** hidden inside `<details class="solution-reveal">`. Always opens with `<strong>Solution.</strong>` inside `.solution-body`.

The reveal pattern is load-bearing: readers should engage with the problem before seeing the answer. Do not switch to a non-reveal layout.

Each case-studies page ends with a "pattern across all N" wrap section + a `related-topics` block.

### 2.5 Naming
- Topic page filenames: `kebab-case.html`, matching the topic name (e.g. `cache-locality.html`, not `cache_locality.html`).
- Section anchors inside topic pages: short, semantic (`#why`, `#tiers`, `#caches`, `#takeaway`). The first section is usually `#why` or named after the question it asks; the last is always `#takeaway`.
- Glossary anchors: see §2.3.
- Case-study pages: `class-NN.html` (e.g. `class-04.html`).
- Each individual case study uses `id="csN"` (no zero pad: `cs1`, `cs10`, `cs12`).

### 2.6 Style classes that already exist
Don't reinvent — these are in `styles.css`:

| Class | Use |
|---|---|
| `.callout` + `.callout-label` | Scenario boxes, side-notes |
| `.pullquote` | Highlighted one-liner |
| `.two-col` + `.card` | Two-up comparison |
| `.figure` + `.figure-label` + `.figure-caption` | SVG diagrams |
| `.codeblock` | Multi-line code/CLI snippet |
| `.data-table` | Comparison tables (use `<th>`/`<td>`, `td.mono` for monospace cells) |
| `.toc` | Page-level table of contents |
| `.lede` | First body paragraph (drop-cap) |
| `.divider` | Three-dot section break |
| `.terms-block` + `.terms-block-links` | Compact link strip on topic pages |
| `.terms` + `.terms-label` + `<dl>` | Definition list on case-study pages |
| `.solution-reveal` + `.solution-hint` + `.solution-body` | Hidden case-study answer |
| `.glink` | Inline glossary link in prose |
| `.class-pill` (+ `.meta`) | Class badge in header meta |
| `.related-topics` + `.related-list` + `.related-arrow` + `.related-summary` | Bottom-of-page nav |

SVG text uses `.svg-text`, `.svg-text-bold`, `.svg-text-muted`, `.svg-text-small`, `.ring-line`. Color tokens are CSS vars: `--ink`, `--paper`, `--paper-warm`, `--paper-card`, `--rule`, `--muted`, `--accent`, `--accent-soft`, `--s1`–`--s4` (with `-soft` variants).

**Breakpoints in use.** Most responsive overrides live at `max-width: 640px` (the primary mobile breakpoint). Two narrower-scope breakpoints exist for nav/resources behavior only — don't introduce more without asking:

- `max-width: 380px` — micro-breakpoint for the nav search box and links on very narrow phones.
- `max-width: 1023px` / `min-width: 1024px` — used by `resources.html` to switch between the desktop 2-pane layout and the mobile chip-bar layout (see §2.7).

**Responsive nav.** Below 640px, `.site-nav-inner` wraps onto two rows: the logo + `.site-search` stay on top, while `.site-nav-links` drops to a second row (`order: 3; flex-basis: 100%`) and scrolls horizontally with hidden scrollbars (`overflow-x: auto`, vendor-prefixed scrollbar hiders). The search input shrinks (`width: 160px`, expanding to `200px` on focus) and the results panel is pinned to `right: 0` so it doesn't overflow the viewport. At ≤380px the search shrinks further and link spacing tightens. Keep any new nav additions inside `.site-nav-inner` so they participate in this layout.

Anything new needs a responsive override at 640px if it doesn't degrade gracefully by default.

### 2.7 `resources.html` — standalone, off the graph

`resources.html` is the curated YouTube-video index per class. It is deliberately **standalone** and isolated from the rest of the content graph:

- **No search index entry.** It must NOT appear in `scripts/build_index.py`'s `ROOT_PAGES` or `THEME_DIRS`. CI rebuilds the index from those lists only — keep it that way so external video links don't pollute search results.
- **No cross-links from topic, theme, case-study, or glossary pages.** Don't add `glink`s, related-topics rows, or `<a>`s pointing into `resources.html#…` from anywhere. The only inbound link is the **Resources** entry in the top `site-nav-links` (present on every page).
- **No glossary entries** for terms that only show up here. Glossary scope (§2.3) stays strict — videos are external, not authored content.
- **Outbound links go off-site only** (YouTube). Every title link uses `target="_blank" rel="noopener noreferrer"`.

Page anatomy (top to bottom):
1. Standard `site-nav` (with `Resources` marked `class="active"` here).
2. `<section class="classes-section">` — the whole body of the page. **No hero, no separate "jump to class" grid.** Navigation lives entirely in the sidebar TOC, which doubles as the mobile chip bar.
   - `<aside class="resource-toc">` — sidebar TOC. Wraps a `.resource-toc-inner` containing a `.resource-toc-label` and a `<nav>` of `.toc-group[data-class="..."]` blocks. Each group has an `<a class="toc-class" href="#class-NN">` row and a `<ul>` of topic links (`href="#class-NN-tMM"` or `#foundations-pN`). The `data-class` attribute is what the JS uses to mark the active group.
   - `<div class="resource-main">` — right column. Holds one optional `<div class="resource-class" id="foundations">` for pre-class / primer material (currently: a beginner SQL track) followed by one `<div class="resource-class" id="class-NN">` per class. Each `.resource-class` holds a `.resource-class-head` (sticky to the top of the main column, with class number + title + summary) and one `.resource-topic` per topic. **Every `.resource-topic` must carry a stable id** — `class-NN-tMM` for class topics, `foundations-pN` for the foundations block — so the sidebar can link to it and the scrollspy can match. Each topic has an `<h3 class="resource-topic-title">` and one `.data-table` with three columns: **Title** (URL embedded, opens in new tab), **Channel**, **Duration** (`td.mono`). Desktop table is fixed-layout with 60/28/12 widths; mobile (≤640px) collapses each row into a stacked card.
3. Footer.
4. Inline `<script>` (see "Behavior" below) — must remain at the end of `<body>` after the markup.

**Behavior — focus mode + locked viewport.** This page does not scroll the whole document the way other pages do. The script enforces these invariants:

- Only one `.resource-class` is visible in `.resource-main` at a time. The sidebar always lists every class, but the main column hides all `.resource-class` blocks except the one with `.is-visible`. Clicking a class link (or a topic link) sets the active class. The script reads the URL hash on load and treats `#foundations`, `#class-03`, `#class-NN-tMM`, `#foundations-pN` etc. as routes — topic hashes derive the class via a regex (`-tNN`/`-pN` suffix).
- On desktop (`min-width: 1024px`), `<body>` is `display: flex; flex-direction: column; height: 100vh; overflow: hidden;`. The `.classes-section` is a 2-column grid (`240px minmax(0, 1fr)`, gap 56px) that fills the remaining height; both the `.resource-toc` and `.resource-main` columns scroll independently with themed scrollbars. `overscroll-behavior: contain` prevents scroll chaining to the page.
- Below 1024px the locked-viewport CSS is dropped. `.classes-section` becomes a single column, the sidebar turns into a sticky horizontal **chip bar** (`top: 56px`, below the nav) showing class-level links only — topic `<ul>`s collapse via `display: none`. `.resource-class-head` is no longer sticky on mobile. `.resource-class` and `.resource-topic` use `scroll-margin-top: 110px` so jumps land below the chip bar.
- The script also runs an `IntersectionObserver` scrollspy *inside* `.resource-main` (not the viewport) that highlights the topic link of the currently visible `.resource-topic` within the active class. Class navigation is hash-based; topic highlight is scroll-based.

When a new class lands and ships videos:
1. Add a `<div class="resource-class" id="class-NN">` block inside `.resource-main`, after the previous class.
2. Add a matching `<div class="toc-group" data-class="class-NN">` to the sidebar `<nav>` — a `.toc-class` link plus a `<ul>` with one `<li><a href="#class-NN-tMM">` per topic.
3. Give every new `.resource-topic` a stable `id="class-NN-tMM"` (zero-padded; matches the sidebar links).
4. If the videos are queued before the class is taught (or vice versa), mark it with `<span class="upcoming-pill">Upcoming</span>` next to the class title and a one-line note in the summary.

Do not touch search, glossary, or any other page. Do not re-introduce a hero or a separate jump-grid — the sidebar/chip bar replaces both.

The optional `#foundations` block is the **only** non-class section allowed on this page. Keep it above Class 03 if present, and follow the same sidebar-group pattern (`data-class="foundations"`, topic ids `foundations-pN`).

---

## 3. Adding a new class

When the user finishes a new class (say Class 04), follow this sequence in order. **Don't start writing topic pages until step 2 is settled with the user.**

### Step 1 — Read the source
Read `notes/class-NN.md` (the class's own readme) to understand:
- What the class is *about* (one-line theme).
- Which topics were taught (each becomes one topic page).
- Whether topics fit existing themes or warrant a new theme folder.

### Step 2 — Decide theme placement
For each topic, decide its theme. Use this matrix:

| Topic is about… | Theme |
|---|---|
| Hardware costs / pressure / silicon | `hardware/` |
| OS abstractions over hardware (threads, scheduler, loops) | `execution/` |
| State spread across machines (placement, consistency) | `distribution/` |
| Latency / throughput / capacity vocabulary | `performance/` |
| Failure-mode patterns (retry, breaker, throttle) | `reliability/` |
| Contracts at system boundaries (API design, HTTPS, pagination) | `interfaces/` |
| Process / interview / estimation skills | `craft/` |

If a topic doesn't fit, **ask the user before creating a new theme folder**. New themes are a structural change. The full checklist when one lands:

- Create the theme folder and `theme/index.html` (model after `craft/index.html`).
- Add a theme card to `index.html` (homepage), bump the "Themes" stat, and renumber any themes whose ordinal shifted.
- Update the prev/next footer links of the two adjacent themes (and the new one).
- **Register the new directory in `scripts/build_index.py`** — add it to both `THEME_DIRS` and `THEME_LABELS`. Without this, the new theme's pages are silently absent from the search index. (CI rebuilds the index on every push, but it can only see directories the script knows about.)
- Update the theme matrix above so the next class's notes find the new theme.

### Step 3 — Write each topic page
Use the template in §4 below. For each new technical term:
- Inline-link first occurrence with `<a class="glink" href="../glossary.html#term">...</a>`.
- Add the term to the bottom `terms-block` strip.
- Add the term to `glossary.html` (alphabetical position, with "Used in:" backlink).

### Step 4 — Update theme indexes
For each theme that gained topics, edit `theme/index.html` and add a `<a class="topic-row">` for each new topic. Theme topic counts on `index.html` (homepage) need to be bumped too.

### Step 5 — Update `classes.html`
Add a new `<div class="class-card">` for Class N. Include all topics that landed in this class (across whatever themes they live in). Add a placeholder Case Studies link (live-link it in step 7).

### Step 6 — Update homepage stats
On `index.html`:
- Bump `<span class="stat-value">` for "Topic pages" by however many new topics landed.
- Bump "Classes covered."
- Update each affected theme card's `theme-card-meta` (topic count, class list).

### Step 7 — Case studies (if the class has any)
Create `case-studies/class-NN.html` using the four-block structure (§2.4) and the template in §6. Then:
- Edit `case-studies/index.html` and add a `<a class="topic-row">` for the new hub.
- Edit the corresponding row in `classes.html` to link to the new case-studies page.

### Step 8 — Final pass
- Run the link/anchor sweep (§7) to catch typos.
- Open the homepage and click through every new page.
- Spot-check on mobile (375px width).

---

## 4. Topic page template

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{Title}} — TJIP Phase 02</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,700;1,9..144,400&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../styles.css" />
  </head>
  <body>
    <nav class="site-nav">
      <div class="site-nav-inner">
        <a href="../index.html" class="site-logo"><span class="logo-dot"></span>TJIP · Phase 02</a>
        <div class="site-nav-links">
          <a href="../index.html">Themes</a>
          <a href="../classes.html">Classes</a>
          <a href="../case-studies/index.html">Case Studies</a>
          <a href="../glossary.html">Glossary</a>
        </div>
      </div>
    </nav>

    <div class="container">
      <header>
        <div class="eyebrow"><a href="index.html">← {{Theme name}}</a></div>
        <h1>{{Title with one <em>word</em> italicized}}</h1>
        <p class="deck">{{One-sentence hook.}}</p>
        <div class="meta">
          <span class="class-pill">Class 0N</span>
          <span>Theme · {{Theme name}}</span>
        </div>
      </header>

      <div class="toc">
        <div class="toc-title">What's inside</div>
        <ol>
          <li><a href="#why">{{Section 1 title}}</a></li>
          <!-- ... -->
          <li><a href="#takeaway">The one-line takeaway</a></li>
        </ol>
      </div>

      <p class="lede">{{First paragraph — drop-cap. Set up the question.}}</p>

      <h2 id="why"><span class="num">01</span>{{Section 1 title}}</h2>
      <p>{{Body. Inline-link first occurrence of cross-topic terms with <a class="glink" href="../glossary.html#anchor">term</a>.}}</p>

      <!-- ... more sections, figures (.figure), tables (.data-table), code (.codeblock), callouts (.callout), two-col cards (.two-col + .card) ... -->

      <h2 id="takeaway"><span class="num">0N</span>The one-line takeaway</h2>
      <p class="pullquote">{{Memorable one-liner.}}</p>
      <p>{{Closing paragraph.}}</p>

      <div class="terms-block">
        <div class="terms-block-label">Terms used here</div>
        <div class="terms-block-links">
          <a href="../glossary.html#term-a">term a</a><a href="../glossary.html#term-b">term b</a>
        </div>
      </div>

      <div class="related-topics">
        <div class="related-label">Related topics</div>
        <ul class="related-list">
          <li>
            <a href="sibling-topic.html">
              <span class="related-arrow">→</span>
              <span>{{Sibling Title}}</span>
              <span class="related-summary">— one-line gist.</span>
            </a>
          </li>
          <!-- two more -->
        </ul>
      </div>
    </div>

    <footer class="site-footer">
      Class 0N · {{Theme}}. <a href="index.html" style="color: var(--accent)">Back to theme →</a>
    </footer>
  </body>
</html>
```

---

## 5. Glossary entry template

Insert in alphabetical position. Letter section (`<section id="x">`) must already exist; create it if this is the first entry for that letter.

```html
<div class="glossary-entry" id="{{kebab-anchor}}">
  <div class="glossary-entry-term">{{Term}} <span class="glossary-entry-aliases">{{alias}} · {{alias}}</span></div>
  <div class="glossary-entry-def">{{2–3 sentence definition. Use <code>...</code> for code-shaped tokens.}}</div>
  <div class="glossary-entry-used">
    <span style="margin-right: 14px;">Used in:</span>
    <a href="{{theme}}/{{page}}.html#{{section}}">{{Page Title}}</a>
  </div>
</div>
```

When a letter sees its first entry, also remove `class="empty"` from its jumpbar entry near the top of `glossary.html`.

---

## 6. Case-study template (one case)

```html
<h2 id="csN"><span class="num">0N</span>{{Title}}</h2>

<div class="callout">
  <div class="callout-label">Scenario</div>
  {{2–4 concrete sentences. Real numbers. End with the dilemma or pointed question.}}
</div>

<p><strong>What's happening.</strong> {{Diagnosis paragraph. Name the concept being exercised. Every technical term used here also appears in the Terms block below.}}</p>

<div class="terms">
  <div class="terms-label">Terms to know</div>
  <dl>
    <dt>{{Term 1}}</dt>
    <dd>{{1–2 sentence definition.}}</dd>
    <!-- 4–7 terms is the sweet spot -->
  </dl>
</div>

<details class="solution-reveal">
  <summary>
    <span>Reveal the solution
      <span class="solution-hint">{{One-line teaser.}}</span>
    </span>
  </summary>
  <div class="solution-body">
    <p><strong>Solution.</strong> {{The fix. Use .two-col / ordered list / table as appropriate.}}</p>
    <!-- optional pullquote, callout, table -->
  </div>
</details>
```

The page wrapper (nav, header with class pill, TOC, lede, "How to read this page" callout, wrap section, related-topics, footer) follows the same shape as topic pages — see existing `case-studies/class-0N.html` files for a working example.

---

## 7. Verification scripts

Run these from the repo root after any change.

**Glossary anchor sweep** — every `#anchor` in topic-page glossary links must exist in `glossary.html`:

```bash
grep -rohE 'href="[^"]*glossary\.html#[a-z0-9-]+"' . | \
  sed -E 's/.*#([a-z0-9-]+)"$/\1/' | sort -u > /tmp/refs.txt
grep -oE 'id="[a-z0-9-]+"' glossary.html | sed -E 's/id="(.*)"/\1/' | sort -u > /tmp/defs.txt
comm -23 /tmp/refs.txt /tmp/defs.txt   # should be empty
```

**Cross-page link & anchor sweep** — verifies every `href` resolves to a real file and (if anchored) a real `id`:

```bash
python3 - << 'EOF'
import os, re, glob
ids = {}
for f in glob.glob('**/*.html', recursive=True):
    with open(f) as fh: ids[f] = set(re.findall(r'id="([^"]+)"', fh.read()))
errors = []
for f in glob.glob('**/*.html', recursive=True):
    d = os.path.dirname(f)
    with open(f) as fh: c = fh.read()
    for href in re.findall(r'href="([^"]+)"', c):
        if href.startswith(('http', 'mailto:')): continue
        if href.startswith('#'):
            if href[1:] not in ids[f]: errors.append(f"{f}: in-page #{href[1:]}")
            continue
        path, _, anchor = href.partition('#')
        if not path: continue
        target = os.path.normpath(os.path.join(d, path))
        if not os.path.exists(target):
            errors.append(f"{f}: dead file '{href}'")
        elif anchor and target in ids and anchor not in ids[target]:
            errors.append(f"{f}: missing anchor #{anchor} in {target}")
for e in errors: print(e)
print("OK" if not errors else f"{len(errors)} errors")
EOF
```

**Stub sweep** — find any leftover `coming-soon` markers (excluding `styles.css` which legitimately defines the class):

```bash
grep -rn "coming-soon" . | grep -v "styles.css"
```

Run all three after every milestone. They take seconds and catch most regressions.

---

## 8. Local preview

The site is plain static HTML — opening any page directly in a browser works for reading. **One exception:** the nav search box loads `search-index.json` via `fetch()`, which browsers block on `file://` URLs. To preview search, serve the site over HTTP.

One-shot:

```bash
./scripts/preview.sh        # builds the index, serves on http://localhost:8000/
PORT=8765 ./scripts/preview.sh   # override port if 8000 is taken
```

`search-index.json` is gitignored and rebuilt by CI (`.github/workflows/deploy.yml`) on every push to `main`. Don't commit it locally — it produces full-file diffs on every content change and creates merge conflicts on parallel PRs. The CI build is the authoritative source.

---

## 9. User preferences (collected from past sessions)

These shaped the current design. Honour them unless explicitly overridden.

- **Theme-first taxonomy, classes secondary.** Topics group by *what they're about*, not when they were taught.
- **Compact terms-block at the bottom of topic pages — just hyperlinked terms, no descriptions.** The `a + a::before` separator pattern is intentional.
- **TOC kept on every topic page.** Read-time meta line (`9 minute read · Visual guide · No prior experience`) was dropped.
- **Three related-topics links is the standard.** Mix sibling-theme and cross-theme.
- **Inline `glink` density: first occurrence per page.** Don't link every mention.
- **Glossary scope is strict** — only terms actually referenced in pages. No "adjacent" terms.
- **Visual style follows the v1 palette** (Fraunces / Inter / JetBrains Mono, dark/cream, accent orange). Don't redesign.
- **One topic = one page.** Don't split topics into sub-pages without asking.
- **Class pill on every topic page.** "Meta" pill for cross-class content (e.g. interview framework).
- **Case-study reveal pattern is durable.** Always Scenario → What's happening → Terms → hidden Solution.
- **Confirm before structural changes** — new themes, renaming files, restructuring nav. Content additions don't need a checkpoint.

---

## 10. What goes where (decision matrix)

| Question | Answer |
|---|---|
| Where does the class pill go? | In `<div class="meta">` inside `<header>`. First span. |
| Where do I add a new theme card? | `index.html` (root), in the `.themes-grid` block, in folder order. |
| Should this term go in the glossary? | Only if it's referenced in at least one topic or case-study page. |
| Where does an interview-method-shaped page go? | `craft/` — that theme exists for meta-skills. |
| What if a topic crosses two themes? | Pick the dominant one; mention the other in `related-topics`. Don't duplicate. |
| What if a class introduces a topic that already has a page? | Don't create a duplicate. Update the existing page's class pill if needed; add the case study to the new class's case-studies page. |
| Does the homepage need a "what's new" section? | No — the user declined this in M1. Just refresh stats. |
| Should I put the deep-dive on Step 6 of the framework into the framework page or a separate page? | The framework page links out to existing topic pages for the deep-dive vocabulary. Don't duplicate. |
| What if Class 04 has zero new topics (pure review)? | Still add a row to `classes.html` listing the topics covered. No new theme cards or topic pages needed. |
| Where do recommended YouTube videos go? | `resources.html` only. Standalone page — see §2.7. Don't link from topic/case-study pages, don't index, don't add to glossary. |

---

## 11. History

The original v1 site (a flat list of `*.html` files at the repo root) was retired and replaced by this theme-organised v2 site, which now lives at the repo root. The `topics/` subfolder no longer exists — all HTML, the stylesheet, and theme folders sit directly at the root.
