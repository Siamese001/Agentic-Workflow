# Wave C Current-State Gap Map

**Version**: 1.0 · **Status**: Active · **Date**: 2026-04-16
**Produced by**: C1.3 (read-only inventory synthesis — no code, ingestion, or topology changes)
**Binding scope**: `docs/requirements/wave_c_handoff_contract.md` v2.0 + `.windsurf/plans/wave_c_plan.md`
**Drives**: C2.1, C2.2, C3.1 (optional), C4 validation

---

## 1. Scope and Frozen Constraints

**In scope for this document**: classification of current-state implementation status for all B7-relevant
families inspected during C1.1 and C1.2. No code, ingestion, routing, or topology changes are made here.

**Frozen constraints carried forward from handoff contract §9**:

- 3-collection topology unchanged (`ext_authority`, `repo_evidence`, `ext_raw`)
- `query_router.py` domain-to-collection mappings frozen
- `evidence_shaper.py` `allowed_collections` default frozen
- `invalid_for_normative_use` values on existing chunks frozen
- F25-int adjudication final — do not add ext_authority sources for F25-int
- TS-03, TS-04, TS-07, TS-09, TS-19 ADEQUATE at B7 — do not reopen
- No retrieval path redesign, hybrid fusion, reranking pipeline, or query intent detection in Wave C
- No Wave D implementation starts until C4 closeout

---

## 2. Evidence Sources Used

### C1.1 code inspections (read-only)

| File | Key Finding |
|------|-------------|
| `agentic_core/L1_cognition/reasoning/query_planner.py` | Decomposition-only; lifecycle markers are ADG contract annotations |
| `agentic_core/L0_routing/reasoning/path_router.py` | Payload-shape dispatch (check_ids → Path.A/B/C/D); no R5 route |
| `agentic_core/L0_routing/reasoning/escalation_router.py` | Violation-triggered escalation only; no confidence-floor abstain |
| `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` | `lexical_score=0.0` always; expansion methods are stubs |
| `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py` | `filter_normative_sources()` + `apply_authority_rerank()` implemented; `LOW_NORMATIVE_COVERAGE` signal has no production consumer |
| `agentic_core/L4_state/cache/gptcache_client.py` | Exact + semantic cache implemented |
| `agentic_core/cache/redis_cache_client.py` | `DeterministicRedisCache` — content-hashed exact cache implemented |
| `agentic_core/L1_cognition/reasoning/reranking_engine.py` | LightGBM reranker exists but not wired to Wave B `ext_authority`/`repo_evidence` path |
| `agentic_core/base_agents/` (directory) | No `healing_tier_router.py` or `confidence_dispatch.py` present |
| `docs/requirements/registry/` | 3 YAML stubs (AGEN-0001, AGEN-0002, AGEN-0050): policy/best_practice only; zero normative_req domain entries |

### C1.2 grep / call-site analysis

| Target | Finding |
|--------|---------|
| `grep LOW_NORMATIVE_COVERAGE *.py` | Defined at `evidence_shaper.py:8`; imported only in `tools/validate/validate_authority_enforcement.py:199` and `tests/unit/.../test_query_routing.py:29` (both assert constant export only — no production consumer) |
| `tools/eval/retrieval_eval_curated.py` | Uses `COLLECTIONS = ["repo_evidence", "ext_raw", "ext_authority"]` + ChromaDB `query_texts` only; `lexical_score` never tested; confirms G-C1 eval gap |

### C1.2 `repo_evidence` queries

| Query | dist@1 | Top hit | Verdict |
|-------|--------|---------|---------|
| "normative requirements specification for the agentic routing system" | **0.4033** | `docs/requirements/agentic_requirements_registry_spec.md` (format spec, Status=Design, `invalid_for_normative_use=true`) | DOC_GAP confirmed |
| "confidence-scored tiered healing dispatch routing tiers local rules model retry human escalation" | **0.3881** | `docs/reference/agentic_process_mapping_v29.md` — describes `dispatch_healing()` + `healing_tier_router` tiers; `HEALER_RETRY_HARDENING_SPEC.md` — `RetryConfig.strictness_escalation: [0.7, 0.85, 0.95]` | Concept documented, implementation module absent |

