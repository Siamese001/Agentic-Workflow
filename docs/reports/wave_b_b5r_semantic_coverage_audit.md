# Wave B B5R Semantic Coverage Audit

**Date**: 2026-04-15
**Supersedes**: `wave_b_v30_coverage_audit.md` (B5/15-family framing)
**Baseline**: Wave B external-only audit — 14/20 adequately grounded, G9 FAIL at 70%
**Checklist sources**: `agentic_process_mapping_v30.md` + phase docs `01–06` + component docs `C0–C7` — used as capability checklists ONLY
**Anti-drift rule**: Target-state guidance MUST be grounded from `ext_authority` only. Checklist docs define what to test; they do not define what good should be.

---

## 1. Ranked Audit Findings

| Rank | Severity | Finding |
|------|----------|---------|
| 1 | **BLOCKING** | **F08 — R1A Exact Cache**: MISSING — no ext_authority source covers deterministic policy-driven LLM response caching |
| 2 | **BLOCKING** | **F09 — R1B Semantic Cache**: MISSING — no ext_authority source covers vector-similarity query cache lookup |
| 3 | **BLOCKING** | **F12 — C0 Evidence Fetch (full pipeline)**: WEAK — hybrid/sparse (TS-03), parent-child (TS-07), embedding (TS-19) all WEAK; dense-only ADEQUATE |
| 4 | **BLOCKING** | **F13 — C0 Evidence Shaping**: WEAK — reranking (TS-04) WEAK; dedup/prune ADEQUATE via TS-08 |
| 5 | **BLOCKING** | **F14 — C0 Evidence Contract / Refine-Abstain**: WEAK — abstain (TS-09) WEAK; provenance ADEQUATE via TS-05 |
| 6 | **BLOCKING** | **F17 — R5 Fallback / Abstain Route**: WEAK — TS-09 dist@1=0.510 |
| 7 | **BLOCKING** | **F06 — L1 Validation / Abstain Planning**: WEAK — TS-09 WEAK; plan eval ADEQUATE via TS-17 |
| 8 | **BLOCKING** | **F25 — Healing / Escalation Tiers**: WEAK — no ext_authority source covers confidence-scored tier dispatch (local/model/human) for agentic repair; **net-new B5R gap** |
| 9 | SCOPED OUT | **F21 — Replay Envelope / Freeze Propagation**: INTERNAL — replay_key + L0→L3→L5→L2 freeze is project-specific determinism hardening; not a B6 ext_authority gap |
| 10 | SCOPED OUT | **F22 — Replay Guard**: INTERNAL — wall-clock/entropy/uuid/network interception is internal; not B6 ext_authority scope |
| 11 | ADVISORY | **F02 — Ingress Auth / Quota / Schema**: WEAK — no dedicated agentic ingress-envelope source; lower priority than core retrieval gaps |
| 12 | ADVISORY | **F28 — UWG / Write Governance**: WEAK — single-gate write sovereignty has external analogs (CQRS, event sourcing) but is primarily internal architecture; repo_evidence Lane C scope |
| 13–31 | NON-BLOCKING | All other families: ADEQUATE or STRONG — no B6 source needed |

---

## 2. 31-Family Semantic Checklist with Classifications

