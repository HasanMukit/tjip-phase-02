# Class 05 — API Design

Working notes captured live from class. The unifying question is **"what's the contract between client and server, and what trade-offs follow from each shape that contract can take?"** The class opens with the system-design interview framework (so the student sees *where* API design sits in the broader process), then walks through API styles, REST in depth, idempotency, the HTTP→HTTPS upgrade, the encryption math underneath, and pagination patterns.

Status: **in progress** — being filled in as the user watches the class. Future-me: when promoting to HTML, expect 2–3 topic pages plus probably a case-study page. The interview framework already shipped as `craft/interview-framework.html` from earlier prep — sanity-check it against the framing below before declaring this class done.

---

## 1. The interview framework (recap, in short)

Six steps, in this order:

1. **Requirements** — clarify what's being built. Functional ("what does it do?") and non-functional ("how fast, how reliable, how big?") both surface here. The non-functional ones are the seeds that grow the deep dive in step 6.
2. **Core entities** — the nouns. What objects does the system manipulate (User, Order, Post, Listing)? Identifying entities first makes the API surface obvious — endpoints are basically verbs on these nouns.
3. **API design** — the verbs. How does a client interact with each entity? Picks a style (REST / RPC / GraphQL), then sketches the methods and the request/response shapes. This step is the contract.
4. **Data flow** — for each major operation, trace the request through the system end-to-end. "User clicks Buy → request goes to gateway → auth → orders service → payment service → DB write → kafka event for fulfilment → response." This isn't the architecture diagram yet; it's the storyboard that tells you which boxes you'll need.
5. **High-level design** — the boxes-and-arrows architecture. Services, datastores, caches, queues, the connections between them. Most people *think* "system design" means this step; the framework treats it as just one of six.
6. **Deep dive** — pick the hottest component and pressure-test it against the non-functional requirements from step 1. Three lenses: **bottleneck** ("where does it stall under load?"), **failure mode** ("what breaks first when something fails?"), **trade-off** ("we picked X over Y, here's why").

The asymmetry to remember: **steps 1 and 6 are about non-functional concerns** (scale, latency, availability, durability), and **steps 2–5 are about the functional surface** (what the system does and how it's structured). You learn what numbers you have to hit in step 1; you actually engineer to hit them in step 6. Everything between is what the deep dive then stresses.

A useful sub-claim the class made: **API design comes *before* high-level design on purpose**. The API fixes what state has to be readable, what writes have to be durable, and what can fan out async — and those answers constrain which boxes the architecture diagram needs. Drawing services first and APIs second tends to produce designs that don't actually meet the contract.

(For the full version with timing breakdown, lens definitions, and case-study cross-links, see `craft/interview-framework.html`.)

---

## 2. Types of APIs — REST, RPC, GraphQL

There are three dominant API styles in 2026. They overlap in capability but differ in *what they optimise for*.

### REST (Representational State Transfer)

The dominant style on the public web. Resource-oriented — the URL identifies a resource and the HTTP verb (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) describes the action.

```
GET    /users/123          # read a user
POST   /users              # create a user
PUT    /users/123          # replace user 123
DELETE /users/123          # remove user 123
GET    /users/123/orders   # list user 123's orders
```

Key properties:

- **Stateless.** Each request carries everything needed to process it (auth token, parameters). The server holds no per-client session in memory; this is what lets you scale horizontally — any instance can handle any request.
- **Cacheable via HTTP semantics.** `Cache-Control`, `ETag`, `Last-Modified`, `If-Modified-Since` — the protocol gives you a vocabulary every CDN and browser already understands.
- **Text-based.** Usually JSON, sometimes XML. Human-readable; you can debug it with `curl` or a browser.
- **Loose coupling.** Clients and servers evolve independently — you can add a field without breaking old clients. URLs are the contract, not generated stubs.
- **HATEOAS (worth knowing, not universal).** Roy Fielding's purist take is that responses should embed hyperlinks to next actions (`"links": { "cancel": "/orders/45/cancel" }`) so the client navigates by following links rather than hard-coding URI templates. HAL, JSON:API, Siren lean into this. Most public REST APIs ship URI templates in their docs and skip it. Added 2026-05-08.

**CORS (browser-only concern, lives next to `OPTIONS`).** Same-origin policy blocks cross-origin JS calls by default. Server opts in with `Access-Control-Allow-Origin`. Simple requests (`GET`/`HEAD`/form-encoded `POST`) go through directly; non-simple ones (custom headers, JSON body, `PUT`/`DELETE`/`PATCH`) trigger an `OPTIONS` preflight first. `Access-Control-Max-Age` caches the preflight verdict — generous values turn a two-RTT cost back into one. Class didn't cover but added 2026-05-08 because adjacent.

### RPC — gRPC, Protobuf, Thrift

Function-oriented instead of resource-oriented. You call a remote method as if it were a local function: `userService.GetUser(123)`. The framework hides the network behind a generated client stub.

**gRPC** is Google's modern RPC framework, the de-facto standard for service-to-service calls inside a single system. Two pieces:

- **Protocol Buffers (protobuf)** — schema-first IDL. You write a `.proto` file describing your messages and methods; a compiler generates type-safe client and server stubs in many languages (Go, Java, Python, Rust, etc.).
- **HTTP/2 + binary framing** — multiplexed streams over a single TCP connection. Supports unary (one request, one response), server streaming, client streaming, and bidirectional streaming.

A protobuf message:

```
message User {
  int64  id    = 1;
  string name  = 2;
  string email = 3;
}
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
}
```

The wire format is binary and **schema-aware** — `id=123` becomes ~3 bytes (field tag + varint), not the 20+ bytes of JSON's `{"id": 123}`. Compactness and parse speed are the headline wins.

Trade-offs:

- Binary on the wire — you can't `curl` it and read the response. You need `grpcurl` or a generated client.
- Browsers can't speak gRPC natively (HTTP/2 trailers aren't exposed); gRPC-Web exists as a workaround but adds a proxy.
- The schema couples client and server harder than REST does — a renamed field can break old clients unless the team is disciplined about field-number stability.
- Best-fit niche: **internal service-to-service** where you control both ends and want speed plus types.

