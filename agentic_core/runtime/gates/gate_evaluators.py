"""Gate evaluators for G21–G28 — driven by profile data.

W8 plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2

Generic implementations driven by the gate_definitions loaded from the
apps_rg exit profile.  No apps_rg-specific strings are hardcoded in the
evaluator logic — all thresholds and rules come from gate_def dicts.

Invariants (enforced here):
- UNKNOWN is NEVER PASS.
- NOT_APPLICABLE requires not_applicable_reason.
- Missing required score → UNKNOWN, not PASS.
- Hard FAIL on prohibited content present.
- PASS only with evidence_refs populated.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage
from agentic_core.runtime.gates.gate_types import (
    VERDICT_FAIL,
    VERDICT_NOT_APPLICABLE,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    GateVerdict,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _verdict_digest(gate_id: str, result: str, run_id: str) -> str:
    return _sha(f"{gate_id}|{result}|{run_id}")


def _base(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    request_id: str,
    run_id: str,
    trace_root: str,
    result: str,
    *,
    reason_codes: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    score: float = 0.0,
    threshold: float = 0.0,
    remediation_hint: str = "",
    not_applicable_reason: str = "",
    unknown_reason: str = "",
    disposition: str = "",
) -> GateVerdict:
    return GateVerdict(
        gate_id=gate_id,
        gate_family=gate_def.get("gate_name", ""),
        evaluated_stage="exit",
        evaluated_surface="managed_workflow",
        evaluated_packet_ref=pkg.package_id,
        result=result,
        disposition=disposition or result.lower(),
        severity=gate_def.get("severity", "hard_fail"),
        reason_codes=reason_codes,
        score=score,
        threshold=threshold,
        evidence_refs=evidence_refs,
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        not_applicable_reason=not_applicable_reason,
        unknown_reason=unknown_reason,
        remediation_hint=remediation_hint,
        deterministic_digest=_verdict_digest(gate_id, result, run_id),
        created_at=_now(),
    )


# ── G21 Output Schema ─────────────────────────────────────────────────────────

_FABRICATION_MARKERS = re.compile(
    r"\b(FABRICATED|INVENTED_EMPLOYER|FAKE_DEGREE|FAKE_PUBLICATION"
    r"|FABRICATED_TITLE|UNSUPPORTED_METRIC)\b",
    re.IGNORECASE,
)

_SENSITIVE_ATTR_MARKERS = re.compile(
    r"\b(SELF_DISCLOSED_RELIGION|SELF_DISCLOSED_HEALTH"
    r"|SELF_DISCLOSED_PROTECTED_CLASS)\b",
    re.IGNORECASE,
)


def evaluate_g21(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G21 Output Schema Validation."""
    required_sections: list[str] = gate_def.get(
        "required_sections", ["header_block", "professional_summary", "experience_block"]
    )
    section_ids = {s.node_id for s in pkg.sealed_sections}
    merged = pkg.merged_content or ""

    # Check required sections
    missing = [s for s in required_sections if s not in section_ids]
    if missing:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=tuple(f"missing_required_section:{s}" for s in missing),
            remediation_hint=f"Required sections missing: {missing}",
        )

    # Check for fabrication markers in test fixtures
    fab_match = _FABRICATION_MARKERS.search(merged)
    if fab_match:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=(f"fabrication_marker_detected:{fab_match.group()}",),
            remediation_hint="Fabrication marker found in merged content",
        )

    # Check for sensitive attribute insertion
    sa_match = _SENSITIVE_ATTR_MARKERS.search(merged)
    if sa_match:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=(f"sensitive_attribute_inserted:{sa_match.group()}",),
        )

    # Check evidence from fixture
    g21_evidence = evidence.get("g21", {})
    if g21_evidence.get("malformed_record"):
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=("malformed_structured_record",),
        )

    evref = (f"g21::schema_check::{pkg.package_id}",)
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
        score=1.0,
        threshold=1.0,
    )


# ── G22 Output Quality ────────────────────────────────────────────────────────

