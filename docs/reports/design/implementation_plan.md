# Implementation Plan
**Phase**: Design Only — No code changes permitted  
**Date**: 2026-04-09  
**Note**: This plan is a design artifact. All HITL-gated batches require explicit human sign-off before coding begins.

---

## Wave Structure

| Wave | Batch IDs | Focus | Risk Level | HITL Before Coding |
|---|---|---|---|---|
| Wave 1 | B01, B02, B03 | P0-CRITICAL gaps: ingress envelope, exit gate, HITL re-clearance | HIGH | YES (B03 is HITL-gated) |
| Wave 2 | B04, B05, B06, B07 | P1-HIGH foundational contracts: L1 plan contract, C0 evidence contract, heal loop snapshot binding, proof of ledger | MEDIUM | No |
| Wave 3 | B08, B09, B10 | P1-HIGH infrastructure: verify spine + L6EvidenceBundle, ACL pre-routing gate placement, Freeze propagation map | MEDIUM | No |
| Wave 4 | B11, B12 | P1-HIGH capability gating: Commandant's Gauntlet promotion, C7 capability chokepoint | HIGH | YES (B11 is HITL-gated) |
| Wave 5 | B13, B14, B15 | P2-MEDIUM: ingestion lifecycle sync, index eval feedback loop, runtime handoff readiness | LOW | No |

---

## Batch B01 — Ingress Envelope Check

| Field | Value |
|---|---|
| **batch_id** | B01 |
| **objective** | Create a unified E1–E6 ingress envelope check as the single mandatory pre-pipeline gate |
| **req_ids** | REQ-001, REQ-002 |
| **gap_ids** | GAP-001 |
| **exact_files_likely_to_change** | `agentic_core/L5_safety/enforcement/ingress_envelope_check.py` (NEW); `agentic_core/gateway/api_gateway_integration.py` (route rate-limit call to ingress gate); `agentic_core/L5_safety/enforcement/__init__.py` (register new module) |
| **why_this_batch_exists** | No single ingress gate enforces the complete E1–E6 contract. Requests may enter the pipeline without auth, quota, or trace_root stamping. |
| **blast_radius** | L5_safety/enforcement (new module), gateway (routing change), downstream L1 input (must accept stamped request) |
| **risk_level** | MEDIUM — new module does not touch write path; risk is integration with gateway |
| **HITL_required_before_coding** | No |
| **proposed_tests** | `tests/unit/agentic_core/L5_safety/enforcement/test_ingress_envelope_check.py`: valid request passes all six checks; malformed schema → rejected with reason_code; auth failure → rejected; rate-limit exceeded → rejected; output contains request_id, session_id, trace_root, caller_scope_baseline; replay of same request_id → deduplicate |
| **acceptance_criteria** | All E1–E6 checks run before any L1 invocation; output type is typed `StampedRequest` with six required fields; every rejection emits `RejectionSlip(reason_code, request_id, trace_root)` |

---

## Batch B02 — Exit Control Gate

| Field | Value |
|---|---|
| **batch_id** | B02 |
| **objective** | Create the four-dimensional X1A–X1D exit evaluation gate with explicit ExitDisposition enum |
| **req_ids** | REQ-012 |
| **gap_ids** | GAP-004 |
| **exact_files_likely_to_change** | `agentic_core/L5_safety/enforcement/exit_control_gate.py` (NEW); `agentic_core/L5_safety/enforcement/policy_enforcement_point.py` (wire to gate); `agentic_core/L6_observability/enforcement/outcome_logger.py` (receive gate disposition) |
| **why_this_batch_exists** | No standalone exit gate module enforcing X1A–X1D evaluation with explicit dispositions exists. Unsafe L2 artifacts may reach response path without formal gate decision. |
| **blast_radius** | L5_safety/enforcement, response path wiring, UWG trigger, HITL trigger |
| **risk_level** | HIGH — touches the response path; incorrect implementation may block all responses or allow unsafe ones |
| **HITL_required_before_coding** | YES — HITL-003 must be resolved first (see hitl_decision_log.md) |
| **proposed_tests** | `tests/unit/agentic_core/L5_safety/enforcement/test_exit_control_gate.py`: secrets in output → DENY_RETURN; policy fail → DENY_RETURN; grounded + safe → ALLOW_RESPONSE; commit payload present → COMMIT_TO_UWG; low confidence → ESCALATE_TO_HITL; unknown/error disposition → DENY_RETURN (fail-closed); no silent fallback path reachable |
| **acceptance_criteria** | `ExitDisposition` enum has exactly four values; every code path through the gate produces a non-null explicit disposition; no catch-all silent fallback; gate output wired to outcome_logger and BUS_D/E |

