---
plan_id: apps-rg-source-refreeze-c03-assertion-embeddings-c03a5e
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "C:\\Users\\amita\\.codex\\attachments\\0924326f-b3ca-4157-bdea-4dbfa45f8937\\pasted-text.txt"
dod_exempt: false
supersedes:
  - apps-rg-c03-graph-health-embedding-closure-b8d4f1
supersedes_embedding_policy: apps-rg-c03-graph-health-embedding-closure-b8d4f1
preserves_completed_runtime_baseline: true
mandatory_embedding_policy: one_vector_per_eligible_atomic_skill_assertion
no_embedding_promotion_is_success: false
---

# Apps RG Source Refreeze And C0.3 Assertion Embeddings

Repair the two frozen source defects first, then gate C0.3 authority, assertion-level BGE-M3 embeddings, and source certification before any standalone migration restart.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: SR0
BLOCKED_WAVE: NONE
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-07-19
STARTING_BRANCH: origin/main
STARTING_COMMIT: fc7039821148151e08459f8473cc8428df39bc8b
STARTING_TREE: 8e3fa68878aef4224f781335850a9eab7ff2c6c9
EXECUTION_WORKTREE: C:\Git\Agentic-Workflow-FRESH-worktrees\codex-apps-rg-source-refreeze
EXECUTION_BRANCH: codex-apps-rg-source-refreeze
ADG_POLICY: DEPRECATED_AND_FORBIDDEN
STANDALONE_TARGET: ABSENT
STANDALONE_WORKTREE_DEPENDENCY: FORBIDDEN
PARENT_STANDALONE_BLOCKER: W1D_SOURCE_REFREEZE_REQUIRED
BLOCKER: NONE
SR0A_STATUS: CONTRACT_AUTHORITY_APPROVED
SR0B_STATUS: CONTRACT_AUTHORITY_APPROVED
SR0H_STATUS: PASS
SR0_IMPLEMENTATION_AUTHORIZED: true
SR0A_IMPLEMENTATION_AUTHORIZED: true
SR0B_IMPLEMENTATION_AUTHORIZED: true
SOURCE_IMPLEMENTATION_AUTHORIZED: true
SOURCE_REFREEZE_COMPLETE: false
GRAPH_WORK_AUTHORIZED: false
ASSERTION_WORK_AUTHORIZED: false
EMBEDDING_WORK_AUTHORIZED: false
GRAPH_COMPLETION_REQUIRED_BEFORE_MIGRATION: true
GRAPH_SKILL_EMBEDDINGS_MANDATORY: true
EMBEDDING_UNIT: ATOMIC_SKILL_ASSERTION
NO_EMBEDDING_PROMOTION_IS_SUCCESS: false
RUNTIME_TRACE_CONTINUATION_AUTHORIZED: false
TARGET_CREATION_AUTHORIZED: false
PUSH_AUTHORIZED: false
PR_AUTHORIZED: false
MERGE_AUTHORIZED: false

---

## Context (SCQA)

- **Situation** — The source at `fc703982` has two conditionally reachable local import defects. The prior standalone W1/W1D evidence is immutable historical diagnosis.
- **Complication** — The ingestion cache-miss rebuild has no authoritative contract, and manifest integrity imports an absent active L4 configuration provider. C0.3 graph data and assertion embeddings must be completed before a new target baseline can exist.
- **Question** — How do we repair the source contracts without inventing authority, then sequence graph/assertion/embedding work for a future independent migration?
- **Answer** — SR0 may repair only independently characterized source contracts. Current evidence does not characterize either defect, so SR0 is blocked without a source implementation; SR1–SR6 remain explicitly gated and no target repository is created.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | SR0A, SR0B | Repair source ingestion and active-config contracts | ~18K | SR0 implementation authority is explicit | IN PROGRESS | Contract repairs, guarded proof, and local commits complete |
| W2 | SR1 | Lock canonical C0.3 graph authority/data | ~12K | Separate authorization required after SR0 | TODO | Graph readiness, exact parity, and zero unknown authority |
| W3 | SR2 | Lock atomic skill-assertion corpus | ~12K | SR1 graph lock is stable | TODO | Atomicity, corpus lock, and no unknown assertion authority |
| W4 | SR3 | Lock operational control plane | ~8K | Genuine producer evidence exists | TODO | Control-plane PASS with no UNKNOWN normalization |
| W5 | SR4 | Qualify pinned local BGE-M3 | ~16K | Frozen corpus, graph, qrels, and holdout | TODO | Qualified GO without authority/path regression |
| W6 | SR5 | Build immutable assertion-vector projection | ~14K | SR4 qualification is GO | TODO | Exact assertion/vector parity and zero authority bypass |
| W7 | SR6 | Certify source product and refreeze | ~18K | SR0–SR5 complete | TODO | Serial 11/11 source certification and SOURCE_REFREEZE_COMPLETE |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| SR0A | Ingestion loader contract evidence and repair | IN PROGRESS -- implementation authorized |
| SR0B | Immutable active-config snapshot provider | IN PROGRESS -- implementation authorized |
| SR1 | C0.3 graph authority/data lock | TODO — separate authorization |
| SR2 | Atomic skill-assertion corpus lock | TODO — separate authorization |
| SR3 | Operational control-plane lock | TODO — separate authorization |
| SR4 | BGE-M3 qualification | TODO — separate authorization |
| SR5 | Immutable embedding projection | TODO — separate authorization |
| SR6 | Source certification and final refreeze | TODO — separate authorization |

