# Agentic Routing and Retrieval System — Normative Requirements Specification

**ID**: `AGENTIC-NORMATIVE-REQS-v1`
**Version**: 1.0
**Status**: Active
**Domain**: `normative_req`
**Authority tier**: `T4_repo_canonical`
**Normative scope**: `repo_internal`
**Lane**: `repo_evidence` Lane C (`source_band: repo_canonical`)
**Date**: 2026-04-16
**Produced by**: Wave C2.1 — closes WC-G01 (TS-20 DOC_GAP) per `docs/reports/wave_c_gap_map.md`

---

## 1. Purpose

This document is the authoritative **internal normative requirements specification** for the
agentic routing and retrieval system. It defines MUST-level behavioural requirements for the
current-state codebase to satisfy, expressed at the architectural layer level, with a stable
`AGEN-XXXX` identifier per requirement.

This document is **repo-internal only**. It does not redefine the Wave B external
target-state baseline (`docs/requirements/wave_b_target_state_registry.md`). Where an external
target-state baseline exists in `ext_authority`, this document asserts the corresponding
internal obligation that the implementation must satisfy when it is built.

## 2. Scope

### In scope
- Query-time abstain planning (F06)
- Hybrid retrieval — lexical + dense fusion (F12)
- Retrieval expansion — parent-child and ADG-based (F12 expansion)
- Evidence sufficiency signal consumer (F14)
- Fallback / abstain routing (F17 / R5)
- Normative filter integration with the shaping pipeline (F13/F14 interface)
- Determinism and reproducibility obligations cross-cutting the above

### Out of scope
- External best-practice / target-state guidance — lives in `ext_authority` only
- F25-int healing dispatch routing — authored in Wave C2.2 as a separate ADR
- Wave B topology, route purity, and metadata contract — frozen by handoff contract v2.0
- Implementation ordering — sequenced by Wave D planning after C4 closeout

## 3. Binding Authority

| Source | Relation |
|--------|---------|
| `.claude/rules/constitutional.md` | Supersedes these requirements where they conflict |
| `docs/requirements/wave_c_handoff_contract.md` v2.0 | Frozen topology and route-purity constraints |
| `docs/reports/wave_c_gap_map.md` | Evidence for each requirement's gap classification |
| `docs/requirements/wave_b_target_state_registry.md` | Target-state baseline this doc internalises |
| `docs/requirements/wave_b_metadata_contract.md` | 14-field metadata contract for ingestion |

Where any statement in this document conflicts with the constitutional floor or the Wave C
handoff contract, the constitutional floor and the handoff contract control. This document
does not extend the allowed-writes envelope.

## 4. Requirement Format

Each requirement is a stable record with these fields:

- **id** — `AGEN-XXXX` identifier (stable)
- **title** — short human-readable label
- **domain** — `normative_req`
- **status** — `active`
- **family** — one of the Wave B family identifiers (F06, F12, F13, F14, F17, etc.)
- **statement** — MUST-level behavioural requirement
- **rationale** — why this requirement exists
- **current_state** — ABSENT / PARTIAL / IMPLEMENTED (from C1.3 gap map)
- **acceptance** — how the requirement is verified when implemented
- **references** — supporting evidence paths

---

## 5. Requirements

### AGEN-0100 — Query-Time Abstain Planning

- **id**: `AGEN-0100`
- **title**: Query-time abstain planning MUST be implemented in the query planning stage
- **domain**: `normative_req`
- **status**: `active`
- **family**: F06
- **statement**:
  The query planning stage MUST evaluate whether a query has sufficient normative coverage
  and retrieval quality before dispatch. When normative coverage is inadequate, the planner
  MUST either (a) emit a refined or decomposed sub-query set, or (b) emit a structured abstain
  signal that downstream routing honours. The planner MUST NOT silently proceed with a query
  whose planned evidence coverage is below the threshold encoded by the system contract.
- **rationale**:
  Without a planner-level abstain or refine branch, queries with inadequate normative sources
  produce low-confidence outputs that bypass the shaping-stage normative filter's fail-closed
  semantics. The planner is the correct layer for this decision because it can re-plan,
  whereas the shaping stage can only reject.
- **current_state**: ABSENT (WC-G07 in `wave_c_gap_map.md`)
- **acceptance**:
  - A confidence or coverage score is computed at planning time
  - A threshold is applied; below threshold, the planner emits either a refined plan or a
    structured abstain signal
  - The abstain signal is consumable by the routing layer (see AGEN-0104)
  - Unit tests cover the abstain branch and the refine branch separately
