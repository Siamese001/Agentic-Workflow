│ 🔵 Ingress: Query Intent Vector
│ 🛡️ Ingress: Scope Metadata (Tenant/ACL/Freshness/Version)
│ 🗂️ Ingress: L1 Plan / Route Task Details / Reuse Class
▼
==========================================================================================
[R1B] SEMANTIC CACHE - EXPLODED ARCHITECTURE
==========================================================================================

  ┌─────────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
  │ [R1B.1] PRE-FILTER: BOUNDARY ISOLATION      │       │ [ L4 STATE / DATA STORES ]                   │
  │  ├─► Apply strict tenant / region gate      │       │                                              │
  │  ├─► Enforce freshness window + TTL class   │       │   ┌────────────────────────────────────────┐ │
  │  ├─► Require same policy / route family     │       │   │ [DB] SEMANTIC CACHE                   │ │
  │  ├─► Restrict to reuse-safe task shapes     │       │   │ - Cached 🔵 query_vecs                │ │
  │  ├─► Exclude mutation / live-fact requests  │       │   │ - Cached sparse term maps / BM25      │ │
  │  └─► Narrow to same corpus / source scope   │       │   │ - Prior answer payloads               │ │
  └──────────────────────┬──────────────────────┘       │   │ - Support manifests / citation spans   │ │
                         │ (Bounded Search Space)       │   │ - Freshness / expiry metadata          │ │
                         ▼                              │   │ - Policy hash / route shape / ACL      │ │
  ┌─────────────────────────────────────────────┐       │   │ - Optional fact-vector support bundle  │ │
  │ [R1B.2] CANDIDATE RECALL: HYBRID LOOKUP     │       │   └────────────────────────────────────────┘ │
  │  ├─► Dense: compare 🔵 query_vec to cached  │◄──────┼──────────────────────────────────────────────┘
  │  │    ask vectors via cosine / dot product  │
  │  ├─► Sparse: BM25 / lexical overlap over    │
  │  │    query terms, entities, anchors, nums  │
  │  ├─► Metadata: filter by task, freshness,   │
  │  │    source family, evidence class         │
  │  ├─► Optional fact-vector check against     │
  │  │    stored support bundle for topic fit   │
  │  └─► Produce top bounded candidate set only │
  └──────────────────────┬──────────────────────┘
                         │ (Candidate Hits)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [R1B.3] MATCH FUSION: SEMANTIC + LEXICAL    │
  │  ├─► Blend dense similarity with sparse     │
  │  │    BM25 score, exact entity overlap,     │
  │  │    and phrase/number alignment           │
  │  ├─► Down-rank broad semantic cousins that  │
  │  │    "feel similar" but miss exact facts   │
  │  ├─► Up-rank candidates whose prior answer  │
  │  │    was grounded by the same fact pattern │
  │  └─► Emit fused reuse score + reason codes  │
  └──────────────────────┬──────────────────────┘
                         │ (Ranked Candidates)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [R1B.4] POLICY: VALIDATION & SHAPE          │
  │  ├─► Approximate-match bounds check         │
  │  ├─► Verify task shape fits prior answer    │
  │  ├─► Confirm same answerability class       │
  │  ├─► Check support bundle still satisfies   │
  │  │    minimum citation / evidence contract  │
  │  ├─► Reject if freshness-sensitive facts    │
  │  │    may have drifted beyond cache window  │
  │  ├─► Confirm no contextual contradictions   │
  │  │    from new scope, actor, time, source   │
  │  └─► Require policy-safe reuse threshold    │
  └──────────────────────┬──────────────────────┘
                         │ (Validated Hit)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [R1B.5] EMIT: SHORT-CIRCUIT YIELD           │
  │  ├─► Fetch prior answer payload             │
  │  ├─► Attach confidence + fused score        │
  │  ├─► Attach reuse reason codes              │
  │  ├─► Append semantic-hit telemetry          │
  │  ├─► Mark cache lineage / hit_id / ttl      │
  │  └─► Bypass deep pipeline (NO C0 NEEDED)    │
  └──────────────────────┬──────────────────────┘
                         │
