# Class 01 — Hardware & the Execution Model

The bottom layer of system design, in two halves. **Half one** (hardware): what a request actually costs on real hardware, the speed-vs-size-vs-cost pyramid, and why "big-O" lies once cache lines and branch predictors enter the picture. **Half two** (execution model): how the OS gives you the illusion of "many things at once" — processes, threads, the event loop, context switching, core pinning — and where each abstraction's cost shows up.

## Topic pages

### Hardware foundations

- [hardware-pressure.html](../hardware-pressure.html) — "1M req/s" is meaningless until you say what one request costs. Walks through CPU, RAM, disk, network as four pressure points, then five concrete request types (health check, password hash, cache lookup, durable write, video segment) showing where each one squeezes. Pressure-shape → capacity-plan recipe at the end.
- [memory-hierarchy.html](../memory-hierarchy.html) — Eight tiers from registers to tape. L1/L2/L3 explained as three caches with three jobs (private/private/shared, fast/medium/coherence-rendezvous). The "fastest storage" question (registers by definition; L1 in practice; SSD if "fastest persistent"). Speed/size/cost trade-off pyramid; ephemeral-vs-persistent volatility line.
- [cache-locality.html](../cache-locality.html) — Cache lines (64 bytes), spatial vs temporal locality, AoS vs SoA layout. CPU pipelining and branch prediction; cost of a misprediction (~10–20 cycles). The famous Stack Overflow sorted-array experiment as the canonical demo. Why "inefficient" sorts beat "better" ones below the crossover (insertion vs quicksort, vector vs list, linear vs binary).

### Execution model

- [process-vs-thread.html](../process-vs-thread.html) — A process is a memory boundary; a thread is an execution cursor. The thread's "private kit" — stack, registers, program counter (literally a "you are here" pointer) — lives in the core's register file while running and in a **Process Control Block (PCB)** in RAM while paused. Every context switch is a CPU↔RAM round-trip (registers ~0.3 ns vs RAM ~80 ns) — the irreducible direct cost. What each owns, what they share, the five-row diff (address space, comms, blast radius, creation cost, switch cost). COW for fork; lightweight threads (goroutines, virtual threads). Decision tree for picking one. Includes a **core vs thread (terminology collision)** section that disambiguates physical core / hardware thread (SMT/HT) / OS thread — and frames SMT as the hardware shortcut around the PCB round-trip ("duplicate the register file so the second context never has to leave the chip").
- [concurrency-vs-parallelism.html](../concurrency-vs-parallelism.html) — Rob Pike's distinction: concurrency = composition / many in flight, parallelism = simultaneous execution. The jugglers analogy. Four combinations (sequential / concurrent only / parallel only / both). Why the vocabulary matters when diagnosing "why is this slow?"
- [event-loop.html](../event-loop.html) — JavaScript's single-threaded model: call stack + microtask queue + macrotask queue + the loop itself. One-tick walkthrough. Microtasks vs macrotasks (Promise.then beats setTimeout(0)). Why setTimeout(0) isn't 0. The cardinal rule: never block the loop. Workers for true parallelism.
- [context-switching.html](../context-switching.html) — What the OS does on a thread switch (registers, TLB, scheduler bookkeeping). Direct vs indirect cost (cold cache and predictor are the real tax). Voluntary vs involuntary. The throughput-vs-thread-count cliff: more threads can mean less throughput. C10K and the move from thread-per-connection to event loops + lightweight threads.
- [core-pinning.html](../core-pinning.html) — The kernel migrates threads between cores by default; pinning (sched_setaffinity / taskset / isolcpus) overrides it. Cost of migration: cold L1/L2, cold branch predictor, cross-NUMA memory. NUMA-awareness on multi-socket boxes. When pinning is wrong (general-purpose servers, hyperthread siblings, premature). HFT, DPDK, real-time as the canonical use cases.

## Key ideas to keep in the back of your head

### Hardware

