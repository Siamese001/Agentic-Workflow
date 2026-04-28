"""Tier 2 metadata generator.

Reads the Tier 2 selection (`docs/reference/contracts/tier2/TIER2_SELECTION.json`)
and emits four normalized metadata-surface files plus a schema validation
report under ``artifacts/runtime/requirements_proof/``.

This is metadata/linkage work only. It does NOT implement runtime behavior,
run tests, run proof harnesses, execute replay, or run OTEL exporters.
It does NOT claim proof, coverage, or readiness.

First-pass policy: only on-disk references that already map cleanly to a
Tier 2 row are populated. When a reference dict is empty for a REQ_ID,
the corresponding NEEDS_* blocker remains and the row is classified as
PARTIAL_LINK / LINKED_CONCEPTUAL / NO_LINK accordingly.

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
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier2" / "TIER2_SELECTION.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

OUT_FILES: Dict[str, str] = {
    "index": "tier2_requirements_index.generated.json",
    "coverage": "tier2_coverage_matrix.generated.json",
    "impl": "tier2_implementation_map.generated.json",
    "artifact": "tier2_artifact_linkage.generated.json",
}
OUT_VALIDATION_REPORT = "tier2_schema_validation_report.md"

# ---------------------------------------------------------------------------
# Stable expected_fail_reason mapping. Populated when the requirement's
# failure mode is obvious from the REQ_ID + requirement text. Otherwise the
# row keeps the NEEDS_EXPECTED_FAIL_REASON blocker.
# ---------------------------------------------------------------------------
EXPECTED_FAIL_REASONS: Mapping[str, str] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": "VALIDATED_REQUEST_HANDOFF_REQUIRED",
    "REQ-U0-ANTI-BYPASS-001": "INTAKE_VALIDATION_BYPASS_BLOCKED",
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": "ORIGIN_TRUST_LABEL_MISSING",
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": "L1_ADHOC_PLAN_PAYLOAD_BLOCKED",
    "REQ-L1-NO-RETRIEVAL-001": "L1_RETRIEVAL_BLOCKED",
    "REQ-L1-NO-EXECUTE-001": "L1_EXECUTION_BLOCKED",
    "REQ-L0-NO-RETRIEVAL-001": "L0_RETRIEVAL_BLOCKED",
    "REQ-L3-L2-STEP-HANDOFF-001": "L3_L2_HANDOFF_CHECKPOINT_MISSING",
    "REQ-C0-EVIDENCE-FETCH-001": "C0_RETRIEVAL_PLAN_BYPASS_BLOCKED",
    "REQ-C0-NO-EXECUTE-001": "C0_EXECUTION_BLOCKED",
    "REQ-PA-PROVIDER-AWARE-RENDER-001": "PROVIDER_TEMPLATE_NOT_DECLARED",
    "REQ-PA-AIRLOCK-SECURITY-001": "PA_AIRLOCK_SECURITY_BLOCKED",
    "REQ-L2-PTC-SANDBOX-001": "PTC_SANDBOX_REQUIRED",
    "REQ-L2-VERIFY-THEN-EXECUTE-001": "VERIFY_THEN_EXECUTE_REQUIRED",
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": "EXIT_GATE_DECISION_OVERLAP_BLOCKED",
    "REQ-L4-RETRIEVAL-SURFACE-001": "L4_RETRIEVAL_SURFACE_VIOLATION",
    "REQ-L4-CACHE-STATE-001": "L4_CACHE_STATE_VIOLATION",
    "REQ-L5-RISK-TIER-BANDS-001": "L5_RISK_TIER_POLICY_MISMATCH",
    "REQ-L5-HITL-RECLEARANCE-001": "HITL_RECLEARANCE_REQUIRED",
    "REQ-L6-SIGNAL-FUSION-RCA-001": "L6_SIGNAL_FUSION_FROM_UNSEALED_RECORD_BLOCKED",
    "REQ-E2E-MUTATION-BOUNDARY-001": "E2E_MUTATION_BOUNDARY_FAULT_MISSING",
    "REQ-E2E-CONTRACT-EMISSION-001": "E2E_CONTRACT_EMISSION_MISSING",
}

# ---------------------------------------------------------------------------
# On-disk reference candidates. Empty tuples → no reference; the
# corresponding NEEDS_* blocker remains. First-pass policy: do NOT invent
# file names. Only paths verified to exist on disk are included; paths
# that do not exist are silently dropped via _filter_existing.
# ---------------------------------------------------------------------------
CODE_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "agentic_core/L0_routing/intake/validated_request.py",
        "agentic_core/L0_routing/intake/handoff.py",
        "agentic_core/L0_routing/intake/pipeline.py",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "agentic_core/L0_routing/intake/pipeline.py",
        "agentic_core/L0_routing/intake/stages.py",
        "agentic_core/L0_routing/intake/verdicts.py",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "agentic_core/L0_routing/intake/origin_labels.py",
        "agentic_core/L5_safety/v5/g2a_origin_trust.py",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "agentic_core/L1_cognition/planning/plan_contract_handoff.py",
        "agentic_core/L1_cognition/types/plan_contract_types.py",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "agentic_core/L3_orchestration/types/orchestration_handoff_contract.py",
        "agentic_core/L3_orchestration/types/agent_handoff.py",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "agentic_core/L0_routing/c0_retrieval/evidence_contract.py",
        "agentic_core/L0_routing/c0_retrieval/evidence_projections.py",
        "agentic_core/knowledge/retrieval/retrieval_plan.py",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "agentic_core/L1_cognition/c0_context/contract.py",
        "agentic_core/L1_cognition/c0_context/safety.py",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "agentic_core/prompt_governance/prompt_assembly/pa6_provider_rendering.py",
        "agentic_core/prompt_governance/core/sovereign_prompt_renderer.py",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "agentic_core/prompt_governance/prompt_assembly/pa3_u0_airlock.py",
        "agentic_core/L5_safety/enforcement/airlock_guardrail.py",
        "agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "agentic_core/L2_execution/utils/ptc_contract.py",
        "agentic_core/L2_execution/types/ptc_execution_profile.py",
        "agentic_core/L2_execution/types/sandbox_envelope_types.py",
        "agentic_core/L2_execution/enforcement/preventative_sandbox.py",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "agentic_core/L2_execution/types/l2_local_critique.py",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "agentic_core/L3_orchestration/exit_eval/gates.py",
        "agentic_core/L3_orchestration/exit_eval/disposition.py",
        "agentic_core/L5_safety/runtime_gates/dispatch.py",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (),
    "REQ-L4-CACHE-STATE-001": (
        "agentic_core/L4_state/cache/cache_key_builders.py",
        "agentic_core/L4_state/cache/redis_cache_client.py",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "agentic_core/L5_safety/runtime_gates/g05_risk_tier.py",
        "agentic_core/L5_safety/v5/risk_tier_controls.py",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "agentic_core/L5_safety/contracts/hitl.py",
        "agentic_core/L5_safety/enforcement/exit_control_hitl.py",
        "agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py",
        "agentic_core/L3_orchestration/exit_control/runtime_hitl_ledger.py",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "agentic_core/L6_observability/shadow_eval/rca.py",
        "agentic_core/L6_observability/utils/evaluation/rca_aggregator.py",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "agentic_core/L0_routing/enforcement/mutation_prohibition.py",
        "agentic_core/L0_routing/enforcement/runtime_mutation_guard.py",
        "agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py",
        "agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py",
        "agentic_core/L5_safety/validators/global_mutation_validator.py",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "agentic_core/L3_orchestration/types/orchestration_handoff_contract.py",
        "agentic_core/L1_cognition/planning/plan_contract_handoff.py",
        "agentic_core/L0_routing/intake/handoff.py",
    ),
}
VALIDATOR_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "agentic_core/L0_routing/intake/verdicts.py",
        "agentic_core/L0_routing/intake/doctrine_contracts.py",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "agentic_core/L0_routing/intake/verdicts.py",
        "agentic_core/L0_routing/intake/doctrine_contracts.py",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "agentic_core/L5_safety/v5/g2a_origin_trust.py",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "agentic_core/L1_cognition/types/plan_contract_types.py",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "agentic_core/L3_orchestration/types/orchestration_handoff_contract.py",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "agentic_core/L0_routing/c0_retrieval/evidence_contract.py",
        "agentic_core/L1_cognition/c0_context/contract.py",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "agentic_core/L1_cognition/c0_context/safety.py",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "agentic_core/prompt_governance/prompt_assembly/pa6_provider_rendering.py",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "agentic_core/L5_safety/enforcement/airlock_guardrail.py",
        "agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "agentic_core/L2_execution/enforcement/preventative_sandbox.py",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "agentic_core/L2_execution/types/l2_local_critique.py",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "agentic_core/L3_orchestration/exit_eval/gates.py",
        "agentic_core/L5_safety/runtime_gates/enforcement.py",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (),
    "REQ-L4-CACHE-STATE-001": (
        "agentic_core/L4_state/cache/cache_key_builders.py",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "agentic_core/L5_safety/runtime_gates/g05_risk_tier.py",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py",
        "agentic_core/L5_safety/enforcement/exit_control_hitl.py",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "agentic_core/L6_observability/utils/evaluation/rca_aggregator.py",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "agentic_core/L5_safety/validators/global_mutation_validator.py",
        "agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "agentic_core/L3_orchestration/types/orchestration_handoff_contract.py",
    ),
}
TEST_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "tests/agentic_core/L0_routing/intake/test_01_5_correlation_replay.py",
        "tests/agentic_core/L0_routing/intake/test_01_4_schema_origin_security.py",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "tests/agentic_core/L0_routing/intake/test_01_5_correlation_replay.py",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "tests/agentic_core/L0_routing/intake/test_01_4_schema_origin_security.py",
        "tests/unit/agentic_core/L5_safety/v5/test_g2a_origin_trust.py",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "tests/unit/agentic_core/L1_cognition/test_plan_contract_v4_fields.py",
        "tests/unit/agentic_core/L1_cognition/test_plan_contract_v2.py",
        "tests/unit/agentic_core/L1_cognition/test_plan_contract_types.py",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "tests/agentic_core/L3_orchestration/types/test_orchestration_handoff_contract.py",
        "tests/unit/agentic_core/L3_orchestration/types/test_orchestration_handoff_contract_behavior.py",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "tests/agentic_core/L0_routing/c0_retrieval/test_evidence_contract.py",
        "tests/runtime/test_c0_evidence_contract.py",
        "tests/agentic_core/knowledge/retrieval/test_retrieval_plan.py",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "tests/unit/agentic_core/L0_routing/policy/test_c0_authority_leak.py",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa6_provider_rendering.py",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa3_u0_airlock.py",
        "tests/unit/agentic_core/L5_safety/enforcement/test_airlock_guardrail.py",
        "tests/unit/agentic_core/L5_safety/enforcement/test_final_airlock_trimmer_enforcer.py",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "tests/agentic_core/L2_execution/enforcement/test_preventative_sandbox.py",
        "tests/agentic_core/L2_execution/utils/test_ptc_contract.py",
        "tests/integration/agentic_core/L2_execution/tools/test_ptc_contract_enforcement.py",
        "tests/unit/agentic_core/L2_execution/test_ptc_execution_contracts.py",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "tests/unit/agentic_core/L2_execution/test_l2_local_critique.py",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "tests/runtime_gates/test_gate_mesh_no_bypass.py",
        "tests/runtime_gates/test_gate_mesh_result.py",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (),
    "REQ-L4-CACHE-STATE-001": (
        "tests/unit/agentic_core/L4_state/cache/test_cache_key_builders.py",
        "tests/unit/agentic_core/L4_state/cache/test_cache_init.py",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "tests/unit/agentic_core/L5_safety/runtime_gates/test_g01_g06.py",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "tests/unit/agentic_core/L5_safety/runtime_gates/test_g01_g06.py",
        "tests/agentic_core/L3_orchestration/exit_control/test_hitl_spans.py",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "tests/unit/L6_observability/shadow_eval/test_06_5_rca.py",
        "tests/agentic_core/L6_observability/utils/evaluation/test_rca_aggregator.py",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "tests/runtime_gates/test_gate_mutation_forbidden.py",
        "tests/agentic_core/L0_routing/enforcement/test_mutation_prohibition.py",
        "tests/unit/agentic_core/L0_routing/enforcement/test_runtime_mutation_guard.py",
        "tests/unit/agentic_core/L5_safety/enforcement/test_mutation_prohibition_enforcer.py",
        "tests/unit/agentic_core/L5_safety/validators/test_global_mutation_validator.py",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "tests/agentic_core/L3_orchestration/types/test_orchestration_handoff_contract.py",
    ),
}
ARTIFACT_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-HITL/rc_hitl_ValidatedRequest.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R1A/rc_r1a_ValidatedRequest.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_ValidatedRequest.json",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "artifacts/runtime/requirements_proof/anti_bypass_results.json",
        "artifacts/runtime/requirements_proof/traces/scenario_D_anti_bypass.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-HITL/rc_hitl_no_bypass_receipt.json",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_R_u0_origin_trust_injection.json",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-HITL/rc_hitl_L1PlanContract.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R1A/rc_r1a_L1PlanContract.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_L1PlanContract.json",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3R4-MANAGED/rc_r3r4_managed_L3WorkflowContract.json",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_FinalEvidenceContract.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-UWG/rc_uwg_FinalEvidenceContract.json",
        "artifacts/runtime/requirements_proof/traces/scenario_C_weak_evidence.json",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_M_c0_no_execute.json",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_PromptEnvelope.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-UWG/rc_uwg_PromptEnvelope.json",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_PromptEnvelope.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-UWG/rc_uwg_PromptEnvelope.json",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_L2ExecutionRequest.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_SealedL2Artifact.json",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_L2ExecutionRequest.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3R4-MANAGED/rc_r3r4_managed_L2ExecutionRequest.json",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_disposition.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_ExitReviewPacket.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_X3DispositionReceipt.json",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (),
    "REQ-L4-CACHE-STATE-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_P_l4_cache_state.json",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_Q_l5_risk_tier_bands.json",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-HITL/rc_hitl_ValidatedRequest.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-HITL/rc_hitl_X3DispositionReceipt.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-HITL/rc_hitl_disposition.json",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_l6_exhaust_receipt.json",
        "artifacts/e2e/_smoke_all/scenarios/RC-R3/rc_r3_RuntimeExhaustBundle.json",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "artifacts/e2e/boundary_faults/proof_bundle.json",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "artifacts/e2e/det1/bundle.json",
        "artifacts/e2e/det2/bundle.json",
        "artifacts/e2e/evidence/bundle.json",
    ),
}
REPLAY_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_request.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_request.json",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "artifacts/runtime/requirements_proof/replay/replay_D_anti_bypass_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_D_anti_bypass_run_2.json",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "artifacts/runtime/requirements_proof/replay/replay_R_u0_origin_trust_injection_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_R_u0_origin_trust_injection_run_2.json",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_l1_plan.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_l1_plan.json",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "artifacts/runtime/requirements_proof/replay/replay_O_l3_l2_step_handoff_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_O_l3_l2_step_handoff_run_2.json",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_final_evidence_contract.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_final_evidence_contract.json",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "artifacts/runtime/requirements_proof/replay/replay_M_c0_no_execute_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_M_c0_no_execute_run_2.json",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_prompt_envelope.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_prompt_envelope.json",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_prompt_envelope.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_prompt_envelope.json",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_sealed_l2_artifact.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_sealed_l2_artifact.json",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_l2_execution_request.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_l2_execution_request.json",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "artifacts/e2e/det1/scenarios/GP-001/gp_001_disposition.json",
        "artifacts/e2e/det2/scenarios/GP-001/gp_001_disposition.json",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (),
    "REQ-L4-CACHE-STATE-001": (
        "artifacts/runtime/requirements_proof/replay/replay_P_l4_cache_state_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_P_l4_cache_state_run_2.json",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "artifacts/runtime/requirements_proof/replay/replay_Q_l5_risk_tier_bands_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_Q_l5_risk_tier_bands_run_2.json",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "artifacts/runtime/requirements_proof/replay/replay_N_l5_hitl_reclearance_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_N_l5_hitl_reclearance_run_2.json",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "artifacts/runtime/requirements_proof/replay/replay_K_l6_signal_fusion_rca_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_K_l6_signal_fusion_rca_run_2.json",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "artifacts/runtime/requirements_proof/replay/replay_L_e2e_mutation_boundary_run_1.json",
        "artifacts/runtime/requirements_proof/replay/replay_L_e2e_mutation_boundary_run_2.json",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "artifacts/e2e/det1/bundle.json",
        "artifacts/e2e/det2/bundle.json",
    ),
}
OTEL_SPAN_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "agentic_core/L0_routing/intake/events.py",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "agentic_core/L0_routing/intake/events.py",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "agentic_core/L0_routing/intake/events.py",
        "agentic_core/L5_safety/v5/governance_spans.py",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "agentic_core/L1_cognition/planning/otel.py",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "agentic_core/runtime/prove_requirements/tier2_otel_refs/l3_l2_step_handoff_spans.py",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "agentic_core/L1_cognition/c0_context/observability.py",
        "agentic_core/L0_routing/c0_retrieval/events.py",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "agentic_core/L1_cognition/c0_context/observability.py",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "agentic_core/runtime/prove_requirements/tier2_otel_refs/pa_provider_aware_render_spans.py",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "agentic_core/runtime/prove_requirements/tier2_otel_refs/pa_airlock_security_spans.py",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "agentic_core/runtime/prove_requirements/tier2_otel_refs/l2_ptc_sandbox_spans.py",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "agentic_core/runtime/prove_requirements/tier2_otel_refs/l2_verify_then_execute_spans.py",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "agentic_core/L3_orchestration/exit_eval/otel_spans.py",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (
        "agentic_core/L4_state/otel/spans.py",
    ),
    "REQ-L4-CACHE-STATE-001": (
        "agentic_core/L4_state/otel/spans.py",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "agentic_core/L5_safety/v5/governance_spans.py",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "agentic_core/L3_orchestration/exit_control/hitl_spans.py",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "agentic_core/L6_observability/shadow_eval/otel_spans.py",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "agentic_core/L4_state/otel/spans.py",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "agentic_core/L1_cognition/planning/otel.py",
        "agentic_core/L0_routing/intake/events.py",
    ),
}
NEGATIVE_CONTROL_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-U0-VALIDATED-REQUEST-HANDOFF-001": (
        "tests/agentic_core/L0_routing/test_boundary_contracts.py",
        "tests/agentic_core/L0_routing/enforcement/test_boundary_contracts.py",
    ),
    "REQ-U0-ANTI-BYPASS-001": (
        "artifacts/runtime/requirements_proof/anti_bypass_results.json",
        "tests/runtime/test_anti_bypass_runtime_cheat_proof.py",
        "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
    ),
    "REQ-U0-ORIGIN-TRUST-INJECTION-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_R_u0_origin_trust_injection.json",
    ),
    "REQ-L1-PLAN-CONTRACT-HANDOFF-001": (
        "tests/unit/agentic_core/L1_cognition/planning/test_negative_boundaries.py",
    ),
    "REQ-L1-NO-RETRIEVAL-001": (),
    "REQ-L1-NO-EXECUTE-001": (),
    "REQ-L0-NO-RETRIEVAL-001": (),
    "REQ-L3-L2-STEP-HANDOFF-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_O_l3_l2_step_handoff.json",
    ),
    "REQ-C0-EVIDENCE-FETCH-001": (
        "tests/agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/test_negative.py",
        "tests/unit/agentic_core/L1_cognition/c0_context/test_c0_anti_bypass.py",
    ),
    "REQ-C0-NO-EXECUTE-001": (
        "tests/unit/agentic_core/L1_cognition/c0_context/test_c0_anti_bypass.py",
    ),
    "REQ-PA-PROVIDER-AWARE-RENDER-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa0_boundary.py",
    ),
    "REQ-PA-AIRLOCK-SECURITY-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa0_boundary.py",
        "tests/unit/agentic_core/L5_safety/reasoning/test_AdversarialRedTeamerAgent.py",
        "tests/unit/agentic_core/L5_safety/reasoning/test_RedTeamAgent.py",
    ),
    "REQ-L2-PTC-SANDBOX-001": (
        "tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py",
        "tests/integration/agentic_core/L2_execution/enforcement/test_boundary_end_to_end.py",
    ),
    "REQ-L2-VERIFY-THEN-EXECUTE-001": (
        "tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py",
    ),
    "REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001": (
        "tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_anti_bypass.py",
        "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
    ),
    "REQ-L4-RETRIEVAL-SURFACE-001": (
        "tests/runtime/test_uwg_write_sovereignty.py",
        "tests/unit/apps_shared/proof/test_write_sovereignty.py",
    ),
    "REQ-L4-CACHE-STATE-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_P_l4_cache_state.json",
    ),
    "REQ-L5-RISK-TIER-BANDS-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_Q_l5_risk_tier_bands.json",
    ),
    "REQ-L5-HITL-RECLEARANCE-001": (
        "artifacts/runtime/requirements_proof/traces/scenario_N_l5_hitl_reclearance.json",
    ),
    "REQ-L6-SIGNAL-FUSION-RCA-001": (
        "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
    ),
    "REQ-E2E-MUTATION-BOUNDARY-001": (
        "tests/e2e/test_boundary_fault_matrix.py",
        "tests/agentic_core/adg/runtime/test_boundary_verifier.py",
        "tests/e2e/agentic_core/test_layer_sovereignty_e2e.py",
        "tests/governance/test_negative_control_exit0_tamper.py",
    ),
    "REQ-E2E-CONTRACT-EMISSION-001": (
        "tests/governance/test_negative_control_exit0_tamper.py",
        "tests/unit/apps_shared/proof/test_negative_controls.py",
    ),
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filter_existing(paths: Sequence[str]) -> List[str]:
    """Drop paths that do not exist on disk. Never invents files."""
    return [p for p in paths if (REPO_ROOT / p).exists()]


def _filter_matching_req_id(paths: Sequence[str], req_id: str) -> List[str]:
    """Drop JSON paths whose `step1_req_id` is present and does not match
    `req_id`. Files without `step1_req_id` are kept. Non-JSON paths are
    kept as-is.
    """
    out: List[str] = []
    for p in paths:
        full = REPO_ROOT / p
        if not full.is_file() or not p.endswith(".json"):
            out.append(p)
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            out.append(p)
            continue
        if isinstance(data, dict) and "step1_req_id" in data:
            if data["step1_req_id"] != req_id:
                continue
        out.append(p)
    return out


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
    artifact_refs = _filter_matching_req_id(
        _filter_existing(ARTIFACT_REFERENCES.get(rid, ())), rid
    )
    replay_refs = _filter_matching_req_id(
        _filter_existing(REPLAY_REFERENCES.get(rid, ())), rid
    )
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
        "tier": "TIER2",
        "step1_req_id": rid,
        "source_matrix_file": selected["source_matrix_file"],
        "owner_layer": selected["owner_layer"],
        "owner_subsystem": selected["owner_subsystem"],
        "requirement_text": selected["requirement_text"],
        "requirement_strength": selected["requirement_strength"],
        "release_gate_rule": selected["release_gate_rule"],
        "risk_category": selected["risk_category"],
        "why_tier2": selected["why_tier2"],
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
        "tier": "TIER2",
        "surface": surface,
        "purpose": "Tier 2 metadata linkage. Selection-derived; no proof claims.",
        "generated_at": _utc_now_iso(),
        "source_files": {
            "selection": "docs/reference/contracts/tier2/TIER2_SELECTION.json",
            "step1_matrices_dir": "docs/reference/contracts/step1/",
        },
        "row_count": len(rows),
        "rows": list(rows),
    }


def _validate(
    rows: Sequence[Mapping[str, Any]],
) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
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
        "why_tier2",
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
        if row.get("tier") != "TIER2":
            errors.append(f"{row.get('step1_req_id', '?')}: tier!=TIER2")
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
    report_lines.append("# Tier 2 Schema Validation Report")
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
    print(f"Tier 2 row count per file: {len(rows)}")
    print(f"Schema validation: {'OK' if not errors else 'FAILED'}")
    print(f"Linkage status counts: {linkage_counts}")
    print(f"Blocker counts: {blocker_counts}")
    return written


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