---

## 3. Gap Map Table

> **Grade key**: STRONG = dist@1 ≤ 0.35 | ADEQUATE = dist@1 ≤ 0.50 | WEAK = dist@1 > 0.50 | N/A = out of ext_authority scope

| Gap ID | Topic / Family | ext_authority B7 Baseline | Current-State Status | Gap Type | Exact Repo Evidence | Wave C Action |
|--------|---------------|--------------------------|----------------------|----------|---------------------|---------------|
| — | F08: Exact cache (R1A) | ADEQUATE (B6 P1) | **IMPLEMENTED** | NONE | `gptcache_client.NativePersistentCacheClient.get()` → Redis exact hash + SQLite fallback; `cache/redis_cache_client.DeterministicRedisCache.get()`/`set()` | None |
| — | F09: Semantic cache (R1B) | ADEQUATE (B6 P2) | **IMPLEMENTED** | NONE | `gptcache_client.NativePersistentCacheClient.search_similar()` → ChromaDB `query_texts` + similarity threshold | None |
| WC-G05 | F12: Hybrid retrieval / BM25+dense (C0.2 Fetch) | ADEQUATE (B6 P3/P9) | **PARTIAL** | IMPL_GAP | `hybrid_search_engine.HybridSearchEngine.search()` calls `_vector_search()` only; `lexical_score=0.0` on every result; `expand_results_with_parent_child()` returns `list(results)` unchanged; `expand_results_with_adg()` returns `list(results)` unchanged | None — Wave D implementation scope. Gap recorded for C4 sequencing note. |
| — | F13: Evidence shaping / authority reranking (C0.4 Shape) | ADEQUATE (B6 P4 + dist@1=0.445) | **IMPLEMENTED** (Wave B path) | NONE | `evidence_shaper.apply_authority_rerank()` + `_TIER_RERANK_DISCOUNT`; `filter_normative_sources()`; `doc_family_dedup()`; `collapse_group_dedup()` — all wired to Wave B query path. `reranking_engine.RerankingEngine` (LightGBM) exists but consumes `FusionResult` over `repo_*` collections — not wired to Wave B path | None for main path. ML reranker wiring is Wave D scope. |
| WC-G06 | F14: Evidence sufficiency / refine-abstain (C0.5 Contract) | ADEQUATE (B6 P6/P11) | **PARTIAL** | IMPL_GAP | `evidence_shaper.LOW_NORMATIVE_COVERAGE` constant defined; `filter_normative_sources()` gate correct and fail-closed. No production call site consumes the signal — `validate_authority_enforcement.py:199` and `test_query_routing.py:29` only assert constant export. No refine loop, re-query, or abstain action is triggered. | None — Wave D implementation scope. Gap recorded for C4 sequencing note. |
| WC-G07 | F06: Abstain planning (F06 / R5 abstain path) | ADEQUATE (B6 P6/P11) | **ABSENT** | IMPL_GAP | `query_planner.query_planner` class has 5 methods (decompose, expand, HyDE only). `_emit_gated_by_confidence` at module lines 249–280 are ADG lifecycle contract annotations, not functional logic. No confidence variable, no threshold, no abstain branch in class body. | None — Wave D implementation scope. Gap recorded for C4 sequencing note. |
| WC-G08 | F17: Fallback / abstain route (R5) | ADEQUATE — routing principles (dist@1=0.473) | **ABSENT** | IMPL_GAP | `path_router.PathRouter.select_path()` routes by `check_ids`/`sanitized` flags → `Path.{A,B,C,D}` (governance dispatch). `RoutingOutcomeStatus.ROUTE_SUCCEEDED` is the only outcome recorded. `escalation_router.decide_mode_from_prior_violations()` handles violation-triggered escalation only — no confidence-floor trigger. No R5 fallback-collection or abstain path exists anywhere in the routing stack. | None — Wave D implementation scope. Gap recorded for C4 sequencing note. |
| WC-G01 | TS-20: Normative requirements spec | N/A (repo_evidence Lane C only) | **ABSENT** | DOC_GAP | `docs/requirements/agentic_requirements_registry_spec.md` is format/schema spec (Status=Design, `invalid_for_normative_use=true`). Registry has 3 stubs (AGEN-0001: bare-except, AGEN-0002: subprocess-timeout, AGEN-0050: ADG-first) — all policy/best_practice domain; zero normative_req domain entries. repo_evidence query dist@1=0.4033 returns only format spec. | **C2.1** — write `docs/requirements/normative_requirements_spec.md`; add to `repo_evidence` Lane C; verify dist@1 < 0.50 after rebuild |
| WC-G02 | F25-int: Confidence-scored healing dispatch routing | N/A (repo_evidence Lane C only; ext_authority addition forbidden per contract §9) | **IMPL_GAP** (concept documented, module absent) | IMPL_GAP | `agentic_process_mapping_v29.md` chunk 20 describes `dispatch_healing()` with tiers LOCAL\_AGENT → COORDINATED → ESCALATED and references `healing_tier_router` (dist@1=0.3881). `HEALER_RETRY_HARDENING_SPEC.md` has `RetryConfig.strictness_escalation: [0.7, 0.85, 0.95]`. No `healing_tier_router.py` in `base_agents/`. `healing_memory_retriever.py` is advisory read-only only. | **C2.2** — write `docs/architecture/healing_dispatch_routing_adr.md`; add to `repo_evidence` Lane C; verify dist@1 < 0.50 after rebuild |
| WC-G03 | F02: Ingress auth / quota / schema | Not in B7 grounded list (advisory) | **UNCLEAR** | ADVISORY | Not inspected in C1. No dedicated ingress auth module found in C1.1 scope. | **C3.1 (optional)** — evaluate ext_authority candidate source; accept only if dist@1 < 0.45. Skip C3 if gate fails. |
| WC-G04 | F28: UWG / write governance | Not in B7 grounded list (advisory) | Not inspected | ADVISORY | Out of C1 inspection scope | Post-C4 advisory (Wave D) |
| — | F25-ext: Tiered escalation / HITL / durable execution | ADEQUATE advisory (running_agents.md HITL section) | ADEQUATE in ext_authority | NONE | ext_authority grounded at B7; adjudication final; do not reopen | None |
| — | F05: Query decomposition / multi-query | Not a B7 hard gate | **IMPLEMENTED** | NONE | `query_planner.decompose_query()`, `multi_query_generation()` — fully functional | None |
| — | All other B7 grounded topics (orchestrator-workers, MCP tools, FastMCP, agent handoffs, single/multi-agent, safety guardrails, evaluator-optimizer, context engineering, contextual retrieval, embedding model, chunking) | ADEQUATE to STRONG | ADEQUATE in ext_authority | NONE | B7 freeze gates G9–G11 passing at ≥95%; no regression | None |