- "1M req/s" is meaningless until you describe one request. CPU, RAM, disk, network — figure out which fills up first; everything else is decoration.
- Network has two limits: bandwidth (Gbps) and packets-per-second. A flood of tiny requests can saturate pps long before bytes.
- Memory hierarchy: registers (~0.3 ns) → L1 (~1 ns, 32–64 KB, per-core, split i/d) → L2 (~3 ns, 256 KB–1 MB, per-core) → L3 (~10 ns, 8–64 MB, shared) → DRAM (~80 ns, GBs) → NVMe SSD (~30 µs, TBs) → HDD (~10 ms) → tape.
- Volatility line cuts between DRAM and SSD: above is ephemeral (lost on power cut), below is persistent. Every "we lost data" incident is misplaced state above the line.
- Cache lines are 64 bytes. Sequential access uses all 16 ints per line; random access wastes 15. Spatial + temporal locality are why caches work.
- Branch prediction is the CPU betting which side of an `if` will be taken. >95% accuracy on biased branches, ~50% on random ones; a misprediction costs ~10–20 cycles. The sorted-array experiment is the canonical demo.
- Big-O hides the constants, and the constants are mostly cache misses and branch mispredicts. Standard libraries switch to insertion sort below n≈16 for this exact reason.
- False sharing: independent variables on the same 64-byte cache line ping-pong between cores under coherence traffic. Pad to cache-line boundaries.

### Execution model

- A process is a memory boundary; a thread is an execution cursor. Threads share heap by default and isolate by effort (locks). Processes isolate by default and share by effort (IPC). Pick whichever default matches the failure mode you fear most.
- A thread's "private kit" is stack + registers + program counter. While running it lives in the core's register file (~0.3 ns access, one slot per core). While paused it lives in a **Process Control Block (PCB)** in RAM (~80 ns). Every context switch is a save (regs → PCB) + load (PCB → regs) round-trip — that's the irreducible direct cost, and why SMT (which keeps two contexts on-chip in two register files) is so much faster than an OS context switch.
- "Thread" is overloaded across three things: **physical core** (silicon execution engine, own ALU/L1/predictor), **hardware thread / SMT / Hyper-Thread** (per-core slot — own register file + PC, shared everything else, ~1.2–1.4× throughput per pair on CPU-bound work), and **OS thread / software thread** (kernel-scheduled execution cursor onto a logical CPU). 8-core box with 2-way SMT = 16 logical CPUs; capacity-plan against physical cores, not HTs. SMT, in one sentence: duplicate the register file so the second context never has to leave the chip.
- Race conditions are about contested *data*, not contested cycles. Hyper-threading and multi-core make threads more physically simultaneous; locks/atomics exist because the heap is shared regardless of how the threads are scheduled.
- Fork is cheap on Linux because of copy-on-write — pages are duplicated only on write, and most fork-exec patterns never write at all. Lightweight threads (goroutines, virtual threads, fibers) push thread-creation cost from µs into ns.
- Concurrency = the program's structure (many things in flight). Parallelism = the hardware's execution (simultaneous on multiple cores). They're orthogonal — you can have either, both, or neither.
- The JS event loop is the canonical "concurrency without parallelism" model. One thread, one stack, two queues, one rule: never block the loop. Microtasks always drain before the next macrotask runs.
- Context switch direct cost is ~1–10 µs; indirect cost (cold L1/L2, cold predictor, TLB misses) lasts another ~50–500 µs. That's the real tax.
- More threads is not a free lever. Throughput-vs-thread-count peaks and then collapses past the peak — because switching, cache thrash, and lock contention compound. CPU-bound peak is ~1–2× cores; I/O-bound peak can be hundreds.
- Core pinning trades the kernel's load balancing for cache continuity. Right answer for tail-latency-critical hot paths (HFT, DPDK, real-time); wrong answer for general-purpose servers where the scheduler already does a great job.

## Case studies — `class-01-case-studies.html`