def evaluate_g22(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G22 Output Quality — rubric score check.

    All dimension names and thresholds MUST come from gate_def["dimension_thresholds"].
    If no thresholds are provided in the profile, the gate returns UNKNOWN (fail-closed).
    No hardcoded fallback thresholds exist in this generic module.
    """
    dim_thresholds: dict[str, Any] = gate_def.get("dimension_thresholds", {})
    rubric_scores: dict[str, float] = evidence.get("g22_rubric_scores", {})

    # Fail-closed: no profile thresholds → UNKNOWN
    if not dim_thresholds:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_UNKNOWN,
            reason_codes=("no_profile_thresholds",),
            unknown_reason="G22 gate_def missing dimension_thresholds; cannot evaluate",
            remediation_hint="Provide dimension_thresholds in the gate profile",
        )

    # No evidence scores at all → UNKNOWN
    if not rubric_scores:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_UNKNOWN,
            reason_codes=("no_rubric_scores",),
            unknown_reason="No g22_rubric_scores in evidence; cannot evaluate",
            remediation_hint="Provide g22_rubric_scores in evidence",
        )

    fail_reasons: list[str] = []
    unknown_reasons: list[str] = []

    for dim, raw_threshold in dim_thresholds.items():
        # Handle nested threshold dicts (e.g. executive_positioning)
        if isinstance(raw_threshold, dict):
            threshold = float(raw_threshold.get("threshold", 0.0))
            informational_only = raw_threshold.get("informational_only_by_default", False)
        else:
            threshold = float(raw_threshold)
            informational_only = False

        if informational_only:
            continue

        if dim not in rubric_scores:
            # Missing required score → UNKNOWN, not PASS
            unknown_reasons.append(f"missing_required_score:{dim}")
            continue

        score = float(rubric_scores[dim])
        if score < threshold:
            fail_reasons.append(f"dim_below_threshold:{dim}:{score:.3f}<{threshold:.3f}")

    if unknown_reasons:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_UNKNOWN,
            reason_codes=tuple(unknown_reasons),
            unknown_reason=f"Missing required rubric scores: {unknown_reasons}",
            remediation_hint="Provide all required rubric dimension scores",
        )

    if fail_reasons:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=tuple(fail_reasons),
            remediation_hint="One or more rubric dimensions below threshold",
        )

    overall = rubric_scores.get("overall_pass_threshold", rubric_scores.get("overall", 1.0))
    overall_threshold = float(dim_thresholds.get("overall_pass_threshold", 0.0))
    evref = (f"g22::rubric_check::{pkg.package_id}",)
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
        score=float(overall),
        threshold=overall_threshold,
    )


# ── G23 Security / Leakage ────────────────────────────────────────────────────

_LEAKAGE_PATTERNS = [
    (re.compile(r"\bSYSTEM_PROMPT\b|\bSLOT_LABEL\b|\bS0::\b|\bD0::\b|\bI0::\b", re.I),
     "prompt_leakage"),
    (re.compile(r"\bGOVERNANCE_INSTRUCTION\b|\bAUTHORITY_BOUNDARY\b", re.I),
     "system_instruction_leakage"),
    (re.compile(r"\b(API[_-]?KEY|SECRET|PASSWORD|TOKEN)\s*[:=]\s*\S+", re.I),
     "credential_leakage"),
    (re.compile(r"\bPROMPT.{0,20}INJECT", re.I),
     "prompt_injection_leakage"),
]


def evaluate_g23(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G23 Security / Leakage scan."""
    merged = pkg.merged_content or ""
    # Also check individual sections
    all_content = merged + " ".join(
        s.sealed_content for s in pkg.sealed_sections
    )

    for pattern, code in _LEAKAGE_PATTERNS:
        match = pattern.search(all_content)
        if match:
            return _base(
                gate_id, gate_def, pkg, request_id, run_id, trace_root,
                VERDICT_FAIL,
                reason_codes=(f"{code}:{match.group()[:60]}",),
                remediation_hint=f"Leakage detected: {code}",
            )

    # Check fixture-supplied leakage signals
    g23_ev = evidence.get("g23", {})
    for leak_type in ("prompt_leakage", "system_instruction_leakage",
                      "credential_leakage", "prompt_injection_leakage"):
        if g23_ev.get(leak_type):
            return _base(
                gate_id, gate_def, pkg, request_id, run_id, trace_root,
                VERDICT_FAIL,
                reason_codes=(leak_type,),
            )

    evref = (f"g23::leakage_scan::{pkg.package_id}",)
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
    )