---

## 4. Confirmed Implementation Gaps (IMPL_GAP)

These gaps exist in the current repo implementation relative to the B7 target-state baseline.
**None require Wave C implementation.** All are Wave D scope. They are recorded here to:
(a) establish the current-state baseline; (b) drive the C4 sequencing note; (c) prevent premature closure.

### WC-G05 — F12: Hybrid Retrieval (BM25 + dense fusion, expansion)

- **Status**: PARTIAL
- **File**: `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py`
- **Evidence**:
  - `HybridSearchEngine.search()` calls `_vector_search()` only; `lexical_score` field is structurally `0.0`
  - `expand_results_with_parent_child()` → `return list(results)` (stub)
  - `expand_results_with_adg()` → `return list(results)` (stub)
- **Target-state baseline**: `ext_authority` ADEQUATE at B7 (BM25+dense hybrid pattern grounded by B6 P3/P9)
- **Wave C action**: None — implementation is Wave D scope

### WC-G06 — F14: Evidence Sufficiency Signal Consumer

- **Status**: PARTIAL
- **File**: `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py`
- **Evidence**:
  - `LOW_NORMATIVE_COVERAGE = "LOW_NORMATIVE_COVERAGE"` defined at line 8
  - `filter_normative_sources()` correctly implemented and fail-closed
  - Zero production callers consume the signal to trigger refine/retry/abstain
  - Docstring mandates: "caller MUST NOT fall back … surface `LOW_NORMATIVE_COVERAGE` instead" — no such caller exists