- **references**:
  - `agentic_core/L1_cognition/reasoning/query_planner.py` — current implementation is decomposition-only
  - `docs/reports/wave_c_gap_map.md` §4 WC-G07
  - `ext_authority` target-state baseline: abstain / refine signals (ADEQUATE at B7)

---

### AGEN-0101 — Hybrid Retrieval: BM25 + Dense Fusion

- **id**: `AGEN-0101`
- **title**: Hybrid retrieval MUST combine a lexical (BM25) score with a dense vector score
- **domain**: `normative_req`
- **status**: `active`
- **family**: F12 (core)
- **statement**:
  The hybrid search engine MUST execute both a dense vector retrieval and a lexical (BM25 or
  equivalent) retrieval for every query whose route requires hybrid search. Each result MUST
  carry a non-trivial `lexical_score` computed from the lexical backend. The fused ranking
  MUST use both scores and MUST NOT degenerate to the dense-only ranking. A `lexical_score`
  that is structurally `0.0` for every result is a non-conformance.
- **rationale**:
  Dense-only retrieval misses literal keyword matches, identifier fragments, and rare terms.
  The Wave B target-state baseline requires BM25+dense fusion (ADEQUATE at B7, grounded by
  B6 P3/P9). The current implementation populates `lexical_score=0.0` on every result,
  which is observationally equivalent to dense-only retrieval and fails the contract.
- **current_state**: PARTIAL (WC-G05 in `wave_c_gap_map.md`) — `HybridSearchEngine.search()` calls
  `_vector_search()` only; `lexical_score=0.0` always
- **acceptance**:
  - A lexical backend (BM25 index or equivalent) is operational for every collection routed
    to hybrid search
  - `lexical_score` on each result is non-zero for at least some queries in the eval harness
  - The fused score differs from the dense-only score on the golden query set
  - The eval harness in `tools/eval/retrieval_eval_curated.py` exercises the fused path
- **references**:
  - `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` — current implementation
  - `docs/reports/wave_c_gap_map.md` §4 WC-G05
  - `ext_authority` target-state baseline: Hybrid retrieval / BM25+dense (ADEQUATE at B7)

---

### AGEN-0102 — Retrieval Expansion: Parent-Child and ADG

- **id**: `AGEN-0102`
- **title**: Retrieval expansion MUST be implemented for parent-child chunk relations and ADG fan-in
- **domain**: `normative_req`
- **status**: `active`
- **family**: F12 (expansion)
- **statement**:
  When a chunk is returned by the hybrid retrieval stage, the expansion stage MUST be able to
  surface (a) the parent chunk and adjacent sibling chunks from the same document section, and
  (b) structurally-related chunks via the ADG fan-in graph when the query targets a code
  symbol, import, or file path. Stub implementations that return the unmodified input list
  do not satisfy this requirement.
- **rationale**:
  Single-chunk retrieval loses section context and structural relations that are essential
  for correctness-critical queries (code-symbol lookup, import analysis, policy cross-reference).
  The Wave B target-state baseline requires parent-child chunk expansion (ADEQUATE at B7,
  grounded by B6 P5/P9).
- **current_state**: ABSENT (WC-G05 in `wave_c_gap_map.md`) — `expand_results_with_parent_child()`
  and `expand_results_with_adg()` are stubs that return the input list unchanged
- **acceptance**:
  - `expand_results_with_parent_child()` returns a list that is a strict superset of the input
    when a parent chunk exists and is not already present
  - `expand_results_with_adg()` uses the ADG MCP (not grep) to surface structurally-related
    nodes when the query targets Python identifiers, files, or layers
  - Eval harness coverage exercises both expansion paths on queries where expansion matters
- **references**:
  - `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` — current stubs
  - `docs/reports/wave_c_gap_map.md` §4 WC-G05
  - `ext_authority` target-state baseline: Parent-child chunk expansion (ADEQUATE at B7)

---

### AGEN-0103 — Evidence Sufficiency Signal Consumer

- **id**: `AGEN-0103`
- **title**: `LOW_NORMATIVE_COVERAGE` MUST have a production consumer that triggers refine, retry, or abstain
- **domain**: `normative_req`
- **status**: `active`
- **family**: F14
- **statement**:
  The `LOW_NORMATIVE_COVERAGE` signal emitted by `filter_normative_sources()` MUST be consumed
  by at least one production caller that triggers one of the following actions: (a) a refined
  re-query with broader scope, (b) a retry with an expanded evidence set, or (c) a structured
  abstain surfaced to the user. An implementation in which the signal is defined and emitted
  but has no production consumer is a non-conformance, regardless of whether tests assert the
  constant's export.