---

## Out Of Scope

- Creating `C:\Git\apps_rg`, restarting standalone W1, or running its remaining 16 scenarios.
- Any ADG use, dependency, build, test, CI, or target runtime surface.
- SR1 graph-data edits, assertion-corpus edits, embedding generation, production pointer publication, push, PR creation, or merge.
- Rewriting or deleting W1/W1D evidence, including the 71 third-party-root and 213 asset-candidate diagnostics.

---

## Wave 1 — SR0 Source Contract Repair

WAVE_ID: SR0H_SOURCE_CONTRACT_AUTHORITY_DECISION
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: DECISION_DRAFTING_ONLY
CHECKPOINT: SR0H

**Authorization**: SR0 local implementation is authorized only for the two approved source contracts, their narrow compatibility and consumer seams, directly relevant tests, plan/receipt updates, and local commits on this branch. Graph, assertion, embedding, target, push, PR, merge, and source-refreeze work remain prohibited.

**Current evidence**: `artifacts/apps_rg_source_refreeze/sr0/contract-authority-assessment-20260719/sr0_contract_authority_assessment.json` remains `CONTRACT_AUTHORITY_ABSENT`, and its tests remain `DIAGNOSTIC_EVIDENCE`. The Architecture Owner has approved option A for both newly approved architecture contracts in the SR0H ADRs and receipt. Implementation must stop at any named SR0 authority, scope, boundary, side-effect, or integration blocker.

**Phases**:
- **SR0A** — Establish and repair the canonical ingestion loader/cache contract | PHASE_STATUS: IN PROGRESS | PHASE_COMPLETE: NO | implementation authorized
- **SR0B** — Establish and repair the immutable active-configuration snapshot provider | PHASE_STATUS: IN PROGRESS | PHASE_COMPLETE: NO | implementation authorized

**Acceptance**:
- `SR0A_INGESTION_LOADER_CONTRACT_PASS`
- `SR0B_ACTIVE_CONFIG_PROVIDER_PASS`
- `SOURCE_PRODUCT_IMPORT_SMOKE_PASS`
- `DETERMINISTIC_MANIFEST_INTEGRITY_PASS`
- `ZERO_UNAUTHORIZED_SOURCE_WRITES`
- `ZERO_ADG_DEPENDENCY`
- `SR0_SOURCE_DEFECTS_REPAIRED_PASS`

**SR0H approval gate**: `SR0A_CONTRACT_AUTHORITY_APPROVED` and `SR0B_CONTRACT_AUTHORITY_APPROVED` are bound by the Architecture Owner decision; `SR0H_SOURCE_CONTRACT_AUTHORITY_PASS` is recorded. SR0 implementation now has separate local authority and must stop before push, PR, merge, refreeze, graph, assertion, embedding, or target work.

**Supersession record**: This plan supersedes only the conditional embedding-policy decision in `apps-rg-c03-graph-health-embedding-closure-b8d4f1`; it preserves the completed C0.3 graph-runtime hardening baseline. Mandatory future policy remains one vector per eligible atomic skill assertion, and no embedding promotion is not success.

### SR0A — Ingestion Loader Contract