| # | Family | Source Doc Reference | Scope | Grade | TS Basis | Net-New vs B5? |
|---|--------|---------------------|-------|-------|----------|----------------|
| F01 | Request-source modes and bounded ingress | 01 U0–U4 queue | ext_authority | ADEQUATE | TS-11 (agentic arch) | Refined from old B5-F01 |
| F02 | Identity/quota/schema/normalization/stamped ingress contract | 01 E1–E6 front desk | ext_authority | **WEAK** | TS-16, TS-20 | NEW |
| F03 | L1 intent framing and work classification | 02 I1–I4 | ext_authority | ADEQUATE | TS-01, TS-11 | NEW |
| F04 | L1 priors/policy/example loading | 02 M1–M4 | ext_authority | ADEQUATE | TS-01, TS-11 | NEW |
| F05 | L1 decomposition/dependency/proposed-route drafting | 02 P1–P4 | ext_authority | **STRONG** | TS-12 (0.349), TS-18 (0.329) | NEW |
| F06 | L1 validation/simplify/clarify/abstain planning | 02 V1–V5 | ext_authority | **WEAK** | TS-09 WEAK (0.510), TS-17 ADEQUATE | NEW — shares TS-09 gap |
| F07 | L0 route authority/prefilters/freshness/ACL | 03 L0 dispatcher; tenant/ACL/region bounds | ext_authority | ADEQUATE | TS-10, TS-11 | Refined from old B5-F01 |
| F08 | R1A exact cache route | 03 D1→R1A; norm query, permissions, zero inference | ext_authority | **MISSING** | None | Confirmed MISSING from B5 |
| F09 | R1B semantic cache route | 03 D2→R1B; query_vec vs cached_vecs, freshness | ext_authority | **MISSING** | None | Confirmed MISSING from B5 |
| F10 | R3 grounded-context decision | 03 D3→R3; factual/policy claims need backing | ext_authority | ADEQUATE | TS-02, TS-10 | NEW (split from old B5-F04) |
| F11 | C0 retrieval planning/scoping | C5 C0.1; scope, freshness, ACL, version, tenant, mode | ext_authority | ADEQUATE | TS-01, TS-02 | NEW (split from old B5-F05) |
| F12 | C0 evidence fetch: dense/sparse/cache/metadata hydration/parent-child | C5 C0.2; fact_vec + lexical + cache + parent-child expansion | ext_authority | **WEAK** | TS-02 ADEQUATE; TS-03 WEAK (0.561), TS-07 WEAK (0.515), TS-19 WEAK (0.510) | Expanded from old B5-F07 |
| F13 | C0 evidence shaping: dedup/rerank/prune/conflicts | C5 C0.3; dedup, expand, rerank, preserve provenance | ext_authority | **WEAK** | TS-08 ADEQUATE (0.445); TS-04 WEAK (0.531) | Expanded from old B5-F07 |
| F14 | C0 evidence contract: verified chunks/cited spans/refine-abstain | C5 C0.4; verified_chunks, cited_spans, coverage gaps, refine vs abstain | ext_authority | **WEAK** | TS-05 ADEQUATE (0.498); TS-09 WEAK (0.510) | NEW |
| F15 | Prompt assembly: load/slot/budget/contract | 03 PA.1–PA.4; template load, context slot, token budget, PromptEnvelope+HMAC | ext_authority | ADEQUATE | TS-01, TS-08 | Retained from old B5-F08 |
| F16 | R4 external action route | 03 D4→R4; dispatch, external payload, mutate state | ext_authority | **STRONG** | TS-13 (0.277), TS-14 (0.347) | Retained from old B5-F09 |
| F17 | R5 fallback/clarify/abstain route | 03 D4→R5; safest bound, abstain/clarify, ungrounded default | ext_authority | **WEAK** | TS-09 WEAK (0.510) | Retained from old B5-F10 |
| F18 | Governance invocation and authority context | C0 G1–G2; triage mode, integrity check, load policy/charter | ext_authority | ADEQUATE | TS-16 (0.456), TS-11 | NEW (split from old B5-F11) |
| F19 | Structure/registry/classification/policy chokepoint | C0 G3–G6; layer isolation, registry validation, shape classify, risk-tier chokepoint | ext_authority | ADEQUATE | TS-13 STRONG, TS-16 ADEQUATE | NEW |
| F20 | Sovereign egress/compliance artifacts/capability token/sandbox envelope | C0 G7, C7 G4–G6; symbolic→provider, capability_token, sandbox_envelope, fail-closed | ext_authority | ADEQUATE | TS-13 STRONG, TS-16 ADEQUATE | NEW |
| F21 | Replay envelope and freeze propagation | C1 BUILD REPLAY ENVELOPE + PROPAGATION; replay_key, policy_hash, L0→L3→L5→L2 freeze signal | **INTERNAL** | OUT OF SCOPE | — | NEW — internal determinism |
| F22 | Replay guard: time/entropy/identity/network/reads/writes | C1 REPLAY GUARD + DETERMINISM SURFACE; intercept wall-clock, seeded entropy, stable IDs, photocopy network | **INTERNAL** | OUT OF SCOPE | — | NEW — internal determinism |
| F23 | Determinism digest and replay verification | C1 Receipts Clerk; request/response logs, timing offsets, state diffs | Mixed (mostly internal) | ADEQUATE | TS-05 (provenance, 0.498) | NEW — internal replay specifics out of scope; audit trail/provenance ADEQUATE |
| F24 | L2 execution lifecycle E1–E5 | 04 E1–E5; freeze env, validate, bounded execute, heal loop, seal output | ext_authority | ADEQUATE | TS-12 STRONG (0.349), TS-15 STRONG (0.335) | Retained from old B5-F15 |
| F25 | Healing/remediation/escalation tiers | C3 Healing Tier Router + Dispatcher; local/model/human lanes, tier confidence scoring, sovereign gateway for repair | ext_authority | **WEAK** | TS-12 partial (coordination, not repair tiers) | **NET-NEW B5R BLOCKING GAP** |
| F26 | Current-run exit review and explicit dispositions | 05 X1–X2, C6 LIVE EXIT REVIEW; rubrics, answer fit, safety, groundedness, ALLOW/DENY/ESCALATE/COMMIT | ext_authority | ADEQUATE | TS-17 ADEQUATE (0.429), TS-16 ADEQUATE | Refined from old B5-F13 |
| F27 | HITL airlock and L5 re-clearance | 05 X3B H1–H4; freeze authority_state, bounded packet, human review, L5 re-clearance, APPROVE→ALLOW/COMMIT | ext_authority | ADEQUATE | TS-11 ADEQUATE, TS-16 ADEQUATE | NEW (split from old B5-F13) |
| F28 | UWG/state sovereignty/write governance/read-surface refresh | C4; serialized UWG, verify_boss, RBAC blast-radius, claim write lock, commit+chain, alias swap, cache refresh | Mixed (primarily internal) | **WEAK** | TS-16, TS-11 tangential | NEW — advisory; repo_evidence Lane C |
| F29 | L6 observability/verify spine/control buses/evidence bundle | C2 L6 VERIFY SPINE; time audit, isolation check, drift detect, BUS D/E/T, L6EvidenceBundle (Recall@K/MRR) | ext_authority | ADEQUATE | TS-17 (0.429), TS-05 (0.498), openai-agents tracing | Retained from old B5-F14 |
| F30 | Shadow evaluation/RCA/promotion pipeline | 06 S4, C6 PHASES 2–3; shadow eval, case file, investigation, rule drafting, commandant gauntlet, UWG promotion | ext_authority | ADEQUATE | TS-17, TS-11 | Retained from old B5-F14 |
| F31 | Capability/tool/model/network/memory/write access-control plane | C7 G1–G7; resource class, allowed_models, ACL, lane routing, capability_token, intercept call, invocation record | ext_authority | ADEQUATE | TS-13 STRONG (0.277), TS-16 ADEQUATE | NEW |

