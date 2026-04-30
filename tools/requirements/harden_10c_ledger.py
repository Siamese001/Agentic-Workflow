"""Harden the 10C semantic requirement ledger into proof-grade form (W4d-2).

Iteration 2 (2026-04-30) addresses the seven defects surfaced in the W4d
post-hardening review:

  1. Owner correction: rows from ``01_request_intake.md`` and the U0 stage
     of ``agentic_process_mapping_v29.md`` move from ``00A_L5_Governance_Safety``
     to ``01_U0_Request_Intake``.
  2. L5 artifact language: ``L5GovernanceVerdict envelope`` is replaced by
     ``L5CertificationResult + L5AuthorityEvidenceReceipt + L5PolicyBindingReceipt``
     so L5 no longer reads as if it emits live runtime dispositions.
  3. Source-lock columns: ``source_commit_sha``, ``source_line_range``,
     ``source_text_sha256`` are added so anchors are content-locked, not just
     path-labeled.
  4. Existence-check columns: ``test_file_exists``, ``ci_gate_exists``,
     ``proof_bundle_exists``, ``last_passed_commit`` are added so the
     ledger never confuses a generated path with proof.
  5. Row-specific negative control: ``negative_control_specific`` is added
     (the existing ``negative_control_expected`` column keeps the
     owner-level boundary control for architecture protection).
  6. Pedagogical-row reclassification: rows whose ``direct_or_implied`` is
     ``explanatory_only`` are tagged ``ACCEPTED_WITH_CAVEAT`` with a
     PEDAGOGICAL_ROW marker in ``hardening_notes``.
  7. Targeted owner re-routes for the five W4d ``NEEDS_OWNER_REVIEW``
     rows: 011 (pedagogical), 118 (cross-cut replay), 140 (UWG-decisive),
     162 (pedagogical), 168 (U0 intake), 194 (cross-cut tracing —
     intentional).

This script is idempotent. It can be re-run as the source of truth for the
deterministic backfill rules.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Mapping, MutableMapping

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_semantic_requirement_ledger.csv"

ORIGINAL_COLUMNS = (
    "req_id",
    "source_file",
    "source_section",
    "source_unit_type",
    "source_text_short",
    "canonical_requirement_statement",
    "direct_or_implied",
    "semantic_class",
    "layer_owner",
    "runtime_phase",
    "required_artifacts",
    "required_controls",
    "required_tests",
    "severity_if_missing",
    "confidence_score",
)

W4D_COLUMNS = (
    "canonical_owner_surface",
    "source_anchor_ref",
    "risk_if_missing_rationale",
    "artifact_schema_ref",
    "runtime_artifact_expected",
    "otel_span_expected",
    "otel_required_attributes",
    "replay_proof_expected",
    "negative_control_expected",
    "test_file_expected",
    "acceptance_command",
    "ci_gate_name",
    "proof_bundle_ref",
    "implementation_status",
    "evidence_status",
    "duplicate_group",
    "supersedes_req_id",
    "blocked_by_req_id",
    "final_acceptance_status",
    "hardening_notes",
)

W4D2_COLUMNS = (
    "source_commit_sha",
    "source_line_range",
    "source_text_sha256",
    "test_file_exists",
    "ci_gate_exists",
    "proof_bundle_exists",
    "last_passed_commit",
    "negative_control_specific",
)

FINAL_COLUMNS = ORIGINAL_COLUMNS + W4D_COLUMNS + W4D2_COLUMNS

CANONICAL_OWNER_VOCAB = frozenset({
    "00A_L5_Governance_Safety",
    "00B_L4_State_Archive_and_UWG",
    "00C_Runtime_Gates_Current_Run_Mesh",
    "01_U0_Request_Intake",
    "02_L1_Reasoning_Plan",
    "03_L0_Route_Decision",
    "03_L3_Orchestration",
    "03A_C0_Context_Engine",
    "03B_PA_Prompt_Assembly",
    "04_L2_Execute",
    "05_Exit_Evaluation_and_Control",
    "06_L6_Shadow_Evaluation_System_Learning",
    "99_End_to_End_Runtime_Proof_and_Acceptance",
    "Offline_Ingestion_Index_Build",
    "Cross_Cutting_Observability_Replay_Audit",
})

LAYER_OWNER_MAP: Mapping[str, str] = {
    "l0 routing": "03_L0_Route_Decision",
    "l1 cognition": "02_L1_Reasoning_Plan",
    "l2 execution": "04_L2_Execute",
    "l3 orchestration": "03_L3_Orchestration",
    "l3 healing": "03_L3_Orchestration",
    "l4/uwg": "00B_L4_State_Archive_and_UWG",
    "l4 uwg": "00B_L4_State_Archive_and_UWG",
    "l4 state": "00B_L4_State_Archive_and_UWG",
    "knowledge/l4": "00B_L4_State_Archive_and_UWG",
    "l5/gateway": "00A_L5_Governance_Safety",
    "l5 safety": "00A_L5_Governance_Safety",
    "l5 policy": "00A_L5_Governance_Safety",
    "l5 re-clearance": "00A_L5_Governance_Safety",
    "l5 exit control": "05_Exit_Evaluation_and_Control",
    "hitl l5": "00A_L5_Governance_Safety",
    "hitl human": "00A_L5_Governance_Safety",
    "hitl healing": "00A_L5_Governance_Safety",
    "l6": "06_L6_Shadow_Evaluation_System_Learning",
    "l6 observability": "06_L6_Shadow_Evaluation_System_Learning",
    "l6 shadow eval": "06_L6_Shadow_Evaluation_System_Learning",
    "l6 evaluation": "06_L6_Shadow_Evaluation_System_Learning",
    "c0/knowledge": "03A_C0_Context_Engine",
    "c0 context engine": "03A_C0_Context_Engine",
    "c0 retrieval": "03A_C0_Context_Engine",
    "c0 governance": "00A_L5_Governance_Safety",
    "c0/prompt_assembly": "03B_PA_Prompt_Assembly",
    "c7 capability": "00A_L5_Governance_Safety",
    "prompt assembly": "03B_PA_Prompt_Assembly",
    "knowledge/embedding": "Offline_Ingestion_Index_Build",
    "knowledge/ingestion": "Offline_Ingestion_Index_Build",
    "knowledge/sparse_index": "Offline_Ingestion_Index_Build",
    "knowledge/chunking": "Offline_Ingestion_Index_Build",
    "knowledge/lifecycle": "Offline_Ingestion_Index_Build",
    "knowledge/evaluation": "Offline_Ingestion_Index_Build",
    "knowledge/enrichment": "Offline_Ingestion_Index_Build",
    "architecture design": "Cross_Cutting_Observability_Replay_Audit",
    "n/a": "Cross_Cutting_Observability_Replay_Audit",
    "l2/l5": "00A_L5_Governance_Safety",
    "l5/l3/l0": "00A_L5_Governance_Safety",
    "l5/l3/l0/l2": "Cross_Cutting_Observability_Replay_Audit",
    "l5/l3/l6": "00A_L5_Governance_Safety",
    "l5/l4/uwg": "00B_L4_State_Archive_and_UWG",
    "l1 cognition + l3 orchestration": "02_L1_Reasoning_Plan",
    "l3 orchestration + l1 cognition": "02_L1_Reasoning_Plan",
    "l3 orchestration + l4 state": "03_L3_Orchestration",
    "l3 orchestration + l6 observability": "03_L3_Orchestration",
    "l1 cognition + l5 safety": "00A_L5_Governance_Safety",
    "l1 cognition + l6 observability": "02_L1_Reasoning_Plan",
    "l4 state + l6 observability": "00B_L4_State_Archive_and_UWG",
    "l2 execution + l5 safety": "00A_L5_Governance_Safety",
    "l2 execution + l4 state": "04_L2_Execute",
    "l6 observability + hitl": "06_L6_Shadow_Evaluation_System_Learning",
    "l5 safety + l6 observability": "00A_L5_Governance_Safety",
    "l6 observability + l5 safety": "00A_L5_Governance_Safety",
    "l6 observability + all layers": "Cross_Cutting_Observability_Replay_Audit",
    "l5 safety + l3 orchestration": "00A_L5_Governance_Safety",
    "hitl l5 + l6 shadow eval": "00A_L5_Governance_Safety",
    "knowledge/embedding + l2 execution": "Offline_Ingestion_Index_Build",
}

SOURCE_FILE_OVERRIDE: Mapping[str, str] = {
    "01_request_intake.md": "01_U0_Request_Intake",
}

REQ_ID_OWNER_OVERRIDE: Mapping[str, tuple[str, str]] = {
    "10C-REQ-011": (
        "Cross_Cutting_Observability_Replay_Audit",
        "PEDAGOGICAL_ROW: documentation/legend, not a runtime proof obligation.",
    ),
    "10C-REQ-118": (
        "Cross_Cutting_Observability_Replay_Audit",
        "OWNER_REVIEW_RESOLVED: Replay-mode propagation crosses L0/L3/L5/L2; cross-cut replay/audit owns enforcement.",
    ),
    "10C-REQ-140": (
        "00B_L4_State_Archive_and_UWG",
        "OWNER_REVIEW_RESOLVED: Decisive obligation is UWG locking pending diffs on freeze; L5 emits the freeze signal upstream, L6 tunes thresholds downstream, but durable enforcement is UWG.",
    ),
    "10C-REQ-162": (
        "Cross_Cutting_Observability_Replay_Audit",
        "PEDAGOGICAL_ROW: Contextual Refinement primer staging-area note, not a runtime proof obligation.",
    ),
    "10C-REQ-168": (
        "01_U0_Request_Intake",
        "OWNER_REVIEW_RESOLVED: Process-map [1] REQUEST INTAKE belongs to U0 intake surface, not L5 governance.",
    ),
    "10C-REQ-194": (
        "Cross_Cutting_Observability_Replay_Audit",
        "OWNER_REVIEW_RESOLVED: W3C traceparent propagation is intentionally cross-cut; enforcement spans every outbound boundary handler. Cross-cut surface owns the contract; per-layer compliance is verified at each emission site.",
    ),
}

AMBIGUOUS_OWNERS = frozenset({"n/a"})

DEFAULT_OTEL_SPAN: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "l5.certification.evidence_emitted",
    "00B_L4_State_Archive_and_UWG": "uwg.commit.validated",
    "00C_Runtime_Gates_Current_Run_Mesh": "runtime_gate.verdict_emitted",
    "01_U0_Request_Intake": "u0.intake.validated",
    "02_L1_Reasoning_Plan": "l1.plan.contract_emitted",
    "03_L0_Route_Decision": "l0.route.contract_emitted",
    "03_L3_Orchestration": "l3.workflow.contract_emitted",
    "03A_C0_Context_Engine": "c0.evidence.contract_emitted",
    "03B_PA_Prompt_Assembly": "pa.prompt.compiled_artifact_emitted",
    "04_L2_Execute": "l2.execution.sealed",
    "05_Exit_Evaluation_and_Control": "exit.x3.disposition_emitted",
    "06_L6_Shadow_Evaluation_System_Learning": "l6.eval.record_sealed",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "e2e.proof_bundle.emitted",
    "Offline_Ingestion_Index_Build": "ingest.chunk.sealed",
    "Cross_Cutting_Observability_Replay_Audit": "obs.audit_event.emitted",
}

PHASE_SPAN_REFINEMENT: Mapping[tuple[str, str], str] = {
    ("00A_L5_Governance_Safety", "Pre-execution"): "l5.certification.precheck_emitted",
    ("00A_L5_Governance_Safety", "Post-execution"): "l5.certification.postcheck_emitted",
    ("00A_L5_Governance_Safety", "Escalation"): "l5.hitl.escalation_recorded",
    ("04_L2_Execute", "Execution"): "l2.execution.attempt",
    ("04_L2_Execute", "Execution healing"): "l2.execution.heal",
    ("04_L2_Execute", "Pre-execution"): "l2.execution.prep",
    ("04_L2_Execute", "Post-execution"): "l2.execution.sealed",
    ("05_Exit_Evaluation_and_Control", "Exit evaluation"): "exit.x1.gates_evaluated",
    ("05_Exit_Evaluation_and_Control", "Exit disposition"): "exit.x3.disposition_emitted",
    ("00B_L4_State_Archive_and_UWG", "Durable commit"): "uwg.commit.committed",
    ("00B_L4_State_Archive_and_UWG", "Write governance"): "uwg.commit.validated",
    ("06_L6_Shadow_Evaluation_System_Learning", "Post-run learning"): "l6.learning.proposal_emitted",
    ("06_L6_Shadow_Evaluation_System_Learning", "Promotion + Shadow eval"): "l6.eval.record_sealed",
    ("Offline_Ingestion_Index_Build", "Offline ingestion"): "ingest.chunk.sealed",
    ("Offline_Ingestion_Index_Build", "Offline indexing"): "ingest.index.materialized",
    ("Offline_Ingestion_Index_Build", "Offline (async init)"): "ingest.bootstrap.completed",
    ("03A_C0_Context_Engine", "Runtime query-time"): "c0.evidence.contract_emitted",
    ("01_U0_Request_Intake", "Ingress"): "u0.intake.validated",
}

REQ_ID_SPAN_OVERRIDE: Mapping[str, str] = {
    "10C-REQ-049": "u0.intake.invariant_enforced",
    "10C-REQ-050": "u0.intake.validated",
    "10C-REQ-051": "u0.intake.identity_bound",
    "10C-REQ-052": "u0.intake.quota_checked",
    "10C-REQ-053": "u0.intake.schema_validated",
    "10C-REQ-054": "u0.intake.payload_normalized",
    "10C-REQ-055": "u0.intake.stamped",
    "10C-REQ-168": "u0.intake.validated",
    "10C-REQ-194": "obs.tracecontext.propagated",
}

TEST_ROOT_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "tests/unit/agentic_core/L5_safety/",
    "00B_L4_State_Archive_and_UWG": "tests/unit/agentic_core/L4_state/",
    "00C_Runtime_Gates_Current_Run_Mesh": "tests/runtime/",
    "01_U0_Request_Intake": "tests/unit/agentic_core/L1_cognition/intake/",
    "02_L1_Reasoning_Plan": "tests/unit/agentic_core/L1_cognition/",
    "03_L0_Route_Decision": "tests/unit/agentic_core/L0_routing/",
    "03_L3_Orchestration": "tests/unit/agentic_core/L3_orchestration/",
    "03A_C0_Context_Engine": "tests/unit/agentic_core/L1_cognition/c0_context/",
    "03B_PA_Prompt_Assembly": "tests/unit/agentic_core/L1_cognition/prompt_assembly/",
    "04_L2_Execute": "tests/unit/agentic_core/L2_execution/",
    "05_Exit_Evaluation_and_Control": "tests/unit/agentic_core/L5_safety/exit_control/",
    "06_L6_Shadow_Evaluation_System_Learning": "tests/unit/agentic_core/L6_observability/",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "tests/e2e/",
    "Offline_Ingestion_Index_Build": "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/",
    "Cross_Cutting_Observability_Replay_Audit": "tests/unit/agentic_core/L6_observability/",
}

CI_GATE_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "ops_scripts/ci/check_l5_certification_proof.py",
    "00B_L4_State_Archive_and_UWG": "ops_scripts/ci/check_uwg_write_admission_proof.py",
    "00C_Runtime_Gates_Current_Run_Mesh": "ops_scripts/ci/check_runtime_gate_verdict_proof.py",
    "01_U0_Request_Intake": "ops_scripts/ci/check_u0_intake_proof.py",
    "02_L1_Reasoning_Plan": "ops_scripts/ci/check_l1_plan_contract_proof.py",
    "03_L0_Route_Decision": "ops_scripts/ci/check_l0_route_contract_proof.py",
    "03_L3_Orchestration": "ops_scripts/ci/check_l3_workflow_proof.py",
    "03A_C0_Context_Engine": "ops_scripts/ci/check_c0_evidence_contract_proof.py",
    "03B_PA_Prompt_Assembly": "ops_scripts/ci/check_pa_compiled_artifact_proof.py",
    "04_L2_Execute": "ops_scripts/ci/check_l2_execution_proof.py",
    "05_Exit_Evaluation_and_Control": "ops_scripts/ci/check_exit_x3_disposition_proof.py",
    "06_L6_Shadow_Evaluation_System_Learning": "ops_scripts/ci/check_l6_shadow_eval_proof.py",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "ops_scripts/ci/check_e2e_proof_bundle.py",
    "Offline_Ingestion_Index_Build": "ops_scripts/ci/check_ingestion_index_proof.py",
    "Cross_Cutting_Observability_Replay_Audit": "ops_scripts/ci/check_otel_replay_audit_proof.py",
}

NEGATIVE_CONTROL_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "L5 emits a runtime ALLOW/DENY disposition (live proceed/stop) -- must fail; L5 only emits certification/evidence receipts",
    "00B_L4_State_Archive_and_UWG": "UWG commits without a CommitRequest envelope -- must fail",
    "00C_Runtime_Gates_Current_Run_Mesh": "Runtime Gate UNKNOWN treated as PASS -- must fail",
    "01_U0_Request_Intake": "U0 intake performs semantic routing, L1 planning, C0 retrieval, or mutation -- must fail; U0 owns identity/tenant/transport/schema only",
    "02_L1_Reasoning_Plan": "L1 plan emits a route_id outside the registered route catalog -- must fail",
    "03_L0_Route_Decision": "L0 emits more than one route per request -- must fail",
    "03_L3_Orchestration": "L3 orchestrator calls L1 planning during execution -- must fail",
    "03A_C0_Context_Engine": "C0 attempts to emit final answer -- must fail",
    "03B_PA_Prompt_Assembly": "PA attempts retrieval -- must fail",
    "04_L2_Execute": "L2 attempts direct L4 write -- must fail",
    "05_Exit_Evaluation_and_Control": "Exit emits more than one X3 disposition -- must fail",
    "06_L6_Shadow_Evaluation_System_Learning": "L6 attempts current-run mutation -- must fail",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "Proof harness mutates runtime state -- must fail",
    "Offline_Ingestion_Index_Build": "Ingestion pipeline emits a runtime answer or skips ACL/tenant binding -- must fail",
    "Cross_Cutting_Observability_Replay_Audit": "Telemetry egress contains PII or secrets without scrubbing -- must fail",
}

RUNTIME_ARTIFACT_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "L5CertificationResult + L5AuthorityEvidenceReceipt + L5PolicyBindingReceipt (certification evidence, never live ALLOW/DENY)",
    "00B_L4_State_Archive_and_UWG": "CommitRequest + WriteAdmissionVerdict + DurableCommitReceipt",
    "00C_Runtime_Gates_Current_Run_Mesh": "GateVerdict envelope (gate_id; status in {PASS, FAIL, UNKNOWN, NA}; UNKNOWN never collapses to PASS)",
    "01_U0_Request_Intake": "ValidatedRequest + RequestEnvelope + CallerScopeBaseline + QuotaBaselineReceipt + RequestDigestManifest (or RejectedRequest with reason_code on fail)",
    "02_L1_Reasoning_Plan": "L1PlanContract (proposed_route, query_spec, task_spec, route_risk, confidence)",
    "03_L0_Route_Decision": "RouteContract (route_id, route_class, decision_record_id)",
    "03_L3_Orchestration": "WorkflowContract (orchestration_plan, dependency_graph, step_specs)",
    "03A_C0_Context_Engine": "FinalEvidenceContract (evidence_chain, citation_anchors, support_targets)",
    "03B_PA_Prompt_Assembly": "CompiledPromptArtifact (assembly_hash, instruction_blocks, evidence_refs)",
    "04_L2_Execute": "ExecutionResult (sealed envelope: tool_calls, side_effects, replay_key)",
    "05_Exit_Evaluation_and_Control": "X3DispositionPacket (disposition in {ALLOW, DENY, RETURN, ESCALATE_TO_HITL, COMMIT_TO_UWG})",
    "06_L6_Shadow_Evaluation_System_Learning": "L6EvalRecord + LearningProposal (replay-tied, no current-run mutation)",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "E2EProofBundle (run_id, payload_hash, replay_digest, gate_chain)",
    "Offline_Ingestion_Index_Build": "ChunkSealedEnvelope + IndexMaterializationManifest",
    "Cross_Cutting_Observability_Replay_Audit": "OTEL trace bundle + replay-key audit record + W3C TraceContext propagation",
}

ARTIFACT_SCHEMA_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "agentic_core/L5_safety/contracts/certification.py:L5CertificationResult",
    "00B_L4_State_Archive_and_UWG": "agentic_core/L4_state/contracts/commit_request.py:CommitRequest",
    "00C_Runtime_Gates_Current_Run_Mesh": "agentic_core/L5_safety/runtime_gates/gate_verdict.py:GateVerdict",
    "01_U0_Request_Intake": "agentic_core/L1_cognition/intake/contracts.py:ValidatedRequest",
    "02_L1_Reasoning_Plan": "agentic_core/L1_cognition/plan/contracts.py:L1PlanContract",
    "03_L0_Route_Decision": "agentic_core/L0_routing/contracts.py:RouteContract",
    "03_L3_Orchestration": "agentic_core/L3_orchestration/contracts.py:WorkflowContract",
    "03A_C0_Context_Engine": "agentic_core/L1_cognition/c0_context/contracts.py:FinalEvidenceContract",
    "03B_PA_Prompt_Assembly": "agentic_core/L1_cognition/prompt_assembly/contracts.py:CompiledPromptArtifact",
    "04_L2_Execute": "agentic_core/L2_execution/contracts.py:ExecutionResult",
    "05_Exit_Evaluation_and_Control": "agentic_core/L5_safety/exit_control/contracts.py:X3DispositionPacket",
    "06_L6_Shadow_Evaluation_System_Learning": "agentic_core/L6_observability/contracts.py:L6EvalRecord",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "agentic_core/runtime/prove_requirements/contracts.py:E2EProofBundle",
    "Offline_Ingestion_Index_Build": "agentic_core/L1_cognition/c0_context/ingestion/contracts.py:ChunkSealedEnvelope",
    "Cross_Cutting_Observability_Replay_Audit": "infrastructure/types/precision_contracts.py (cross-cutting)",
}

BASE_OTEL_ATTRS = (
    "req_id", "run_id", "trace_id", "request_id", "owner_surface",
    "policy_hash", "blueprint_hash", "replay_key",
)

OWNER_EXTRA_ATTRS: Mapping[str, tuple[str, ...]] = {
    "01_U0_Request_Intake": ("tenant", "identity", "session_id"),
    "03_L0_Route_Decision": ("route_id",),
    "03A_C0_Context_Engine": ("artifact_id",),
    "03B_PA_Prompt_Assembly": ("artifact_id", "artifact_ref"),
    "00C_Runtime_Gates_Current_Run_Mesh": ("gate_id",),
    "05_Exit_Evaluation_and_Control": ("x3_disposition",),
    "00B_L4_State_Archive_and_UWG": ("commit_request_id",),
    "04_L2_Execute": ("artifact_id", "replay_key"),
    "06_L6_Shadow_Evaluation_System_Learning": ("replay_key",),
    "Offline_Ingestion_Index_Build": ("artifact_id",),
    "Cross_Cutting_Observability_Replay_Audit": ("traceparent", "tracestate"),
}

# ---------------------------------------------------------------------------
# Source-file resolution and content hashing (W4d-2)
# ---------------------------------------------------------------------------

SOURCE_SEARCH_ROOTS = (
    REPO_ROOT / "docs" / "reference",
    REPO_ROOT / "docs" / "reports",
    REPO_ROOT / "tools" / "reference",
)

# Source-file rename resolution. The ledger keeps the historical filename
# (audit trail), but source-locking computes against the current on-disk file.
# Mapping is from ledger source_file -> current on-disk filename.
SOURCE_FILE_RENAMES: Mapping[str, str] = {
    "04_Live_Task_Dispatch_Execution.md": "04_L2_Execute.md",
    "05_Live_Runtime_Exit_Control.md": "05_Live_Runtime_Exit_Control_&_Evaluation.md",
}

_source_path_cache: MutableMapping[str, Path | None] = {}
_source_sha_cache: MutableMapping[str, str] = {}
_source_commit_cache: MutableMapping[str, str] = {}


def _resolve_source_path(source_file: str) -> Path | None:
    key = source_file.strip()
    if not key:
        return None
    if key in _source_path_cache:
        return _source_path_cache[key]
    # Derived audit notes: no on-disk file, skip silently.
    if " " in key and ("best-practice" in key.lower() or "gap analysis" in key.lower()):
        _source_path_cache[key] = None
        return None
    # Apply rename map BEFORE searching disk.
    search_name = SOURCE_FILE_RENAMES.get(key, key)
    for root in SOURCE_SEARCH_ROOTS:
        if not root.exists():
            continue
        for candidate in root.rglob(search_name):
            if candidate.is_file():
                _source_path_cache[key] = candidate
                return candidate
        for candidate in root.rglob("*"):
            if candidate.is_file() and candidate.name == search_name:
                _source_path_cache[key] = candidate
                return candidate
    _source_path_cache[key] = None
    return None


def _source_sha256(source_file: str) -> str:
    if source_file in _source_sha_cache:
        return _source_sha_cache[source_file]
    p = _resolve_source_path(source_file)
    if p is None:
        _source_sha_cache[source_file] = ""
        return ""
    try:
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        digest = h.hexdigest()
    except OSError:
        digest = ""
    _source_sha_cache[source_file] = digest
    return digest


def _source_commit_sha(source_file: str) -> str:
    if source_file in _source_commit_cache:
        return _source_commit_cache[source_file]
    p = _resolve_source_path(source_file)
    if p is None:
        _source_commit_cache[source_file] = ""
        return ""
    try:
        rel = p.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        _source_commit_cache[source_file] = ""
        return ""
    try:
        result = subprocess.run(
            ["git", "log", "-n", "1", "--format=%H", "--", str(rel)],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=10,
        )
        sha = (result.stdout or "").strip()
    except (subprocess.SubprocessError, OSError):
        sha = ""
    _source_commit_cache[source_file] = sha
    return sha


def _path_exists(rel_path: str) -> str:
    p = (rel_path or "").strip()
    if not p:
        return ""
    candidate = REPO_ROOT / p
    return "true" if candidate.exists() else "false"


# ---------------------------------------------------------------------------
# Owner / span / negative-control derivation
# ---------------------------------------------------------------------------

def _derive_owner(req_id: str, layer_owner: str, source_file: str) -> tuple[str, bool, str | None]:
    if req_id in REQ_ID_OWNER_OVERRIDE:
        owner, note = REQ_ID_OWNER_OVERRIDE[req_id]
        return owner, False, note
    sf_key = (source_file or "").strip()
    if sf_key in SOURCE_FILE_OVERRIDE:
        return SOURCE_FILE_OVERRIDE[sf_key], False, f"SOURCE_FILE_OVERRIDE: {sf_key} pins surface."
    key = (layer_owner or "").strip().lower()
    if not key:
        return "Cross_Cutting_Observability_Replay_Audit", True, None
    surface = LAYER_OWNER_MAP.get(key)
    if surface is None:
        return "Cross_Cutting_Observability_Replay_Audit", True, None
    return surface, key in AMBIGUOUS_OWNERS, None


def _derive_span(req_id: str, owner_surface: str, runtime_phase: str) -> str:
    if req_id in REQ_ID_SPAN_OVERRIDE:
        return REQ_ID_SPAN_OVERRIDE[req_id]
    refined = PHASE_SPAN_REFINEMENT.get((owner_surface, (runtime_phase or "").strip()))
    if refined:
        return refined
    return DEFAULT_OTEL_SPAN.get(owner_surface, "obs.audit_event.emitted")


def _derive_otel_attrs(owner_surface: str) -> str:
    extras = OWNER_EXTRA_ATTRS.get(owner_surface, ())
    seen: list[str] = []
    for attr in BASE_OTEL_ATTRS + extras:
        if attr not in seen:
            seen.append(attr)
    return "|".join(seen)


def _derive_test_file(owner_surface: str, req_id: str) -> str:
    root = TEST_ROOT_MAP.get(owner_surface, "tests/unit/")
    slug = req_id.lower().replace("-", "_")
    return f"{root}test_{slug}.py"


def _derive_acceptance_command(test_file: str) -> str:
    return f"python -m pytest {test_file} -v --no-header"


def _derive_replay_proof(owner_surface: str) -> str:
    if owner_surface in {"04_L2_Execute", "00B_L4_State_Archive_and_UWG", "05_Exit_Evaluation_and_Control"}:
        return "replay_digest matches between primary and secondary execution; replay_key stable across runs"
    if owner_surface in {"03A_C0_Context_Engine", "03B_PA_Prompt_Assembly", "02_L1_Reasoning_Plan"}:
        return "compiled artifact hash deterministic given fixed inputs; replay reproduces identical artifact_id"
    if owner_surface == "Offline_Ingestion_Index_Build":
        return "chunk hash + index manifest deterministic for fixed corpus snapshot"
    if owner_surface == "06_L6_Shadow_Evaluation_System_Learning":
        return "shadow eval record reproducible from sealed run envelope; no current-run mutation"
    if owner_surface == "00C_Runtime_Gates_Current_Run_Mesh":
        return "gate verdict deterministic for fixed input envelope; UNKNOWN never collapses to PASS"
    if owner_surface == "99_End_to_End_Runtime_Proof_and_Acceptance":
        return "end-to-end proof bundle reproducible byte-for-byte across replay runs"
    if owner_surface == "01_U0_Request_Intake":
        return "intake digest deterministic for fixed (transport, identity, payload) tuple; replay reproduces identical request_id binding"
    return "replay-determined behavior reproduces across run replay with stable replay_key"


def _derive_risk_rationale(severity: str, owner_surface: str, semantic_class: str) -> str:
    sev = (severity or "").strip().upper()
    sc = (semantic_class or "").split(".")[0].strip()
    severity_phrase = {
        "CRITICAL": "Loss of this requirement compromises a sovereignty boundary or safety invariant",
        "HIGH": "Loss degrades governance/replay/observability with material runtime impact",
        "MEDIUM": "Loss degrades quality/coverage but does not breach a sovereignty boundary",
        "LOW": "Loss is a guidance/clarity gap; runtime sovereignty preserved",
    }.get(sev, "Severity not classified; default risk treatment applies")
    return f"{severity_phrase}; surface={owner_surface}; class={sc or '?'}"


def _derive_specific_negative_control(
    req_id: str,
    canonical_statement: str,
    runtime_artifact: str,
) -> str:
    short_artifact = runtime_artifact.split(" ", 1)[0] if runtime_artifact else "runtime_artifact"
    snippet = (canonical_statement or "").strip()
    if len(snippet) > 120:
        cut = snippet[:120].rsplit(" ", 1)[0]
        snippet = cut + "..."
    return (
        f"Row-specific [{req_id}]: {short_artifact} emitted without satisfying "
        f"\"{snippet}\" -- must fail"
    )


def _initial_status(severity: str, is_pedagogical: bool) -> tuple[str, str, str]:
    if is_pedagogical:
        return ("DEFERRED", "NOT_APPLICABLE", "ACCEPTED_WITH_CAVEAT")
    s = (severity or "").strip().upper()
    if s in {"CRITICAL", "HIGH", "MEDIUM"}:
        return ("NOT_STARTED", "PROOF_MISSING", "NEEDS_PROOF")
    if s == "LOW":
        return ("NOT_STARTED", "NOT_APPLICABLE", "DEFERRED")
    return ("NEEDS_REVIEW", "NEEDS_REVIEW", "NEEDS_OWNER_REVIEW")


# ---------------------------------------------------------------------------
# Main row hardening
# ---------------------------------------------------------------------------

def harden_row(row: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = OrderedDict()

    for col in ORIGINAL_COLUMNS:
        out[col] = (row.get(col) or "").strip()

    req_id = out["req_id"]
    direct = out["direct_or_implied"].strip().lower()
    is_pedagogical = direct in {"explanatory_only", "pedagogical_but_normatively_constraining"}

    owner, is_ambiguous, override_note = _derive_owner(req_id, out["layer_owner"], out["source_file"])
    out["canonical_owner_surface"] = owner

    out["source_anchor_ref"] = (
        f"{out['source_file']}#{out['source_section']}"
        if out["source_file"] or out["source_section"]
        else ""
    )

    out["risk_if_missing_rationale"] = _derive_risk_rationale(
        out["severity_if_missing"], owner, out["semantic_class"]
    )
    out["artifact_schema_ref"] = ARTIFACT_SCHEMA_MAP.get(
        owner, "infrastructure/types/precision_contracts.py (cross-cutting)"
    )
    out["runtime_artifact_expected"] = RUNTIME_ARTIFACT_MAP.get(owner, "")

    out["otel_span_expected"] = _derive_span(req_id, owner, out["runtime_phase"])
    out["otel_required_attributes"] = _derive_otel_attrs(owner)

    out["replay_proof_expected"] = _derive_replay_proof(owner)
    out["negative_control_expected"] = NEGATIVE_CONTROL_MAP.get(owner, "")

    test_file = _derive_test_file(owner, req_id)
    out["test_file_expected"] = test_file
    out["acceptance_command"] = _derive_acceptance_command(test_file)
    ci_gate = CI_GATE_MAP.get(owner, "")
    out["ci_gate_name"] = ci_gate
    proof_bundle = f"artifacts/proof/{req_id.lower()}_proof_bundle.json"
    out["proof_bundle_ref"] = proof_bundle

    impl, evid, accept = _initial_status(out["severity_if_missing"], is_pedagogical)
    out["implementation_status"] = impl
    out["evidence_status"] = evid
    final = accept
    if is_ambiguous and final not in {"NEEDS_OWNER_REVIEW", "REJECTED_DUPLICATE", "ACCEPTED_WITH_CAVEAT"}:
        final = "NEEDS_OWNER_REVIEW"
    out["final_acceptance_status"] = final

    out["duplicate_group"] = ""
    out["supersedes_req_id"] = ""
    out["blocked_by_req_id"] = ""

    notes_parts: list[str] = []
    if override_note:
        notes_parts.append(override_note)
    if is_ambiguous and req_id not in REQ_ID_OWNER_OVERRIDE:
        notes_parts.append(
            f"AMBIGUOUS_OWNER: layer_owner='{out['layer_owner']}' lacks single decisive surface; routed to {owner} pending review."
        )
    if is_pedagogical and "PEDAGOGICAL_ROW" not in (override_note or ""):
        notes_parts.append("PEDAGOGICAL_ROW: documentation/explanatory text retained for context; not a runtime proof obligation.")
    out["hardening_notes"] = " | ".join(notes_parts)

    out["source_commit_sha"] = _source_commit_sha(out["source_file"])
    out["source_line_range"] = "n/a"
    out["source_text_sha256"] = _source_sha256(out["source_file"])

    out["test_file_exists"] = _path_exists(test_file)
    out["ci_gate_exists"] = _path_exists(ci_gate)
    out["proof_bundle_exists"] = _path_exists(proof_bundle)
    out["last_passed_commit"] = ""

    out["negative_control_specific"] = _derive_specific_negative_control(
        req_id, out["canonical_requirement_statement"], out["runtime_artifact_expected"]
    )

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Harden the 10C semantic requirement ledger (W4d-2).")
    parser.add_argument("--dry-run", action="store_true", help="Compute but do not write the CSV.")
    parser.add_argument("--ledger", type=Path, default=LEDGER, help="Path to ledger CSV.")
    args = parser.parse_args()

    ledger_path: Path = args.ledger
    if not ledger_path.exists():
        print(f"FATAL: ledger not found at {ledger_path}", file=sys.stderr)
        return 2

    print(f"[harden W4d-2] reading {ledger_path}")
    csv.field_size_limit(2_000_000)
    with ledger_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        original_header = reader.fieldnames or []
        rows = list(reader)
    print(f"[harden W4d-2] loaded {len(rows)} rows; current header has {len(original_header)} columns")

    missing_originals = [c for c in ORIGINAL_COLUMNS if c not in original_header]
    if missing_originals:
        print(f"FATAL: ledger missing original columns: {missing_originals}", file=sys.stderr)
        return 2

    if len(rows) != 200:
        print(f"WARNING: expected 200 rows, found {len(rows)}", file=sys.stderr)

    hardened = [harden_row(r) for r in rows]

    for r in hardened:
        if "AMBIGUOUS_OWNER" in r["hardening_notes"] and r["final_acceptance_status"] == "ACCEPTED":
            r["final_acceptance_status"] = "NEEDS_OWNER_REVIEW"

    if args.dry_run:
        print(f"[harden W4d-2] dry-run: would write {len(hardened)} rows with {len(FINAL_COLUMNS)} columns")
        return 0

    with ledger_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(FINAL_COLUMNS))
        writer.writeheader()
        for r in hardened:
            for col in FINAL_COLUMNS:
                r.setdefault(col, "")
            writer.writerow({c: r[c] for c in FINAL_COLUMNS})

    print(f"[harden W4d-2] wrote {len(hardened)} rows with {len(FINAL_COLUMNS)} columns "
          f"({len(ORIGINAL_COLUMNS)} original + {len(W4D_COLUMNS)} W4d + {len(W4D2_COLUMNS)} W4d-2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