---

## Batch B03 — HITL Re-Clearance Sequence

| Field | Value |
|---|---|
| **batch_id** | B03 |
| **objective** | Implement or confirm the full exit-control HITL sequence: freeze→materialize→review→re-clear, treating human input as untrusted DATA |
| **req_ids** | REQ-013 |
| **gap_ids** | GAP-005 |
| **exact_files_likely_to_change** | Dependent on HITL-004 decision: either `agentic_core/L5_safety/enforcement/exit_control_hitl.py` (NEW, separate from healing HITL) or extension of existing `hitl_gate.py` and `re_clear_loop_enforcer.py` |
| **why_this_batch_exists** | The exit-control HITL path (H1–H5 with authority_state=FROZEN) may not be covered by the healing HITL gate. Human-modified output bypassing L5 re-clearance is a P0 security concern. |
| **blast_radius** | L5_safety/enforcement, exit gate, UWG commit path, re-clearance loop — touches write-path-adjacent controls |
| **risk_level** | HIGH — directly adjacent to write path and HITL escalation; any error here bypasses human oversight |
| **HITL_required_before_coding** | YES — HITL-004 must be resolved first |
| **proposed_tests** | MODIFY_DIFF without re-clear gate → blocked; APPROVE bypassing L5 confirmation → blocked; authority_state FROZEN during review (no concurrent mutations); bounded packet contains only the materialized data (no live state reference); human input to re-clear treated as untrusted input to L5 policy validator |
| **acceptance_criteria** | H1–H5 sequence enforced as code contract; authority_state=FROZEN during review is a typed invariant; re-clearance result is the ONLY path to ALLOW/COMMIT from HITL |

---

## Batch B04 — L1 Plan Contract Type

| Field | Value |
|---|---|
| **batch_id** | B04 |
| **objective** | Define and enforce `L1PlanContract` as the mandatory typed output of L1 reasoning |
| **req_ids** | REQ-003 |
| **gap_ids** | GAP-002 |
| **exact_files_likely_to_change** | `agentic_core/L1_cognition/types/plan_contract_types.py` (NEW); `agentic_core/L1_cognition/enforcement/reasoning_chokepoint.py` (enforce output type); `agentic_core/L0_routing/reasoning/agentic_router.py` (validate L1PlanContract input) |
| **why_this_batch_exists** | Without a formal typed output contract, L0 cannot deterministically consume L1 output; grounding_required flag may be absent, silently skipping C0 retrieval. |
| **blast_radius** | L1 types, L1 chokepoint, L0 routing input parser |
| **risk_level** | MEDIUM — type-only change with enforcement; should not change runtime behavior if existing output already provides these fields |
| **HITL_required_before_coding** | No |
| **proposed_tests** | L1 output validated as `L1PlanContract`; missing any field → exception at chokepoint; grounding_required=False bypasses C0; grounding_required=True triggers C0 |
| **acceptance_criteria** | `L1PlanContract` is a frozen dataclass with all seven fields mandatory; `reasoning_chokepoint.py` raises `PlanContractViolation` if output fails validation |

---

## Batch B05 — C0 Evidence Contract Type

| Field | Value |
|---|---|
| **batch_id** | B05 |
| **objective** | Define `C0EvidenceContract` as the mandatory typed output of the retrieval pipeline, wiring abstain_hint to prompt assembler |
| **req_ids** | REQ-007, REQ-008 |
| **gap_ids** | GAP-007, GAP-003 (partial) |
| **exact_files_likely_to_change** | `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` (NEW); `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` (enforce output type); `agentic_core/prompt_governance/core/prompt_assembler.py` (consume abstain_hint; add HMAC; enforce C0-before-U0 ordering) |
| **why_this_batch_exists** | Without typed C0 contract, prompt assembler cannot make well-formed ABSTAIN decisions or verify evidence coverage. |
| **blast_radius** | L3_orchestration types, hybrid search engine output, prompt assembler input, token budget |
| **risk_level** | MEDIUM |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Coverage_score below threshold → abstain_hint=True; abstain_hint=True in C0EvidenceContract → prompt assembler emits ABSTAIN disposition; cited_spans present in all non-ABSTAIN responses; HMAC of PromptEnvelope verifiable after replay |
| **acceptance_criteria** | `C0EvidenceContract` is a frozen dataclass with all six required fields; hybrid search engine raises `C0ContractViolation` if output incomplete; prompt assembler validates HMAC on every envelope produced |