---

## 3. Mapping from Old B5 Families to B5R Families

| Old B5 Family | Old Grade | B5R Successor(s) | Change |
|--------------|-----------|-----------------|--------|
| F01 — L0 Route Authority | ADEQUATE | F01 (source modes) + F07 (route authority) | Split, both ADEQUATE |
| F02 — R1A Exact Cache | MISSING | F08 — R1A | Renumbered, still MISSING |
| F03 — R1B Semantic Cache | MISSING | F09 — R1B | Renumbered, still MISSING |
| F04 — R3 Agentic RAG | ADEQUATE | F10 (R3 decision) + F11 (C0 planning) | Split, both ADEQUATE |
| F05 — C0 Context Assembly | ADEQUATE | F11 (retrieval planning) + F15 (prompt assembly) | Split, both ADEQUATE |
| F06 — V1 Dense Vector Retrieval | ADEQUATE | F12 (dense component) | Dense component ADEQUATE; full pipeline WEAK |
| F07 — V1 Full Retrieval Pipeline | WEAK | F12 (evidence fetch) + F13 (evidence shaping) | Both still WEAK; F14 added |
| F08 — Prompt Assembly | ADEQUATE | F15 | Unchanged, ADEQUATE |
| F09 — R4 External Action | STRONG | F16 | Unchanged, STRONG |
| F10 — R5 Fallback | WEAK | F17 | Unchanged, WEAK |
| F11 — L5 Guardrails | ADEQUATE | F18 + F19 + F20 | Split into 3; all ADEQUATE |
| F12 — L5 Normative Requirements | WEAK (repo scope) | F02 (ingress) advisory + F28 (UWG) advisory | Both advisory/internal |
| F13 — [5] Exit Control | ADEQUATE | F26 (exit review) + F27 (HITL airlock) | Split, both ADEQUATE |
| F14 — [6] Future-Run Learning | ADEQUATE | F29 (L6 observability) + F30 (shadow eval) | Split, both ADEQUATE |
| F15 — L2 Execution Contract | STRONG | F24 (L2 lifecycle) ADEQUATE + F21/F22 INTERNAL | Downgraded: STRONG→ADEQUATE (internal components scoped out) |

