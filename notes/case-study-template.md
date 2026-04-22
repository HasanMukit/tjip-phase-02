# Case Study Template

Copy this skeleton when building `class-NN-case-studies.html` for a new class. Replace `{{…}}` placeholders. Target 5–8 case studies per class.

## Durable convention — do not change without user approval

**Every case study has four blocks, in this order:**

1. `Scenario` — a `.callout` setting up the situation (2–4 sentences, concrete).
2. `What's happening` — a paragraph diagnosing the problem in plain language. Explains *why* the scenario breaks, names the concept being exercised, and introduces any technical terms.
3. `Terms to know` — a styled `<div class="terms">` with a `<dl>` glossing every piece of jargon used in blocks 1–2. Even if a term feels "obvious," define it — the page must be readable cold by a first-time reader.
4. `<details class="solution-reveal">` — the solution is hidden until the user clicks "Reveal the solution." Inside, a `.solution-body` contains the fix, options (two-col / list / table), and a closing lesson.

**Why this structure.** The user wants readers to engage with the problem and form their own answer before seeing the fix. Reveal-on-interaction makes this physical: the reader commits before the answer is visible. Terms-to-know makes the page self-contained — a reader who doesn't know "vnode" or "Little's Law" can still do the exercise.

**How to apply.** Use this structure for *every* case study on *every* class's case-studies page. If a scenario doesn't need a terms block (no jargon), keep it anyway and define the core concept — that's the teaching moment.

## Header block

```html
<header>
  <div class="eyebrow">Class NN · Case studies</div>
  <h1>{{Class theme}} <em>{{emphasized word}}</em></h1>
  <p class="deck">{{One sentence hook. End with: "Read the problem, understand the terms, think about what you'd do — then reveal the solution."}}</p>
  <div class="meta">
    <span>{{N}} minute read</span>
    <span>Problem &amp; solution</span>
    <span>Assumes you've read {{topic pages}}</span>
  </div>
</header>
```

## Page-level "how to read" callout

Place this right after the `<p class="lede">` so readers understand the reveal pattern up front:

```html
<div class="callout">
  <div class="callout-label">How to read this page</div>
  Every case study has three blocks you'll see immediately: <strong>Scenario</strong> (the setup), <strong>What's happening</strong> (the diagnosis), and <strong>Terms to know</strong> (definitions for the jargon used). The <strong>solution</strong> is hidden behind a "Reveal" toggle. Try your own answer first — the fix lands harder when you've already committed to a guess.
</div>
```

## One case study — the full skeleton

```html
<h2 id="csN"><span class="num">0N</span>{{Scenario title}}</h2>

<div class="callout">
  <div class="callout-label">Scenario</div>
  {{2–4 sentences of concrete setup. Use real-sounding numbers. End with the dilemma or pointed question.}}
</div>

<p><strong>What's happening.</strong> {{Diagnosis paragraph. Explain why the scenario breaks. Name the concept being exercised (e.g. "tail-at-scale", "the bottleneck rule", "CAP dilemma"). Every technical term used here must also appear in the Terms block below. Don't hint at the solution yet — describe the problem.}}</p>

<div class="terms">
  <div class="terms-label">Terms to know</div>
  <dl>
    <dt>{{Term 1}}</dt>
    <dd>{{Short, concrete definition — one to two sentences. Use <code> for anything code-shaped.}}</dd>

    <dt>{{Term 2}}</dt>
    <dd>{{Definition.}}</dd>

    <!-- 4–7 terms is the sweet spot per case study -->
  </dl>
</div>

<details class="solution-reveal">
  <summary>
    <span>Reveal the solution
      <span class="solution-hint">{{One-line teaser about the shape of the fix — e.g. "Two options depending on whether the workload is read-heavy."}}</span>
    </span>
  </summary>
  <div class="solution-body">
    <p><strong>Solution.</strong> {{The fix. If there are branching options, introduce them with "Two common patterns:" or "Three options, in order of cost:" and follow with a .two-col block or ordered list.}}</p>

    <div class="two-col">
      <div class="card">
        <h4>{{Option A}}</h4>
        <p>{{One paragraph, including trade-off.}}</p>
      </div>
      <div class="card">
        <h4>{{Option B}}</h4>
        <p>{{One paragraph, including trade-off.}}</p>
      </div>
    </div>

    <p>{{Optional closing paragraph — the deeper lesson, often one sentence.}}</p>
  </div>
</details>
```

