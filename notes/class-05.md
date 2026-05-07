# Class 05 — API Design

The contract between client and server: how to structure it, how the design step fits into the larger interview framework, and the trade-offs that follow from each choice. The class opens with a meta-page on the 6-step interview framework so the reader sees *where* API design sits in the broader process before diving into it.

## Topic pages

- [interview-framework.html](../interview-framework.html) — the 6-step system design interview framework. Sections: why a framework, the six steps overview (with timeline figure), each step in detail, time-boxing, and the one-line takeaway. Cross-links into Class 02 (CAP, consistent hashing) and Class 03 (latency, throughput, BoE, resilience).
- *(pending)* `api-design.html` — the API design topic itself. Topics still to confirm with user.

## Key ideas to keep in the back of your head

- The 6 steps in order: clarify → estimate → API → high-level → data model → deep-dive. Outputs of each step feed the next.
- Time-boxing for a 45-min interview: 5 / 5 / 5 / 10 / 5 / 15. Deep dive is the largest block by design and most candidates shrink it — that's the wrong move.
- Three groups: scoping (steps 1-2), designing (steps 3-5), hardening (step 6).
- The deep dive needs three lenses on any hot component: bottleneck, failure mode, trade-off.
- API design comes *before* high-level design because the API fixes what state has to be readable, what writes have to be durable, what can fan out async.

## Case studies — `class-05-case-studies.html`

*(pending — write after `api-design.html` so cases can reference both topic pages)*

## When extending this class

- The framework page is meant to be referenced from every future class's case studies (Step 6 is where Class 02 + 03 vocabulary gets applied). Don't duplicate the framework explanation elsewhere — link to it.
- If the user asks for additional process pages later (e.g. SLO/SLI design, capacity planning as a discipline), they fit naturally as siblings to `interview-framework.html` rather than expanding it.
