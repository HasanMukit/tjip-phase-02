# Class 03 — Performance Fundamentals

The vocabulary of fast systems: latency, throughput, the trade-off between them, Little's Law, and why percentiles matter more than averages.

## Topic pages

- [latency.html](../latency.html) — per-request stopwatch; the 1,000× hierarchy (Jeff Dean's list, refreshed to 2026 hardware); access latency vs bandwidth; budget-driven tech choices.
- [throughput.html](../throughput.html) — system-wide rate; RPS/QPS/TPS/goodput; the bottleneck rule; levers (parallelism, horizontal scale, batching, async, load shedding).
- [latency-throughput.html](../latency-throughput.html) — independent-but-coupled axes; the knee of the curve; Little's Law (`L = λ × W`); averages vs p95/p99; tail-at-scale.

## Key ideas to keep in the back of your head

- Latency is a stopwatch (per-request); throughput is a counter (per-window). Both are needed to describe a system.
- The 1,000× hierarchy: L1 ~1 ns → RAM ~80 ns → NVMe ~30 µs → same-DC RTT ~500 µs → HDD seek ~10 ms → cross-continent ~150 ms.
- "1 MB from X" is a bandwidth number; "random access on X" is a latency number. Conflating them is the classic trap.
- Bottleneck rule: system throughput = slowest stage's throughput. Optimizing elsewhere is zero-impact.
- Little's Law holds unconditionally for any stable system: concurrency = throughput × latency. Three numbers; fix any two, the third is forced.
- Averages hide tails. p99 is what power users experience; in an N-way fan-out, the page's latency is dominated by the worst tail of N.
- The knee of the latency–throughput curve is where a small load increase tips the system into overload.

## Case studies — `class-03-case-studies.html`

All eight use the durable four-block structure: Scenario → What's happening → Terms to know → hidden Solution (inside `<details class="solution-reveal">`). See `notes/case-study-template.md`.

1. **The dashboard is green but users say it's slow.** Tail-at-scale in an 8-way fan-out; fix with p99 SLOs + hedged requests.
2. **A payment API over its 100 ms budget.** Cross-region hop eats the budget; fix with in-region replica or cache.
3. **A Kafka consumer that can't keep up.** Bottleneck is downstream DB; batch writes to trade latency for throughput.
4. **The autoscaler that thrashes at the knee.** CPU is a lagging signal; scale on p95 or queue depth and add load shedding.
5. **A 7-hour ETL we need to finish in 90 minutes.** Throughput problem, not latency; batch + parallelize + defer indexes.
6. **The cold-cache spike on every deploy.** Hierarchy gap between RAM and DB; pre-warm, shared cache, or gradual rollout.
7. **"12k RPS" that is actually 8k.** Retry amplification inflates throughput; measure goodput + jittered backoff + circuit breakers.
8. **The connection pool that looks big but isn't.** Little's Law reveals pool = 100 was exactly capacity; small W increase cascades.

## When extending this class

- The natural next topics are queueing theory, SLOs/SLIs/error budgets, load shedding patterns, and capacity planning. Any of these deserve their own topic pages; case studies 3, 4, 7, 8 already touch them and can be cross-referenced.
- If the user adds a dedicated "Little's Law" page, keep case study 8 as the flagship application.
