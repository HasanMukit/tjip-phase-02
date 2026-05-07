# Class 04 — The Path of a Request (DNS, Caching, API Gateway)

Working notes captured live from class. The unifying question of the class is **"what actually happens between hitting Enter on `www.google.com` and a packet arriving at a Google server?"** — answered in three layers: name resolution (DNS), cache invalidation rules that keep DNS sane, and the request-handling pipeline that sits in front of every modern backend (API gateway → auth → rate limit → routing → load balancer → reverse proxy → server).

Status: **in progress** — being filled in as the user watches the class. Future-me: when we promote this to HTML, expect 2–3 topic pages (DNS resolution, caching/TTL, API gateway pipeline) plus a case-study page.

---

## 1. What happens when you type `www.google.com` (DNS resolution)

The address bar gives you a **name**. The network only routes **IP addresses**. DNS is the system that translates one to the other, and it does so through a **layered cache hierarchy** — every layer that has the answer short-circuits the rest.

### The lookup walk (in order)

A browser's DNS query walks this chain. The first layer that has a non-expired answer wins; it returns immediately and no later layer is touched.

1. **Browser cache** — Chrome, Firefox, Safari each keep an in-memory DNS cache scoped to the browser process. Lifetime is controlled by the record's TTL (with browser-imposed caps; Chrome historically clamps to ~1 minute regardless of TTL). View it at `chrome://net-internals/#dns`.
2. **OS cache (stub resolver)** — every OS ships a local resolver. On macOS it's `mDNSResponder`; on Linux it's `systemd-resolved` or `nscd`; on Windows it's the DNS Client service. This layer also consults `/etc/hosts` first — a static override file. If `/etc/hosts` answers, no DNS query leaves the box.
3. **Router-level cache** — your home/office router runs a tiny DNS forwarder/cache. The first device on the LAN that resolved the name pays the cost; the rest get it from the router for free.
4. **Recursive resolver** — your ISP's resolver, or a public one like `8.8.8.8` (Google), `1.1.1.1` (Cloudflare), `9.9.9.9` (Quad9). This is the box that **does the actual recursion** — i.e., walks the authoritative chain on your behalf and hands back the final answer. It also caches aggressively (often the deepest cache outside your machine).
5. **Authoritative DNS** — the nameservers that own the zone. For `www.google.com` the recursion goes: **root** (`.`) → **TLD** (`.com`) → **authoritative** (`ns1.google.com`, etc.). Only the authoritative server speaks the truth; everyone else is a cache of its words.

### Recursive vs authoritative — the distinction to nail

- **Recursive resolver** = the worker. Knows nothing on its own; *finds* the answer by asking root → TLD → authoritative in sequence, then caches the result.
- **Authoritative server** = the source. Holds the actual zone file. Doesn't recurse on your behalf; just answers "this is what I know about my zone."

A common confusion: "isn't `8.8.8.8` authoritative for the internet?" No — it's a recursive resolver with a huge cache. Authority is per-zone and lives with whoever runs the zone.

### Why the layered cache exists

If every page load did the full root → TLD → authoritative dance, the root servers would melt and every request would pay tens of milliseconds of network round-trips. The hierarchy turns the **common case** (popular names, repeat visits) into a sub-millisecond local memory read.

### Record types worth naming when we write this up

- `A` — name → IPv4
- `AAAA` — name → IPv6
- `CNAME` — name → another name (alias)
- `NS` — who's authoritative for this zone
- `MX` — mail servers
- `TXT` — free-form (SPF, DKIM, domain verification)

Class focused on `A` and `CNAME`; the others are footnotes for when we write the page.

### A vs CNAME — the two records you'll set 99% of the time

- **`A` record — name → IP.** The terminal answer. `www.example.com → 93.184.216.34`. The resolver hands this straight to the browser and the connection is made. (`AAAA` is the same idea for IPv6 — different record type because the address shape is different.)
- **`CNAME` record — name → another name.** An *alias*. `blog.example.com → example.wordpress.com`. The resolver doesn't get an IP back; it gets *another name*, which it must now resolve. Resolvers follow the chain (CNAME → CNAME → … → A) until they land on a terminal record.

The mental model: an `A` record is a street address; a `CNAME` is a "see also" pointer to a different listing. Phonebooks allow both, but with rules.

### Two CNAME rules that trip people up

#### Rule 1 — A name with a CNAME can have *no other records*

