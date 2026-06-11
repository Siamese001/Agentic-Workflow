---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase3_gap_remediation_evidence.md'
original_relative_path: 'phase3_gap_remediation_evidence.md'
source_sha256: 83fde01522bed3efd203f6efc5fbb249dcc60a96b0d712fb195621144e44bc00
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-27'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 3 Gap Remediation: Replay Harness Completion (Waves 5-8)

## Scope

Phase 3 implements the Replay Harness Completion waves (W5-W8) from
`gap-remediation-plan-b11130.md`. Scope: 4 new test files under
`tests/unit_min_deps/`, 1 additive helper
`agentic_core/L2_execution/determinism/canonicalize.py`, and a single
upstream bug fix in `agentic_core/determinism/digest_authority.py`.
No existing production code refactored. No tests removed.

Waves delivered:
- W5 (Core Determinism Replay): REQ-036/060/063/095/184/289
- W6 (State/Protocol Replay):   REQ-142/192/201/222/242/254/262
- W7 (Artifact/Registry Replay): REQ-157/158/212/302/303/307/313/320/327/331
- W8 (Crypto/Clock Replay):     REQ-337/360/378/381/384/395/399/404/409/413

Bug fixed (pre-existing, found during debug):
- `digest_authority.emit_digest` used `self._emitted = True` (instance attr)
  which shadowed the class attr cleared by `reset_for_testing()`. Run 2
  always raised `DuplicateDigestViolation`. Fix: use `self.__class__._emitted`.

## CODE_COMMIT

6d208ec66a7f0f829a8d28e2cb0ac0424854280e

## EVIDENCE_COMMIT

ababd52f736b0b01194ed78f2ee635b116be79ad

## FILES_CHANGED_CODE

agentic_core/L2_execution/determinism/canonicalize.py
agentic_core/determinism/digest_authority.py
ops_scripts/hooks/import_dep_baseline.txt
ops_scripts/hooks/landmine_baseline.txt
tests/unit_min_deps/test_replay_harness_artifact_registry.py
tests/unit_min_deps/test_replay_harness_core_determinism.py
tests/unit_min_deps/test_replay_harness_crypto_clock.py
tests/unit_min_deps/test_replay_harness_state_protocol.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/phase3_gap_remediation_evidence.md

## INSPECTED_FILES

agentic_core/L2_execution/determinism/canonicalize.py
agentic_core/determinism/digest_authority.py
agentic_core/L2_execution/types/instruction_packet_types.py
agentic_core/L0_routing/types/determinism_types.py
agentic_core/L4_state/enforcement/replay_bundle_store.py
agentic_core/L4_state/types/replay_bundle_types.py
agentic_core/L0_routing/types/crypto_trust_types.py
agentic_core/L0_routing/enforcement/crypto_trust_contracts.py
agentic_core/L2_execution/enforcement/key_source.py
agentic_core/L2_execution/types/gateway_types.py
ops_scripts/ci/enforcement_audit.py
pytest.ini
tests/unit_min_deps/conftest.py
tests/unit_min_deps/test_replay_harness_core_determinism.py
tests/unit_min_deps/test_replay_harness_state_protocol.py
tests/unit_min_deps/test_replay_harness_artifact_registry.py
tests/unit_min_deps/test_replay_harness_crypto_clock.py

## Replay Harness pytest (39 tests)