**Read-first evidence**: enumerate all callers, schemas/configuration, current cache-hit behavior, fixtures/artifacts, payload-shape tests, and ambiguities. Do not implement merely to make the absent import resolve.

**Required contract**: canonical producer and input schema/version; input/config/output digests; cache key; validated hit/miss/stale/malformed/incompatible-version behavior; deterministic authorized rebuild; atomic publication; concurrent reader/writer behavior; durable-write authority; fail-closed statuses; and receipts.

**Non-negotiable controls**: read-only cache reads do not mutate data; no silent empty/partial result; unauthorized rebuild returns structured non-success without writing; no network/provider/graph-data fabrication; no repository-root discovery in the public contract.

**Required tests**: valid hit; authorized miss rebuild; unauthorized miss; stale/malformed/wrong-schema/wrong-config cache; changed input during rebuild; concurrent rebuild; failed atomic publication; unauthorized durable write; and zero source mutation for read-only invocation.

**Stop condition**: if authoritative evidence does not determine cache-miss/rebuild behavior, emit `SR0A_CONTRACT_AUTHORITY_REQUIRED` and do not invent it.

### SR0B — Active-Config Snapshot Provider

**Required provider contract**: immutable configuration identity/schema/canonical bytes/digest, applicable policy/provider/model/section-registry/graph-policy digests, provenance, load boundary/freshness state, and immutable snapshot receipt.

**Non-negotiable controls**: one snapshot per manifest validation; fail closed for missing/malformed/unsupported/stale configuration; invalidate changes during manifest construction; environment only selects declared profiles; no post-snapshot env override, mutable-global fallback, or durable write; replay has sufficient provenance.

**Required tests**: valid snapshot; missing/malformed/unsupported/stale configuration; profile mismatch; source changed during load; configuration changed after manifest start; digest mismatch; nondeterministic serialization; mutable-global rejection; and replay using the same snapshot.

---

## Wave 2 — SR1 C0.3 Graph Authority And Data Lock

WAVE_ID: SR1_C03_GRAPH_AUTHORITY_LOCK
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: SR1

Every canonical skill/required graph object must resolve exact facts, sources, nodes, taxonomy, lifecycle, visibility, section eligibility, external-claim policy, typed edges/paths, and retrieval eligibility. Canonical JSON remains authority; exact SQLite is a read-only derived projection. Required markers: `C03_SOURCE_AUTHORITY_LOCK_PASS`, `C03_GRAPH_DATA_READINESS_PASS`, `C03_EXACT_GRAPH_PARITY_PASS`, and `ZERO_UNKNOWN_GRAPH_AUTHORITY`.

---

## Wave 3 — SR2 Atomic Skill-Assertion Corpus

WAVE_ID: SR2_C03_ASSERTION_CORPUS_LOCK
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: SR2

The vector identity is `assertion_id`, while `skill_id` is grouping identity. A compound skill splits only through reviewed canonical source data. Semantic cards contain deterministic retrieval semantics only; authority envelopes remain outside similarity text and both bind the assertion-document digest. Required markers: `C03_ASSERTION_ATOMICITY_PASS`, `C03_ASSERTION_CORPUS_LOCK_PASS`, `ZERO_COMPOUND_ACTIVE_ASSERTIONS`, and `ZERO_UNKNOWN_ASSERTION_AUTHORITY`.

---

## Wave 4 — SR3 Operational Control Plane Lock

WAVE_ID: SR3_C03_CONTROL_PLANE_LOCK
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: SR3

Bind operational metrics to real producer evidence and fail closed on UNKNOWN. Production vector publication remains prohibited until SR1–SR3 pass, including `C03_GRAPH_CONTROL_PLANE_PASS`.

---

## Wave 5 — SR4 Local BGE-M3 Qualification

WAVE_ID: SR4_C03_EMBEDDING_QUALIFICATION
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: SR4

Use only a pinned, local, offline BGE-M3 artifact: 1024 dimensions, float32, normalized vectors, frozen corpus/graph/policy/query/qrel/holdout evidence, and unchanged thresholds. Compare exact/sparse, fact-vector+exact, dense+rehydration, and hybrid+rehydration. The only receipt decision is `QUALIFIED_GO` or `NO_EMBEDDING_PROMOTION`; only the former permits SR5 and emits `GRAPH_EMBEDDINGS_QUALIFIED`.

---

## Wave 6 — SR5 Immutable Assertion-Vector Projection

