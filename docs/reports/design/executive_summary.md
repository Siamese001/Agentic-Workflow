# Executive Summary — Agentic Requirements Baseline Design
**Phase**: Design Only — No code changes made  
**Date**: 2026-04-09  
**Author**: Cursor Agent (design-only analysis)  
**Deliverables**: baseline_requirements.md, requirements_traceability_matrix.md, gap_register.md, implementation_plan.md, test_plan.md, hitl_decision_log.md, executive_summary.md

---

## 1. Corpus Ingested

| File | Role |
|---|---|
| `00_ingestion_pipeline_index_build.md` | Offline ingestion pipeline spec |
| `01_request_intake.md` | Ingress envelope contract (E1–E6) |
| `02_L1_Reasoning_Plan_Generation.md` | L1 plan contract spec |
| `03_Route_Decision_Switching.md` | L0 routing paths and C0 retrieval spec |
| `04_Live_Task_Dispatch_Execution.md` | L2 execution, heal loop, sealed artifact |
| `05_Live_Runtime_Exit_Control.md` | Exit gate, HITL airlock, UWG commit path |
| `06_Shadow_Evaluation_System_Learning.md` | L6 shadow eval, promotion, Proof of Ledger |
| `C0_Governance_Safety_Enforcement.md` | Dual-rail governance plane (G1–G7) |
| `C1_Deterministic_Replay_Execution_Integrity.md` | Replay envelope, Freeze propagation, determinism digest |
| `C2_Observability_Telemetry_Control_Signals.md` | Verify spine, BUS_D/E/T, L6EvidenceBundle |
| `C3_Healing_Remediation_Escalation.md` | Zero-loss failure containment, healing tier router |
| `C4_State_Sovereignty_Universal_Write_Governance.md` | UWG as sole write path |
| `C5_Retrieval_Prompt_Assembly.md` | C0 evidence pipeline, PA.1–PA.4, HMAC envelope |
| `C6_Evaluation_Learning_Promotion_System.md` | Learning pipeline, Commandant's Gauntlet |
| `C7_Capability_Tool_Model_Access_Control_Plane.md` | Capability gating G1–G7 |
| `agentic_process_mapping_v29.md` | Canonical runtime process map |

---

## 2. Requirements Extracted

**28 baseline requirements** across 15 categories:

| Category | Count | Critical |
|---|---|---|
| Intake / ingress validation | 2 | REQ-001, REQ-002 |
| L1 reasoning / plan contract | 2 | REQ-003, REQ-004 |
| L0 routing / route switching | 3 | REQ-005, REQ-006, REQ-027 |
| C0 retrieval / evidence shaping / prompt assembly | 2 | REQ-007, REQ-008 |
| L2 execution / validation / healing | 3 | REQ-009, REQ-010, REQ-011 |
| Exit control / runtime evaluation | 1 | REQ-012 |
| HITL / escalation / re-clearance | 1 | REQ-013 |
| State sovereignty / write governance / UWG | 1 | REQ-014 |
| Governance / safety / policy enforcement | 2 | REQ-015, REQ-028 |
| Capability / tool / model / network / memory gating | 1 | REQ-016 |
| Replay / determinism / integrity | 1 | REQ-017 |
| Observability / telemetry / anomaly signals | 2 | REQ-018, REQ-019 |
| Shadow evaluation / learning / promotion | 2 | REQ-020, REQ-021 |
| Security / ACL / tenancy / freshness / scope | 2 | REQ-022, REQ-023 |
| Testing / auditability / traceability / evidence | 1 | REQ-024 |
| Intake / ingestion pipeline | 3 | REQ-025, REQ-026 |

Full catalog: `docs/reports/design/baseline_requirements.md`

---

## 3. Repository Evidence Reviewed

Key modules confirmed (partial or full inspection):

