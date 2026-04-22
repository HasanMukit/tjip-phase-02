# Repo Notes — Index

Persistent, repo-local context so future conversations can pick up cold without re-reading every HTML file. This directory lives in the repo (not in the user-layer `~/.claude` memory) by the user's explicit request.

## Durable rules (load these before writing any new case studies)

- **Problems first, solutions hidden behind user interaction.** Each case study reveals its solution only when the reader clicks the `<details class="solution-reveal">` toggle. This is a pedagogical commitment — do not flatten it without the user's explicit approval.
- **Every technical term gets defined in a Terms-to-know block** (`<div class="terms">`) inside the same case study, even if the term seems obvious. The page must be readable cold.
- Full four-block structure, CSS, and copy-paste skeleton: [case-study-template.md](case-study-template.md).

## What lives here

- [PLAN.md](PLAN.md) — roadmap for all 24 classes, status, how to extend, durable design rules
- [style-guide.md](style-guide.md) — HTML/CSS conventions extracted from the existing class pages
- [case-study-template.md](case-study-template.md) — canonical skeleton for class-NN-case-studies.html (four-block + reveal structure)
- [class-02.md](class-02.md) — Class 02 summary, topic pages, case study index
- [class-03.md](class-03.md) — Class 03 summary, topic pages, case study index

## How to use

- Starting a new class? Open `PLAN.md` first (what's the next class, what topics does it cover), then `style-guide.md` and `case-study-template.md` before writing HTML.
- Adding case studies to an existing class? Open the matching `class-NN.md` to see what's already there and avoid duplicating scenarios.
- Finished a class? Update `PLAN.md` (mark done) and create/update `class-NN.md`.

## Conventions

- One `class-NN.md` per class. Name them with leading zero to match HTML filenames.
- Keep each `class-NN.md` under ~100 lines — it's a pointer file, not a re-write of the HTML.
- The index file (this one) only lists pointers and one-line hooks. Content belongs in the referenced files.
