│ 🔵 Ingress: Query Intent Vector
                         │ 🛡️ Ingress: Scope Metadata (Tenant/ACL/Freshness)
                         │ 🗂️ Ingress: L1 Plan / Route Task Details
                         ▼
==========================================================================================
[R1B] CACHE TIER MAP — POSITIONING VS. PROVIDER-SIDE CACHES
==========================================================================================

R1B is ONE layer in a four-tier cache stack. Each tier has a different key model,
a different invalidation profile, and a different correctness risk. They are
complementary — not substitutes.

  TIER 1 — PROVIDER PREFIX-KV CACHE
    Examples: Anthropic `cache_control: ephemeral` (5 min / 1 hr); OpenAI prompt
              caching; Google Vertex context caching (implicit + explicit).
    Keyed on: exact token-prefix hash of the outgoing prompt.
    Invalidates when: ANY byte in the cached prefix changes.
    Risk: over-reuse impossible (exact match); mis-layered prefix evicts whole cache.
    Owned by: provider. Cascade enables via request flags, not R1B.

  TIER 2 — R1B SEMANTIC ANSWER CACHE (★ THIS DOCUMENT ★)
    Keyed on: (tenant, embedding_model_id, namespace, corpus_version, query_hash).
    Match: hybrid dense + sparse with support-manifest + freshness/policy gates.
    Invalidates when: evidence fingerprint changes, freshness expires, policy/route/
                      ACL drifts, or negative-feedback neighborhood evict fires.
    Risk: hallucination amplification (one bad entry serves many similar queries);
          semantic cousins mis-matched as equivalents — mitigated by R1B.3 fusion.

  TIER 3 — C0 RAG RETRIEVAL CACHE (top-k results)
    Keyed on: (u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff).
    Invalidates when: source-document fingerprints change; embedder version rolls.
    Risk: stale-doc serve if invalidation is key-based only — needs CDC-style
          source→cache inverse index.

  TIER 4 — EMBEDDING INDEX (vector store itself)
    Rebuilt: incrementally on document change (ideal) or full-reindex (expensive).
    Risk: embedding model version drift → numerically incompatible vectors if
          model id not part of the index namespace.

Key invariants for R1B vs. Tier 1:
- Tier 1 caches the PROMPT PREFIX. R1B caches the ANSWER.
- Tier 1 fails CLOSED on any byte change. R1B must fail CLOSED on freshness /
  policy / support-manifest drift, but fails OPEN on minor phrasing variation
  within the same task shape.
- Tier 1 has NO hallucination amplification. R1B does — this is why R1B.3 hybrid
  fusion and R1B.4 policy gates are structural, not optional.
- Using Tier 1 does NOT remove the need for R1B. Prefix caching cuts cost on the
  prompt side; R1B cuts latency AND cost by skipping the model call entirely on
  validated reuse.

==========================================================================================
[R1B] BOTTOM LINE
==========================================================================================

  ┌─────────────────────────────────────────────┐       ┌────────────────────────────────┐
  │ [R1B.1] PRE-FILTER: BOUNDARY ISOLATION      │       │ [ L4 STATE / DATA STORES ]     │
  │  ├─► Apply Strict Tenant / Region Gate      │       │                                │
  │  ├─► Enforce Cache Freshness Window         │       │                                │
  │  └─► Restrict to Reuse-Safe Task Types      │       │                                │
  └──────────────────────┬──────────────────────┘       │                                │
                         │ (Bounded Search Space)       │                                │
                         ▼                              │                                │
  ┌─────────────────────────────────────────────┐       │   ┌──────────────────────────┐ │
  │ [R1B.2] MATCH: VECTOR SIMILARITY            │       │   │                          │ │
  │  ├─► Compare 🔵 query_vec to cached vecs 🔵 │◄──────┼──►│ [DB] SEMANTIC CACHE      │ │
  │  ├─► Calculate Distance (Cosine/Dot Prod)   │       │   │ - Cached 🔵 query_vecs   │ │
  │  └─► Filter by Support/Similarity Threshold │       │   │ - Prior Output Payloads  │ │
  └──────────────────────┬──────────────────────┘       │   │ - Expiry Metadata        │ │
                         │ (Candidate Hits)             │   └──────────────────────────┘ │
                         ▼                              │                                │
  ┌─────────────────────────────────────────────┐       │                                │
  │ [R1B.3] POLICY: VALIDATION & SHAPE          │       │                                │
  │  ├─► Approximate match bounds check         │       │                                │
  │  ├─► Verify Task Shape Fits Prior Answer    │       │                                │
  │  └─► Confirm NO Contextual Contradictions   │       │                                │
  └──────────────────────┬──────────────────────┘       │                                │
                         │ (Validated Hit)              └────────────────────────────────┘
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [R1B.4] EMIT: SHORT-CIRCUIT YIELD           │
  │  ├─► Fetch Exact Prior Answer Payload       │
  │  ├─► Append Semantic Hit Telemetry          │
  │  └─► Bypass Deep Pipeline (NO C0 NEEDED)    │
  └──────────────────────┬──────────────────────┘
                         │
=========================▼================================================================
                     [SEMANTIC CACHE PAYLOAD]
                         │
                         ├─► Exact Prior Answer Payload
                         ├─► Cache Confidence Score
                         ├─► Telemetry / Hit ID
                         │
                         ▼
                   [ RETURN / Direct Output ]