- **rationale**:
  The normative filter is correctly fail-closed, but without a downstream handler the signal
  is silently dropped and the query response is effectively empty with no recovery attempt.
  The Wave B target-state baseline requires abstain/refine signals to be actionable, not
  cosmetic (ADEQUATE at B7, grounded by B6 P6/P11).
- **current_state**: PARTIAL (WC-G06 in `wave_c_gap_map.md`) — signal defined and emitted; no
  production consumer exists (only `tools/validate/validate_authority_enforcement.py:199` and
  `tests/unit/.../test_query_routing.py:29` reference the constant, both for assertion only)
- **acceptance**:
  - At least one production module (not test, not validation script) imports
    `LOW_NORMATIVE_COVERAGE` from `evidence_shaper.py`
  - That module branches on the signal and invokes a refine / retry / abstain action
  - An end-to-end test reproduces a low-coverage query and asserts the refine or abstain
    branch executes
- **references**:
  - `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py` — signal definition and emission
  - `docs/reports/wave_c_gap_map.md` §4 WC-G06
  - `ext_authority` target-state baseline: abstain / refine signals (ADEQUATE at B7)

---

### AGEN-0104 — Fallback and Abstain Route (R5)

- **id**: `AGEN-0104`
- **title**: The routing layer MUST provide an R5 fallback / abstain route distinct from hard error
- **domain**: `normative_req`
- **status**: `active`
- **family**: F17
- **statement**:
  The semantic-intent routing layer MUST provide an R5 route that is distinct from both
  `ROUTE_SUCCEEDED` (primary success) and `RoutingContractError` (hard contract refusal). The
  R5 route MUST be selected when confidence or evidence thresholds are not met and MUST either
  (a) dispatch to a documented fallback collection with reduced authority, or (b) emit a
  structured abstain response. Payload-shape dispatch (`PathRouter.select_path()` selecting
  Path.A/B/C/D from `check_ids`/`sanitized`) does not satisfy this requirement; R5 operates
  on semantic intent and confidence, not on payload shape.
- **rationale**:
  The current routing stack offers only success (`ROUTE_SUCCEEDED`) or hard refusal
  (`RoutingContractError`). Queries with low confidence but no contract violation have no
  graceful path. The spec diagram in `docs/reference/03_L0_Routing/03_Route_Decision_Switching v3.md`
  describes R5 as a first-class route; the implementation MUST include it.
- **current_state**: ABSENT (WC-G08 in `wave_c_gap_map.md`) — `PathRouter` and `escalation_router`
  do not implement a confidence-floor fallback/abstain route
- **acceptance**:
  - A new `RoutingOutcomeStatus.ROUTE_ABSTAINED` or equivalent is defined and emitted
  - A confidence or evidence threshold governs R5 selection and is documented
  - R5 selection is consumable by the abstain planner (AGEN-0100) and the evidence
    sufficiency consumer (AGEN-0103), forming a coherent abstain chain
  - Unit tests cover the R5 branch without requiring a contract violation
- **references**:
  - `agentic_core/L0_routing/reasoning/path_router.py` — current PathRouter is payload-shape dispatch
  - `agentic_core/L0_routing/reasoning/escalation_router.py` — violation-triggered escalation only
  - `docs/reference/03_L0_Routing/03_Route_Decision_Switching v3.md` — R5 spec diagram
  - `docs/reports/wave_c_gap_map.md` §4 WC-G08
  - `ext_authority` target-state baseline: routing principles (ADEQUATE at B7)

---

### AGEN-0105 — Normative Filter Integration

- **id**: `AGEN-0105`
- **title**: Shaping pipeline MUST integrate the normative filter with the sufficiency consumer and the abstain planner
- **domain**: `normative_req`
- **status**: `active`
- **family**: F13/F14 (integration)
- **statement**:
  The evidence shaping pipeline MUST preserve the existing normative filter semantics
  (`filter_normative_sources()` partitions results into accepted and rejected; accepted-empty
  surfaces `LOW_NORMATIVE_COVERAGE`). The pipeline MUST forward the `LOW_NORMATIVE_COVERAGE`
  signal to the sufficiency consumer (AGEN-0103) and permit the abstain planner (AGEN-0100) to
  observe the shaping outcome when planning the next action. The pipeline MUST NOT fall back
  to `rejected` chunks for normative use under any circumstance.
- **rationale**:
  The filter behaviour is already correct; this requirement ensures that future changes
  preserve the contract and that the three layers (shaping, sufficiency, planning) are wired
  as a coherent abstain chain rather than three disconnected components.