---

## Batch B06 — Heal Loop Same-Snapshot Binding

| Field | Value |
|---|---|
| **batch_id** | B06 |
| **objective** | Enforce that the heal loop reads the same policy_hash/blueprint_hash snapshot as the originating execution; add parent_packet_id binding |
| **req_ids** | REQ-010 |
| **gap_ids** | GAP-006 |
| **exact_files_likely_to_change** | `agentic_core/interfaces/IHealerProtocol.py` (add policy_hash, blueprint_hash, parent_packet_id to HealRequest); `agentic_core/L5_safety/enforcement/HealingStrategy.py` (add assertion: heal_context.policy_hash == originating_context.policy_hash) |
| **why_this_batch_exists** | Heal loop upgrading to a newer policy mid-run breaks determinism and makes the repair non-replayable. |
| **blast_radius** | IHealerProtocol, HealingStrategy, heal request types |
| **risk_level** | LOW-MEDIUM — additive to existing interface; existing tests should remain valid if they already bind policy_hash |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Heal request with mismatched policy_hash → SnapshotMismatchError; parent_packet_id propagated through repair chain; same-snapshot validation fires before any repair action |
| **acceptance_criteria** | `HealRequest` type has `policy_hash`, `blueprint_hash`, `parent_packet_id` as mandatory fields; `HealingStrategy` raises `SnapshotMismatchError` if snapshots diverge |

---

## Batch B07 — Proof of Ledger Artifact

| Field | Value |
|---|---|
| **batch_id** | B07 |
| **objective** | Create the formal five-field Proof of Ledger sealed artifact, wired to UWG post-commit |
| **req_ids** | REQ-024 |
| **gap_ids** | GAP-013 |
| **exact_files_likely_to_change** | `agentic_core/L4_state/enforcement/proof_of_ledger.py` (NEW); `agentic_core/L2_execution/enforcement/UniversalWriteGateway.py` (call proof_of_ledger after durable commit) |
| **why_this_batch_exists** | External audit requires reconstructable proof; five-field artifact is the compliance evidence. |
| **blast_radius** | L4_state/enforcement (new module), UWG post-commit sequence |
| **risk_level** | LOW — additive to UWG post-commit; does not change commit semantics |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Every UWG commit produces a `ProofOfLedger` artifact; knowledge_state_digest changes after state mutation; proof is verifiable from hash chain alone (no live state needed) |
| **acceptance_criteria** | `ProofOfLedger` is a frozen dataclass with five required fields; UWG raises `LedgerProofMissing` if post-commit proof is not produced |

---

## Batch B08 — L6 Verify Spine + L6EvidenceBundle

| Field | Value |
|---|---|
| **batch_id** | B08 |
| **objective** | Create `verify_spine.py` orchestrating four-check sequence; formalize `L6EvidenceBundle` type; wire BUS_D/E to exit gate |
| **req_ids** | REQ-018 |
| **gap_ids** | GAP-008 |
| **exact_files_likely_to_change** | `agentic_core/L6_observability/enforcement/verify_spine.py` (NEW); `agentic_core/L6_observability/types/l6_evidence_bundle_types.py` (NEW); `agentic_core/L5_safety/enforcement/exit_control_gate.py` (B02 dependency: receive BUS_D/E signals) |
| **why_this_batch_exists** | Observability signals are scattered; no unified spine delivers live control signals to exit gate. |
| **blast_radius** | L6_observability/enforcement, L6_observability/types, exit gate wiring (depends on B02) |
| **risk_level** | MEDIUM — depends on B02 (exit gate) for BUS_D/E wiring |
| **HITL_required_before_coding** | No (but depends on B02 HITL-003 resolution) |
| **proposed_tests** | Drift detected → BUS_D signal emitted and received at exit gate; time audit failure → BUS_E escalate signal; L6EvidenceBundle has all five fields populated per run; determinism_status reflects replay guard result |
| **acceptance_criteria** | `VerifySpine` runs all four checks in order; emits typed `BUS_D`, `BUS_E`, `BUS_T` signals; `L6EvidenceBundle` is frozen dataclass with five required fields |

---

## Batch B09 — ACL Pre-Routing Gate Placement