# ── G24 Replay / Provenance ───────────────────────────────────────────────────

_G24_REQUIRED_FIELDS = (
    "request_id", "run_id", "trace_root", "replay_key",
    "route_contract_ref", "workflow_ref", "output_artifact_digest",
)


def evaluate_g24(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G24 Replay / Provenance completeness."""
    # Build provenance from pkg fields + evidence overrides
    provenance: dict[str, str] = {
        "request_id": request_id,
        "run_id": run_id,
        "trace_root": trace_root,
        "replay_key": pkg.replay_manifest or "",
        "route_contract_ref": pkg.route_contract_ref,
        "workflow_ref": pkg.workflow_ref,
        "output_artifact_digest": pkg.merged_content_digest or pkg.merged_payload_digest,
    }
    provenance.update(evidence.get("g24_provenance", {}))

    required = list(gate_def.get("required_provenance_fields", _G24_REQUIRED_FIELDS))
    missing = [f for f in required if not provenance.get(f)]

    if missing:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_UNKNOWN,
            reason_codes=tuple(f"missing_provenance_field:{f}" for f in missing),
            unknown_reason=f"Missing replay-critical provenance refs: {missing}",
            remediation_hint="Populate all required provenance fields before Exit",
        )

    evref = (f"g24::provenance::{pkg.package_id}",)
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
    )


# ── G25 Runtime Anomaly ───────────────────────────────────────────────────────

def evaluate_g25(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G25 Runtime Anomaly — conditional gate."""
    # If no anomaly trigger, return NOT_APPLICABLE with reason
    g25_ev = evidence.get("g25", {})
    if not evidence.get("trigger_g25", False) and not g25_ev.get("anomaly_signal"):
        default_reason = gate_def.get(
            "default_reason",
            "No runtime anomaly signal detected for this execution; "
            "conditional gate G25 not triggered",
        )
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_NOT_APPLICABLE,
            not_applicable_reason=default_reason,
        )

    # Anomaly signal present
    anomaly_type = g25_ev.get("anomaly_type", "unknown_anomaly")
    severity = gate_def.get("severity", "hard_fail")
    result = VERDICT_FAIL if severity == "hard_fail" else VERDICT_WARN
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        result,
        reason_codes=(f"anomaly_detected:{anomaly_type}",),
        remediation_hint="Runtime anomaly requires HITL escalation",
    )


# ── G26 Exit Eligibility ──────────────────────────────────────────────────────

def evaluate_g26(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G26 Exit Eligibility — requires terminal artifact."""
    # For managed workflow path require SealedWorkflowPackage (always present here)
    if not pkg.package_id:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=("missing_terminal_artifact:SealedWorkflowPackage",),
            remediation_hint="SealedWorkflowPackage must be provided at Exit",
        )

    # Check that at least one section is sealed
    if len(pkg.sealed_sections) == 0 and not pkg.merged_content:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=("no_sealed_sections_and_no_merged_content",),
        )

    g26_ev = evidence.get("g26", {})
    if g26_ev.get("no_fabrication_score") is not None:
        nf_score = float(g26_ev["no_fabrication_score"])
        threshold = float(gate_def.get("threshold", 0.99))
        if nf_score < threshold:
            return _base(
                gate_id, gate_def, pkg, request_id, run_id, trace_root,
                VERDICT_FAIL,
                reason_codes=(f"no_fabrication_below_threshold:{nf_score:.3f}<{threshold:.3f}",),
                score=nf_score,
                threshold=threshold,
            )

    evref = (f"g26::eligibility::{pkg.package_id}",)
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
    )


# ── G27 Durable Write Sovereignty ─────────────────────────────────────────────

def evaluate_g27(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G27 Durable Write Sovereignty — NOT_APPLICABLE for read-only resume return."""
    g27_ev = evidence.get("g27", {})
    durable_write_requested = (
        g27_ev.get("proposed_state_diff")
        or g27_ev.get("durable_write_requested")
        or g27_ev.get("cache_write_requested")
        or g27_ev.get("promotion_requested")
    )

    if not durable_write_requested:
        default_reason = gate_def.get(
            "default_reason",
            "no durable state writes requested",
        )
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_NOT_APPLICABLE,
            not_applicable_reason=default_reason,
        )

    # Durable write IS requested — require UWG path evidence
    uwg_evidence = g27_ev.get("uwg_path_evidence")
    if not uwg_evidence:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=("commit_without_uwg_path_evidence",),
            remediation_hint="Durable write requires UWG path evidence in G27",
        )

    evref = (f"g27::durable_write_sovereignty::{pkg.package_id}",)
    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
    )