If `blog.example.com` has a CNAME, it cannot also have an A, MX, TXT, or anything else. Per **RFC 1034 §3.6.2**, a CNAME is exclusive at its name (except for DNSSEC-related metadata).

The reason is semantic, not arbitrary. CNAME means "this name **is** that other name — go ask there for everything." If you also defined an MX record locally, the resolver wouldn't know whether to honor the local MX or follow the alias and ask the target's MX. The spec resolves the ambiguity by forbidding it: CNAME wins, alone, or it doesn't exist.

This is why "I added a TXT record for domain verification but my CNAME stopped working" is a recurring help-desk ticket. The TXT silently breaks the CNAME (or vice versa, depending on the provider's behavior).

#### Rule 2 — You cannot CNAME the apex (`example.com` itself)

The **apex** (or "root", or "naked domain") is the zone name itself — `example.com`, not `www.example.com`. By DNS rules, the apex must carry mandatory records: at minimum **SOA** (zone metadata) and **NS** (who's authoritative). These are required by the protocol — they're how the rest of DNS finds your zone at all.

Combine that with Rule 1 (CNAME excludes all other records) and the contradiction is direct: a CNAME at the apex would have to coexist with the required SOA/NS, which the spec forbids. So the apex cannot be a CNAME, full stop.

This is annoying in practice, because hosted services (Heroku, Netlify, Vercel, S3 static sites) typically tell you "point a CNAME at `myapp.herokudns.com`." That works fine for `www.myapp.com` but not for `myapp.com` itself.

The workaround DNS providers invented:

- **Route 53 ALIAS**, **Cloudflare CNAME flattening**, **DNSimple ALIAS**, **NS1 ALIAS / ANAME** — all variants of the same trick. The provider resolves the target name *at query time* and returns the resulting IPs as a real `A` record. To the configurer it feels like "a CNAME at the apex"; on the wire it's a perfectly legal A record. The provider eats the indirection cost so the spec doesn't have to bend.

When the user asks "why can't I just CNAME my root domain?", the short answer is: **because SOA and NS are required at the apex, and CNAME refuses to share a name with anything else.** The longer answer is the ALIAS workaround.

---

## 2. Cache invalidation — IPs and TTL

DNS is a giant distributed cache. The single hardest problem in caches is **invalidation**: how do you tell every cached copy that the answer changed? DNS doesn't try to push invalidations — it relies on **TTL expiry** instead.

### TTL = the lease, not the lifetime

Every DNS record carries a **TTL (time-to-live)** in seconds. When a resolver caches the record, that TTL is how long it's allowed to keep using the cached answer before re-asking the authoritative server. After expiry, the next query re-fetches. Until expiry, the cached answer is what gets served — *even if the authoritative answer has already changed*.

That last sentence is the whole story of DNS propagation delay.

### Who sets the TTL

The **zone administrator** — i.e., whoever owns the domain — sets TTL on each record at the authoritative server. It's per-record, baked into the record itself; not a global system parameter. When you edit a record at Cloudflare / Route 53 / Namecheap, the TTL field next to "value" is what you're setting.

Two zone-level knobs sit alongside the per-record TTL:

- The zone's `SOA` record carries a **default TTL** that records inherit if not specified explicitly.
- The `SOA` also carries a **negative-cache TTL** (the `MINIMUM` field) that controls how long `NXDOMAIN` answers are cached. This is the clock that bites you if a record briefly disappears during a botched cutover.

Resolvers and clients are *expected* to honour the configured TTL — but with caveats. Some recursive resolvers floor very low values; some clients (Chrome, certain JVM versions) cap very high values; the browser, OS, and router caches each have their own enforcement. The configured TTL is your *intent*; what actually happens in any given cache is a negotiation between that intent and whatever implementation is reading it.

### Two TTLs when a CNAME is involved

When a name resolves through a CNAME chain, every record on the chain has **its own TTL**, and those clocks tick independently. Concrete example:

```
blog.example.com.    3600    IN    CNAME    target.cloud.com.
target.cloud.com.    60      IN    A        192.0.2.42
```

A resolver doing a fresh lookup gets back both records and caches each independently. Implications:

- After 60 s the A record is stale and the resolver re-fetches **just the A** — it still knows from cache that `blog.example.com` is an alias of `target.cloud.com`. Only when the CNAME's 3600 s elapses does the whole chain get re-walked.
- **Changing the IP at the target** propagates within the *target's* TTL (60 s).
- **Changing where the CNAME points** propagates within the *CNAME's* TTL (3600 s).
- **For any change requiring re-walking the chain, the slowest TTL bounds the cutover.**

This split-clock behaviour is *why* CNAMEs to managed services work so well:

- Heroku / AWS ELB / Cloudflare / Vercel keep low TTLs (~60 s) on their A records so they can rotate IPs at will.
- You keep a longer TTL (~1 h) on your CNAME because you rarely change *which provider* you point at.
- Both sides win: end-user resolution is cheap (one CNAME lookup per hour), but the provider can still move IPs in a minute.

Mental model: each link in the chain has its own clock, and only the link you change starts ticking.

### Changing a DNS record without breaking users — the four-phase playbook

You're moving `api.example.com` from one IP to another. The naive change — just edit the record and wait — strands users on the old IP for as long as the *current* TTL says caches may keep it. If the steady-state TTL is `86400` (24 hours), some users won't see the new IP for a full day. That's the bug.

The fix is to make the cache window *small* before you change anything, do the change inside that small window, then make the window large again once it's stable. Four phases:

#### Phase 1 — Pre-lower the TTL, then wait one *old* TTL

Drop the record's TTL to a small value (60s is the convention; 30s is fine; 300s is the safe maximum if you're cautious). Then **wait at least one full old TTL**.

The waiting step is the one that gets skipped, and it's the one that matters. Here's why: a resolver that cached the record yesterday saw the old TTL of 86400, and it will hold that record for up to 24 hours regardless of what you change at the authority *today*. Lowering the TTL only affects caches that re-fetch *after* the lowering. So you have to wait long enough for every existing cached copy to expire and be re-fetched with the new low TTL.

After this phase, every resolver in the world is holding a copy that says "good for 60s." Your cache window has shrunk from a day to a minute.

#### Phase 2 — Change the record, verify against authority

Update the record at the authoritative server. Immediately confirm the change landed by querying the authoritative server *directly* (this bypasses every cache — see the `dig @ns1` workflow above):

```bash
dig api.example.com @ns1.example.com +short
# → 198.51.100.42      (the new IP)
```

If the authority reports the new IP, the change is real. Public resolvers will still show the old IP for up to the new low TTL (~60s) — that's expected, not a bug.

#### Phase 3 — Wait one new TTL, then verify propagation

Wait at least the new low TTL period (60s+). During this window, every cache that holds a stale copy will refresh on its next request and pick up the new IP. Spot-check with multiple public resolvers to confirm global propagation:

```bash
for ns in 8.8.8.8 1.1.1.1 9.9.9.9 208.67.222.222; do
  echo -n "$ns → "; dig api.example.com @$ns +short
done
```

If they all return the new IP, propagation is done.

#### Phase 4 — Raise the TTL back up

Once the change is stable (give it longer than the bare minimum — an hour is a comfortable cushion), raise the TTL back to its steady-state value (typical: 1 hour to 24 hours). Why bother:

- Low TTL means every cache re-fetches every minute, so your authoritative servers carry roughly **TTL-old / TTL-new ×** the query load they had before. For a 1-day → 60s drop that's a 1440× multiplier.
- First-hit users at each cache pay the full recursion cost (root → TLD → authoritative) on every expiry — bad p99 for cold paths.
- Raising back is just hygiene: low TTL is for cutovers, not for steady state.

#### A concrete timeline

| Time     | Action                                             | What caches hold |
| -------- | -------------------------------------------------- | ---------------- |
| `T-25h`  | Steady state. TTL = 86400. Old IP everywhere.      | old IP, ≤24h     |
| `T-24h`  | Lower TTL to 60. (Nothing else changes yet.)       | old IP, ≤24h     |
| `T-0`    | 24h has passed. Every cache now holds TTL=60.      | old IP, ≤60s     |
| `T-0`    | **Change the IP.** Verify with `dig @ns1`.         | old IP, ≤60s     |
| `T+60s`  | Caches refresh. Spot-check with public resolvers.  | new IP, ≤60s     |
| `T+1h`   | Stable. Raise TTL back to 86400.                   | new IP, ≤24h     |

The whole thing takes ~25 hours wall-clock for a 1-day TTL, but the *user-visible disruption window* is bounded by the new low TTL — about a minute.

#### Gotchas to remember (and to write up as case studies later)

- **Long-lived connections pin to the old IP.** DNS resolution happens at *connect* time only. WebSockets, gRPC streams, and HTTP/2 keepalive connections that opened before the change keep talking to the old IP until they reconnect. **Run both IPs in parallel during the cutover** — don't tear down the old one the moment the DNS change goes in.
- **Some clients ignore TTL.** Chrome caps DNS TTL at ~60s regardless of what you set; some Java clients cache DNS for the JVM lifetime by default (`networkaddress.cache.ttl`); some load balancers and SDKs do their own DNS pinning. Low TTL is a hint, not a guarantee.
- **Some recursive resolvers floor the TTL.** A resolver may refuse to respect TTLs below 30s or 60s. You can't make global propagation faster than the slowest resolver in the chain.
- **Negative caching is its own clock.** If the record briefly disappears (NXDOMAIN), that absence is also cached, governed by the **SOA `MINIMUM`** field, not your record's TTL. A botched intermediate state can poison caches for hours. Never delete-then-recreate; always replace in place.
- **OS-level caches need manual flushing during debugging.** `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` on macOS, `sudo systemd-resolve --flush-caches` on Linux, `ipconfig /flushdns` on Windows. Useful for *you*, not for users.

The one-line takeaway: **DNS changes are bounded by whatever TTL was in effect when the cache picked up the previous answer**. Pre-lowering is how you shrink that bound before you need it.

### Verifying a DNS change actually happened — `dig`

After changing a record you want to answer two different questions, and they need different tools:

1. **Did the authoritative server accept my change?** Query the authoritative server *directly*, bypassing every cache.
2. **Has the change propagated to the rest of the world yet?** Query a public resolver and watch its TTL count down.

`dig` is the standard tool. Useful invocations:

```bash
# Default — uses the system resolver, just like a browser would
dig www.example.com

# Just the answer, nothing else
dig www.example.com +short

# Ask a specific resolver (Google's public DNS in this case)
dig www.example.com @8.8.8.8

# Ask the authoritative server DIRECTLY — bypasses every cache.
# This is the move for "did my change actually land?"
dig www.example.com @ns1.example.com

# Show the full recursion: root → TLD → authoritative
dig www.example.com +trace

# Specific record types
dig example.com NS        # who's authoritative for this zone
dig example.com MX        # mail servers
dig example.com TXT       # SPF / DKIM / verification
dig example.com SOA       # zone metadata (TTL defaults, serial number)
```

#### The "is my change live?" workflow

```bash
# 1. Find the zone's authoritative nameservers.
dig example.com NS +short
# → ns1.example.com.
#   ns2.example.com.

# 2. Ask one of them directly. If this returns the new value, your DNS provider
#    has accepted the change. (No cache between you and the source of truth.)
dig www.example.com @ns1.example.com +short

# 3. Now ask a public resolver. If this still shows the old value, the change
#    is real but caches are still serving stale data. Watch the TTL count down
#    on repeated queries — when it hits 0 the next query will refetch.
dig www.example.com @8.8.8.8
```

The key insight: **querying the authoritative server is the only way to know the truth**. Every other answer is some cache's opinion, and might be minutes or hours behind. If you skip step 2 and panic-debug from step 3 only, you'll waste an afternoon thinking your change didn't go through when really it just hadn't propagated yet.

#### Reading dig output

```
;; ANSWER SECTION:
www.example.com.    287    IN    A    93.184.216.34
                    ^^^
                    TTL remaining in seconds
```

The TTL shown is what the *resolver you queried* has left on its cached copy — it counts down on repeated queries. Hit 0 and the next query refetches from upstream. Querying the authoritative server shows the *full configured TTL* (because there's no cache between you and the source).

Alternatives: `nslookup` (older, more terse output) and `host` (simpler, less info). `dig` is the one to learn — it's what every DNS doc and incident-runbook will assume.

### Trade-off: low TTL vs high TTL

| Low TTL                                          | High TTL                                       |
| ------------------------------------------------ | ---------------------------------------------- |
| Fast propagation (good for cutovers, failover)   | Slow propagation (cutovers take forever)       |
| More queries hit the authoritative server        | Most queries served from cache                 |
| Higher resolver + authoritative load             | Lower load                                     |
| Cheaper to *change* records                      | Cheaper to *serve* records                     |

Common shape: keep TTL high during steady state (1–24h), drop it to 30–60s before a planned change, raise it again after.

### Invalidation modes — push vs pull

Worth naming because it shows up everywhere caching does:

- **TTL-based pull (DNS, CDN default)** — cache asks again after expiry. Simple, scales, but stale data is possible during the TTL window.
- **Explicit push/purge (CDNs, internal caches)** — origin tells caches "this key is now wrong, drop it." Stronger consistency, harder to build (need a fan-out channel to every cache).
- **Write-through / write-back** — caches that sit in the write path and update on writes. (We'll meet this again later when we do caching strategies properly.)

DNS picked **TTL pull** because the topology is a tree of mutually-distrusting cachers; there's no fan-out channel that reaches every resolver on the internet.

---

## 3. The request-handling pipeline (API gateway → server)

Once DNS gave the client an IP, the request actually arrives. In a modern system it doesn't go straight to a server — it threads through a pipeline of edge components, each doing one cross-cutting job.

### The pipeline

```
client ─► API gateway ─► auth ─► rate limit ─► routing ─► load balancer ─► reverse proxy ─► server
                              (SSL/TLS termination, compression, caching happen at the proxy layer)
```

These are *roles*, not always separate boxes. In practice an API gateway is often one process that internally does auth + rate limit + routing, and the load balancer + reverse proxy are often the same NGINX/Envoy/HAProxy instance. But conceptually each role is distinct, and large systems split them across separate tiers.

### The roles, in order

#### API gateway — the single front door

- One public endpoint that fronts many backend services.
- Owns **cross-cutting concerns** that you don't want each service re-implementing: auth, rate limiting, request shaping, observability, API versioning.
- Lets backends be plain services without each one knowing how to authenticate every kind of client or count tokens.
- Common implementations: Kong, AWS API Gateway, Apigee, Envoy, Tyk, NGINX with custom modules.

The mental model: a hotel front desk. Every guest passes through it; the back-of-house rooms don't each need their own check-in.

#### Authentication & authorization

- **Authentication = "who are you?"** Verifies identity. Mechanisms: API key, JWT, OAuth2 access token, mTLS client cert, session cookie.
- **Authorization = "what are you allowed to do?"** Checks the authenticated identity against the requested action. Roles, scopes, ACLs, policy engines (OPA).
- The gateway short-circuits unauthorized requests *before* they cost the rest of the pipeline anything — this is itself a defense (saves CPU, prevents amplification attacks).
- Token validation is usually stateless (verify a JWT signature) so the gateway doesn't need a session lookup per request — that's part of why it's cheap to put here.

#### Rate limiting

- Caps how many requests a given identity (user, API key, IP) can issue per window.
- Two reasons: **fairness** (one noisy tenant can't starve everyone else) and **defense** (cap the cost of abuse, scraping, DoS).
- Algorithms: **token bucket** (allows bursts up to bucket size, refills at rate R), **leaky bucket** (smooths to a steady rate), **fixed window** (simple but has edge-of-window double-burst), **sliding window log** (precise but expensive).
- Lives at the gateway because the gateway sees every request — putting it deeper means the limit only kicks in *after* you've already paid for routing.
- Pairs with **resilience patterns** from Class 03 (Retry-After header, jittered backoff on the client side).

#### Routing

- Picks the **right backend service** based on the request: path (`/api/users/*` → users service), host (`payments.example.com` → payments service), header, method, even body shape.
- This is where a monolithic-looking external API decomposes into microservices internally.
- Routing decisions can also be *weighted* — useful for canary deploys ("send 1% of traffic to v2").

#### Load balancer

- Spreads requests across the **N instances of a single service** chosen by routing.
- Two main flavors:
  - **L4 (transport layer)** — sees TCP/UDP; balances by 5-tuple. Fast, protocol-agnostic, but blind to HTTP. Examples: AWS NLB, IPVS.
  - **L7 (application layer)** — speaks HTTP; balances by URL, header, cookie. Slower (parses HTTP), but lets you do sticky sessions, content-based routing, etc. Examples: AWS ALB, NGINX, Envoy, HAProxy in HTTP mode.
- Algorithms: **round-robin** (rotate), **least connections** (pick the instance with the fewest active conns — adapts to real load), **least response time**, **consistent hashing** (sticky placement; ties back to Class 02), **weighted** (give bigger boxes more traffic).
- Health checks remove dead instances from the pool — without this the LB happily routes into a black hole.

#### Reverse proxy (SSL/TLS termination, compression, caching)

A reverse proxy sits in front of one or more backend servers and **pretends to be the server** to the client. The same physical box is often also the load balancer, but the *role* is different — load balancing is about spreading load; proxying is about wrapping the backend with edge functionality.

The three jobs called out in class:

- **SSL/TLS termination.** The proxy holds the certificate and private key. It decrypts incoming HTTPS once, then talks plain HTTP (or re-encrypted HTTP) to the backend. Why: certificate management in one place; backends don't pay TLS CPU; you can inspect/route by HTTP content (you can't if it's still encrypted).
- **Compression.** Gzip / Brotli responses on the way out. Done at the edge so backends don't each need to implement it; saves bandwidth and tail latency for clients on slow links.
- **Caching.** Repeat responses (especially `GET`s with cacheable headers) get served from the proxy without ever touching the backend. This is the same idea as DNS caching, one layer up: **TTL-based pull**, **purge** APIs for explicit invalidation, **stale-while-revalidate** to hide refresh latency. CDNs like Cloudflare/Fastly/Akamai are reverse proxies turned global.

Other things the proxy commonly handles: HTTP/2 → HTTP/1 translation, request/response header rewriting, WebSocket upgrade handling, basic WAF rules.

#### Server

- The actual application. By the time the request gets here, it's been authenticated, rate-checked, routed to the right service, sent to a healthy instance, decrypted, and possibly served from a cache before it was woken up.
- The server can therefore be much simpler — it doesn't need to know about TLS certs, JWT signing keys, gzip, or rate-limit storage. That's the point of the pipeline.

### How they're interconnected

A few connections worth pointing out when we write this up:

- **Auth and rate limit are both gates** — they cheap-fail before expensive work. Order matters: auth first (so anonymous abusers can't even count against per-user limits), then rate limit (so authenticated abusers still get bounded).
- **Routing and load balancing look similar but answer different questions.** Routing: *which service?* Load balancing: *which instance of that service?* In tools like Envoy these are the same config language but semantically separate stages.
- **Reverse proxy + load balancer often live in one process** (NGINX, Envoy). The terms describe what it's doing for a given request, not where it runs.
- **Caching at the reverse proxy connects back to Class 03's resilience patterns** — single-flight, stale-while-revalidate, TTL jitter all belong here. Worth a forward link when we promote.
- **DNS sits *outside* this whole pipeline** — it ran before any of this. The pipeline starts only once the client has an IP. But the same TTL/invalidation idea recurs at the proxy cache layer, which is why the class teaches DNS first.

---

## Things to capture later (for the HTML build)

When we promote this to topic pages, the natural split is:

- `dns-resolution.html` — the cache hierarchy + recursive vs authoritative + record types. Diagram: the staircase of caches with a request short-circuiting at each step.
- `dns-ttl-and-invalidation.html` *(or fold into the above)* — TTL playbook, the lower-then-change-then-raise procedure, push vs pull invalidation. Diagram: timeline of TTL during a cutover.
- `api-gateway-pipeline.html` — the full chain with each role explained, the L4/L7 LB distinction, the reverse-proxy three-jobs callout. Diagram: the horizontal pipeline above, with arrows annotated by what each stage adds.

Case-study seeds (rough — flesh out when the class is done):

- "We changed the IP and half our users were broken for a day" — TTL not lowered before the change.
- "Our `/etc/hosts` test entry didn't go away" — local override masking real DNS during a debug session.
- "The auth service is down and the whole API is down" — gateway auth as a hard dependency; need fail-open vs fail-closed thinking.
- "Rate limit by IP and a corporate NAT looks like one user" — identity choice for rate limit keys.
- "TLS termination at the LB but the backend log shows HTTP" — confused engineer; explain the termination concept.
- "The CDN is serving a stale 500" — proxy caching gone wrong; needs `Cache-Control: no-store` on errors or negative-caching tuning.

---

## Open items / to confirm with the user as more of class 4 is watched

- Did the class cover **specific algorithms for rate limiting** in detail (token bucket vs leaky bucket math), or just name them?
- Did the class cover **L4 vs L7 load balancing** explicitly, or only "load balancer" generically?
- Was **CDN** discussed as its own thing or folded into "reverse proxy"?
- Was there any **TLS handshake** detail (1.2 vs 1.3, session resumption)?
- Was anycast / GeoDNS mentioned for the DNS part?

These shape whether each becomes its own topic page or a paragraph inside another.
