"""Tier 1 metadata generator.

Reads the Tier 1 selection (`docs/reference/contracts/tier1/TIER1_SELECTION.json`)
and emits four normalized metadata-surface files plus a schema validation
report under ``artifacts/runtime/requirements_proof/``.

This is metadata/linkage work only. It does NOT implement runtime behavior,
run tests, run proof harnesses, execute replay, or run OTEL exporters.
It does NOT claim proof, coverage, or readiness.

Status vocabulary used here:
  - LINKED_LITERAL / LINKED_CONCEPTUAL / PARTIAL_LINK / NO_LINK (linkage)
  - blocker codes per spec (NEEDS_*, NO_LINK)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier1" / "TIER1_SELECTION.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

OUT_FILES: Dict[str, str] = {
    "index": "tier1_requirements_index.generated.json",
    "coverage": "tier1_coverage_matrix.generated.json",
    "impl": "tier1_implementation_map.generated.json",
    "artifact": "tier1_artifact_linkage.generated.json",
}
OUT_VALIDATION_REPORT = "tier1_schema_validation_report.md"

# ---------------------------------------------------------------------------
# Stable expected_fail_reason mapping. Only populated when the requirement's
# failure mode is obvious from the REQ_ID + requirement text. If it is not
# obvious, the row keeps the NEEDS_EXPECTED_FAIL_REASON blocker rather than
# inventing an obscure code.
# ---------------------------------------------------------------------------
EXPECTED_FAIL_REASONS: Mapping[str, str] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": "DIRECT_L4_WRITE_BLOCKED",
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": "DIRECT_L4_WRITE_BLOCKED",
    "REQ-UWG-OBS-ANTI-BYPASS-001": "UWG_BYPASS_WRITE_BLOCKED",
    "REQ-GATE-OBS-ANTI-BYPASS-001": "RUNTIME_GATE_BYPASS_BLOCKED",
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": "L5_LIVE_RUNTIME_DISPOSITION_BLOCKED",
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": "PROMPT_BOUNDARY_VIOLATION_BLOCKED",
    "REQ-PA-AUTHORITY-REDTEAM-001": "PROMPT_BOUNDARY_VIOLATION_BLOCKED",
    "REQ-C0-OBS-ANTI-BYPASS-001": "C0_EVIDENCE_CONTRACT_BYPASS_BLOCKED",
    "REQ-L2-OBS-ANTI-BYPASS-001": "ANTI_BYPASS_CONTROL_MISSING",
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": "ARTIFACT_INTEGRITY_MISMATCH",
    "REQ-EXIT-X1G-X1I-REPLAY-001": "REPLAY_INTEGRITY_MISMATCH",
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": "REPLAY_INTEGRITY_MISMATCH",
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": "L6_CURRENT_RUN_MUTATION_BLOCKED",
    "REQ-EXIT-OBS-ANTI-BYPASS-001": "ANTI_BYPASS_CONTROL_MISSING",
    "REQ-L5-STATIC-GOV-DRIFT-001": "STATIC_GOVERNANCE_DRIFT_DETECTED",
}

# ---------------------------------------------------------------------------
# On-disk reference candidates. Every path MUST exist (validated at build
# time). Empty tuples → no reference for that REQ; the corresponding NEEDS_*
# blocker remains.
# ---------------------------------------------------------------------------
_TRACES = "artifacts/runtime/requirements_proof/traces"
_REPLAY = "artifacts/runtime/requirements_proof/replay"
_PROOF = "artifacts/runtime/requirements_proof"

# The anti_bypass scenario D artifacts and tests demonstrate UWG bypass
# detection, which is exactly what the three write_sovereignty Tier 1 rows
# are about. They are referenced (not invented).
_ANTI_BYPASS_ARTIFACTS: Tuple[str, ...] = (
    f"{_TRACES}/scenario_D_anti_bypass.json",
    f"{_PROOF}/anti_bypass_results.json",
)
_ANTI_BYPASS_REPLAY: Tuple[str, ...] = (
    f"{_REPLAY}/replay_D_anti_bypass_run_1.json",
    f"{_REPLAY}/replay_D_anti_bypass_run_2.json",
)
_ANTI_BYPASS_TESTS: Tuple[str, ...] = (
    "tests/runtime/test_uwg_write_sovereignty.py",
    "tests/runtime/test_anti_bypass_runtime_cheat_proof.py",
    "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
)
_ANTI_BYPASS_NEGATIVE_CONTROLS: Tuple[str, ...] = (f"{_PROOF}/anti_bypass_results.json",)

TEST_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_TESTS,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_TESTS,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_TESTS,
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        "tests/runtime_gates/test_runtime_gates_hardening.py",
        "tests/runtime_gates/test_runtime_gates_edge_cases.py",
        "tests/runtime/test_runtime_gates_g01_g29.py",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        "tests/agentic_core/L0_routing/enforcement/test_safety_enforcement_seam.py",
        "tests/unit/agentic_core/L0_routing/enforcement/test_safety_enforcement_seam_behavior.py",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        "tests/unit/agentic_core/L5_safety/v5/test_g2a_origin_trust.py",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        "tests/unit/agentic_core/L5_safety/reasoning/test_AdversarialRedTeamerAgent.py",
        "tests/unit/agentic_core/L5_safety/reasoning/test_RedTeamAgent.py",
        "tests/agentic_core/prompt_governance/security/test_assembly_injection_neutralizer.py",
        "tests/unit/agentic_core/prompt_governance/security/detectors/test_injection_detector.py",
        "tests/unit/agentic_core/L5_safety/enforcement/security/test_injection_regression_gate.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa4_validation.py",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        "tests/unit/agentic_core/L1_cognition/c0_context/test_c0_anti_bypass.py",
        "tests/runtime/test_c0_evidence_contract.py",
        "tests/agentic_core/L0_routing/c0_retrieval/test_evidence_contract.py",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        "tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py",
        "tests/unit/agentic_core/L2_execution/test_l2_sequencer_adapter.py",
        "tests/unit/agentic_core/L2_execution/test_l2_sequencer_contract.py",
        "tests/agentic_core/L2_execution/enforcement/test_preventative_sandbox.py",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa7_dispatch_states.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa7_signature.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa4_validation.py",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        "tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_x1_gates.py",
        "tests/agentic_core/L3_orchestration/exit_eval/test_factory_x1g.py",
        "tests/runtime_gates/00c_5/test_g21_g24_gates.py",
        "tests/unit/agentic_core/L5_safety/runtime_gates/test_g19_g24.py",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        "tests/l4/test_audit_ledger.py",
        "tests/e2e/data/test_uwg_determinism_e2e.py",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        "tests/unit/L6_observability/shadow_eval/test_06_7_gauntlet.py",
        "tests/runtime/test_l6_learning_firewall.py",
        "tests/agentic_core/L6_observability/utils/evaluation/test_promotion_gauntlet.py",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        "tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_anti_bypass.py",
        "tests/runtime/test_exit_x3_disposition_wireup.py",
        "tests/agentic_core/L5_safety/types/test_exit_disposition_types.py",
        "tests/runtime_gates/00c_6/test_g25_g29_gates.py",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        "tests/unit/agentic_core/L5_safety/v5/test_static_drift.py",
        "tests/unit/agentic_core/L5_safety/utils/test_structure_drift_writer.py",
        "tests/unit/agentic_core/L5_safety/v5/test_governance_plane.py",
    ),
}
_E2E = "artifacts/e2e/h3/scenarios"

ARTIFACT_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_ARTIFACTS,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_ARTIFACTS,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_ARTIFACTS,
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        f"{_E2E}/RC-UWG/rc_uwg_no_bypass_receipt.json",
        f"{_E2E}/GP-001/gp_001_no_bypass_receipt.json",
        f"{_PROOF}/anti_bypass_results.json",
        f"{_TRACES}/scenario_D_anti_bypass.json",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        f"{_E2E}/GP-001/gp_001_groundedness_receipt.json",
        f"{_E2E}/GP-001/gp_001_no_bypass_receipt.json",
        f"{_E2E}/GP-001/gp_001_exit_review_packet.json",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        f"{_E2E}/GP-001/gp_001_prompt_envelope.json",
        f"{_E2E}/RC-R3/rc_r3_prompt_envelope.json",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        f"{_E2E}/GP-001/gp_001_sealed_l2_artifact.json",
        f"{_E2E}/GP-001/gp_001_prompt_envelope.json",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        f"{_E2E}/RC-R3/rc_r3_final_evidence_contract.json",
        f"{_E2E}/RC-R3/rc_r3_groundedness_receipt.json",
        f"{_PROOF}/anti_bypass_results.json",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        f"{_E2E}/RC-R3/rc_r3_runtime_exhaust_bundle.json",
        f"{_E2E}/RC-R3/rc_r3_no_bypass_receipt.json",
        f"{_PROOF}/anti_bypass_results.json",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        f"{_E2E}/RC-R3/rc_r3_sealed_l2_artifact.json",
        f"{_E2E}/RC-HITL/rc_hitl_sealed_l2_artifact.json",
        f"{_E2E}/GP-001/gp_001_sealed_l2_artifact.json",
        f"{_E2E}/RC-R3/rc_r3_prompt_envelope.json",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        f"{_E2E}/RC-R3/rc_r3_replay_receipt.json",
        f"{_E2E}/RC-R3/rc_r3_exit_review_packet.json",
        f"{_E2E}/RC-R3/rc_r3_otel_trace.json",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        f"{_E2E}/RC-UWG/rc_uwg_replay_receipt.json",
        f"{_E2E}/RC-UWG/rc_uwg_uwg_commit_receipt.json",
        f"{_E2E}/RC-UWG/rc_uwg_uwg_receipt.json",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        f"{_E2E}/RC-R3/rc_r3_l6_exhaust_receipt.json",
        f"{_E2E}/GP-001/gp_001_l6_exhaust_receipt.json",
        f"{_E2E}/RC-UWG/rc_uwg_l6_exhaust_receipt.json",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        f"{_E2E}/RC-R3/rc_r3_x3_disposition.json",
        f"{_E2E}/RC-R3/rc_r3_disposition.json",
        f"{_E2E}/RC-R3/rc_r3_no_bypass_receipt.json",
        f"{_PROOF}/anti_bypass_results.json",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        f"{_TRACES}/scenario_I_static_governance_drift.json",
    ),
}
_DET1 = "artifacts/e2e/det1/scenarios"
_DET2 = "artifacts/e2e/det2/scenarios"

REPLAY_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_REPLAY,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_REPLAY,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_REPLAY,
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        f"{_REPLAY}/replay_F_gate_schema_unknown_not_pass_run_1.json",
        f"{_REPLAY}/replay_F_gate_schema_unknown_not_pass_run_2.json",
        f"{_REPLAY}/replay_G_gate_schema_na_requires_reason_run_1.json",
        f"{_REPLAY}/replay_G_gate_schema_na_requires_reason_run_2.json",
        f"{_REPLAY}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY}/replay_D_anti_bypass_run_2.json",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        f"{_DET1}/GP-001/gp_001_replay_receipt.json",
        f"{_DET2}/GP-001/gp_001_replay_receipt.json",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        f"{_DET1}/GP-001/gp_001_replay_receipt.json",
        f"{_DET2}/GP-001/gp_001_replay_receipt.json",
        f"{_DET1}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET2}/RC-R3/rc_r3_replay_receipt.json",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        f"{_DET1}/GP-001/gp_001_replay_receipt.json",
        f"{_DET2}/GP-001/gp_001_replay_receipt.json",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        f"{_REPLAY}/replay_C_weak_evidence_run_1.json",
        f"{_REPLAY}/replay_C_weak_evidence_run_2.json",
        f"{_REPLAY}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY}/replay_D_anti_bypass_run_2.json",
        f"{_DET1}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET2}/RC-R3/rc_r3_replay_receipt.json",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        f"{_REPLAY}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY}/replay_D_anti_bypass_run_2.json",
        f"{_DET1}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET2}/RC-R3/rc_r3_replay_receipt.json",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        f"{_DET1}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET2}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET1}/RC-HITL/rc_hitl_replay_receipt.json",
        f"{_DET2}/RC-HITL/rc_hitl_replay_receipt.json",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        f"{_REPLAY}/replay_comparison.json",
        f"{_REPLAY}/replay_A_grounded_read_run_1.json",
        f"{_REPLAY}/replay_A_grounded_read_run_2.json",
        f"{_DET1}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET2}/RC-R3/rc_r3_replay_receipt.json",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        f"{_REPLAY}/replay_E_authorized_commit_run_1.json",
        f"{_REPLAY}/replay_E_authorized_commit_run_2.json",
        f"{_DET1}/RC-UWG/rc_uwg_replay_receipt.json",
        f"{_DET2}/RC-UWG/rc_uwg_replay_receipt.json",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        f"{_REPLAY}/replay_H_l6_firewall_no_current_run_mutation_run_1.json",
        f"{_REPLAY}/replay_H_l6_firewall_no_current_run_mutation_run_2.json",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        f"{_REPLAY}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY}/replay_D_anti_bypass_run_2.json",
        f"{_DET1}/RC-R3/rc_r3_replay_receipt.json",
        f"{_DET2}/RC-R3/rc_r3_replay_receipt.json",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        f"{_REPLAY}/replay_I_static_governance_drift_run_1.json",
        f"{_REPLAY}/replay_I_static_governance_drift_run_2.json",
    ),
}
_AB_NEG_MOD = "agentic_core/runtime/prove_requirements/anti_bypass_negatives.py"
_AB_RES = f"{_PROOF}/anti_bypass_results.json"

NEGATIVE_CONTROL_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_NEGATIVE_CONTROLS,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_NEGATIVE_CONTROLS,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_NEGATIVE_CONTROLS,
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        _AB_NEG_MOD,
        _AB_RES,
        "tests/runtime/test_anti_bypass_runtime_cheat_proof.py",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        "tests/integration/agentic_core/test_authority_boundary.py",
        "tests/unit/agentic_core/L5_safety/enforcement/test_layer_sovereignty_enforcer.py",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        "tests/agentic_core/L0_routing/enforcement/test_boundary_contracts.py",
        "tests/unit/agentic_core/L5_safety/reasoning/test_BoundaryTestingAgent.py",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        "tests/unit/agentic_core/L5_safety/reasoning/test_AdversarialRedTeamerAgent.py",
        "tests/unit/agentic_core/L5_safety/reasoning/test_RedTeamAgent.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa0_boundary.py",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        _AB_NEG_MOD,
        _AB_RES,
        "tests/unit/agentic_core/L1_cognition/c0_context/test_c0_anti_bypass.py",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        _AB_NEG_MOD,
        _AB_RES,
        "agentic_core/L2_execution/enforcement/anti_bypass_guards.py",
        "tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa0_boundary.py",
        "tests/unit/agentic_core/L5_safety/reasoning/test_InterfaceBoundaryAgent.py",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        _AB_NEG_MOD,
        _AB_RES,
        "tests/runtime/test_anti_bypass_runtime_cheat_proof.py",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        _AB_RES,
        "tests/runtime/test_uwg_write_sovereignty.py",
        "tests/unit/apps_shared/proof/test_write_sovereignty.py",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        _AB_NEG_MOD,
        "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        _AB_NEG_MOD,
        _AB_RES,
        "tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_anti_bypass.py",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        "tests/unit/agentic_core/L5_safety/v5/test_static_drift.py",
        "tests/unit/agentic_core/L5_safety/utils/test_structure_drift_writer.py",
    ),
}

# Code, validator, and OTEL-span references. Every path is verified to exist
# on disk via _filter_existing(); paths that vanish later degrade gracefully
# rather than poisoning the metadata.
CODE_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": (
        "agentic_core/L2_execution/enforcement/durable_write_wrapper.py",
        "agentic_core/L4_state/uwg/durable_write_gateway.py",
    ),
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": (
        "agentic_core/L4_state/uwg/durable_write_gateway.py",
        "agentic_core/L6_observability/utils/evaluation/promotion_gauntlet.py",
        "agentic_core/L6_observability/shadow_eval/gauntlet.py",
    ),
    "REQ-UWG-OBS-ANTI-BYPASS-001": (
        "agentic_core/L4_state/uwg/durable_write_gateway.py",
        "agentic_core/L4_state/uwg/durable_write_consistency_gate.py",
        "agentic_core/runtime/prove_requirements/anti_bypass_negatives.py",
    ),
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        "agentic_core/L5_safety/runtime_gates/orchestrator.py",
        "agentic_core/L5_safety/runtime_gates/dispatch.py",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        "agentic_core/L0_routing/enforcement/safety_enforcement_seam.py",
        "agentic_core/L5_safety/runtime_gates/orchestrator.py",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        "agentic_core/L0_routing/intake/origin_labels.py",
        "agentic_core/L5_safety/v5/g2a_origin_trust.py",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        "agentic_core/prompt_governance/prompt_assembly/assembly_injection_neutralizer.py",
        "agentic_core/prompt_governance/prompt_assembly/injection_detector.py",
        "agentic_core/L5_safety/reasoning/RedTeamAgent.py",
        "agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        "agentic_core/L0_routing/c0_retrieval/evidence_contract.py",
        "agentic_core/knowledge/retrieval/evidence_contract_builder.py",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        "agentic_core/L2_execution/orchestration/l2_sequencer_adapter.py",
        "agentic_core/L2_execution/types/l2_sequencer_contract.py",
        "agentic_core/L2_execution/enforcement/preventative_sandbox.py",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        "agentic_core/prompt_governance/prompt_assembly/prompt_assembler.py",
        "agentic_core/prompt_governance/prompt_assembly/compiled_artifact_types.py",
        "agentic_core/prompt_governance/prompt_assembly/pa7_dispatch_states.py",
        "agentic_core/prompt_governance/prompt_assembly/pa7_signature.py",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        "agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py",
        "agentic_core/L5_safety/runtime_gates/g24_determinism_replay.py",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        "agentic_core/L4_state/audit/audit_ledger.py",
        "agentic_core/L4_state/uwg/durable_write_gateway.py",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        "agentic_core/L6_observability/shadow_eval/gauntlet.py",
        "agentic_core/L6_observability/utils/evaluation/promotion_gauntlet.py",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        "agentic_core/L3_orchestration/exit_eval/v6/x3_dispositions.py",
        "agentic_core/L3_orchestration/exit_eval/disposition.py",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        "agentic_core/L2_execution/audit/drift_detector.py",
        "agentic_core/L6_observability/utils/engines/drift_detector.py",
        "agentic_core/prompt_governance/scripts/detect_template_drift.py",
    ),
}

VALIDATOR_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": (
        "agentic_core/L4_state/enforcement/uwg_verifier.py",
        "agentic_core/adg/applications/uwg_write_authority_validator.py",
        "agentic_core/L5_safety/runtime_gates/g27_durable_write_sovereignty.py",
    ),
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": (
        "agentic_core/L5_safety/runtime_gates/g27_durable_write_sovereignty.py",
        "agentic_core/L5_safety/runtime_gates/g29_learning_firewall.py",
        "agentic_core/adg/applications/uwg_write_authority_validator.py",
    ),
    "REQ-UWG-OBS-ANTI-BYPASS-001": (
        "agentic_core/L2_execution/enforcement/anti_bypass_guards.py",
        "agentic_core/L4_state/enforcement/uwg_verifier.py",
        "agentic_core/L5_safety/runtime_gates/g27_durable_write_sovereignty.py",
    ),
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        "agentic_core/L5_safety/runtime_gates/enforcement.py",
        "agentic_core/L2_execution/enforcement/anti_bypass_guards.py",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        "agentic_core/L5_safety/runtime_gates/enforcement.py",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        "agentic_core/L5_safety/v5/g2a_origin_trust.py",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        "agentic_core/prompt_governance/prompt_assembly/pa4_validation.py",
        "agentic_core/prompt_governance/prompt_assembly/validate_assembly.py",
        "agentic_core/prompt_governance/prompt_assembly/slot_contracts.py",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        "agentic_core/L2_execution/enforcement/anti_bypass_guards.py",
        "agentic_core/runtime/prove_requirements/anti_bypass_negatives.py",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        "agentic_core/L2_execution/enforcement/anti_bypass_guards.py",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        "agentic_core/prompt_governance/prompt_assembly/output_schema_validator.py",
        "agentic_core/prompt_governance/prompt_assembly/l2_handoff.py",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        "agentic_core/L5_safety/runtime_gates/g24_determinism_replay.py",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        "agentic_core/L5_safety/runtime_gates/g28_audit_trace_completeness.py",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        "agentic_core/L5_safety/runtime_gates/g29_learning_firewall.py",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        "agentic_core/L5_safety/runtime_gates/g26_exit_disposition.py",
        "agentic_core/L2_execution/enforcement/anti_bypass_guards.py",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        "agentic_core/prompt_governance/scripts/detect_template_drift.py",
    ),
}

OTEL_SPAN_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": (
        "agentic_core/L4_state/otel/uwg_write_spans.py",
    ),
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": (
        "agentic_core/L4_state/otel/uwg_write_spans.py",
    ),
    "REQ-UWG-OBS-ANTI-BYPASS-001": (
        "agentic_core/L4_state/otel/uwg_write_spans.py",
    ),
    "REQ-GATE-OBS-ANTI-BYPASS-001": (
        "agentic_core/L5_safety/runtime_gates/otel_spans.py",
        "agentic_core/L5_safety/runtime_gates/otel_feed.py",
    ),
    "REQ-L5-SAFETY-ENFORCE-PLANE-001": (
        "agentic_core/L5_safety/v5/governance_spans.py",
        "agentic_core/L5_safety/v5/otel_spans.py",
    ),
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": (
        "agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py",
    ),
    "REQ-PA-AUTHORITY-REDTEAM-001": (
        "agentic_core/prompt_governance/prompt_assembly/trace_spans.py",
    ),
    "REQ-C0-OBS-ANTI-BYPASS-001": (
        "agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/otel.py",
    ),
    "REQ-L2-OBS-ANTI-BYPASS-001": (
        "agentic_core/L2_execution/observability/l2_spans.py",
        "agentic_core/L2_execution/observability/l2_otel_emitter.py",
    ),
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": (
        "agentic_core/prompt_governance/prompt_assembly/trace_spans.py",
    ),
    "REQ-EXIT-X1G-X1I-REPLAY-001": (
        "agentic_core/L3_orchestration/exit_eval/otel_spans.py",
        "agentic_core/L3_orchestration/exit_eval/v6/otel.py",
    ),
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": (
        "agentic_core/L4_state/otel/spans.py",
        "agentic_core/L4_state/otel/uwg_write_spans.py",
    ),
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": (
        "agentic_core/L6_observability/shadow_eval/otel_spans.py",
    ),
    "REQ-EXIT-OBS-ANTI-BYPASS-001": (
        "agentic_core/L3_orchestration/exit_eval/otel_spans.py",
        "agentic_core/L3_orchestration/exit_eval/v6/otel.py",
    ),
    "REQ-L5-STATIC-GOV-DRIFT-001": (
        "agentic_core/L5_safety/v5/governance_spans.py",
    ),
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filter_existing(paths: Sequence[str]) -> List[str]:
    """Drop paths that do not exist on disk. Never invents files."""
    return [p for p in paths if (REPO_ROOT / p).exists()]


def _load_selection() -> Dict[str, Any]:
    return json.loads(SELECTION_PATH.read_text(encoding="utf-8"))


def _is_applicable(gap_value: str) -> bool:
    """A gap field marks evidence as applicable unless it is NOT_APPLICABLE."""
    if not gap_value:
        return False
    return "NOT_APPLICABLE" not in gap_value.upper()


def _build_row(selected: Mapping[str, Any]) -> Dict[str, Any]:
    rid = selected["req_id"]
    blockers: List[str] = []

    efr = EXPECTED_FAIL_REASONS.get(rid, "").strip()
    if not efr:
        blockers.append("NEEDS_EXPECTED_FAIL_REASON")

    code_refs = _filter_existing(CODE_REFERENCES.get(rid, ()))
    validator_refs = _filter_existing(VALIDATOR_REFERENCES.get(rid, ()))
    test_refs = _filter_existing(TEST_REFERENCES.get(rid, ()))
    artifact_refs = _filter_existing(ARTIFACT_REFERENCES.get(rid, ()))
    replay_refs = _filter_existing(REPLAY_REFERENCES.get(rid, ()))
    otel_span_refs = list(OTEL_SPAN_REFERENCES.get(rid, ()))
    negative_control_refs = _filter_existing(NEGATIVE_CONTROL_REFERENCES.get(rid, ()))

    if not code_refs:
        blockers.append("NEEDS_CODE_REF")
    if not validator_refs:
        blockers.append("NEEDS_VALIDATOR_REF")
    if not otel_span_refs:
        blockers.append("NEEDS_OTEL_SPAN")

    if _is_applicable(selected.get("likely_test_gap", "")) and not test_refs:
        blockers.append("NEEDS_TEST_MAPPING")
    if _is_applicable(selected.get("likely_artifact_gap", "")) and not artifact_refs:
        blockers.append("NEEDS_ARTIFACT_FIELD")
    if _is_applicable(selected.get("likely_replay_gap", "")) and not replay_refs:
        blockers.append("NEEDS_REPLAY_FIELD")
    if _is_applicable(selected.get("likely_negative_control_gap", "")) and not negative_control_refs:
        blockers.append("NEEDS_NEGATIVE_CONTROL")

    # Linkage classification.
    if blockers:
        if (
            test_refs
            or artifact_refs
            or replay_refs
            or negative_control_refs
            or code_refs
            or validator_refs
            or otel_span_refs
        ):
            linkage_status = "PARTIAL_LINK"
        elif efr:
            linkage_status = "LINKED_CONCEPTUAL"
        else:
            linkage_status = "NO_LINK"
            if "NO_LINK" not in blockers:
                blockers.append("NO_LINK")
    else:
        linkage_status = "LINKED_LITERAL"

    return {
        "tier": "TIER1",
        "step1_req_id": rid,
        "source_matrix_file": selected["source_matrix_file"],
        "owner_layer": selected["owner_layer"],
        "owner_subsystem": selected["owner_subsystem"],
        "requirement_text": selected["requirement_text"],
        "requirement_strength": selected["requirement_strength"],
        "release_gate_rule": selected["release_gate_rule"],
        "risk_category": selected["risk_category"],
        "why_tier1": selected["why_tier1"],
        "expected_fail_reason": efr,
        "linkage_status": linkage_status,
        "blockers": blockers,
        "code_refs": code_refs,
        "validator_refs": validator_refs,
        "test_refs": test_refs,
        "test_executed": False,
        "artifact_refs": artifact_refs,
        "artifact_verified": False,
        "replay_refs": replay_refs,
        "replay_executed": False,
        "otel_span_refs": otel_span_refs,
        "negative_control_refs": negative_control_refs,
        "negative_control_executed": False,
    }


def _build_rows() -> List[Dict[str, Any]]:
    selection = _load_selection()
    return [_build_row(sel) for sel in selection["selected"]]


def _surface_payload(surface: str, rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "tier": "TIER1",
        "surface": surface,
        "purpose": ("Tier 1 metadata linkage. Selection-derived; no proof claims."),
        "generated_at": _utc_now_iso(),
        "source_files": {
            "selection": "docs/reference/contracts/tier1/TIER1_SELECTION.json",
            "step1_matrices_dir": "docs/reference/contracts/step1/",
        },
        "row_count": len(rows),
        "rows": list(rows),
    }


def _validate(rows: Sequence[Mapping[str, Any]]) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
    errors: List[str] = []
    allowed_linkage = {"LINKED_LITERAL", "LINKED_CONCEPTUAL", "PARTIAL_LINK", "NO_LINK"}
    allowed_blockers = {
        "NEEDS_STEP1_ROW",
        "NEEDS_EXPECTED_FAIL_REASON",
        "NEEDS_CODE_REF",
        "NEEDS_VALIDATOR_REF",
        "NEEDS_TEST_MAPPING",
        "NEEDS_ARTIFACT_FIELD",
        "NEEDS_REPLAY_FIELD",
        "NEEDS_OTEL_SPAN",
        "NEEDS_NEGATIVE_CONTROL",
        "NO_LINK",
    }
    required_fields = {
        "tier",
        "step1_req_id",
        "source_matrix_file",
        "owner_layer",
        "owner_subsystem",
        "requirement_text",
        "requirement_strength",
        "release_gate_rule",
        "risk_category",
        "why_tier1",
        "expected_fail_reason",
        "linkage_status",
        "blockers",
        "code_refs",
        "validator_refs",
        "test_refs",
        "artifact_refs",
        "replay_refs",
        "otel_span_refs",
        "negative_control_refs",
    }
    forbidden_tokens = {
        "PASS",
        "FAIL",
        "PROVEN",
        "FULLY_PROVEN",
        "ARCHITECTURE_PROVEN",
        "COMPLETE",
        "COVERED",
        "CLOSED",
    }

    linkage_counts: Dict[str, int] = {k: 0 for k in allowed_linkage}
    blocker_counts: Dict[str, int] = {k: 0 for k in allowed_blockers}

    for row in rows:
        missing = required_fields - set(row.keys())
        if missing:
            errors.append(f"{row.get('step1_req_id', '?')}: missing fields {sorted(missing)}")
        if row.get("tier") != "TIER1":
            errors.append(f"{row.get('step1_req_id', '?')}: tier!=TIER1")
        ls = row.get("linkage_status")
        if ls not in allowed_linkage:
            errors.append(f"{row.get('step1_req_id', '?')}: invalid linkage_status={ls!r}")
        else:
            linkage_counts[ls] += 1
        for b in row.get("blockers", []):
            if b not in allowed_blockers:
                errors.append(f"{row.get('step1_req_id', '?')}: invalid blocker={b!r}")
            else:
                blocker_counts[b] += 1
        for forbidden in forbidden_tokens:
            if row.get("linkage_status") == forbidden:
                errors.append(f"{row.get('step1_req_id', '?')}: forbidden status token {forbidden}")

    return errors, linkage_counts, blocker_counts


def generate() -> Dict[str, Path]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = _build_rows()
    written: Dict[str, Path] = {}
    for surface, fname in OUT_FILES.items():
        path = ARTIFACTS_DIR / fname
        path.write_text(
            json.dumps(_surface_payload(surface, rows), indent=2),
            encoding="utf-8",
        )
        written[surface] = path

    errors, linkage_counts, blocker_counts = _validate(rows)
    report_lines: List[str] = []
    report_lines.append("# Tier 1 Schema Validation Report")
    report_lines.append("")
    report_lines.append(f"- Generated at: {_utc_now_iso()}")
    report_lines.append(f"- Row count: {len(rows)}")
    report_lines.append(f"- Surface files: {len(written)}")
    report_lines.append(f"- Schema validation: {'OK' if not errors else 'FAILED'}")
    report_lines.append("")
    report_lines.append("## Linkage status counts")
    for k, v in linkage_counts.items():
        report_lines.append(f"- {k}: {v}")
    report_lines.append("")
    report_lines.append("## Blocker counts")
    for k, v in blocker_counts.items():
        report_lines.append(f"- {k}: {v}")
    if errors:
        report_lines.append("")
        report_lines.append("## Validation errors")
        for e in errors:
            report_lines.append(f"- {e}")
    report_path = ARTIFACTS_DIR / OUT_VALIDATION_REPORT
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    written["validation_report"] = report_path

    print(f"Generated {len(OUT_FILES)} files + report at {report_path}")
    print(f"Tier 1 row count per file: {len(rows)}")
    print(f"Schema validation: {'OK' if not errors else 'FAILED'}")
    print(f"Linkage status counts: {linkage_counts}")
    print(f"Blocker counts: {blocker_counts}")
    return written


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