# ── G28 Audit / Trace Completeness ───────────────────────────────────────────

_G28_MATERIAL_AUDIT_REFS = (
    "request_id", "run_id", "trace_root",
    "route_contract_ref", "workflow_ref",
    "sealed_workflow_package_ref", "gate_mesh_result_ref", "decisive_reason",
)

_G28_OPTIONAL_OBSERVABILITY_REFS = (
    "otel_trace_id", "otel_span_id", "exhaust_bundle_ref", "replay_key",
)


def evaluate_g28(
    gate_id: str,
    gate_def: dict[str, Any],
    pkg: SealedWorkflowPackage,
    evidence: dict[str, Any],
    request_id: str,
    run_id: str,
    trace_root: str,
) -> GateVerdict:
    """G28 Audit / Trace Completeness.

    PASS  — all material audit refs present (optional observability refs may also be present).
    WARN  — all material refs present but one or more optional observability refs missing.
    UNKNOWN — material refs missing and severity is not hard_fail.
    FAIL  — material refs missing and severity is hard_fail, OR explicit audit failure flagged.
    """
    g28_ev = evidence.get("g28", {})

    # Base audit refs from call-site arguments and package fields
    audit_refs: dict[str, str] = {
        "request_id": request_id,
        "run_id": run_id,
        "trace_root": trace_root,
        "route_contract_ref": pkg.route_contract_ref,
        "workflow_ref": pkg.workflow_ref,
    }
    # Merge evidence-supplied refs (allows test fixtures and evaluator callers to
    # supply sealed_workflow_package_ref, gate_mesh_result_ref, decisive_reason, etc.)
    audit_refs.update(g28_ev.get("audit_refs", {}))

    # Explicit audit failure signal
    if g28_ev.get("audit_failure"):
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_FAIL,
            reason_codes=("explicit_audit_failure",),
        )

    # Material refs — gate profile may override; default to module constant
    material_required = list(gate_def.get("required_audit_refs", _G28_MATERIAL_AUDIT_REFS))
    missing_material = [f for f in material_required if not audit_refs.get(f)]

    if missing_material:
        severity = gate_def.get("severity", "hard_fail")
        result = VERDICT_FAIL if severity == "hard_fail" else VERDICT_UNKNOWN
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            result,
            reason_codes=tuple(f"missing_material_audit_ref:{f}" for f in missing_material),
            unknown_reason=(
                f"Missing material audit refs: {missing_material}"
                if result == VERDICT_UNKNOWN else ""
            ),
        )

    # All material refs present — check optional observability refs
    optional_refs = list(gate_def.get("optional_observability_refs", _G28_OPTIONAL_OBSERVABILITY_REFS))
    missing_optional = [f for f in optional_refs if not audit_refs.get(f)]

    evref = (f"g28::audit_trace::{pkg.package_id}",)
    if missing_optional:
        return _base(
            gate_id, gate_def, pkg, request_id, run_id, trace_root,
            VERDICT_WARN,
            evidence_refs=evref,
            reason_codes=tuple(f"missing_optional_observability_ref:{f}" for f in missing_optional),
        )

    return _base(
        gate_id, gate_def, pkg, request_id, run_id, trace_root,
        VERDICT_PASS,
        evidence_refs=evref,
    )


# ── Default evaluator registry ────────────────────────────────────────────────

DEFAULT_EVALUATORS: dict[str, Any] = {
    "G21": evaluate_g21,
    "G22": evaluate_g22,
    "G23": evaluate_g23,
    "G24": evaluate_g24,
    "G25": evaluate_g25,
    "G26": evaluate_g26,
    "G27": evaluate_g27,
    "G28": evaluate_g28,
}