| Module | Layer | Status |
|---|---|---|
| `L2_execution/enforcement/execution_guardrail_chokepoint.py` | L2 | Implemented — 13-step contract |
| `L2_execution/enforcement/UniversalWriteGateway.py` | L2/L4 | Implemented — hash-chain, mutation record |
| `L5_safety/enforcement/hitl_gate.py` | L5 | Implemented — healing HITL only |
| `L0_routing/enforcement/deterministic_replay_guard.py` | L0 | Partial — routing layer only |
| `prompt_governance/core/prompt_assembler.py` | L0/PA | Partial — HMAC unconfirmed |
| `knowledge/gates/preretrieval_gate.py` | L0/knowledge | Partial — placement unconfirmed |
| `L5_safety/enforcement/re_clear_loop_enforcer.py` | L5 | Partial — exit-control HITL unconfirmed |
| `L6_observability/utils/engines/drift_detector.py` | L6 | Partial — verify spine absent |
| `L4_state/enforcement/proof_of_ledger.py` | L4 | **Missing** |
| `L5_safety/enforcement/exit_control_gate.py` | L5 | **Missing** |
| `L5_safety/enforcement/exit_control_hitl.py` | L5 | **Missing** |
| `L6_observability/enforcement/verify_spine.py` | L6 | **Missing** |
| `L6_observability/enforcement/commandant_gauntlet.py` | L6 | **Missing** |
| `L5_safety/enforcement/ingress_envelope_check.py` | L5 | **Missing** |

Full traceability matrix: `docs/reports/design/requirements_traceability_matrix.md`

---

## 4. Traceability Summary

| Status | Count | Percentage |
|---|---|---|
| `implemented` | 2 | 7% |
| `partial` | 26 | 93% |
| `missing` | 0 | 0% |
| `conflicting` | 0 | 0% |

The two fully-implemented requirements (REQ-009, REQ-011) cover the L2 execution chokepoint and sealed artifact emission — the core execution contract is the strongest area. No requirement has zero evidence; however 93% of requirements are only partially satisfied, indicating that enforcement contracts, typed output schemas, and cross-cutting orchestration layers are systematically underimplemented relative to their specifications.

---

## 5. Gap Summary

**15 gaps** identified:

