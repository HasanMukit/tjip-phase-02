# Class 02 — Distributed Systems Fundamentals

How data is distributed across machines, and the core trade-offs that forces on any system that stores state on more than one box.

## Topic pages

- [consistent-hashing.html](../consistent-hashing.html) — hash ring, vnodes, replication, gossip, failure handling. Based on the Dynamo paper (2007).
- [cap-theorem.html](../cap-theorem.html) — C, A, P as precise terms; why P is mandatory; CP vs AP with real-system examples; PACELC extension.

## Key ideas to keep in the back of your head

- `hash(key) mod N` is unusable at scale — changing N rewrites nearly every key's destination.
- Consistent hashing solves *placement*, not *skew*. Hot keys still exist.
- Vnodes (150–256 per physical server) exist only in the ring. They route; they don't store.
- CAP's "pick two" framing is misleading. P is always in the picture on a real network. The real choice is CP vs AP *during a partition*.
- Most modern systems (Cassandra, DynamoDB, Riak) are tunable per query via R and W quorum sizes. `R + W > N` is the linearizability threshold.
- Rack-aware placement is what turns a single-AZ outage from catastrophic to routine.

## Case studies — `class-02-case-studies.html`

All seven use the durable four-block structure: Scenario → What's happening → Terms to know → hidden Solution (inside `<details class="solution-reveal">`). See `notes/case-study-template.md`.

1. **Cache fleet resize — the `mod N` catastrophe.** 10→15 nodes causes 67% miss storm; fix with consistent hashing + vnodes.
2. **The celebrity hot shard.** Consistent hashing doesn't fix skew; fix with key salting or a read-path cache.
3. **A fintech ledger during a regional split.** CP choice: Raft-based ledger, minority returns 503 rather than double-spend.
4. **A shopping cart that must never fail.** AP choice with CRDT (OR-Set) or vector-clock reconciliation.
5. **Picking R and W for a tunable store.** One cluster, three profiles: R=1/W=1 (analytics, AP), R=2/W=2 (profiles, balanced), R=3/W=3 (billing, CP).
6. **Rolling upgrade of a live database cluster.** Vnodes + RF=3 + gossip make node-at-a-time upgrades invisible.
7. **Losing an entire availability zone.** Rack-aware replica placement keeps each key at 2-of-3 during an AZ failure.

## When extending this class

- If the user adds new topics (consensus, replication protocols, gossip deep-dive, sharding strategies), add new case studies rather than rewriting existing ones.
- Aim to keep Class 02 case studies focused on *placement + consistency trade-offs*. Failure detection, replication internals, and consensus protocols are likely future classes.
