"""v6 §5.0 + §5.1 — Pre-flight inputs validation and normalization.

Implements:
- §5.0 *Immediate fail before grading if missing* — 7 hard receipt-field checks
- §5.1 N1 source classification
- §5.1 N2 normalize artifact -> ExitReviewPacket
- §5.1 N3 bind run identity (cross-field consistency)
- §5.1 N4 declare disposition candidates
- §5.1 N5 attach live control signals
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    SourceType,
)

# Spec §5.0 - immediate fail codes (lookup map: receipt field -> reason code)
IMMEDIATE_FAIL_CODES: dict[str, str] = {
    "policy_hash": "POLICY_HASH_MISSING",
    "replay_key": "REPLAY_KEY_MISSING",
    "route_contract": "ROUTE_CONTRACT_MISSING",
    "terminal_class": "TERMINAL_CLASS_MISSING",
    "sandbox_envelope": "SANDBOX_SCOPE_MISSING",  # required for action
    "capability_token": "CAPABILITY_TOKEN_MISSING",  # required for tool/model/action
    "evidence_contract": "EVIDENCE_CONTRACT_MISSING",  # required for grounded answer
}


@dataclass(slots=True)
class PreflightFailure:
    """Single pre-flight failure (one per missing/invalid field)."""

    field: str
    reason_code: str
    detail: str = ""


# ---- 5.1 N1 ----


def classify_source(receipts: dict[str, Any]) -> SourceType:
    """5.1 N1 — classify the runtime source of the sealed work.

    Reads ``receipts['source_type']`` if explicitly set; otherwise infers from
    available shape clues.
    """
    explicit = receipts.get("source_type", "")
    if explicit:
        try:
            return SourceType(explicit)
        except ValueError as exc:
            raise ValueError(
                f"unknown source_type {explicit!r}; valid: {[s.value for s in SourceType]}"
            ) from exc
    # Infer from shape clues.
    if receipts.get("workflow_package"):
        return SourceType.L3_WORKFLOW_PACKAGE
    if receipts.get("cache_hit_kind") == "exact":
        return SourceType.RET_CACHE_EXACT
    if receipts.get("cache_hit_kind") == "semantic":
        return SourceType.RET_CACHE_SEMANTIC
    if receipts.get("cache_hit_kind") == "fallback":
        return SourceType.RET_FALLBACK
    if receipts.get("hitl_recleared"):
        return SourceType.HITL_RECLEARED_PACKET
    return SourceType.L2_SEALED_ARTIFACT


# ---- 5.0 immediate-fail validation ----


def validate_required_receipts(receipts: dict[str, Any]) -> list[PreflightFailure]:
    """§5.0 *Immediate fail before grading if missing*.

    Returns empty list on success. Conditional fields (sandbox_envelope,
    capability_token, evidence_contract) only fire when the corresponding
    use-case applies.
    """
    failures: list[PreflightFailure] = []

    # Always required.
    for field, code in (
        ("policy_hash", IMMEDIATE_FAIL_CODES["policy_hash"]),
        ("replay_key", IMMEDIATE_FAIL_CODES["replay_key"]),
    ):
        if not receipts.get(field):
            failures.append(PreflightFailure(field=field, reason_code=code))

    # route_contract may be the dict itself or a route_contract sub-mapping.
    rc = receipts.get("route_contract")
    if not rc or (isinstance(rc, dict) and not any(rc.values())):
        failures.append(
            PreflightFailure(
                field="route_contract",
                reason_code=IMMEDIATE_FAIL_CODES["route_contract"],
            )
        )

    if not receipts.get("terminal_class"):
        failures.append(
            PreflightFailure(
                field="terminal_class",
                reason_code=IMMEDIATE_FAIL_CODES["terminal_class"],
            )
        )

    # Conditional: sandbox_envelope required for action-class terminals.
    terminal = str(receipts.get("terminal_class", ""))
    is_action = terminal in {"with_state_diff", "external_action", "durable_write", "action"}
    if is_action and not receipts.get("sandbox_envelope"):
        failures.append(
            PreflightFailure(
                field="sandbox_envelope",
                reason_code=IMMEDIATE_FAIL_CODES["sandbox_envelope"],
                detail=f"required for terminal_class={terminal!r}",
            )
        )

    # Conditional: capability_token required when tool/model/action invoked.
    has_tool_or_model = bool(
        receipts.get("exec_trace", {}).get("tool_calls")
        or receipts.get("exec_trace", {}).get("model_calls")
        or is_action
    )
    if has_tool_or_model and not receipts.get("capability_token"):
        failures.append(
            PreflightFailure(
                field="capability_token",
                reason_code=IMMEDIATE_FAIL_CODES["capability_token"],
                detail="required for tool/model/action invocation",
            )
        )

    # Conditional: evidence_contract required for grounded answer.
    needs_grounding = bool(receipts.get("grounding_required") or receipts.get("evidence_bundle"))
    if needs_grounding and not receipts.get("final_evidence_contract"):
        failures.append(
            PreflightFailure(
                field="evidence_contract",
                reason_code=IMMEDIATE_FAIL_CODES["evidence_contract"],
                detail="required for grounded answer",
            )
        )

    # Spec §5.6 H4 hard law: a HITL_RECLEARED_PACKET re-entering the runtime
    # MUST carry positive L5 re-clearance evidence. A modified packet that
    # arrives without ``hitl_packet.l5_cleared = True`` is treated as
    # smuggled-authority and fails closed before grading. This closes the
    # "human modification slips into X3D/X3C without re-clearance" bypass.
    declared_source = receipts.get("source_type") or ""
    if str(declared_source).upper() == "HITL_RECLEARED_PACKET" or receipts.get("hitl_recleared"):
        hitl = receipts.get("hitl_packet") or {}
        if not hitl.get("l5_cleared"):
            failures.append(
                PreflightFailure(
                    field="hitl_packet.l5_cleared",
                    reason_code="RECLEARANCE_MISSING",
                    detail=(
                        "HITL_RECLEARED_PACKET re-entry requires hitl_packet.l5_cleared=True per §5.6 H4"
                    ),
                )
            )

    return failures


# ---- 5.1 N3 ----


def bind_run_identity(receipts: dict[str, Any]) -> list[PreflightFailure]:
    """5.1 N3 — verify cross-field identity coherence."""
    failures: list[PreflightFailure] = []
    request_id = receipts.get("request_id", "")
    trace_root = receipts.get("trace_root", "")
    run_id = receipts.get("run_id", "")
    route_id = receipts.get("route_id") or receipts.get("route_contract", {}).get("route_id", "")
    replay_key = receipts.get("replay_key", "")

    # Each field must be present and non-empty for identity binding.
    for fld, val in (
        ("request_id", request_id),
        ("trace_root", trace_root),
        ("run_id", run_id),
        ("route_id", route_id),
        ("replay_key", replay_key),
    ):
        if not val:
            failures.append(
                PreflightFailure(
                    field=fld,
                    reason_code="IDENTITY_BINDING_INCOMPLETE",
                    detail=f"missing {fld}",
                )
            )

    # No hidden reroute after L0 contract emission.
    rc = receipts.get("route_contract", {}) or {}
    if route_id and rc.get("route_id") and route_id != rc.get("route_id"):
        failures.append(
            PreflightFailure(
                field="route_id",
                reason_code="HIDDEN_REROUTE_DETECTED",
                detail=f"top-level route_id={route_id!r} != route_contract.route_id={rc.get('route_id')!r}",
            )
        )

    # policy_hash and blueprint_hash must agree with route_contract snapshot.
    for hash_field in ("policy_hash", "blueprint_hash"):
        top = receipts.get(hash_field, "")
        rc_val = rc.get(hash_field, "")
        if top and rc_val and top != rc_val:
            failures.append(
                PreflightFailure(
                    field=hash_field,
                    reason_code="POLICY_HASH_MISMATCH"
                    if hash_field == "policy_hash"
                    else "BLUEPRINT_HASH_MISMATCH",
                    detail=f"top={top!r} contract={rc_val!r}",
                )
            )

    return failures


# ---- 5.1 N2 + N5 — full normalization ----


def normalize_to_packet(receipts: dict[str, Any]) -> ExitReviewPacket:
    """5.1 N2 (normalize) + N5 (attach live control signals).

    Lossless mapping from raw runtime receipts to a single ``ExitReviewPacket``.
    Lineage (``source_type``) is preserved, never flattened away.
    """
    source_type = classify_source(receipts)
    rc = receipts.get("route_contract", {}) or {}
    return ExitReviewPacket(
        source_type=source_type,
        request_id=str(receipts.get("request_id", "")),
        run_id=str(receipts.get("run_id", "")),
        session_id=str(receipts.get("session_id", "")),
        trace_root=str(receipts.get("trace_root", "")),
        route_id=str(receipts.get("route_id") or rc.get("route_id", "")),
        policy_hash=str(receipts.get("policy_hash", "")),
        blueprint_hash=str(receipts.get("blueprint_hash", "")),
        prompt_hash=str(receipts.get("prompt_hash", "")),
        replay_key=str(receipts.get("replay_key", "")),
        compliance_hash=str(receipts.get("compliance_hash", "")),
        manifest_hash=str(receipts.get("manifest_hash", "")),
        hmac_sig=str(receipts.get("hmac_sig", "")),
        route_contract=dict(rc),
        sandbox_envelope=dict(receipts.get("sandbox_envelope", {}) or {}),
        capability_token=dict(receipts.get("capability_token", {}) or {}),
        provider_lane=str(receipts.get("provider_lane", "")),
        cost_tier=str(receipts.get("cost_tier", "")),
        slo_slice=dict(receipts.get("slo_slice", {}) or {}),
        timeout_ms=int(receipts.get("timeout_ms", 0)),
        budget_counters=dict(receipts.get("budget_counters", {}) or {}),
        terminal_class=str(receipts.get("terminal_class", "")),
        exec_trace=dict(receipts.get("exec_trace", {}) or {}),
        state_diff=dict(receipts.get("state_diff", {}) or {}),
        write_intent_class=str(receipts.get("write_intent_class", "")),
        evidence_bundle=dict(receipts.get("evidence_bundle", {}) or {}),
        final_evidence_contract=dict(receipts.get("final_evidence_contract", {}) or {}),
        prompt_assembly_status=dict(receipts.get("prompt_assembly_status", {}) or {}),
        compiled_prompt_artifact=dict(receipts.get("compiled_prompt_artifact", {}) or {}),
        output=dict(receipts.get("output", {}) or {}),
        validation_counters=dict(receipts.get("validation_counters", {}) or {}),
        retry_counters=dict(receipts.get("retry_counters", {}) or {}),
        repair_counters=dict(receipts.get("repair_counters", {}) or {}),
        trajectory_snapshot=dict(receipts.get("trajectory_snapshot", {}) or {}),
        grader_composition=dict(receipts.get("grader_composition", {}) or {}),
        track_label=str(receipts.get("track_label", "production")),
        support_score=float(receipts.get("support_score", 0.0)),
        confidence=float(receipts.get("confidence", 0.0)),
        abstain_flags=list(receipts.get("abstain_flags", []) or []),
        contradiction_flags=list(receipts.get("contradiction_flags", []) or []),
        otel_spans=dict(receipts.get("otel_spans", {}) or {}),
        timing_offsets=dict(receipts.get("timing_offsets", {}) or {}),
        anomaly_flags=list(receipts.get("anomaly_flags", []) or []),
        hitl_packet=dict(receipts.get("hitl_packet", {}) or {}),
        # 5.1 N5 — live control signals
        bus_d_signals=list(receipts.get("bus_d_signals", []) or []),
        bus_e_signals=list(receipts.get("bus_e_signals", []) or []),
        replay_guard_violations=list(receipts.get("replay_guard_violations", []) or []),
        isolation_anomalies=list(receipts.get("isolation_anomalies", []) or []),
        drift_warnings=list(receipts.get("drift_warnings", []) or []),
        # APPS-DOM runtime binding — carry app-specific contract refs onto the
        # packet so the pipeline's app_specific_evaluator call at §4b can bind
        # without requiring each caller to pre-populate the packet. Reads
        # top-level receipt first, then falls back to route_contract. Missing
        # on both sides preserves the "" default and evaluator returns
        # bound=False (existing non-app-bound behavior).
        app_id=str(receipts.get("app_id") or rc.get("app_id", "")),
        task_class=str(receipts.get("task_class") or rc.get("task_class", "")),
        rubric_ref=str(receipts.get("rubric_ref") or rc.get("rubric_ref", "")),
        threshold_profile_ref=str(
            receipts.get("threshold_profile_ref")
            or rc.get("threshold_profile_ref", "")
        ),
        grader_roster_ref=str(
            receipts.get("grader_roster_ref")
            or rc.get("grader_roster_ref", "")
        ),
    )


__all__ = [
    "IMMEDIATE_FAIL_CODES",
    "PreflightFailure",
    "bind_run_identity",
    "classify_source",
    "normalize_to_packet",
    "validate_required_receipts",
]