| Field | Value |
|---|---|
| **batch_id** | B09 |
| **objective** | Confirm and enforce that `PreRetrievalGate` fires at L0 routing boundary before cache lookup, not only at vector search |
| **req_ids** | REQ-005, REQ-023 |
| **gap_ids** | GAP-010 |
| **exact_files_likely_to_change** | `agentic_core/L0_routing/enforcement/` (ADD call to PreRetrievalGate before R1A/R1B cache check); or `agentic_core/knowledge/gates/preretrieval_gate.py` (confirm call order documentation) |
| **why_this_batch_exists** | Cache hits (R1B semantic cache) must not bypass ACL; cross-tenant contamination via cache is a P0 security risk. |
| **blast_radius** | L0_routing/enforcement, semantic cache path (R1B) |
| **risk_level** | MEDIUM — touches routing hot path |
| **HITL_required_before_coding** | No |
| **proposed_tests** | R1B semantic cache hit with cross-tenant item → blocked by pre-routing gate; ACL deny fires before cache lookup (not after); expired-scope request denied before cache is consulted |
| **acceptance_criteria** | `PreRetrievalGate.decide()` is called before R1A/R1B cache access in L0 routing; any DENY result aborts routing before cache check |

---

## Batch B10 — Determinism Surface Map + Freeze Chain Audit

| Field | Value |
|---|---|
| **batch_id** | B10 |
| **objective** | Document and enforce the Freeze signal propagation chain (L0→L3→L5→L2); audit all non-deterministic call sites for replay_guard_mixin coverage |
| **req_ids** | REQ-017 |
| **gap_ids** | GAP-011 |
| **exact_files_likely_to_change** | `agentic_core/adg/runtime/determinism_control.py` (add DETERMINISM_SURFACE_MAP constant); `ops_scripts/ci/` (add static enforcement gate for unguarded tool calls) |
| **why_this_batch_exists** | Without a confirmed Freeze chain, some execution paths may produce non-replayable output with a passing determinism_digest that does not reflect real non-determinism. |
| **blast_radius** | L0/L3/L5/L2 (audit only — no runtime logic change); ops_scripts/ci (new gate) |
| **risk_level** | LOW — audit + documentation + CI gate; no runtime behavior change |
| **HITL_required_before_coding** | No |
| **proposed_tests** | CI gate blocks any tool call not wrapped in replay_guard_mixin; DETERMINISM_SURFACE_MAP enumerated and verified in test; wall-clock call outside replay_guard → test fails |
| **acceptance_criteria** | `DETERMINISM_SURFACE_MAP` documents all four non-deterministic surfaces; CI gate present and enforced; no unguarded tool call sites in production code |

---

## Batch B11 — Commandant's Gauntlet

| Field | Value |
|---|---|
| **batch_id** | B11 |
| **objective** | Implement the Commandant's Gauntlet as a gated promotion pipeline: shadow replay + regression + SME sign-off + sovereign approve/veto before Master Ledger Commit |
| **req_ids** | REQ-020 |
| **gap_ids** | GAP-009 |
| **exact_files_likely_to_change** | `agentic_core/L6_observability/enforcement/commandant_gauntlet.py` (NEW); `agentic_core/L4_state/enforcement/promotion_authority.py` (wire to gauntlet gate); `agentic_core/L2_execution/enforcement/UniversalWriteGateway.py` (accept only gauntlet-approved promotion_token) |
| **why_this_batch_exists** | Untested rule changes promoted to production rubrics without SME review or shadow replay is a learning integrity failure. |
| **blast_radius** | L6_observability/enforcement, L4_state/enforcement, UWG write path (promotion path) — TOUCHES WRITE PATH |
| **risk_level** | HIGH — touches UWG write path and learning promotion |
| **HITL_required_before_coding** | YES — HITL-005 must be resolved first |
| **proposed_tests** | Promotion without SME sign-off → blocked at gauntlet gate; shadow replay failure → promotion blocked; regression test failure → promotion blocked; only gauntlet-approved promotion_token accepted by UWG |
| **acceptance_criteria** | `CommandantGauntlet` enforces all four gates sequentially; promotion_token is only issued after all four pass; UWG rejects any promotion_token without gauntlet approval signature |

---

## Batch B12 — C7 Capability Chokepoint

| Field | Value |
|---|---|
| **batch_id** | B12 |
| **objective** | Confirm or create the C7 seven-step capability gating pipeline as an end-to-end enforced sequence covering all six access types |
| **req_ids** | REQ-016 |
| **gap_ids** | (scoped partial gap) |
| **exact_files_likely_to_change** | `agentic_core/L3_orchestration/utils/registry/capability_registry.py` (verify G1–G7 sequence); `agentic_core/L2_execution/enforcement/capability_chokepoint.py` (confirm or add G5 intercept + G7 record) |
| **why_this_batch_exists** | Memory and network access type classification beyond model/tool is unconfirmed; invocation record appended to replay envelope is unconfirmed. |
| **blast_radius** | L3_orchestration/utils/registry, L2_execution/enforcement/capability_chokepoint, replay envelope append |
| **risk_level** | MEDIUM |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Unregistered network access blocked; memory access without capability_token denied; invocation_record present in replay envelope post-execution; capability_token expiry enforced |
| **acceptance_criteria** | All six access types (read/tool/model/network/memory/write) routed through G1–G7 sequence; invocation_record appended to replay envelope for each successful access |