---

## 4. Net-New Families Introduced in B5R

Families with no counterpart in the B5 15-family framing:

| Family | Grade | Impact |
|--------|-------|--------|
| F02 — Ingress auth/quota/schema | WEAK | Advisory; agentic ingress auth source recommended |
| F03 — L1 intent framing | ADEQUATE | No gap |
| F04 — L1 priors loading | ADEQUATE | No gap |
| F05 — L1 decomposition | STRONG | No gap |
| **F06 — L1 abstain planning** | **WEAK** | **Blocking — shares TS-09 gap; same source closes F06, F14, F17** |
| F10 — R3 decision | ADEQUATE | No gap |
| F11 — C0 retrieval planning | ADEQUATE | No gap |
| F14 — C0 evidence contract | WEAK | Blocking — shares TS-09 gap |
| F18 — Governance invocation | ADEQUATE | No gap |
| F19 — Structure/registry/policy chokepoint | ADEQUATE | No gap |
| F20 — Sovereign egress/capability token | ADEQUATE | No gap |
| F21 — Replay envelope/freeze | INTERNAL | Out of B6 scope |
| F22 — Replay guard | INTERNAL | Out of B6 scope |
| F23 — Determinism digest | Mixed/ADEQUATE | TS-05 covers provenance; internal replay out of scope |
| **F25 — Healing/escalation tiers** | **WEAK** | **Blocking — net-new B5R gap; needs dedicated source** |
| F27 — HITL airlock | ADEQUATE | No gap |
| F28 — UWG/write governance | WEAK | Advisory; primarily repo_evidence Lane C scope |
| F31 — Capability/tool/model access plane | ADEQUATE | No gap |

---

## 5. Weak or Missing Families: ext_authority Scope (B6 Required)

| Family | Grade | Gap Characterization | Minimum Source Category |
|--------|-------|---------------------|------------------------|
| **F08 — R1A Exact Cache** | MISSING | No ext_authority source on deterministic LLM response caching or policy-key short-circuit routing. Current sources (openai-agents, MCP, autogen) have no caching docs. | LLM response caching library docs (LangChain caching guide, Semantic Kernel caching) |
| **F09 — R1B Semantic Cache** | MISSING | No ext_authority source on vector-similarity-based query cache lookup for LLMs. TS-19 (embedding dims/metrics) is tangential. | Semantic/vector LLM caching docs (GPTCache, Zilliz semantic cache tutorial) |
| **F12 — C0 Evidence Fetch (full)** | WEAK | Dense retrieval ADEQUATE; BM25+dense hybrid (TS-03 0.561), parent-child expansion (TS-07 0.515), embedding selection (TS-19 0.510) all WEAK. Top-1 results return openai-agents tool docs — not retrieval library docs. | Hybrid dense+sparse retrieval docs + parent-child retrieval docs + embedding model guide |
| **F13 — C0 Evidence Shaping** | WEAK | Dedup/prune ADEQUATE (TS-08). Reranking WEAK (TS-04 0.531) — top-1 returns unrelated agent docs. Cross-encoder reranking pattern needs dedicated source. | Cross-encoder reranking pipeline docs (Cohere reranker, Anthropic retrieval cookbook) |
| **F14 — C0 Evidence Contract** | WEAK | Provenance/citation ADEQUATE (TS-05). Abstain/refine WEAK (TS-09 0.510) — no source covering evidence sufficiency thresholds or graceful abstain signals. | Abstain/refine best practices (shares P6 with F17) |
| **F17 — R5 Fallback / Abstain** | WEAK | TS-09 dist@1=0.510 — borderline WEAK. Top-1 returns generic agent approval flow, not explicit abstain pattern. Same source closes F06, F14, F17. | Abstain / graceful fallback best practices |
| **F06 — L1 Abstain Planning** | WEAK | V5 (V4: lowest viable agency; V5: abstain or clarify) — no external authority on simplify/abstain planning specifically. Shares the TS-09 gap. | Same abstain/refine source as above (P6) |
| **F25 — Healing / Escalation Tiers** | WEAK | C3 describes confidence-scored tier dispatch (high→local rule, medium→model, low→large model, human) with sovereign gateway. No ext_authority source covers tiered healing dispatch for agentic systems. TS-12 covers multi-agent coordination, not repair tier routing. | Tiered healing/escalation patterns: circuit breaker + fallback routing for agentic AI (e.g., LangGraph retry strategies, AutoGen error handling docs) |

---