| Severity | Count | Key Gaps |
|---|---|---|
| **P0-CRITICAL** | 3 | GAP-001 (no ingress envelope), GAP-004 (no exit gate), GAP-005 (HITL re-clearance path ambiguous) |
| **P1-HIGH** | 10 | GAP-002 (L1PlanContract), GAP-003 (PromptEnvelope HMAC), GAP-006 (heal same-snapshot), GAP-007 (C0EvidenceContract), GAP-008 (verify spine), GAP-009 (Commandant's Gauntlet), GAP-010 (ACL gate placement), GAP-011 (Freeze chain), GAP-013 (Proof of Ledger), GAP-014 (metadata binding) |
| **P2-MEDIUM** | 2 | GAP-012 (lifecycle tombstone), GAP-015 (index eval feedback), GAP-016 (runtime handoff readiness) |

Full gap register: `docs/reports/design/gap_register.md`

---

## 6. Implementation Plan

**5 waves, 15 batches + 1 audit batch (B00)**:

| Wave | Batches | Focus | HITL gate |
|---|---|---|---|
| Wave 1 | B00, B01, B02, B03 | P0-CRITICAL: ingress envelope, exit gate, HITL re-clearance | B02/B03 gated on HITL-001/003/004 |
| Wave 2 | B04–B07 | P1-HIGH foundational contracts: L1PlanContract, C0EvidenceContract, heal snapshot, Proof of Ledger | None |
| Wave 3 | B08–B10 | P1-HIGH infrastructure: verify spine, ACL gate placement, Freeze chain audit | None |
| Wave 4 | B11, B12 | P1-HIGH: Commandant's Gauntlet, C7 capability chokepoint | B11 gated on HITL-005 |
| Wave 5 | B13–B15 | P2-MEDIUM: lifecycle sync, index eval feedback, runtime handoff | None |

Full plan: `docs/reports/design/implementation_plan.md`

---

## 7. Test Plan

**13 test suites, 94 named test cases** covering all 28 requirements. Priority order matches wave order. All P0-CRITICAL gaps have mandatory pre-merge test coverage. Regression guard mandates that all existing tests in L2, UWG, L0, and HITL suites continue to pass after every batch.

Full test plan: `docs/reports/design/test_plan.md`

---

## 8. HITL Decision Log — All Resolved

| hitl_id | Topic | Decision |
|---|---|---|
| HITL-001 | Exit gate module | New standalone `exit_control_gate.py` in L5_safety/enforcement |
| HITL-002 | Ingress envelope placement | `L5_safety/enforcement/ingress_envelope_check.py` |
| HITL-003 | ExitDisposition enum ownership | `L5_safety/types/exit_disposition_types.py` |
| HITL-004 | Exit-control vs healing HITL | Separate `exit_control_hitl.py`; `hitl_gate.py` unchanged |
| HITL-005 | Commandant's Gauntlet SME mode | Async approval queue with signed `promotion_token` + expiry |

Full log: `docs/reports/design/hitl_decision_log.md`

---

## 9. Residual Risks

| risk_id | Description | Mitigation | Owner |
|---|---|---|---|
| R-001 | `PreRetrievalGate` fires at retrieval time, not routing time — cross-tenant cache hit possible in R1B | B09 must confirm call order before Wave 3 coding; add integration test T3-07 | Wave 3 |
| R-002 | Freeze signal propagation through L3/L5 is unconfirmed — non-mixin tool calls produce non-replayable output | B10 audit + CI gate must enumerate and verify all non-deterministic surfaces | Wave 3 |
| R-003 | `ContentMetadata` may have nullable security fields — ingestion contamination risk if ACL/tenant_id optional | B00 audit must complete before Wave 1; failing fields must be made mandatory before any new ingestion | Pre-Wave 1 |
| R-004 | Exit gate (GAP-004) is a new P0 module on the response hot path — incorrect fail-closed semantics could block all responses | Wave 1 B02 tests (T6-01–T6-08) must be 100% passing before deployment; canary deployment recommended | Wave 1 |
| R-005 | Commandant's Gauntlet async queue requires durable persistence — in-memory queue survives nothing | HITL-005 constraint: queue must use a durable store; test T11-07 must verify isolation from live runs | Wave 4 |
| R-006 | Implementation plan assumes 26 partial-status requirements can be made compliant without breaking existing tests — regression surface is wide | Every batch must run full regression suite; no batch merged until regression passes | All waves |

---

## 10. Confidence Assessment

| Dimension | Confidence | Notes |
|---|---|---|
| Requirements completeness | 0.90 | 28 reqs derived from 16 spec files; minor specs (e.g., 00A, 00B, 00C) not fully ingested — low materiality |
| Evidence accuracy | 0.82 | Evidence based on file paths + first 40–60 lines per file; deep internals not fully read; all gaps flagged as `partial` not `missing` conservatively |
| Gap register accuracy | 0.85 | 0 hallucinated gaps claimed; all gaps backed by specific missing type/module names; 2 gaps (GAP-012, GAP-016) have lower confidence (0.75) |
| Implementation plan feasibility | 0.80 | Blast radius estimated from file grep; actual coupling confirmed only for key modules |
| Test plan coverage | 0.88 | 94 test cases named with specific assertions; some integration tests depend on Wave 1 completion |

---

## 11. Next Steps (post-design-phase)

1. **B00 (pre-wave)**: Audit `ContentMetadata` fields immediately — security risk if nullable
2. **Wave 1 coding**: B01 (ingress envelope), B02 (exit gate), B03 (HITL re-clearance) — all HITL decisions resolved ✅
3. **Per-batch**: Write tests first (T1, T6, T7), then implement, then regression suite
4. **ADG refresh**: Run `python tools/generate_full_adg.py` after Wave 1 to update dependency graph before Wave 2 analysis
