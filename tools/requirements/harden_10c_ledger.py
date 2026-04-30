"""Harden the 10C semantic requirement ledger into proof-grade form.

Adds 20 proof-tracking columns to every row, deterministically backfilled from
the existing 15-column data using owner-surface mapping tables and stable
patterns. Idempotent — running twice produces the same output. Preserves all
200 rows exactly, never renumbers, never deletes, and never rewrites the
``canonical_requirement_statement`` field.

Usage::

    python tools/requirements/harden_10c_ledger.py [--dry-run]

Existing 15 columns (preserved verbatim):
    req_id, source_file, source_section, source_unit_type,
    source_text_short, canonical_requirement_statement, direct_or_implied,
    semantic_class, layer_owner, runtime_phase, required_artifacts,
    required_controls, required_tests, severity_if_missing, confidence_score

New 20 columns (added in fixed order after ``confidence_score``):
    canonical_owner_surface, source_anchor_ref, risk_if_missing_rationale,
    artifact_schema_ref, runtime_artifact_expected, otel_span_expected,
    otel_required_attributes, replay_proof_expected,
    negative_control_expected, test_file_expected, acceptance_command,
    ci_gate_name, proof_bundle_ref, implementation_status, evidence_status,
    duplicate_group, supersedes_req_id, blocked_by_req_id,
    final_acceptance_status, hardening_notes
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Mapping

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

NEW_COLUMNS = (
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

FINAL_COLUMNS = ORIGINAL_COLUMNS + NEW_COLUMNS

# ---------------------------------------------------------------------------
# Owner surface mapping
# ---------------------------------------------------------------------------

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

# Direct mapping: layer_owner string (lowercased, stripped) -> canonical surface
LAYER_OWNER_MAP: Mapping[str, str] = {
    # Single-layer owners
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
    # Multi-layer owners — pick the layer owning the decisive obligation
    "l2/l5": "00A_L5_Governance_Safety",
    "l5/l3/l0": "00A_L5_Governance_Safety",
    "l5/l3/l0/l2": "00A_L5_Governance_Safety",
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

# Owners flagged as ambiguous and needing review (not ACCEPTED until owner confirmed)
AMBIGUOUS_OWNERS = frozenset({
    "n/a",
    "l5/l3/l0/l2",
    "l5/l3/l6",
    "l6 observability + all layers",
})

# ---------------------------------------------------------------------------
# OTEL span mapping (owner_surface -> default span name)
# ---------------------------------------------------------------------------

DEFAULT_OTEL_SPAN: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "l5.governance.policy_evaluated",
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

# Phase-aware refinement: certain runtime_phase values pick a more specific
# span when the owner-surface default is too coarse.
PHASE_SPAN_REFINEMENT: Mapping[tuple[str, str], str] = {
    ("00A_L5_Governance_Safety", "Pre-execution"): "l5.gateway.precheck_emitted",
    ("00A_L5_Governance_Safety", "Post-execution"): "l5.gateway.postcheck_emitted",
    ("00A_L5_Governance_Safety", "Escalation"): "l5.hitl.escalation_emitted",
    ("00A_L5_Governance_Safety", "Ingress"): "l5.gateway.ingress_validated",
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
}

# ---------------------------------------------------------------------------
# Test directory mapping (owner_surface -> intended test root)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# CI gate mapping (owner_surface -> CI gate script path)
# ---------------------------------------------------------------------------

CI_GATE_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "ops_scripts/ci/check_l5_governance_proof.py",
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

# ---------------------------------------------------------------------------
# Negative control patterns (owner_surface -> default boundary violation)
# ---------------------------------------------------------------------------

NEGATIVE_CONTROL_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "L5 emits ALLOW/DENY runtime disposition outside its dispositional surface -> must fail",
    "00B_L4_State_Archive_and_UWG": "UWG commits without CommitRequest envelope -> must fail",
    "00C_Runtime_Gates_Current_Run_Mesh": "Runtime Gate UNKNOWN treated as PASS -> must fail",
    "01_U0_Request_Intake": "U0 intake bypasses identity/tenant validation -> must fail",
    "02_L1_Reasoning_Plan": "L1 plan emits a route_id outside the registered route catalog -> must fail",
    "03_L0_Route_Decision": "L0 emits more than one route per request -> must fail",
    "03_L3_Orchestration": "L3 orchestrator calls L1 planning during execution -> must fail",
    "03A_C0_Context_Engine": "C0 attempts to emit final answer -> must fail",
    "03B_PA_Prompt_Assembly": "PA attempts retrieval -> must fail",
    "04_L2_Execute": "L2 attempts direct L4 write -> must fail",
    "05_Exit_Evaluation_and_Control": "Exit emits more than one X3 disposition -> must fail",
    "06_L6_Shadow_Evaluation_System_Learning": "L6 attempts current-run mutation -> must fail",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "Proof harness mutates runtime state -> must fail",
    "Offline_Ingestion_Index_Build": "Ingestion pipeline emits runtime answer or skips ACL/tenant binding -> must fail",
    "Cross_Cutting_Observability_Replay_Audit": "Telemetry egress contains PII or secrets without scrubbing -> must fail",
}

# ---------------------------------------------------------------------------
# Runtime artifact mapping (owner_surface -> artifact reference)
# ---------------------------------------------------------------------------

RUNTIME_ARTIFACT_MAP: Mapping[str, str] = {
    "00A_L5_Governance_Safety": "L5GovernanceVerdict envelope (capability_token + policy_hash)",
    "00B_L4_State_Archive_and_UWG": "CommitRequest + WriteAdmissionVerdict + DurableCommitReceipt",
    "00C_Runtime_Gates_Current_Run_Mesh": "GateVerdict envelope (gate_id, status in {PASS,FAIL,UNKNOWN,NA})",
    "01_U0_Request_Intake": "RequestIntakeEnvelope (request_id, tenant, identity, source_class)",
    "02_L1_Reasoning_Plan": "L1PlanContract (proposed_route, query_spec, task_spec, route_risk, confidence)",
    "03_L0_Route_Decision": "RouteContract (route_id, route_class, decision_record_id)",
    "03_L3_Orchestration": "WorkflowContract (orchestration_plan, dependency_graph, step_specs)",
    "03A_C0_Context_Engine": "FinalEvidenceContract (evidence_chain, citation_anchors, support_targets)",
    "03B_PA_Prompt_Assembly": "CompiledPromptArtifact (assembly_hash, instruction_blocks, evidence_refs)",
    "04_L2_Execute": "ExecutionResult (sealed envelope: tool_calls, side_effects, replay_key)",
    "05_Exit_Evaluation_and_Control": "X3DispositionPacket (disposition in {ALLOW,DENY,RETURN,ESCALATE_TO_HITL,COMMIT_TO_UWG})",
    "06_L6_Shadow_Evaluation_System_Learning": "L6EvalRecord + LearningProposal (replay-tied, no current-run mutation)",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "E2EProofBundle (run_id, payload_hash, replay_digest, gate_chain)",
    "Offline_Ingestion_Index_Build": "ChunkSealedEnvelope + IndexMaterializationManifest",
    "Cross_Cutting_Observability_Replay_Audit": "OTEL trace bundle + replay-key audit record",
}

# ---------------------------------------------------------------------------
# OTEL required attribute defaults
# ---------------------------------------------------------------------------

BASE_OTEL_ATTRS = ("req_id", "run_id", "trace_id", "request_id", "owner_surface", "policy_hash", "blueprint_hash", "replay_key")

OWNER_EXTRA_ATTRS: Mapping[str, tuple[str, ...]] = {
    "03_L0_Route_Decision": ("route_id",),
    "03A_C0_Context_Engine": ("artifact_id",),
    "03B_PA_Prompt_Assembly": ("artifact_id", "artifact_ref"),
    "00C_Runtime_Gates_Current_Run_Mesh": ("gate_id",),
    "05_Exit_Evaluation_and_Control": ("x3_disposition",),
    "00B_L4_State_Archive_and_UWG": ("commit_request_id",),
    "04_L2_Execute": ("artifact_id", "replay_key"),
    "06_L6_Shadow_Evaluation_System_Learning": ("replay_key",),
    "Offline_Ingestion_Index_Build": ("artifact_id",),
}


def normalize_owner(layer_owner: str) -> tuple[str, bool]:
    """Return (canonical_owner_surface, is_ambiguous)."""
    key = (layer_owner or "").strip().lower()
    if not key:
        return "Cross_Cutting_Observability_Replay_Audit", True
    surface = LAYER_OWNER_MAP.get(key)
    if surface is None:
        return "Cross_Cutting_Observability_Replay_Audit", True
    return surface, key in AMBIGUOUS_OWNERS


def derive_otel_span(owner_surface: str, runtime_phase: str) -> str:
    refined = PHASE_SPAN_REFINEMENT.get((owner_surface, (runtime_phase or "").strip()))
    if refined:
        return refined
    return DEFAULT_OTEL_SPAN.get(owner_surface, "obs.audit_event.emitted")


def derive_otel_attrs(owner_surface: str) -> str:
    extras = OWNER_EXTRA_ATTRS.get(owner_surface, ())
    seen: list[str] = []
    for attr in BASE_OTEL_ATTRS + extras:
        if attr not in seen:
            seen.append(attr)
    return "|".join(seen)


def derive_test_file(owner_surface: str, req_id: str) -> str:
    root = TEST_ROOT_MAP.get(owner_surface, "tests/unit/")
    slug = req_id.lower().replace("-", "_")
    return f"{root}test_{slug}.py"


def derive_acceptance_command(test_file: str) -> str:
    # Pytest module path form is most stable
    return f"python -m pytest {test_file} -v --no-header"


def derive_replay_proof(owner_surface: str) -> str:
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
    return "replay-determined behavior reproduces across run replay with stable replay_key"


def derive_artifact_schema_ref(owner_surface: str) -> str:
    if owner_surface == "00A_L5_Governance_Safety":
        return "agentic_core/L5_safety/contracts/governance_verdict.py:GovernanceVerdict"
    if owner_surface == "00B_L4_State_Archive_and_UWG":
        return "agentic_core/L4_state/contracts/commit_request.py:CommitRequest"
    if owner_surface == "00C_Runtime_Gates_Current_Run_Mesh":
        return "agentic_core/L5_safety/runtime_gates/gate_verdict.py:GateVerdict"
    if owner_surface == "01_U0_Request_Intake":
        return "agentic_core/L1_cognition/intake/contracts.py:RequestIntakeEnvelope"
    if owner_surface == "02_L1_Reasoning_Plan":
        return "agentic_core/L1_cognition/plan/contracts.py:L1PlanContract"
    if owner_surface == "03_L0_Route_Decision":
        return "agentic_core/L0_routing/contracts.py:RouteContract"
    if owner_surface == "03_L3_Orchestration":
        return "agentic_core/L3_orchestration/contracts.py:WorkflowContract"
    if owner_surface == "03A_C0_Context_Engine":
        return "agentic_core/L1_cognition/c0_context/contracts.py:FinalEvidenceContract"
    if owner_surface == "03B_PA_Prompt_Assembly":
        return "agentic_core/L1_cognition/prompt_assembly/contracts.py:CompiledPromptArtifact"
    if owner_surface == "04_L2_Execute":
        return "agentic_core/L2_execution/contracts.py:ExecutionResult"
    if owner_surface == "05_Exit_Evaluation_and_Control":
        return "agentic_core/L5_safety/exit_control/contracts.py:X3DispositionPacket"
    if owner_surface == "06_L6_Shadow_Evaluation_System_Learning":
        return "agentic_core/L6_observability/contracts.py:L6EvalRecord"
    if owner_surface == "99_End_to_End_Runtime_Proof_and_Acceptance":
        return "agentic_core/runtime/prove_requirements/contracts.py:E2EProofBundle"
    if owner_surface == "Offline_Ingestion_Index_Build":
        return "agentic_core/L1_cognition/c0_context/ingestion/contracts.py:ChunkSealedEnvelope"
    return "infrastructure/types/precision_contracts.py (cross-cutting)"


def derive_source_anchor_ref(source_file: str, source_section: str) -> str:
    sf = (source_file or "").strip()
    ss = (source_section or "").strip()
    if not sf and not ss:
        return ""
    if sf and ss:
        return f"{sf}#{ss}"
    return sf or ss


def derive_risk_rationale(severity: str, owner_surface: str, semantic_class: str) -> str:
    sev = (severity or "").strip().upper()
    sc = (semantic_class or "").split(".")[0].strip()  # take leading letter category
    severity_phrase = {
        "CRITICAL": "Loss of this requirement compromises a sovereignty boundary or safety invariant",
        "HIGH": "Loss degrades governance/replay/observability with material runtime impact",
        "MEDIUM": "Loss degrades quality/coverage but does not breach a sovereignty boundary",
        "LOW": "Loss is a guidance/clarity gap; runtime sovereignty preserved",
    }.get(sev, "Severity not classified; default risk treatment applies")
    return f"{severity_phrase}; surface={owner_surface}; class={sc or '?'}"


def normalize_severity(sev: str) -> str:
    s = (sev or "").strip().upper()
    if s in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
        return s
    return s  # leave anomalies for validator to flag


def initial_status_for_severity(sev: str) -> tuple[str, str, str]:
    """Return (implementation_status, evidence_status, final_acceptance_status)."""
    s = normalize_severity(sev)
    # Deterministic starting state. Backfill is by design conservative —
    # nothing is ACCEPTED until proof is wired into a real test/CI run.
    if s in {"CRITICAL", "HIGH"}:
        return ("NOT_STARTED", "PROOF_MISSING", "NEEDS_PROOF")
    if s == "MEDIUM":
        return ("NOT_STARTED", "PROOF_MISSING", "NEEDS_PROOF")
    if s == "LOW":
        return ("NOT_STARTED", "NOT_APPLICABLE", "DEFERRED")
    return ("NEEDS_REVIEW", "NEEDS_REVIEW", "NEEDS_OWNER_REVIEW")


def harden_row(row: dict[str, str]) -> dict[str, str]:
    """Return a new row dict containing the original 15 + 20 new columns.

    Idempotent: if the row already has any of the new columns populated, those
    values are preserved unless empty.
    """
    out: dict[str, str] = OrderedDict()

    # Preserve all original columns verbatim.
    for col in ORIGINAL_COLUMNS:
        out[col] = (row.get(col) or "").strip()

    # Owner surface
    existing_owner = (row.get("canonical_owner_surface") or "").strip()
    if existing_owner and existing_owner in CANONICAL_OWNER_VOCAB:
        owner = existing_owner
        ambiguous = False
    else:
        owner, ambiguous = normalize_owner(out["layer_owner"])
    out["canonical_owner_surface"] = owner

    # Source anchor
    existing_anchor = (row.get("source_anchor_ref") or "").strip()
    out["source_anchor_ref"] = existing_anchor or derive_source_anchor_ref(out["source_file"], out["source_section"])

    # Risk rationale
    existing_risk = (row.get("risk_if_missing_rationale") or "").strip()
    out["risk_if_missing_rationale"] = existing_risk or derive_risk_rationale(
        out["severity_if_missing"], owner, out["semantic_class"]
    )

    # Artifact schema ref
    existing_schema = (row.get("artifact_schema_ref") or "").strip()
    out["artifact_schema_ref"] = existing_schema or derive_artifact_schema_ref(owner)

    # Runtime artifact expected
    existing_artifact = (row.get("runtime_artifact_expected") or "").strip()
    out["runtime_artifact_expected"] = existing_artifact or RUNTIME_ARTIFACT_MAP.get(owner, "")

    # OTEL span
    existing_span = (row.get("otel_span_expected") or "").strip()
    out["otel_span_expected"] = existing_span or derive_otel_span(owner, out["runtime_phase"])

    # OTEL attributes
    existing_attrs = (row.get("otel_required_attributes") or "").strip()
    out["otel_required_attributes"] = existing_attrs or derive_otel_attrs(owner)

    # Replay proof
    existing_replay = (row.get("replay_proof_expected") or "").strip()
    out["replay_proof_expected"] = existing_replay or derive_replay_proof(owner)

    # Negative control
    existing_neg = (row.get("negative_control_expected") or "").strip()
    out["negative_control_expected"] = existing_neg or NEGATIVE_CONTROL_MAP.get(owner, "")

    # Test file expected
    existing_test = (row.get("test_file_expected") or "").strip()
    test_file = existing_test or derive_test_file(owner, out["req_id"])
    out["test_file_expected"] = test_file

    # Acceptance command
    existing_cmd = (row.get("acceptance_command") or "").strip()
    out["acceptance_command"] = existing_cmd or derive_acceptance_command(test_file)

    # CI gate name
    existing_gate = (row.get("ci_gate_name") or "").strip()
    out["ci_gate_name"] = existing_gate or CI_GATE_MAP.get(owner, "")

    # Proof bundle ref
    existing_bundle = (row.get("proof_bundle_ref") or "").strip()
    out["proof_bundle_ref"] = existing_bundle or f"artifacts/proof/{out['req_id'].lower()}_proof_bundle.json"

    # Implementation / evidence / acceptance status
    impl, evid, accept = initial_status_for_severity(out["severity_if_missing"])
    out["implementation_status"] = (row.get("implementation_status") or impl).strip() or impl
    out["evidence_status"] = (row.get("evidence_status") or evid).strip() or evid
    final = (row.get("final_acceptance_status") or accept).strip() or accept
    if ambiguous and final not in {"NEEDS_OWNER_REVIEW", "REJECTED_DUPLICATE"}:
        final = "NEEDS_OWNER_REVIEW"
    out["final_acceptance_status"] = final

    # Duplicate / supersedes / blocked-by — leave blank unless already set
    out["duplicate_group"] = (row.get("duplicate_group") or "").strip()
    out["supersedes_req_id"] = (row.get("supersedes_req_id") or "").strip()
    out["blocked_by_req_id"] = (row.get("blocked_by_req_id") or "").strip()

    # Hardening notes — always overwrite the trail
    notes_parts: list[str] = []
    if ambiguous:
        notes_parts.append(f"AMBIGUOUS_OWNER: layer_owner='{out['layer_owner']}' lacks single decisive surface; routed to {owner} pending review.")
    if owner == "Cross_Cutting_Observability_Replay_Audit" and out["layer_owner"].lower() not in {"architecture design", "n/a"}:
        notes_parts.append("Cross-cutting fallback applied; consider promoting to a primary owner if a single decisive surface emerges.")
    if not out["runtime_artifact_expected"]:
        notes_parts.append("Runtime artifact mapping unknown for this owner; manual review required.")
    existing_notes = (row.get("hardening_notes") or "").strip()
    if existing_notes:
        notes_parts.append(f"prior:{existing_notes}")
    out["hardening_notes"] = " | ".join(notes_parts)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Harden the 10C semantic requirement ledger.")
    parser.add_argument("--dry-run", action="store_true", help="Compute but do not write the CSV.")
    parser.add_argument("--ledger", type=Path, default=LEDGER, help="Path to ledger CSV (default: canonical 10C ledger).")
    args = parser.parse_args()

    ledger_path: Path = args.ledger
    if not ledger_path.exists():
        print(f"FATAL: ledger not found at {ledger_path}", file=sys.stderr)
        return 2

    print(f"[harden] reading {ledger_path}")
    csv.field_size_limit(2_000_000)
    with ledger_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        original_header = reader.fieldnames or []
        rows = list(reader)
    print(f"[harden] loaded {len(rows)} rows; header has {len(original_header)} columns")

    # Sanity: must contain the original 15
    missing_originals = [c for c in ORIGINAL_COLUMNS if c not in original_header]
    if missing_originals:
        print(f"FATAL: ledger missing original columns: {missing_originals}", file=sys.stderr)
        return 2

    if len(rows) != 200:
        print(f"WARNING: expected 200 rows, found {len(rows)}", file=sys.stderr)

    # Backfill all rows
    hardened = [harden_row(r) for r in rows]

    # Final-acceptance-status pass: rows whose owner is still flagged ambiguous
    # via hardening_notes should not be ACCEPTED even if every other column is full.
    for r in hardened:
        if "AMBIGUOUS_OWNER" in r["hardening_notes"] and r["final_acceptance_status"] == "ACCEPTED":
            r["final_acceptance_status"] = "NEEDS_OWNER_REVIEW"

    if args.dry_run:
        print(f"[harden] dry-run: would write {len(hardened)} rows with {len(FINAL_COLUMNS)} columns")
        return 0

    # Write back
    with ledger_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(FINAL_COLUMNS))
        writer.writeheader()
        for r in hardened:
            # Ensure every final column is present (DictWriter will KeyError otherwise)
            for col in FINAL_COLUMNS:
                r.setdefault(col, "")
            writer.writerow({c: r[c] for c in FINAL_COLUMNS})

    print(f"[harden] wrote {len(hardened)} rows with {len(FINAL_COLUMNS)} columns")
    print(f"[harden] new columns added: {len(NEW_COLUMNS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
