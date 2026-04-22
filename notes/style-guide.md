# Style Guide — HTML & CSS Conventions

Extracted from the existing pages (Class 02 and Class 03). Use as the canonical reference before writing new class pages so they match without trial-and-error.

## Page skeleton

Every content page uses this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{Page Title}} — TJIP Phase 02</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,700;1,9..144,400&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <nav class="site-nav"> ... </nav>
  <div class="container">
    <header>
      <div class="eyebrow">Class NN · {{Section}}</div>
      <h1>{{Title}} <em>{{emphasized word}}</em></h1>
      <p class="deck">{{one-sentence subtitle}}</p>
      <div class="meta">
        <span>N minute read</span>
        <span>Visual guide</span>
        <span>{{prereq hint}}</span>
      </div>
    </header>
    <div class="toc"> ... </div>
    <p class="lede">{{opening paragraph}}</p>
    <h2 id="..."><span class="num">0N</span>{{Section title}}</h2>
    ...
    <footer>...</footer>
  </div>
</body>
</html>
```

The nav and footer markup should match `consistent-hashing.html` exactly so navigation works the same everywhere.

## Design language

- **Dark theme, warm accents.** Body is near-black (`--paper: #111010`), text is warm off-white (`--ink: #e8e2d6`).
- **Serif for reading, sans for UI.** `Fraunces` for paragraphs and headings; `Inter` for nav, meta, captions, and `.card` titles; `JetBrains Mono` for inline `<code>` and numeric tables.
- **Typographic emphasis.** Wrap a single word in each `<h1>` and `<h2>` with `<em>` so it renders in italic Fraunces — the house style.

## Colour tokens (from `styles.css`)

| Token               | Use                                                       |
| ------------------- | --------------------------------------------------------- |
| `--accent` (orange) | Callouts, pullquotes, knee/hot spots, "scenario" emphasis |
| `--s1` (blue)       | Server A / CP systems / first category                    |
| `--s2` (green)      | Server B / healthy zone / second category                 |
| `--s3` (amber)      | Server C / third category                                 |
| `--s4` (pink)       | Server D / fourth category                                |
| `--muted`           | Captions, de-emphasized body text                         |
| `--rule`            | 1 px borders and dividers                                 |

Stick to these tokens; never hardcode hex colours. Two hex exceptions exist in `latency.html` (brown `#8b5a2b` for SSD tier) — follow that precedent only when a new semantic tier genuinely has no token.

## Reusable blocks

- **`.container`** — narrow reading column wrapper around main content.
- **`header`** — eyebrow + h1 + deck + meta, always in this order.
- **`.toc`** with `<ol>` of anchor links — always above `.lede`.
- **`.lede`** — one-paragraph opener with slightly larger type.
- **`h2` with `<span class="num">0N</span>`** — numbered sections. N resets per page.
- **`.two-col`** containing two `.card` elements — the workhorse side-by-side. Each card: `<h4>` title, `<p>` body.
- **`.callout`** with `.callout-label` — orange-bordered box for scenario hooks, side notes, and "important distinction" asides.
- **`.pullquote`** — a single short sentence styled as a serif display quote. Use sparingly (1–3 per page).
- **`.figure`** with `.figure-label`, inline `<svg>`, and `.figure-caption` — hand-drawn SVG diagrams (no external images). Prefer this over screenshots.
- **`.divider`** with three `<span>` children — small centered separator before the closing paragraphs.
- **`.terms`** wrapping a `<div class="terms-label">` and a `<dl>` — the "Terms to know" block used inside every case study. Defines every piece of jargon used in the Scenario / What's happening blocks.
- **`details.solution-reveal`** with `<summary>` and `.solution-body` — the click-to-reveal disclosure that hides every case study's solution. Solutions must never be shown by default; the reveal is part of the pedagogy. See `notes/case-study-template.md` for the canonical markup.

## Tables

Tables are hand-styled inline because there's no `.table` class. Use the pattern from `latency.html`:

```html
<div style="margin: 24px 0 32px; border: 1px solid var(--rule); border-radius: 4px; background: var(--paper-warm); overflow: hidden;">
  <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 13.5px;">
    <thead><tr style="background: var(--paper); border-bottom: 1px solid var(--rule);">
      <th style="text-align: left; padding: 14px 18px; font-weight: 600; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent);">Col</th>
      ...
    </tr></thead>
    <tbody> ... </tbody>
  </table>
</div>
```

The class-02 and class-03 case study pages both use this pattern.

## SVG conventions

- `viewBox` on a clean round number (usually `0 0 640 H`).
- Text inside SVG uses one of these classes: `svg-text`, `svg-text-bold`, `svg-text-muted`, `svg-text-small` (all defined in `styles.css`).
- Fill colours use `var(--s1)` etc., never hex literals.
- Ring diagrams use `class="ring-line"` for the circle outline.

## Writing tone

- **Present tense, active voice.** "A read walks clockwise," not "the read will walk."
- **Short paragraphs.** 2–4 sentences each; let ideas breathe.
- **One takeaway per section**, usually set in a `.pullquote` or `.callout` at the end.
- **Concrete examples beat abstract descriptions.** "Cable under the Atlantic gets cut," not "a communications failure."
- **Name the misconception.** Most sections lead with the wrong mental model, then correct it.
- **End every page** with a `<div class="divider">`, an epilogue paragraph that points to related pages, and a `<footer>` with a provenance line.