## 6. Weak or Missing Families: repo_evidence / Internal Scope (Not B6 ext_authority)

| Family | Classification | Rationale |
|--------|---------------|-----------|
| **F21 — Replay Envelope / Freeze Propagation** | INTERNAL | Project-specific: replay_key tied to policy_hash, freeze signal injected L0→L3→L5→L2. External analogs (snapshot isolation) exist but are too generic to ground this specific pattern. Add architectural decision to repo_evidence Lane C. |
| **F22 — Replay Guard** | INTERNAL | Project-specific: intercepting wall-clock, seeded entropy, stable IDs, photocopy-only network calls, single-snapshot reads. This is a determinism hardening implementation, not a published external pattern. Repo_evidence scope. |
| **F23 — Determinism Digest** | Mostly internal | Receipts Clerk / hash-chain audit trail: external analogs in TS-05 (metadata provenance, ADEQUATE) cover the audit trail aspect. Specific determinism digest computation is internal. No B6 ext_authority action needed. |
| **F28 — UWG / Write Governance** | Primarily internal | Single-write-gate sovereignty, RBAC blast radius, alias swap on commit: internal architectural pattern. General write safety covered by TS-16 (ADEQUATE). If normative write policy must be documented externally, use repo_evidence Lane C (same as old TS-20 recommendation). |
| **F02 — Ingress Auth / Quota / Schema** | Advisory | E1–E6 ingress envelope (auth, quota, schema validation, normalization) is a system boundary concern, not a retrieval or agentic reasoning pattern. Lower retrieval priority. Add to B6 only if scope allows after P1–P8. |

---

## 7. Exact Minimum B6 Source Categories

| Priority | Source Addition | Closes | New Audit Query Needed? |
|----------|----------------|--------|------------------------|
| P1 | LLM response caching library docs (deterministic cache routing) | F08 — R1A | YES — 1 new query |
| P2 | Semantic/vector LLM caching docs (similarity-based query cache) | F09 — R1B | YES — 1 new query |
| P3 | Hybrid dense+sparse retrieval docs (BM25+dense fusion, score normalization) | F12 | TS-03 — existing query |
| P4 | Cross-encoder reranking pipeline docs | F12, F13 | TS-04 — existing query |
| P5 | Parent-child chunk expansion docs | F12 | TS-07 — existing query |
| P6 | Abstain / refine / graceful fallback best practices | F06, F14, F17 | TS-09 — existing query |
| P7 | Embedding model comparison / selection guide | F12 | TS-19 — existing query |
| P8 | Tiered healing / escalation patterns for agentic systems | F25 | YES — 1 new query |

**Total: 8 ext_authority source additions, 3 new audit queries (F08, F09, F25).**

**Do NOT add to ext_authority**: F21, F22 (internal), F28 (primarily internal → repo_evidence Lane C), F23 (provenance already ADEQUATE).

---

## 8. Final Go/No-Go Verdict for B6

**B6: GO — audit is complete enough to define a bounded source-addition plan.**

All 31 families are classified. Blocking gaps are precisely identified. B6 scope is bounded: 8 source additions, 3 new audit queries. The result is unambiguous.

| Condition | Status |
|-----------|--------|
| All 31 families classified | ✅ Done |
| Blocking B6 gaps identified | ✅ 8 families: F06, F08, F09, F12, F13, F14, F17, F25 |
| Internal-scope families scoped out | ✅ F21, F22 scoped out; F28 advisory |
| Exact source categories defined | ✅ P1–P8 |
| New audit queries identified | ✅ 3 new (F08/R1A, F09/R1B, F25/healing) |
| Wave C still blocked | ✅ G9 FAIL; 8 ext_authority gaps unresolved |

**Wave C: NO-GO until B6 complete.**

---

## 9. Single Final Recommendation

**Issue one bounded B6 source-addition prompt** with exactly this scope:

1. Add 8 ext_authority sources (P1–P8)
2. Extend audit to 23 queries (20 existing + 3 new for F08, F09, F25)
3. Re-run all 11 freeze gates
4. Target: ≥18/23 = 78% adequately grounded to exceed G9 75% threshold

Do not modify topology, routing, evidence_shaper, or any existing Wave B collection.  
Do not start Wave C until extended freeze gate audit passes.

This B5R audit supersedes both the B5 15-family audit (`wave_b_v30_coverage_audit.md`) and the B5 gap matrix (`wave_b_v30_gap_matrix.md`). Those documents remain as historical record only.