### GraphQL

Query language *over* the API. Single endpoint (typically `POST /graphql`); the body says exactly which fields to return.

```graphql
query {
  user(id: 123) {
    name
    orders(last: 5) {
      id
      total
      items { name price }
    }
  }
}
```

What it solves: **over-fetching** (REST's `GET /users/123` returns 30 fields when the client wants 3) and **under-fetching** (the client wants user + orders + items and pays N round-trips in REST). GraphQL collapses both into one shaped response.

What it costs:

- **No URL-based caching.** Every query is a `POST` to `/graphql`, so the CDN/browser-cache mechanics REST gets for free no longer apply. Caching shifts to the GraphQL server (DataLoader, Apollo cache, persisted queries).
- **N+1 queries on the resolver side.** If you naively resolve `orders.items` per-order, you get one DB query per order. The standard fix (DataLoader / batch loaders) is mandatory, not optional.
- **Hard to rate-limit by request count.** One query can be tiny; the next can ask for the universe. You end up rate-limiting by query *complexity* — every field has a cost, the query has a budget.
- **Schema and resolver layer have to be built.** More server-side complexity than REST.

The mental model:

- **REST:** server defines endpoints, client picks one.
- **RPC:** server defines functions, client calls one.
- **GraphQL:** server defines a graph, client queries it.

In practice large companies often run **all three** — REST for the public API, gRPC for internal RPC, GraphQL for the BFF (backend-for-frontend) layer that aggregates services for a web/mobile UI.

---

## 3. Issues with REST — and why we still use it anyway

REST's "issues" mostly boil down to *efficiency*. The reasons to keep using it are mostly *reach* and *flexibility*.

### The inefficiencies

- **JSON is verbose.** `{"id": 123, "name": "Alice"}` is ~30 bytes; the protobuf equivalent is ~10. Multiply by millions of requests and that's bandwidth.
- **JSON is slow to parse.** Tokenising text is more work than reading length-prefixed binary fields.
- **Over- and under-fetching** (the same things GraphQL solves). REST endpoints return what they return; clients adapt.
- **Multiple round-trips for related data.** "Get the user, then get their last 5 orders, then get each order's items" is three calls (or N + 2). Network RTT dominates.
- **No native streaming.** REST is request/response; long-lived push needs WebSockets or SSE bolted on.
- **Schema is implicit.** OpenAPI/Swagger help, but they're documentation, not enforcement. A typo in the response shape breaks clients silently.

### Why it still wins for most public APIs

- **Universality.** Every language, every browser, every tool understands HTTP + JSON. A new client can hit your API with `fetch` in 30 seconds; nothing to install, nothing to compile.
- **Caching for free.** CDNs (Cloudflare, Fastly), browser caches, intermediate proxies — they all speak HTTP cache semantics. A `GET /products/123` with `Cache-Control: public, max-age=3600` is cached at the edge automatically. gRPC and GraphQL each have to rebuild this from scratch.
- **Debuggability.** `curl` works. Browser dev tools work. Postman works. When something breaks at 2 a.m. you can read the response with your eyes.
- **Loose coupling.** Adding a field to a JSON response doesn't break old clients; renaming one breaks only the clients that read it. Backwards-compat is easy if you're not careless.
- **Statelessness scales.** No sticky sessions, no per-client server memory; any instance handles any request. Horizontal scaling is the default, not the goal.
- **Conventions are well-known.** A new engineer onboards to a REST API in an afternoon. RPC and GraphQL each carry their own learning curve and tooling demands.

The trade-off in one sentence: **REST is slower on the wire but faster to ship, easier to cache, and easier to evolve.** For a public API serving heterogeneous clients (browsers, mobile apps, partner integrations, scripts), the wire-speed loss is rarely the bottleneck and the operational wins are huge.

---

## 4. The REST verbs

HTTP defines a small set of methods; REST conventionally uses six of them.

| Verb      | Purpose                                   | Idempotent? | Safe?                 |
| --------- | ----------------------------------------- | ----------- | --------------------- |
| `GET`     | Read a resource                           | yes         | yes (no side effects) |
| `POST`    | Create a resource (typically)             | **no**      | no                    |
| `PUT`     | Replace a resource (full overwrite)       | yes         | no                    |
| `PATCH`   | Partially update a resource               | depends     | no                    |
| `DELETE`  | Remove a resource                         | yes         | no                    |
| `HEAD`    | Like `GET` but headers only               | yes         | yes                   |
| `OPTIONS` | Discover allowed methods (CORS preflight) | yes         | yes                   |

Two terms to nail:

- **Safe** — calling it doesn't change server state. `GET`, `HEAD`, `OPTIONS` are safe; the rest modify state.
- **Idempotent** — calling once and calling five times leave the server in the *same* state. `GET` is idempotent (reads don't change anything). `PUT` is idempotent (replace-with-X applied twice is the same as once). `DELETE` is idempotent (deleting an already-deleted thing is a no-op). `POST` is *not* idempotent by default — calling `POST /orders` twice creates two orders.

Why idempotency matters: networks fail mid-request. The client doesn't know if the server got the request, processed it, and the response was lost — or whether the request never landed. **If the operation is idempotent, the client can safely retry. If it isn't, retries can double-charge a credit card.**

`PATCH`'s idempotency is subtle: a JSON Merge Patch (`{"name": "Alice"}` overwrites `name`) is idempotent. A JSON Patch op like `{"op": "add", "path": "/tags/-", "value": "vip"}` is *not* — appending the same tag twice produces two tags. The format determines the property.

---

## 5. Making a `POST` idempotent

The retry problem: a client `POST`s `/payments` to charge $50. The connection times out before the response arrives. Did the charge land? The client can't tell. If it retries blindly and the original landed, the customer gets charged twice.

Two patterns solve this.

### The `Idempotency-Key` header

Stripe popularised this; most payment APIs follow it now.

The client generates a random unique key (UUID is the common choice) and sends it on the request:

```
POST /payments HTTP/1.1
Idempotency-Key: 7f8a3c12-9e4b-4d1a-b2e7-...
Content-Type: application/json

{"amount": 5000, "currency": "USD", ...}
```

The server, on first receipt:

1. Looks up the key in a fast store (Redis with persistence, or a DB table).
2. **Not found** → process the request, store the *full response* (status code + body) under the key with a TTL (24 h to 7 days is typical), return the response.
3. **Found** → return the stored response immediately, without re-processing.

Result: the client can retry the same request as many times as it wants. The first call does the work; the rest replay the stored answer.

Things to get right:

- The key is **client-generated**, not server-generated — that's the whole point. The client knows "this is the same logical request" before the server does.
- **Store the entire response**, not just "success/fail". A client retrying after a network blip wants the same body the first attempt produced (including the order ID, etc.).
- Keep the storage durable — Redis with persistence, or an indexed DB row. Losing the key store loses idempotency.
- Pick a TTL that exceeds the client's retry budget. If the client retries for up to 10 minutes, the TTL should be at least that.
- Validate that a repeat key with a *different request body* is rejected — otherwise an attacker can replay your idempotency key with a malicious body and get a "success" response back.

### Natural-key dedup at the storage layer

Sometimes the request already carries something unique — a client-generated `order_id`, a `transaction_reference`, a `(user_id, day, type)` tuple. The server can use a unique constraint plus an upsert:

```sql
INSERT INTO orders (id, user_id, total, ...)
VALUES (...)
ON CONFLICT (id) DO NOTHING
RETURNING *;
```

If the row already exists, the insert is a no-op and the server returns the existing row. Works without any extra header, because the dedup happens in the database.

When to pick which:

- **Idempotency-Key** is general — works for any operation, even if the body has nothing unique about it.
- **Natural-key dedup** is automatic — no client cooperation needed — but only works when the request structurally identifies itself.
- Big systems often use **both**: header-level dedup for general protection, plus storage-level constraints as the safety net.

---

## 6. HTTP vs HTTPS — what HTTP gets wrong

HTTP is plain text on the wire. Three problems follow from that.

### 1. Eavesdropping

Anyone in the network path — your ISP, the wifi at the coffee shop, every router between you and the server — can read the entire request and response. URLs, form data, cookies, JSON bodies. Logging in over HTTP means every hop sees your password.

### 2. Tampering

A man-in-the-middle (compromised wifi, malicious ISP, captive-portal injection) can *modify* the bytes flowing past. Common attacks: injecting ads, replacing download links with malware, rewriting form action URLs to point at the attacker. The receiver has no way to detect modification — there's no integrity check.

### 3. Impersonation

When you connect to `bank.com`, how do you know the server you're talking to is actually `bank.com`? Without authentication you don't. DNS spoofing, ARP poisoning, or just a malicious wifi hotspot can hand you a server that *looks* like `bank.com` but isn't.

### What HTTPS adds

HTTPS is HTTP carried over TLS (Transport Layer Security; SSL is the deprecated predecessor name still used colloquially — "SSL certificate" is a misnomer for "TLS certificate" but it's everywhere). TLS gives three guarantees, one for each problem above:

- **Encryption** — only the client and the legitimate server can read the payload. Eavesdroppers see ciphertext.
- **Integrity** — every TLS record carries a message authentication code; tampering changes the MAC and the receiver detects it. Either the bytes arrive intact or the connection breaks.
- **Authentication** — the server proves it owns the domain by presenting a certificate signed by a trusted Certificate Authority. The browser ships with a list of CAs it trusts and rejects anything not signed by one of them.

The browser UI cues — the lock icon, no warning interstitial — exist precisely to surface these guarantees to the user.

---

## 7. The HTTPS encryption process — keys, certificates, Diffie-Hellman

The puzzle TLS solves: **two parties on a hostile network agree on a shared symmetric secret without an eavesdropper learning it**. Once they have a shared secret they can use fast symmetric crypto (AES) for the actual data. Everything in the handshake is in service of getting that secret established.

### Asymmetric crypto, in one paragraph

Each party has two mathematically linked keys:

- **Public key** — given out freely.
- **Private key** — kept secret, never leaves the box.

Two operations matter:

- **Encrypt with public, decrypt with private.** Anyone can encrypt a message that only the owner of the private key can read.
- **Sign with private, verify with public.** Only the owner of the private key can produce the signature; anyone can check it.

Asymmetric crypto is **slow** — orders of magnitude slower than symmetric (AES). So TLS uses it sparingly: only for setting up the shared secret, then switches to AES for the real traffic.

### The SSL/TLS certificate

A signed document that says "this public key belongs to `bank.com`". Issued by a Certificate Authority (Let's Encrypt, DigiCert, GlobalSign, etc.). The CA's own public key is shipped inside every browser and OS as part of a "trust store"; that's the root of trust.

When you connect to `bank.com`:

1. The server hands you its certificate.
2. The browser checks the signature on the certificate using the CA's public key from its trust store.
3. If valid, the browser believes "the public key in this certificate really belongs to `bank.com`" — at least to the extent it trusts the CA.

Both sides do *not* both have certificates by default. The server presents one (so the client knows who it's talking to). **Mutual TLS (mTLS)** is when the *client* also presents a cert — used inside zero-trust infra and some B2B APIs, but not for the public web.

### Naive approach (and why it isn't what TLS does)

A first instinct: client encrypts the entire request stream with the server's public key. Bad idea:

- Asymmetric crypto is too slow for stream-level use.
- RSA encryption has a size cap; you'd have to chunk and re-encrypt, multiplying overhead.
- More importantly: if the server's private key is ever stolen later, an eavesdropper who recorded the encrypted traffic can decrypt it retroactively. **No forward secrecy.**

### The actual approach — hybrid encryption

Use asymmetric only to agree on a shared symmetric session key. Then use AES with that session key for everything else. Two ways to do the agreement:

#### Option A: RSA key exchange (older; deprecated in TLS 1.3)

1. Client generates a random session key.
2. Client encrypts it with the server's public key (from the certificate).
3. Sends the encrypted blob.
4. Server decrypts with its private key. Both now have the session key.

Simple. **No forward secrecy.** If the server's long-term private key leaks (say, a year later), every recorded session is now decryptable. This is why TLS 1.3 dropped RSA key exchange.

#### Option B: Diffie-Hellman key exchange — the modern approach

The clever bit: both sides derive the *same* shared secret while only exchanging *public* values over the wire. An eavesdropper who sees the entire conversation can't compute the secret.

The math (the textbook version):

- Both sides agree on public parameters: a large prime `p` and a generator `g`. (These can be hard-coded; they're not secret.)
- **Client** picks a private random `a`. Computes `A = g^a mod p`. Sends `A`.
- **Server** picks a private random `b`. Computes `B = g^b mod p`. Sends `B`.
- Client receives `B`, computes `B^a mod p` = `g^(ab) mod p`.
- Server receives `A`, computes `A^b mod p` = `g^(ab) mod p`.
- Both now hold `g^(ab) mod p` — the shared secret. AES seeded from it.

The eavesdropper sees `A` and `B` — both public. To compute `g^(ab) mod p` from them she'd need to recover `a` from `A = g^a mod p`, which is the **discrete logarithm problem**: easy to compute `g^a` going forward, infeasible to reverse for large primes (think 2048-bit `p`). That asymmetry is what makes DH work.

Crucially, in TLS 1.3 the DH keypairs `a` and `b` are **ephemeral** — generated for this one session and thrown away. Even if the server's long-term certificate key leaks years later, the ephemeral DH secrets are gone, so past recorded sessions can't be decrypted. This is **forward secrecy**, and it's why DH replaced RSA key exchange.

(Modern implementations use **ECDHE** — elliptic-curve Diffie-Hellman ephemeral — which is the same idea over an elliptic-curve group. Smaller keys for equivalent security, faster math. The mental model is identical.)

### Where the certificate fits in

The certificate doesn't *encrypt* anything in the DH exchange. Its job is **authentication**: the server signs its DH public value with the private key from its certificate. The client verifies the signature against the public key in the certificate, and verifies the certificate against a trusted CA. That chain proves "the entity I'm doing DH with really is `bank.com`, not a man-in-the-middle pretending to be `bank.com`."

So:

- **Certificate** → who you're talking to.
- **Diffie-Hellman** → a shared secret nobody listening can derive.
- **Shared secret** → seeds AES for the actual data.

### TLS 1.3 handshake, simplified

1. **Client hello.** Lists supported ciphers, sends its DH public value (`A`).
2. **Server hello + certificate + signature.** Server sends its DH public value (`B`), its certificate, and a signature over the handshake (proving it owns the certificate's private key).
3. **Client verifies certificate** against trusted CAs. Verifies the signature against the certificate's public key.
4. **Both derive the session key** from the shared DH secret.
5. **Encrypted application data flows** with AES (or ChaCha20) using that session key.

TLS 1.3 collapses what TLS 1.2 did in two round-trips into one — a meaningful latency win on every fresh HTTPS connection.

---

## 8. Pagination — offset/limit and cursor

The problem: the API returns a list (posts, orders, comments). Lists grow without bound. You can't ship a million rows in one response — bandwidth, memory, time-to-first-byte all collapse. Pagination is how the client takes the list a slice at a time.

### Offset/limit pagination

The classic shape:

```
GET /posts?limit=20&offset=40
```

Server runs:

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 40;
```

It feels natural — "give me page 3 of 20-per-page" maps to `offset=40, limit=20`. UIs love it because rendering "Page 3 of 50" is straightforward.

It has two serious problems.

#### Problem 1 — performance falls off a cliff at large offsets

`OFFSET 1000000` does **not** mean "skip a million rows cheaply". It means the database has to scan and discard the first million rows before it can return yours. The cost is `O(offset)`, not `O(limit)`. A "load page 50,000" request costs the same as scanning 50,000 pages of data — even though the user only sees 20 rows.

Indexes help the *ordering* step, but they don't avoid the discard-the-first-million step. Deep pagination is slow no matter what you index.

#### Problem 2 — inconsistent results when data changes

Page 1 returns rows 1–20. The user reads them. Then someone inserts a new post at the top. The user clicks "next page". Page 2 returns rows 21–40 — but the post that *was* at position 20 is now at position 21, so the user sees it twice. The reverse happens with deletions: rows skip.

This sounds minor until you've built a feed. A user scrolling through "page 1, 2, 3" of a live-updating timeline sees duplicates and gaps. Worse: if the sort key changes (a post is edited and `updated_at` jumps), every subsequent page is scrambled.

The two problems share a root cause: **offset is computed against the current state of the table at query time**. There's no stable handle.

### Cursor pagination

The fix: instead of "skip 40 rows", say "give me what comes after *this* row". The "this" is a **cursor** — typically the sort key of the last row from the previous page, often base64-encoded so it looks opaque to clients.

```
GET /posts?limit=20                       # first page
→ { "results": [...], "next_cursor": "eyJpZCI6MTIzfQ" }

GET /posts?limit=20&cursor=eyJpZCI6MTIzfQ # next page
→ { "results": [...], "next_cursor": "..." }
```

Server runs:

```sql
SELECT * FROM posts WHERE id < 123 ORDER BY id DESC LIMIT 20;
```

(The exact predicate depends on the sort key — it might be `WHERE created_at < $cursor_ts` or a tuple comparison `WHERE (created_at, id) < ($ts, $id)` to handle ties.)

Why it's better:

- **`O(log N)` per page**, not `O(offset)`. The database does an indexed seek to the cursor position; the offset doesn't appear in the query.
- **Stable across inserts and deletes.** New posts at the top don't shift you; you keep walking forward through the data you've seen.
- **Natural fit for infinite-scroll UIs.** Every "fetch more" call is just "give me what comes after the last thing I have".

What you give up:

- **Can't jump to "page 50".** Only forward (and sometimes backward) sequentially. If the UI needs random-access pagination, cursor doesn't fit.
- **Need a stable, monotonic sort key.** Usually the primary key or a `(created_at, id)` tuple. If the sort changes, the cursor breaks.
- **Cursor should be opaque.** If you expose `cursor=12345` clients will start crafting their own; signing or encrypting the cursor keeps the contract under your control.

### When to pick which

- **Offset/limit** — small datasets, admin dashboards where "Page N of M" is part of the UX, when random-access matters.
- **Cursor** — anything that grows unbounded (feeds, search results, audit logs), anywhere consistency under live writes matters, anywhere deep pages are realistic.

The rough rule: **if your dataset can have a million rows and users routinely scroll past the first thousand, you want cursor.** Offset is fine until the offsets get big.

---

## 9. API design — best practices (good vs bad APIs)

Captured live, then expanded after cross-checking against an APIGuru transcript that surfaced six gaps. Final shape: **eleven habits + one bonus** (expanded 2026-05-08 after a second-pass summary check added async/range/OpenAPI). Each is paired with the failure mode it prevents — framing is "every best practice is a real outage someone else has already paid for."

1. **Clear, consistent naming.** Plural for collections (`/users`), plural-plus-id for an instance (`/users/123`), singular only for genuine singletons (`/me`, `/health`). No verbs in URLs — the verb is already in the HTTP method. Pick one case style (kebab-case for paths, snake_case or camelCase for JSON fields) and never switch.

2. **Idempotency for reliability.** Honour what the spec already promises — `GET`, `PUT`, `DELETE` idempotent by default; `POST` and `PATCH` not. For the non-idempotent ones, make them idempotent on purpose via `Idempotency-Key` header or natural-key dedup. Cross-references the deep-dive on `api-design.html#idempotency`.

3. **API versioning.** URL versioning (`/v1/users`), header versioning, or date-based header versioning. Pair with `Deprecation` / `Sunset` response headers. Keep at least one previous version alive for the duration of the release cycle so clients can migrate on their own deploy schedule. Treat additive changes as free, anything else as a v-bump.

4. **Always paginate list endpoints.** Adopt from v1 even when the table is small — adding it later is a breaking change. Offset/limit for small bounded sets; cursor for anything unbounded or live-written.

5. **Clear query strings — filter, sort, search, partial responses.** One field, one parameter (`?status=pending`). Sort gets two knobs (`?sort=price&order=asc`). Search is its own verb (`/search?q=...`, with `+` between terms, `scope=` for multi-resource queries). Partial responses via `?fields=id,name,email` for sparse fieldsets — the cheaper REST-side fix for over-fetching, paired with `?expand=` going the other way.

6. **Predictable responses and errors.** Honour the `Accept` header for content negotiation, default to JSON when no preference is given, return `406 Not Acceptable` rather than silent fallback, and make sure errors come back in the same format as success bodies. Status codes in three categories (2xx success, 4xx client error, 5xx server error); a small consistent set (e.g., 200/201/204/400/401/403/404/500) used the same way on every endpoint. Error body follows RFC 7807 Problem Details: `code` (machine-readable), `title`/`detail` (human), `hint` (one-line nudge to the fix), `link` (docs URL), `trace_id`. Same envelope on every endpoint.

7. **Security is not an afterthought.** Sensitive data in headers/body, never query strings (browser history, nginx logs, `Referer`). TLS everywhere including internal services. Use OAuth 2.0 (and OIDC for identity) — don't invent your own auth flow; the grant types map to client shapes (Auth Code + PKCE for web/mobile, Client Credentials for service-to-service, Device Code for TVs/CLIs). Verify keys/tokens on every request (signature, expiry, scope, audience), then authorize the action — not just the identity. Don't roll your own crypto.

8. **Keep cross-resource references simple.** One level of nesting is plenty. Prefer flat URLs by ID (`/refunds/2`) over deep paths. Reference related resources by ID, not embedded objects, with an optional `?expand=` escape hatch. Security angle added 2026-05-08: deep paths leak schema (sequential IDs, ownership tree); flat URLs reveal less.

9. **Hand long operations off asynchronously.** Operations that don't fit a single request/response cycle return `202 Accepted` with a `Location` header pointing at a status endpoint; clients poll (or register a webhook). On completion of a create operation, the status endpoint redirects to the resulting resource with `303 See Other`. The job ID is the resumable handle — survives gateway timeouts, dropped connections, browser refreshes. Same idempotency lesson from #2, applied to time. Added 2026-05-08.

10. **Support range requests for large resources.** For genuinely large single resources (video, large export, big image), advertise `Accept-Ranges: bytes`, honour the `Range` header, return `206 Partial Content` with `Content-Range`. Enables resumable downloads, parallel chunking, video seeking. Distinct from pagination (which is for collections). `HEAD` requests probe size before downloading. Added 2026-05-08.

11. **Document with OpenAPI (Swagger).** A single YAML/JSON spec drives interactive docs (Swagger UI, Redoc), generated client SDKs (openapi-generator), server-side request validation, mock servers, and CI contract tests. Spec-first or code-first — pick one source of truth, derive the other. Added 2026-05-08.

**Bonus — plan for rate limiting.** Fairness (per-identity caps) and defense (cap the cost of abuse). Lives at the API gateway. Communicate limits via `X-RateLimit-*` and return `429` with `Retry-After`. For GraphQL, limit by query complexity, not request count.

**Domain layout callout** — `api.example.com` for traffic, `developer.example.com` for the docs portal. Add redirects from `dev.*` and `developers.*` to the canonical, and from a browser hitting `api.*` with no path to the developer portal.

The page lives at `interfaces/api-best-practices.html`. Linked from the three sibling interfaces pages, the gateway pipeline page, and the resilience-patterns page. Glossary entries: `api-versioning`, `content-negotiation`, `oauth2`, `problem-details`. Backlinks added on `idempotency`, `idempotency-key`, `http-method`, `rest`, `offset-pagination`, `cursor-pagination`, `rate-limiting`, `api-gateway`.

## Things to capture later (for the HTML build)

The `interfaces/` theme (06) is live with four topic pages — `api-design.html`, `api-best-practices.html`, `https-handshake.html`, `pagination.html`. Glossary entries added (including `api-versioning`); homepage topic count bumped to 4; `classes.html` updated; reciprocal Related-topics blocks point at the new best-practices page from each sibling. What's still open:

- [x] **Cross-links *into* the new pages from earlier classes** — done 2026-05-08. Three forward-links added:
  - `reliability/resilience-patterns.html` → `interfaces/api-design.html#idempotency` (retries are safe only if the operation is idempotent). Added in the idempotency callout and in the Related-topics block.
  - `distribution/api-gateway-pipeline.html` → `interfaces/https-handshake.html` (TLS termination is one of the proxy's three jobs; deep-dive lives on the new page now). Added inline in the TLS-termination section and in the Related-topics block.
  - `distribution/api-gateway-pipeline.html` → `interfaces/api-design.html` (the gateway is the surface this contract lives on). Added inline in the gateway intro and in the Related-topics block; also paired with a link to `api-best-practices.html`.
- [x] **Case-studies page (`case-studies/class-05.html`)** — shipped 2026-05-08. All six seeds landed as full cases (scenario / what's happening / terms-to-know / hidden-solution reveal). Wrap-up section pulls out three habits across all six (contract is load-bearing; diagnose before migrating; operationalise the "static" things). Linked from `case-studies/index.html` as a Class 05 row. Cross-links into `interfaces/api-design.html#idempotency`, `interfaces/pagination.html#cursor`, `interfaces/https-handshake.html#building-blocks`, plus reliability/resilience-patterns:
  - Case 1: "We added retries and started double-charging customers" — POST without idempotency keys.
  - Case 2: "Page 50,000 of search results takes 20 seconds" — OFFSET cliff; needs cursor.
  - Case 3: "Our public REST API is slow, can we move it to gRPC?" — wrong axis; round-trip count not wire format. BFF endpoint is the fix.
  - Case 4: "We migrated to GraphQL and now the database is on fire" — N+1 resolver; DataLoader + complexity budgets.
  - Case 5: "Cert expired and the whole API went down" — automate ACME, alert before expiry, page a rotation not a person.
  - Case 6: "Our internal certs failed verification after we reissued" — trust-anchor vs cert distinction; dual-bundle the trust store before swapping signatures.
- [ ] **More-topics buffer** — user mentioned more topics will be added. New topics will likely fold into the existing three pages or land as additional siblings under `interfaces/`.

---

## Open items / to confirm with the user

Resolved 2026-05-08:

- [x] **CORS** — class didn't cover it, but added a short subsection on `interfaces/api-design.html` (under the verbs section, next to `OPTIONS`). Covers same-origin policy, simple vs preflighted requests, and the `Access-Control-Max-Age` latency win. Glossary entry added (`#cors`).
- [x] **API versioning** — confirmed already integrated as best practice #3 on `interfaces/api-best-practices.html#versioning` (URL / header / query-param strategies, `Deprecation` + `Sunset` headers, overlap windows). Glossary entry already exists (`#api-versioning`).
- [x] **Pagination — `(timestamp, id)` tuple cursor for ties** — already covered on `interfaces/pagination.html` with the tuple-comparison SQL example. Confirmed adequate as a one-or-two-liner; no deep dive needed.

Deferred (user called on 2026-05-08):

- **Authentication mechanisms** (API keys, JWT, OAuth, mTLS) — class didn't cover beyond the OAuth 2.0 mention already on the security best practice. Leave for a later class if it surfaces.
- **HSTS** — not mentioned in class. Skip.
- **TLS 1.2 vs TLS 1.3** distinction — not covered in class. Skip.