- **Target-state baseline**: `ext_authority` ADEQUATE at B7 (abstain/refine signals grounded by B6 P6/P11)
- **Wave C action**: None — consumer implementation is Wave D scope

### WC-G07 — F06: Abstain Planning

- **Status**: ABSENT
- **File**: `agentic_core/L1_cognition/reasoning/query_planner.py`
- **Evidence**:
  - `query_planner` class: 5 methods only (`__init__`, `multi_query_generation`, `decompose_query`, `decompose_and_expand`, `generate_synthetic_passages`)
  - Module-level `_emit_gated_by_confidence(...)` calls (lines ~249–280) are ADG lifecycle contract annotations
  - No confidence variable, no threshold check, no abstain branch in class body
- **Target-state baseline**: `ext_authority` ADEQUATE at B7 (abstain/refine signals grounded)
- **Wave C action**: None — implementation is Wave D scope

### WC-G08 — F17: R5 Fallback / Abstain Route

- **Status**: ABSENT
- **File**: `agentic_core/L0_routing/reasoning/path_router.py`, `agentic_core/L0_routing/reasoning/escalation_router.py`
- **Evidence**:
  - `PathRouter.select_path()` routes `GovernedPayload` by `check_ids`/`sanitized` → `Path.{A,B,C,D}` (governance dispatch, not semantic intent routing)
  - `RoutingOutcomeStatus.ROUTE_SUCCEEDED` is the only outcome emitted
  - `RoutingContractError` is a hard error, not a fallback
  - `escalation_router.decide_mode_from_prior_violations()` handles prior-violation escalation only; no confidence-floor trigger
  - No module in the inspected routing stack implements an R5 path (fallback collection, abstain emit, or ungrounded-default route)
- **Target-state baseline**: `ext_authority` ADEQUATE at B7 (routing principles grounded, dist@1=0.473)
- **Wave C action**: None — implementation is Wave D scope

### WC-G02 — F25-int: Confidence-Scored Healing Dispatch Routing

- **Status**: IMPL_GAP (concept documented in repo docs/specs; routing module absent)
- **Files**: `agentic_core/base_agents/` (no `healing_tier_router.py`); `agentic_core/L1_cognition/reasoning/healing_memory_retriever.py` (advisory read-only only)
- **Evidence**:
  - `docs/reference/agentic_process_mapping_v29.md` describes `dispatch_healing()` with tiers LOCAL_AGENT → COORDINATED → ESCALATED; references `healing_tier_router` (repo_evidence dist@1=0.3881 — relevant but undocumented as ADR)
  - `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md`: `RetryConfig.strictness_escalation: [0.7, 0.85, 0.95]`
  - No `healing_tier_router.py` module in `agentic_core/base_agents/` or inspected scope
  - Concept exists in reference/spec docs; no ADR or standalone architecture decision document
- **Lane**: repo_evidence Lane C only (ext_authority addition forbidden per handoff contract §9)
- **Wave C action**: **C2.2** — author `docs/architecture/healing_dispatch_routing_adr.md`; ingest to `repo_evidence` Lane C

---

## 5. Confirmed Documentation Gaps (DOC_GAP)

### WC-G01 — TS-20: Normative Requirements Spec

- **Status**: ABSENT (format spec exists; normative content absent)
- **Evidence**:
  - `docs/requirements/agentic_requirements_registry_spec.md`: format/schema specification (`Status: Design`); `authority_tier: T4_implementation_evidence`; `invalid_for_normative_use: true`
  - `docs/requirements/registry/`: 3 YAML stubs — `AGEN-0001` (bare-except policy), `AGEN-0002` (subprocess-timeout policy), `AGEN-0050` (ADG-first best_practice)
  - Zero entries in `normative_req` domain covering F06–F17, F25-int, or any routing/retrieval/caching family
  - repo_evidence query dist@1=0.4033 returns format spec only; all results `invalid_for_normative_use: true`