---

## Batch B13 — Ingestion Lifecycle Sync Confirmation

| Field | Value |
|---|---|
| **batch_id** | B13 |
| **objective** | Confirm dedupe + version compare + tombstone + lineage + reindex trigger pipeline in `knowledge/lifecycle/` |
| **req_ids** | REQ-026 |
| **gap_ids** | GAP-012 |
| **exact_files_likely_to_change** | `agentic_core/knowledge/lifecycle/` modules (read and potentially add `lifecycle_sync_enforcer.py` if missing) |
| **why_this_batch_exists** | Duplicate and stale chunks corrupt retrieval quality; lineage breakage causes parent-child hydration failure. |
| **blast_radius** | knowledge/lifecycle (minimal — offline only) |
| **risk_level** | LOW |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Duplicate doc suppressed (single chunk stored); stale version tombstoned before reindex; parent-child lineage preserved post-tombstone; reindex_trigger emitted on version change |
| **acceptance_criteria** | Lifecycle sync enforcer implements all five steps as an enforced sequence; tombstone emits a record verifiable in genealogy_registry |

---

## Batch B14 — Index Eval Feedback Loop

| Field | Value |
|---|---|
| **batch_id** | B14 |
| **objective** | Create `knowledge/lifecycle/index_eval_feedback.py` consuming retrieval metrics and emitting reindex_trigger signals |
| **req_ids** | REQ-019 |
| **gap_ids** | GAP-015 |
| **exact_files_likely_to_change** | `agentic_core/knowledge/lifecycle/index_eval_feedback.py` (NEW); `agentic_core/utils/workflow_engines/recall_at_k.py` (wire output to feedback) |
| **why_this_batch_exists** | Without feedback loop, retrieval quality degrades silently without triggering reindex or chunking tuning. |
| **blast_radius** | knowledge/lifecycle (new module), utils/workflow_engines (wiring) |
| **risk_level** | LOW |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Recall@K below threshold → reindex_trigger emitted; dense_sparse_balance_update emitted on NDCG drift; chunking_tuning_signal emitted on staleness flag |
| **acceptance_criteria** | `IndexEvalFeedback` consumes retrieval metrics and produces typed feedback signals; signals are consumed by lifecycle sync scheduler |

---

## Batch B15 — Runtime Handoff Readiness Check

| Field | Value |
|---|---|
| **batch_id** | B15 |
| **objective** | Create a five-surface pre-flight check that blocks inference until all storage surfaces are warm |
| **req_ids** | REQ-027 |
| **gap_ids** | GAP-016 |
| **exact_files_likely_to_change** | `agentic_core/knowledge/lifecycle/runtime_handoff_readiness_check.py` (NEW); startup sequence (integrate pre-flight) |
| **why_this_batch_exists** | Inference with incomplete retrieval surfaces silently degrades recall quality. |
| **blast_radius** | knowledge/lifecycle (new module), startup sequence |
| **risk_level** | LOW |
| **HITL_required_before_coding** | No |
| **proposed_tests** | Inference request blocked if BM25 surface not warm; inference request blocked if dense vector surface not warm; all five surfaces pass → inference unblocked |
| **acceptance_criteria** | `RuntimeHandoffReadinessCheck` checks all five surfaces; any surface absent → blocks inference with `SurfaceNotReadyError`; error specifies which surface is missing |

---

## Metadata Binding Audit (Pre-Batch B01)

| Field | Value |
|---|---|
| **batch_id** | B00 (prerequisite audit) |
| **objective** | Audit `ContentMetadata` type in `knowledge/ingestion/modality_types.py` for six required fields; make all six mandatory |
| **req_ids** | REQ-022 |
| **gap_ids** | GAP-014 |
| **risk_level** | MEDIUM (security — mandatory fields may break existing ingestion code that omits them) |
| **HITL_required_before_coding** | No |
| **exact_files_likely_to_change** | `agentic_core/knowledge/ingestion/modality_types.py`; `agentic_core/knowledge/ingestion/intake_clerk.py` (enforce mandatory binding) |