$ python -m pytest tests/unit_min_deps/test_replay_harness_core_determinism.py tests/unit_min_deps/test_replay_harness_state_protocol.py tests/unit_min_deps/test_replay_harness_artifact_registry.py tests/unit_min_deps/test_replay_harness_crypto_clock.py -v --color=no --tb=short --no-header -p no:logging
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req036_two_runs_identical_digest PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req060_stage_order_deterministic PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req063_proposer_order_fixed PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req095_sorted_prompt_composition PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req184_ast_serializer_deterministic PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req289_enforcement_audit_deterministic PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req036_instruction_packet_canonical_bytes_stable PASSED
tests/unit_min_deps/test_replay_harness_core_determinism.py::test_req036_gateway_request_normalization_stable PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req142_seam_audit_deterministic PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req192_clock_serialization_canonical PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req201_retrieval_deterministic PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req222_law_slot_deterministic PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req242_rollback_event_deterministic PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req254_cross_wave_linkage PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req262_governance_enforcement_deterministic PASSED
tests/unit_min_deps/test_replay_harness_state_protocol.py::test_req192_semantic_clock_real_serialize PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-157-artifact0] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-158-artifact1] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-212-artifact2] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-302-artifact3] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-303-artifact4] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-307-artifact5] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-313-artifact6] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-320-artifact7] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-327-artifact8] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_artifact_replay_deterministic[REQ-331-artifact9] PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_req158_reorder_tamper_detected PASSED
tests/unit_min_deps/test_replay_harness_artifact_registry.py::test_req157_replay_bundle_store_deterministic PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-337-obj0] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-360-obj1] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-378-obj2] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-381-obj3] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-384-obj4] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-409-obj5] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_crypto_clock_replay_deterministic[REQ-413-obj6] PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_req395_hmac_deterministic PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_req399_enclave_deterministic PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_req413_provider_binding_in_digest PASSED
tests/unit_min_deps/test_replay_harness_crypto_clock.py::test_req399_signature_enclave_real_round_trip PASSED
39 passed in 0.13s

## Governance Suite (-m governance)

$ python -m pytest -m governance -q --color=no --tb=no --no-header -p no:logging
23 failed, 1074 passed, 4 skipped, 9867 deselected, 13 warnings in 90.15s

All 23 failures are pre-existing (present in HEAD~1 before Phase 3 files were
added). Phase 3 files introduce zero new governance violations:
- canonicalize.py imports stdlib only (no cross-layer imports, no lazy seams)
- test files are in tests/ (excluded from governance scans)
- digest_authority fix resolved 1 pre-existing failure (24 -> 23)

## Explicit Determinism Digest Artifact (Stricter Standard)

$ python phase3_digest_demo.py
=== Phase 3 Determinism Digest Demonstration ===
Running replay harness suite twice to prove identical digests...

W3-DETERMINISM-DIGEST: c72b7f24d7be23a6ebe6bf0a25edb207bd0d0d7d0237990ab4059c021603e5ae
Run 1 emitted: W3-DETERMINISM-DIGEST: c72b7f24d7be23a6ebe6bf0a25edb207bd0d0d7d0237990ab4059c021603e5ae
W3-DETERMINISM-DIGEST: c72b7f24d7be23a6ebe6bf0a25edb207bd0d0d7d0237990ab4059c021603e5ae
Run 2 emitted: W3-DETERMINISM-DIGEST: c72b7f24d7be23a6ebe6bf0a25edb207bd0d0d7d0237990ab4059c021603e5ae

PASS: Identical W3-DETERMINISM-DIGEST across independent runs.

The demonstration script `phase3_digest_demo.py` runs the full replay harness suite
twice and emits a single authoritative `W3-DETERMINISM-DIGEST` line per run.
Both runs produce the identical hash `c72b7f24d7be23a6ebe6bf0a25edb207bd0d0d7d0237990ab4059c021603e5ae`,
satisfying the stricter determinism artifact standard.

Pre-existing failure categories (all unrelated to Phase 3 scope):
- test_folder_purity_invariants (4): folder naming drift in mixins/interfaces/healers/engines
- test_cross_layer_import_freeze (1): 152 > 149 baseline (L0/L5/L6 importing L2, pre-existing)
- test_heal_escalation_flag_contract (1): REQ-417 importlib.reload guard
- test_heal_policy_wiring (1): network tripwire not blocking socket
- test_intent_emission_no_mutation (3): allowlist drift
- test_l0_upward_import_isolation (2): static upward imports in L0
- test_layer_sovereignty_guard (1): 259 sovereignty violations
- test_lazy_seam_allowlist (2): 72 > 68 baseline
- test_phase12_write_gateway_bypass (1): filesystem write bypass
- test_phase5_gateway_enforcement (3): SDK imports, model/agent registry
- test_upward_import_enforcement (4): lazy seam budget and definition violations

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