WAVE_ID: SR5_C03_ASSERTION_EMBEDDING_PROJECTION
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED_AFTER_GRAPH_EMBEDDINGS_QUALIFIED
CHECKPOINT: SR5

Build a distinct immutable `graph_skill_embeddings.<generation-digest>.sqlite` with exactly one active vector per eligible assertion. Exact graph SQLite stays vector-free; runtime reads return only candidate IDs/scores then exact rehydration applies current authority, proof, allocation, and section allowlists. Required markers include `GRAPH_SKILL_EMBEDDING_PARITY_PASS`, `GRAPH_SKILL_EMBEDDING_PROJECTION_PASS`, `GRAPH_SKILL_EMBEDDING_RUNTIME_PASS`, `ZERO_STALE_OR_ORPHANED_VECTORS`, and `ZERO_AUTHORITY_BYPASSING_VECTORS`.

---

## Wave 7 — SR6 Source Certification And Refreeze

WAVE_ID: SR6_C03_SOURCE_PRODUCT_CERTIFICATION
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: SR6

Certify serial 11/11 source lanes with one pinned graph, assertion corpus, embedding generation, model, allocation, and section allowlists. Require exact rehydration, candidate-fact proof, one root X3, UWG-only durable writes, current-run closure, and post-run L6. The only final source marker is `SOURCE_REFREEZE_COMPLETE`; only then may a new standalone analysis worktree restart W1 from first freeze checks.

---

## Gap Register

**GAP-SR0A: ingestion cache rebuild contract is absent**
- The frozen import points to a missing source module and payload/cache authority is not yet evidenced.
- Impact: source local-retrieval initialization cannot be repaired safely until evidence resolves the ambiguity.

**GAP-SR0B: active configuration snapshot provider is absent**
- Manifest integrity names required hash fields but no L4 canonical active-config source exists.
- Impact: a replacement could invent deterministic gate semantics unless independent configuration evidence is found.

**GAP-SR1+: graph/assertion/embedding program is mandatory but unauthorized**
- No graph-data, assertion, embedding, or pointer mutation occurs during SR0.
- Impact: standalone migration stays blocked even after SR0 local repair.

---

## Definition of Done

DoD-1: SR0A is repaired only from an independently characterized ingestion contract.
- Evidence: focused deterministic cache/receipt tests and `SR0A_INGESTION_LOADER_CONTRACT_PASS`.
- Status: TODO

DoD-2: SR0B supplies an immutable, replayable active-config snapshot with fail-closed validation.
- Evidence: focused snapshot/manifest tests and `SR0B_ACTIVE_CONFIG_PROVIDER_PASS`.
- Status: TODO

DoD-3: Source import and manifest integrity behavior pass without network, provider execution, or unauthorized durable writes.
- Evidence: bounded source smoke/probes with `SOURCE_PRODUCT_IMPORT_SMOKE_PASS`, `DETERMINISTIC_MANIFEST_INTEGRITY_PASS`, and `ZERO_UNAUTHORIZED_SOURCE_WRITES`.
- Status: TODO

DoD-4: SR0 contains no ADG dependency and makes no graph-data, assertion, embedding, pointer, target, or standalone-runtime change.
- Evidence: scoped diff and non-ADG static dependency checks.
- Status: TODO

DoD-5: SR0 is isolated in independently reviewable local commits, with no push, PR, or merge.
- Evidence: branch history and worktree status on `codex-apps-rg-source-refreeze`.
- Status: TODO

DoD-6: All W1/W1D evidence is preserved as immutable historical diagnostics and no count is reused as a post-refreeze result.
- Evidence: standalone plan state and W1D packet preservation check.
- Status: TODO

---

## Supersedes

_None — net-new source-refreeze program; it does not supersede the blocked standalone migration plan._

---

## Marker Quick Reference

```
SR0A_CONTRACT_AUTHORITY_REQUIRED
SR0A_INGESTION_LOADER_CONTRACT_PASS
SR0B_ACTIVE_CONFIG_PROVIDER_PASS
SOURCE_PRODUCT_IMPORT_SMOKE_PASS
DETERMINISTIC_MANIFEST_INTEGRITY_PASS
ZERO_UNAUTHORIZED_SOURCE_WRITES
ZERO_ADG_DEPENDENCY
SR0_SOURCE_DEFECTS_REPAIRED_PASS
SOURCE_REFREEZE_COMPLETE
```
