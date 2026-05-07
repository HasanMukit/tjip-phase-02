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
1. `<nav class="site-nav">` with four links: Themes, Classes, Case Studies, Glossary.
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

The mobile breakpoint is `max-width: 640px`. Anything new needs a responsive override there if it doesn't degrade gracefully by default.

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
| Process / interview / estimation skills | `craft/` |

If a topic doesn't fit, **ask the user before creating a new theme folder**. New themes are a structural change — they need a name, a homepage card, and a stats bump.

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

## 8. User preferences (collected from past sessions)

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

## 9. What goes where (decision matrix)

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

---

## 10. History

The original v1 site (a flat list of `*.html` files at the repo root) was retired and replaced by this theme-organised v2 site, which now lives at the repo root. The `topics/` subfolder no longer exists — all HTML, the stylesheet, and theme folders sit directly at the root.