## Wrap section

Every case-studies page ends with a "pattern across all N" section that extracts the common shape:

```html
<h2 id="wrap"><span class="num">0N+1</span>The pattern across all N</h2>

<p>{{One-sentence bridge.}}</p>

<ol style="font-family: 'Inter', sans-serif; font-size: 15px; line-height: 1.75; color: var(--muted); margin: 0 0 24px 20px;">
  <li><strong>{{Habit 1}}.</strong> {{One sentence.}}</li>
  <li><strong>{{Habit 2}}.</strong> {{One sentence.}}</li>
  <li><strong>{{Habit 3}}.</strong> {{One sentence.}}</li>
</ol>

<p>{{Closing one-liner — "The names change; the questions don't."-style.}}</p>

<div class="divider"><span></span><span></span><span></span></div>

<p>Companion reading: {{links to topic pages}}.</p>

<footer>
  Case studies for Class NN · {{Theme}}<br>
  {{Provenance — e.g. "Scenarios adapted from production incidents at ..."}}
</footer>
```

## Picking scenarios

Good scenarios share three properties:

1. **Concrete.** A real-sounding system, a specific number, a clear broken state. "10-node Memcached, +5 nodes, 67% miss" beats "a cache layer that resizes."
2. **Exercises the topics.** Each scenario should be unmistakably *about* one of the class's topic pages. If the fix doesn't route through a named concept from the class, it's a different class's case study.
3. **Non-obvious.** The first-reaction fix should be *wrong*. The teaching moment is the diagnosis, not the code.

Avoid:
- Pure "which database should I pick?" scenarios (too vendor-dependent).
- Scenarios whose fix is "add a cache" with no explanation of why caching helps the specific constraint.
- Scenarios so synthetic they'd never happen in production.

## Writing the Terms block

- Define every technical term used in blocks 1 and 2 (Scenario and What's happening). Err on the side of over-defining.
- Keep definitions to 1–2 sentences. If a term needs more, link out to the topic page.
- Order terms in roughly the order they appear above — readers scan top-to-bottom.
- 4–7 terms per case study is the sweet spot. More than 8 means the scenario introduces too much; split it.
- Use the `(revisit)` suffix on terms repeated across case studies (e.g. "Batching (revisit)") so readers know they've seen it and can skim.
- Use `<code>…</code>` for anything code-shaped (function names, formulas, CLI).

## Writing the Reveal

- `<span class="solution-hint">` inside `<summary>` gives a one-line teaser — enough to shape the reader's guess without spoiling the fix.
- The first paragraph inside `.solution-body` always starts with `<strong>Solution.</strong>`.
- If the solution is a simple paragraph, that's fine. If it has options, use `.two-col` of `.card`s. If it's a sequence of steps, use an ordered list. If it's a comparison matrix, use the inline-styled table pattern from `latency.html`.
- Close with a pullquote, callout, or one-line deeper lesson when there's one to state. If there isn't, don't invent one.

## Linking

- Link from case studies *back* to the relevant topic page section (e.g. `href="cap-theorem.html#choice"`). This reinforces that case studies are applications of theory, not freestanding essays.
- Link between case studies sparingly — the ToC is usually enough.
- The footer should namecheck the source if scenarios come from a known incident or paper.

## Length

- Each case study, before the reveal: ~150–250 words of Scenario + What's happening + Terms.
- Inside the reveal: 100–250 words + any two-col / table.
- Full page: roughly the same length as a topic page (10–15 minute read).
- Don't pad. If a scenario needs only 100 words, leave it at 100.