- **Lane**: repo_evidence Lane C only (project-specific; no https:// source; excluded from ext_authority per contract §7)
- **Wave C action**: **C2.1** — author `docs/requirements/normative_requirements_spec.md`; ingest to `repo_evidence` Lane C; verify dist@1 < 0.50 post-rebuild

---

## 6. Advisory Items

### WC-G03 — F02: Ingress Auth / Quota / Schema

- **Status**: UNCLEAR (not in C1 inspection scope; no dedicated module found)
- **Lane**: ext_authority advisory (non-B7 hard gate)
- **Wave C action**: **C3.1 (optional)** — evaluate one candidate source (e.g. OpenAI platform auth docs). Accept only if dist@1 < 0.45 for the F02 gap query. **Skip C3 entirely if gate fails.**
- **Gate condition per contract §7c**: dist@1 < 0.45 required for acceptance

### WC-G04 — F28: UWG / Write Governance

- **Status**: Not inspected in C1 scope
- **Lane**: repo_evidence Lane C (advisory)
- **Wave C action**: Post-C4 advisory (Wave D). Not a Wave C blocker.

---

## 7. No-Action Items (Already Aligned)

| Family | B7 Grade | Current-State | Rationale |
|--------|----------|---------------|-----------|
| F08: Exact cache (R1A) | ADEQUATE | IMPLEMENTED | `DeterministicRedisCache` + `NativePersistentCacheClient` exact hash lookup |
| F09: Semantic cache (R1B) | ADEQUATE | IMPLEMENTED | `NativePersistentCacheClient.search_similar()` — ChromaDB similarity threshold |
| F13: Evidence shaping (main path) | ADEQUATE | IMPLEMENTED | `apply_authority_rerank()` + tier discount + `filter_normative_sources()` + dedup — all wired to Wave B query path |
| F05: Query decomposition | Not a B7 gate | IMPLEMENTED | `query_planner.decompose_query()` + `multi_query_generation()` fully functional |
| F25-ext: Tiered escalation / HITL | ADEQUATE advisory | ADEQUATE in ext_authority | Grounded by `running_agents.md` HITL section; adjudication final |
| All other B7 grounded topics | ADEQUATE to STRONG | ADEQUATE | G9 ≥ 95% at B7; freeze gates G1–G11 all PASS; no regression |

---

## 8. Priority Ordering (Top Wave C Gaps to Address First)

| Priority | Gap ID | Rationale |
|----------|--------|-----------|
| 1 | **WC-G01 (TS-20)** | Clean write — no conflicting prior content; directly unblocks C4 G4/G5/G6 check for Lane C; foundational for the requirements registry used by all other gaps |
| 2 | **WC-G02 (F25-int)** | Concept already described in process maps (dist@1=0.3881 — above acceptable threshold); ADR authors the missing architectural decision; directly unblocks C4 G4/G5/G6 for Lane C |
| 3 | **WC-G03 (F02)** | Optional — evaluate first, skip if dist@1 ≥ 0.45; low risk, small scope; does not block C4 |
| 4 | **WC-G05 (F12)** | IMPL_GAP recorded for C4 sequencing; no Wave C action; Wave D |
| 5 | **WC-G06 (F14)** | IMPL_GAP recorded for C4 sequencing; no Wave C action; Wave D |
| 6 | **WC-G07 (F06)** | IMPL_GAP recorded for C4 sequencing; no Wave C action; Wave D |
| 7 | **WC-G08 (F17)** | IMPL_GAP recorded for C4 sequencing; no Wave C action; Wave D |

---

## 9. C2 Handoff Note

### C2.1 — What it must write

**Target file**: `docs/requirements/normative_requirements_spec.md`

**Must contain**:
- System-level normative requirements for the agentic routing system
- Coverage of the key families identified as IMPL_GAP (F06, F12, F14, F17) — stating what the system MUST do
- Requirement IDs in `AGEN-XXXX` format, `domain: normative_req`
- `status: active`, `authority_tier: T4_repo_canonical`, `normative_scope: repo_internal`

**Ingestion constraints**:
- `source_band: repo_canonical` (Lane C)
- `invalid_for_normative_use: True`
- `source_url`: repo-relative path, no `https://`
- All 14 mandatory metadata fields from `wave_b_metadata_contract.md`
- Add to `ingest_repo_evidence.py` source list; rebuild `repo_evidence` only

**Acceptance gate**: repo_evidence query `"normative requirements specification for the agentic routing system"` must return dist@1 < 0.50 after rebuild.

---

### C2.2 — What it must write

**Target file**: `docs/architecture/healing_dispatch_routing_adr.md`

**Must contain**:
- Architecture decision record for confidence-scored tiered healing dispatch routing
- Tier definitions: LOCAL_AGENT (in-agent retry), COORDINATED (multi-agent via `healing_tier_router`), ESCALATED (human HITL or abort)
- Confidence thresholds per tier (aligned with `HEALER_RETRY_HARDENING_SPEC.md` `strictness_escalation: [0.7, 0.85, 0.95]`)
- ADR status, context, decision, and consequences
- References to `agentic_process_mapping_v29.md` and `HEALER_RETRY_HARDENING_SPEC.md`

**Ingestion constraints**:
- `source_band: repo_canonical` (Lane C)
- `invalid_for_normative_use: True`
- `source_url`: repo-relative path, no `https://`
- All 14 mandatory metadata fields
- Add to `ingest_repo_evidence.py` source list; rebuild `repo_evidence` only

**Acceptance gate**: repo_evidence query `"confidence-scored tiered healing dispatch routing tiers local rules model retry human escalation"` must return dist@1 < 0.50 after rebuild. (Current dist@1=0.3881 — already below threshold but content is process-map chunks, not an ADR; the ADR must be the authoritative top result.)

---

### C3 — What remains optional

**C3.1**: Evaluate one ext_authority advisory source for F02 (ingress auth/quota/schema).

- Gate: dist@1 < 0.45 for F02 gap query after dry-run embedding
- If gate passes: add source to `ingest_ext_authority.py`, rebuild `ext_authority`, re-run G1/G2/G3/G9
- If gate fails: skip C3 entirely; F02 remains advisory and unresolved; does not block C4
- C3 does not block C2 or C4

---

## 10. Wave D Implementation Sequencing (for C4 Closeout Reference)

The following IMPL_GAPs are out of Wave C scope and recorded here solely to sequence Wave D work. They must not be started before the C4 closeout report is written.

| Gap | Implementation work required |
|-----|------------------------------|
| WC-G07 (F06) | Add confidence-score abstain branch to `query_planner.py` or a dedicated abstain planner |
| WC-G08 (F17) | Implement R5 fallback-collection / abstain route in the semantic intent routing layer |
| WC-G06 (F14) | Add a production caller that consumes `LOW_NORMATIVE_COVERAGE` and triggers refine/retry/abstain |
| WC-G05 (F12) | Implement BM25 lexical search backend and wire into `HybridSearchEngine.search()`; implement `expand_results_with_parent_child()` and `expand_results_with_adg()` |

---

## 11. Single Recommendation

**Proceed to C2.**

All five C1 ambiguities are fully resolved. The gap map is complete and unambiguous:

- **2 Wave C actions are required** (WC-G01 TS-20 → C2.1, WC-G02 F25-int → C2.2)
- **1 optional advisory** (WC-G03 F02 → C3.1)
- **4 IMPL_GAPs recorded** for Wave D sequencing (WC-G05 F12, WC-G06 F14, WC-G07 F06, WC-G08 F17) — no Wave C action
- **No unresolved ambiguities** that would block C2

C2.1 and C2.2 may proceed in any order. Both must complete before C4 runs the freeze gate suite.

---

*Gap map frozen at C1.3. Updates require a new C1.x re-inspection cycle.*