=========================▼================================================================
                     [ SEMANTIC CACHE PAYLOAD ]
                         │
                         ├─► Prior Answer Payload
                         ├─► Cache Confidence Score
                         ├─► Dense Score / BM25 Score / Fused Score
                         ├─► Hit ID / Telemetry / Reuse Reason Codes
                         ├─► Support Manifest / Citation Sufficiency Flag
                         ├─► Freshness Class / Expiry / Policy Hash
                         │
                         ▼
                  [ RETURN / DIRECT OUTPUT ]


==========================================================================================
[R1B] WHAT IS ACTUALLY HAPPENING
==========================================================================================

- R1B is not "vector match = reuse." It is bounded approximate reuse.
- Dense vectors answer: "Is this ask semantically close to a prior ask?"
- BM25 / sparse terms answer: "Did the user ask about the same concrete facts, entities, phrases, or numbers?"
- Fact-vector support bundles answer: "Was the prior answer grounded in the same underlying evidence neighborhood?"
- Policy checks answer: "Even if the asks are similar, is reuse still safe for this route, time horizon, and task class?"

The safe mental model:

1. Dense similarity gets you into the room.
2. BM25 and lexical anchors make sure you are in the right aisle.
3. Fact-vector / support checks make sure the old answer sat on the same shelf of evidence.
4. Policy/freshness checks decide whether reuse is allowed at all.
5. Only then does R1B short-circuit instead of sending the request to C0.

==========================================================================================
[R1B] WHY HYBRID MATTERS
==========================================================================================

Without hybrid scoring, semantic cache can over-reuse answers that are "conceptually similar" but factually off.

Examples:
- "What is the refund policy for enterprise annual plans?" vs
  "What is the refund policy for monthly self-serve plans?"
  Dense similarity may be high, but BM25/entity anchors should separate annual vs monthly.

- "What was revenue in Q3 2025?" vs
  "What was revenue in Q4 2025?"
  Topic is nearly identical. Sparse numeric/date anchors prevent bad reuse.

- "How do I reset Okta MFA?" vs
  "How do I reset Auth0 MFA?"
  Task shape is similar. Entity overlap must prevent cross-system leakage.

So hybrid is not an embellishment. It is what keeps R1B from becoming a lazy near-neighbor trap.

==========================================================================================
[R1B] FACT VECTORS IN R1B
==========================================================================================

R1B can remain a cache route while still carrying fact-awareness.

- The cached answer may store a support manifest:
  - cited source ids
  - supporting spans / chunks
  - optional pooled fact vectors for the evidence set
  - freshness class and retrieval timestamp
  - contradiction or unresolved-gap flags

- At reuse time, R1B does not perform full C0 retrieval.
  It only checks whether the prior answer's evidence footprint still matches the new ask closely enough.

- This gives a middle ground:
  - stronger than pure ask-to-ask similarity
  - cheaper than full grounded retrieval
  - safer for bounded read-only reuse

==========================================================================================
[R1B] HARD REJECTION CASES
==========================================================================================

Do NOT reuse from semantic cache when any of the below is true:

- live or rapidly changing facts are required
- the ask implies current status, latest data, or deadline-sensitive detail
- the task asks for deep reading, synthesis, or source reconciliation
- the actor / tenant / region / permission scope changed
- the answer depended on fragile contextual qualifiers
- the prior support bundle was thin, stale, or contradictory
- the route implies action, mutation, or approval-bound output

If any of those fire, R1B should fall through to grounded retrieval, action routing, or safe fallback.

==========================================================================================
[R1B] BOTTOM LINE
==========================================================================================

R1B is a governed hybrid reuse lane:
- semantic similarity narrows candidates
- BM25 / sparse anchors protect factual precision
- optional fact-vector support bundles improve evidence continuity
- policy, freshness, and task-shape gates decide if reuse is allowed
- only validated approximate matches are allowed to short-circuit
