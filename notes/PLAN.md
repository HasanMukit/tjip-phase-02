# Course Plan — 24 Classes

A single tracker for the whole course. Marks what's done, what's stubbed, and the agreed structure each new class follows.

## Status at a glance

| #     | Title                            | Topic pages                                                  | Case studies                     | Status              |
| ----- | -------------------------------- | ------------------------------------------------------------ | -------------------------------- | ------------------- |
| 01    | *(unassigned)*                   | —                                                            | —                                | stub in index.html  |
| 02    | Distributed Systems Fundamentals | `consistent-hashing.html`, `cap-theorem.html`                | `class-02-case-studies.html` (7) | **done**            |
| 03    | Performance Fundamentals         | `latency.html`, `throughput.html`, `latency-throughput.html` | `class-03-case-studies.html` (8) | **done**            |
| 04–24 | *(unassigned)*                   | —                                                            | —                                | stubs in index.html |

Classes 01 and 04–24 exist in `index.html` as "Coming Soon" cards. 22 classes still need content.

## Standard structure for every class

Each class card in `index.html` should point at:

1. **N topic pages** — one HTML file per sub-topic (see existing class 02 and 03 for the pattern). Deep, visual, SVG-heavy write-ups.
2. **One case-studies page** — `class-NN-case-studies.html`. Five or more problem-and-solution scenarios that exercise the class's topics. See `class-02-case-studies.html` and `class-03-case-studies.html` as the reference. Each case study uses the durable four-block structure: `Scenario` (callout) → `What's happening` (diagnosis paragraph) → `Terms to know` (`.terms` definition list) → hidden `Solution` (inside `<details class="solution-reveal">`). The full template lives in `notes/case-study-template.md` — read it before building a new page.

## How to add a new class

1. Identify the topics for class NN (from course materials or conversation with the user).
2. Open `notes/style-guide.md` and `notes/case-study-template.md`.
3. Write the topic HTML pages first — they're the source of truth the case studies reference.
4. Write `class-NN-case-studies.html` using the template; aim for 5–8 scenarios.
5. In `index.html`, replace the "Coming Soon" stub for class NN with real `class-title`, `class-summary`, and topic-list entries.
6. Create `notes/class-NN.md` with a one-paragraph summary, topic list, and case-study scenario titles.
7. Update this file (mark NN as done, list its pages).

## Naming conventions

- Topic pages: lowercase-kebab, named by topic (e.g. `consistent-hashing.html`, not `class-02-topic-1.html`).
- Case-study pages: `class-NN-case-studies.html` — zero-padded, always in this form.
- Notes files: `class-NN.md` — zero-padded to match.

## Case-study design rules (durable — do not change without user approval)

These are load-bearing. The user asked for them explicitly; they shape the pedagogical contract the site makes with the reader.

- **Problems first, solutions hidden behind user interaction.** Every case study's solution lives inside `<details class="solution-reveal">` so the reader must click to see it. This is a deliberate teaching move: readers should commit to their own answer before the fix is visible. The CSS styling for `.solution-reveal` lives in `styles.css`.
- **Four-block structure per case study.** In order: (1) `Scenario` callout, (2) `What's happening` diagnosis paragraph, (3) `Terms to know` definition list in a `<div class="terms">`, (4) `<details class="solution-reveal">` with the solution inside.
- **Every technical term gets defined.** If a word of jargon appears in blocks 1 or 2, it must have a `<dt>/<dd>` entry in block 3 — even if it feels "obvious." The page must be readable cold by a first-time reader who doesn't know the class's topic pages by heart.
- **Reference the topic pages from the solution.** Link back (e.g. `href="cap-theorem.html#choice"`) so case studies feel like applications of the theory, not freestanding essays.
- **Close with a pullquote or callout when there's a one-liner worth keeping.** Don't invent one; if the solution speaks for itself, leave it.
- **Wrap with a pattern section.** End the page with a numbered list called "The pattern across all N" that extracts the common shape of the scenarios.

The canonical skeleton for all of the above is in `notes/case-study-template.md`. If the user asks for a rule change, update both this file and the template together.

## Not in scope

- Running a dev server or build tooling. This is a static HTML site; open `index.html` in a browser to preview.
- JavaScript frameworks. The only JS is the inline `onclick` toggle on class cards.
- Tests. There's nothing to test — content quality is reviewed by reading.