All twelve use the durable four-block structure: Scenario → What's happening → Terms to know → hidden Solution (inside `<details class="solution-reveal">`). See `notes/case-study-template.md`. Page is split into two arcs — six on hardware, six on execution model.

### Hardware foundations (1–6)

1. **"Can it handle 1M req/s?"** — the trick interview question; answer the pressure-shape question before drawing any boxes.
2. **The matrix loop that's 8× slower one way** — row-major vs column-major iteration on a 4096² matrix; cache lines decide.
3. **The linked list that loses to a vector** — `std::list` vs `std::vector`; pointer-chasing breaks the prefetcher.
4. **A hot loop that gets faster after sorting** — branch prediction; the canonical SO sorted-array case in production form.
5. **Eight cores, one counter, no speedup** — false sharing on a 32-byte counter array; pad to 64-byte lines.
6. **The "O(n log n)" sort that lost to "O(n²)"** — why every standard library falls back to insertion sort below the crossover.

### Execution model (7–12)

7. **The crash that took the whole API down** — Gunicorn `--threads 64` with one worker; OOM kills the process and every in-flight request. Fix: multi-process workers for blast-radius isolation.
8. **Our "64-vCPU" instance performs like 32** — capacity planned against logical CPUs (HTs) instead of physical cores. Two HT siblings ≈ 1.3× one core, not 2×, on CPU-bound work.
9. **Async/await everywhere, no speedup** — added concurrency to a CPU-bound NumPy workload, expected parallelism. async/await is single-threaded; needs `multiprocessing` or native parallel libs.
10. **The Node.js API that freezes for 5 seconds** — synchronous `JSON.parse` on a 50 MB payload blocks the event loop; healthz fails; pod gets killed. Fix: reject big payloads / stream-parse / `worker_threads`.
11. **We doubled the thread pool and throughput dropped** — past the peak of the throughput-vs-thread-count curve. Profile context-switch rate; reduce pool; consider event loop or virtual threads.
12. **The p99 spike that disappears with isolcpus** — kernel migrating hot thread between cores destroys L1/L2 + branch predictor. Fix: pin to a core, isolate it (`isolcpus` + `nohz_full`), reserve the HT sibling, NUMA-bind memory.

### The wrap

The closing "pattern" section now extracts 11 patterns split across both arcs — "the abstraction you're using has a cost you didn't see, and the fix is almost always to make it visible." Hardware patterns: pressure shape, layout over algorithm, predictability, cache-line awareness, constants over asymptotics. Execution-model patterns: process-as-isolation-boundary, count physical cores, concurrency ≠ parallelism, never block the loop, more threads has a peak, pin when latency matters more than aggregate throughput.

## When extending this class

- Natural next topics for hardware: SIMD / vectorization, prefetch hints, GPU memory hierarchy (registers → shared → L2 → HBM mirroring the CPU pyramid), virtual memory & TLB pressure.
- Natural next topics for execution: schedulers in depth (CFS, EEVDF), kernel vs user threads, async runtimes (tokio, libuv), lock-free data structures, memory ordering models (acquire/release, sequential consistency).
- Case-study coverage is now full across both arcs — every topic page has at least one case study that exercises it. If the user adds new topic pages, follow the same pattern: one case study per topic, slotted into the existing twelve in topic order.
- The video referenced in class for the sorted-array experiment is the canonical demo (https://www.youtube.com/watch?v=EmzdmqUWq3o); case study 4 is the production-shaped retelling. Other videos referenced in this class:
  - Process vs thread: https://www.youtube.com/watch?v=4rLW7zg21gI
  - JS event loop: https://www.youtube.com/watch?v=8aGhZQkoFbQ
  - Concurrency vs parallelism: https://www.youtube.com/watch?v=RlM9AfWf1WU
  - Context switching / why more threads slow servers: https://www.youtube.com/watch?v=x-nM3PlmOB0
  - Core pinning: LinkedIn pulse — *CPU Pinning 101: How Assigning Cores Can Supercharge Performance*