- **current_state**: IMPLEMENTED for the filter itself; PARTIAL for the integration
- **acceptance**:
  - `filter_normative_sources()` behaviour is unchanged
  - A callable consumer of the signal exists (see AGEN-0103)
  - An integration test exercises the full path: retrieval → shaping → sufficiency → abstain/refine
- **references**:
  - `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py`
  - `docs/reports/wave_c_gap_map.md` §7 "No-Action Items" (filter main path) and §4 WC-G06 (integration gap)

---

### AGEN-0106 — Determinism and Reproducibility

- **id**: `AGEN-0106`
- **title**: The routing and retrieval stack MUST be deterministic for a fixed query, corpus, and seed
- **domain**: `normative_req`
- **status**: `active`
- **family**: cross-cutting
- **statement**:
  For a fixed query string, a fixed corpus snapshot (fixed `canonical_digest` set), and fixed
  random seeds where applicable, the following MUST be byte-stable across repeated invocations:
  the chosen route, the ranked retrieval result IDs, the shaping output order, and the
  abstain/refine/success outcome. Caching layers MUST either preserve determinism (exact hash
  cache) or carry a policy flag that justifies approximate reuse (semantic cache — AGEN
  follow-up).
- **rationale**:
  Non-determinism in any of these layers breaks evaluation harness repeatability (G9),
  undermines freeze-gate audits, and prevents regression detection.
- **current_state**: IMPLEMENTED for the exact cache and vector retrieval paths; requirements
  in this spec (AGEN-0100..0104) MUST preserve determinism when they are implemented
- **acceptance**:
  - A fixed-seed test fixture reproduces identical route + top-K IDs + shaping order across
    repeated runs
  - Eval harness outputs (`tools/eval/retrieval_eval_curated.py`) are byte-stable on an
    unchanged corpus
- **references**:
  - `agentic_core/L4_state/cache/gptcache_client.py` — exact cache
  - `agentic_core/cache/redis_cache_client.py` — `DeterministicRedisCache` hash-keyed
  - `docs/reports/wave_c_gap_map.md` §7 "No-Action Items"

---

## 6. Traceability to the Current-State Gap Map

| Requirement | Family | Gap Map ID | Current State |
|-------------|--------|-----------|---------------|
| AGEN-0100 | F06 | WC-G07 | ABSENT |
| AGEN-0101 | F12 core | WC-G05 | PARTIAL |
| AGEN-0102 | F12 expansion | WC-G05 | ABSENT |
| AGEN-0103 | F14 | WC-G06 | PARTIAL |
| AGEN-0104 | F17 | WC-G08 | ABSENT |
| AGEN-0105 | F13/F14 integration | — | PARTIAL |
| AGEN-0106 | cross-cutting | — | IMPLEMENTED (must be preserved) |

No requirement in this document is satisfied in current state without further implementation,
except AGEN-0106 which is partially satisfied and MUST be preserved by implementations of the
other requirements. Implementation sequencing is Wave D scope.

## 7. Non-Regression

Implementations satisfying any requirement in this document MUST NOT regress the following:

- Wave B 11 freeze gates (G1–G11) — per `docs/reports/wave_b_b7_freeze_gates.md`
- Route purity — `query_router.py` domain-to-collection mappings frozen
- Metadata contract — 14 required fields per `wave_b_metadata_contract.md`
- `evidence_shaper.py` normative filter semantics — per AGEN-0105
- Constitutional hard constraints — per `.claude/rules/constitutional.md`

## 8. Validation

Each requirement's `acceptance` field is the primary validation criterion. Verification is
executed in Wave D via:

- Unit and integration tests cited per requirement
- Eval harness (`tools/eval/retrieval_eval_curated.py`) for retrieval-layer requirements
- Freeze-gate re-run for non-regression (Wave C4 baseline)

## 9. Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-04-16 | Wave C2.1 | Initial publication — closes WC-G01 (TS-20 DOC_GAP) |

## 10. References

- `docs/reports/wave_c_gap_map.md` — current-state gap map (authoritative for `current_state` fields)
- `docs/requirements/wave_c_handoff_contract.md` — frozen scope for Wave C
- `docs/requirements/wave_b_target_state_registry.md` — external target-state baseline
- `docs/requirements/wave_b_metadata_contract.md` — ingestion metadata contract
- `docs/requirements/agentic_requirements_registry_spec.md` — registry format specification (schema only)
- `docs/requirements/registry/` — per-requirement YAML records (future Wave D expansion)
- `.claude/rules/constitutional.md` — constitutional floor (supersedes this document on conflict)
- `.claude/plans/wave_c_plan.md` — Wave C execution plan
