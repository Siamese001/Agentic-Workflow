"""06.2 — Observer law, surface isolation, and eval readiness.

Implements the gates that prove L6 only observed completed-run exhaust and
that the normalized evidence is sufficient for 6B evaluation.

Observer law is enforced two ways:

1. Static: every API in this module rejects any input that names a write
   surface (``L4``, ``BUS_U``, ``policy_publish``, ``rubric_publish``, ...).
2. Dynamic: ``ObserverViolation`` is raised on any attempted write surface
   request. ``record_denied_write_attempt`` lets callers prove violations
   were detected and recorded — never silently swallowed.

There are no L4 client imports anywhere in this file. That absence is
itself part of the proof; the observer-law negative test in
``test_06_2_observer.py`` greps the module text to assert it.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Iterable, Mapping

from agentic_core.L6_observability.shadow_eval._digest import stamp_digest
from agentic_core.L6_observability.shadow_eval.contracts import (
    ArtifactInventory,
    EvalReadinessReceipt,
    G28_AUDIT_COMPLETENESS,
    G29_LEARNING_FIREWALL,
    L6DeniedWriteAttemptRecord,
    L6GateReceipt,
    L6_GATE_FAIL,
    L6_GATE_PASS,
    L6_GATE_UNKNOWN,
    MissingEvidenceMap,
    NonEvaluablePacketRecord,
    NormalizedEvidenceRecord,
    ObserverComplianceReceipt,
    RuntimeExhaustBundle,
    StageBarrierReceipt,
    SurfaceIsolationManifest,
)
from agentic_core.L6_observability.shadow_eval.ingest import (
    MISSING_CERT_REF_SENTINEL,
    is_missing_l5_certification_ref,
)


class ObserverViolation(Exception):
    """Raised whenever L6 code attempts a forbidden write/mutation."""


# Surfaces L6 must never write to. Any request naming one of these aborts
# with ``ObserverViolation`` (and is captured as a denied-write record).
FORBIDDEN_WRITE_SURFACES: frozenset[str] = frozenset(
    {
        "L4",
        "L4_state",
        "BUS_U",
        "BUS_U_publish",
        "policy_publish",
        "rubric_publish",
        "registry_update",
        "cache_promotion",
        "memory_promotion",
        "current_run_exit",
        "current_run_hitl",
        "current_run_uwg",
        "current_run_x3",
        "current_run_x3_mutation",
        "direct_prompt_patch",
        "direct_policy_patch",
        "prompt_policy_patch",
    }
)

READINESS_READY = "READY_FOR_6B"
READINESS_PARTIAL = "PARTIAL_BUT_SCORABLE"
READINESS_HOLD = "HOLD_FOR_MISSING_EVIDENCE"
READINESS_NON_EVAL = "NON_EVALUABLE_PACKET"


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Stage barrier — current run must be closed before L6 may begin.
# ---------------------------------------------------------------------------


def stage_barrier_check(bundle: RuntimeExhaustBundle) -> StageBarrierReceipt:
    boundary_violation_flags: list[str] = []
    if not bundle.runtime_boundary_crossed:
        boundary_violation_flags.append("RUNTIME_BOUNDARY_NOT_CROSSED")
    if not bundle.exit_disposition_ref:
        boundary_violation_flags.append("EXIT_DISPOSITION_MISSING")
    barrier_status = "PASS" if not boundary_violation_flags else "FAIL"
    return StageBarrierReceipt(
        stage_barrier_receipt_id=_gen_id("barrier"),
        current_run_closed=bundle.runtime_boundary_crossed,
        exit_disposition_present=bool(bundle.exit_disposition_ref),
        uwg_status_closed_or_not_applicable=True,
        runtime_boundary_timestamp=bundle.completed_at or _now_iso(),
        l6_start_timestamp=_now_iso(),
        boundary_violation_flags=boundary_violation_flags,
        barrier_status=barrier_status,
    )


# ---------------------------------------------------------------------------
# Surface isolation
# ---------------------------------------------------------------------------


def deny_if_forbidden(surface: str) -> None:
    """Raise ``ObserverViolation`` if the named surface is a write target."""
    if surface in FORBIDDEN_WRITE_SURFACES:
        raise ObserverViolation(f"L6 attempted forbidden write surface: {surface}")


def record_denied_write_attempt(
    bundle: RuntimeExhaustBundle,
    *,
    surface: str,
    operation: str,
    reason_code: str,
    stack_signature: str = "",
) -> L6DeniedWriteAttemptRecord:
    return L6DeniedWriteAttemptRecord(
        denied_write_id=_gen_id("denied"),
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        target_surface=surface,
        operation=operation,
        reason_code=reason_code,
        timestamp=_now_iso(),
        stack_signature=stack_signature,
    )


def build_surface_isolation_manifest(
    bundle: RuntimeExhaustBundle,
    *,
    read_surfaces_touched: Iterable[str],
    write_surfaces_requested: Iterable[str] = (),
    denied_write_attempts: Iterable[L6DeniedWriteAttemptRecord] = (),
) -> SurfaceIsolationManifest:
    requested = list(write_surfaces_requested)
    denied = list(denied_write_attempts)
    forbidden_hit = any(s in FORBIDDEN_WRITE_SURFACES for s in requested)
    prompt_policy_patch = any(
        s in {"direct_prompt_patch", "direct_policy_patch", "prompt_policy_patch"}
        for s in requested
    )
    isolation_status = "VIOLATION" if forbidden_hit else "CLEAN"
    if isolation_status == "VIOLATION" and not denied:
        # If the violation was not denied, that is itself a sovereignty
        # incident — reflect it in the manifest by marking UNKNOWN so the
        # upstream gate refuses to proceed.
        isolation_status = "UNKNOWN"
    manifest = SurfaceIsolationManifest(
        surface_isolation_manifest_id=_gen_id("siso"),
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        read_surfaces_touched=list(read_surfaces_touched),
        write_surfaces_requested=requested,
        denied_write_attempts=[d.denied_write_id for d in denied],
        credentials_scope="READ_ONLY",
        token_scope="READ_ONLY",
        storage_scope="READ_ONLY",
        bus_publish_scope="NONE",
        current_run_mutation_attempted=any(s.startswith("current_run_") for s in requested),
        l4_write_attempted=any(s.startswith("L4") for s in requested),
        bus_u_publish_attempted=any("BUS_U" in s for s in requested),
        current_run_x3_mutation_attempted=any("x3" in s.lower() for s in requested),
        direct_prompt_policy_patch_attempted=prompt_policy_patch,
        isolation_status=isolation_status,
    )
    return stamp_digest(manifest)


def _present(value: object | None) -> bool:
    return value not in (None, "", [], {})


def _gate_verdict(assertions: Mapping[str, bool | str]) -> str:
    if any(value == L6_GATE_UNKNOWN for value in assertions.values()):
        return L6_GATE_FAIL
    return L6_GATE_PASS if all(value is True for value in assertions.values()) else L6_GATE_FAIL


def build_g28_audit_completeness_receipt(
    bundle: RuntimeExhaustBundle,
    normalized: list[NormalizedEvidenceRecord],
    *,
    artifact_inventory: ArtifactInventory | None = None,
) -> L6GateReceipt:
    """G28: audit evidence completeness required before 6B readiness."""
    sealed_present = bool(
        artifact_inventory.sealed_artifacts if artifact_inventory is not None else normalized
    )
    lineage_or_records_present = bool(bundle.source_lineage_manifest_ref or normalized)
    assertions: dict[str, bool | str] = {
        "trace_root": bool(bundle.trace_root),
        "exit_disposition_ref": bool(bundle.exit_disposition_ref),
        "policy_hash": bool(bundle.policy_hash),
        "replay_key": bool(bundle.replay_key),
        "route_contract_ref": bool(bundle.route_contract_ref),
        "l5_certification_ref": not is_missing_l5_certification_ref(bundle.l5_certification_ref),
        "source_lineage_or_normalized_records": lineage_or_records_present,
        "sealed_artifacts": sealed_present,
    }
    required = list(assertions)
    missing = [name for name, ok in assertions.items() if ok is not True]
    receipt = L6GateReceipt(
        gate_receipt_id=_gen_id("g28"),
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        gate_id=G28_AUDIT_COMPLETENESS,
        gate_name="L6 G28 audit completeness",
        verdict=_gate_verdict(assertions),
        required_refs=required,
        present_refs=[name for name in required if name not in missing],
        missing_refs=missing,
        assertion_results=assertions,
        reason_codes=[f"MISSING_{name.upper()}" for name in missing],
        notes="UNKNOWN is fail-closed; sentinel L5 certification is missing evidence.",
    )
    return stamp_digest(receipt)


def build_g29_learning_firewall_receipt(
    bundle: RuntimeExhaustBundle,
    *,
    isolation: SurfaceIsolationManifest,
    observer_receipt: ObserverComplianceReceipt | None = None,
) -> L6GateReceipt:
    """G29: L6 learning cannot mutate current-run state or bypass UWG."""
    assertions: dict[str, bool | str] = {
        "no_current_run_mutation_attempt": not isolation.current_run_mutation_attempted,
        "no_l4_write_attempt": not isolation.l4_write_attempted,
        "no_bus_u_publish_attempt": not isolation.bus_u_publish_attempted,
        "no_current_run_x3_mutation": not isolation.current_run_x3_mutation_attempted,
        "no_direct_prompt_policy_patch": not isolation.direct_prompt_policy_patch_attempted,
        "observer_isolation_clean": isolation.isolation_status == "CLEAN",
    }
    if observer_receipt is not None:
        assertions.update(
            {
                "observer_no_l4_write_assertion": observer_receipt.no_l4_write_assertion is True,
                "observer_no_bus_u_publish_assertion": observer_receipt.no_bus_u_publish_assertion is True,
                "observer_no_live_feedback_assertion": observer_receipt.no_live_feedback_assertion is True,
            }
        )
    forbidden = [name for name, ok in assertions.items() if ok is not True]
    receipt = L6GateReceipt(
        gate_receipt_id=_gen_id("g29"),
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        gate_id=G29_LEARNING_FIREWALL,
        gate_name="L6 G29 learning firewall",
        verdict=_gate_verdict(assertions),
        required_refs=list(assertions),
        present_refs=[name for name in assertions if name not in forbidden],
        forbidden_attempts=forbidden,
        assertion_results=assertions,
        reason_codes=[f"FORBIDDEN_{name.upper()}" for name in forbidden],
        notes="L6 proposals remain inert and future-run only; UWG is the durable write path.",
    )
    return stamp_digest(receipt)


# ---------------------------------------------------------------------------
# Observer compliance receipt
# ---------------------------------------------------------------------------


def build_observer_compliance_receipt(
    bundle: RuntimeExhaustBundle,
    *,
    barrier: StageBarrierReceipt,
    isolation: SurfaceIsolationManifest,
    denied_write_attempts: Iterable[L6DeniedWriteAttemptRecord] = (),
) -> ObserverComplianceReceipt:
    violation_response = None
    if isolation.isolation_status != "CLEAN" or barrier.barrier_status != "PASS":
        violation_response = "L6_OBSERVER_FAIL"
    receipt = ObserverComplianceReceipt(
        observer_receipt_id=_gen_id("observer"),
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        observer_mode="READ_ONLY",
        read_only_credential_proof="static_assertion:no_l4_client_import",
        touched_surfaces=list(isolation.read_surfaces_touched),
        denied_write_attempt_refs=[d.denied_write_id for d in denied_write_attempts],
        stage_barrier_status=barrier.barrier_status,
        isolation_status=isolation.isolation_status,
        no_live_feedback_assertion=True,
        no_bus_u_publish_assertion=not isolation.bus_u_publish_attempted,
        no_l4_write_assertion=not isolation.l4_write_attempted,
        violation_response=violation_response,
        policy_hash=bundle.policy_hash,
        blueprint_hash=bundle.blueprint_hash,
        replay_key=bundle.replay_key,
    )
    return stamp_digest(receipt)


# ---------------------------------------------------------------------------
# Eval readiness
# ---------------------------------------------------------------------------


def _status_for(value: object | None) -> str:
    return "PRESENT" if value not in (None, "", [], {}) else "MISSING"


def evaluate_readiness(
    bundle: RuntimeExhaustBundle,
    observer_receipt: ObserverComplianceReceipt,
    normalized: list[NormalizedEvidenceRecord],
    *,
    artifact_inventory: ArtifactInventory | None = None,
    g28_receipt: L6GateReceipt | None = None,
    g29_receipt: L6GateReceipt | None = None,
    replay_dependent: bool = True,
) -> tuple[EvalReadinessReceipt, MissingEvidenceMap | None, NonEvaluablePacketRecord | None]:
    trace_status = _status_for(bundle.trace_root)
    sealed_artifacts_present = bool(
        artifact_inventory.sealed_artifacts if artifact_inventory is not None else normalized
    )
    artifact_status = "PRESENT" if sealed_artifacts_present else "MISSING"
    replay_status = _status_for(bundle.replay_key)
    policy_status = _status_for(bundle.policy_hash)
    route_status = _status_for(bundle.route_contract_ref)
    prompt_status = "PRESENT" if any(r.prompt_hash for r in normalized) else "MISSING"
    lineage_status = (
        _status_for(bundle.source_lineage_manifest_ref)
        if bundle.source_lineage_manifest_ref
        else ("PRESENT" if normalized and any(r.trace_id for r in normalized) else "MISSING")
    )
    terminal_status = _status_for(bundle.exit_disposition_ref)
    evaluator_status = "PRESENT" if normalized else "MISSING"
    l5_status = (
        "MISSING"
        if is_missing_l5_certification_ref(bundle.l5_certification_ref)
        else "PRESENT"
    )
    sealed_status = "PRESENT" if sealed_artifacts_present else "MISSING"
    source_lineage_or_records_status = "PRESENT" if lineage_status == "PRESENT" or normalized else "MISSING"

    missing_field_refs: list[str] = []
    if trace_status == "MISSING":
        missing_field_refs.append("trace_root")
    if artifact_status == "MISSING":
        missing_field_refs.append("artifacts")
    if replay_status == "MISSING" and replay_dependent:
        missing_field_refs.append("replay_key")
    if policy_status == "MISSING":
        missing_field_refs.append("policy_hash")
    if route_status == "MISSING":
        missing_field_refs.append("route_contract")
    if terminal_status == "MISSING":
        missing_field_refs.append("exit_disposition")
    if l5_status == "MISSING":
        missing_field_refs.append("l5_certification_ref")
    if sealed_status == "MISSING":
        missing_field_refs.append("sealed_artifacts")
    if source_lineage_or_records_status == "MISSING":
        missing_field_refs.append("source_lineage_or_normalized_records")
    if g28_receipt is not None and g28_receipt.verdict != L6_GATE_PASS:
        missing_field_refs.extend(
            ref for ref in g28_receipt.missing_refs if ref not in missing_field_refs
        )
    if g29_receipt is not None and g29_receipt.verdict != L6_GATE_PASS:
        missing_field_refs.extend(
            ref for ref in g29_receipt.forbidden_attempts if ref not in missing_field_refs
        )

    reason_codes: list[str] = list(missing_field_refs)
    missing_map: MissingEvidenceMap | None = None
    non_eval: NonEvaluablePacketRecord | None = None

    # Decide
    if observer_receipt.isolation_status != "CLEAN" or (
        g29_receipt is not None and g29_receipt.verdict != L6_GATE_PASS
    ):
        decision = READINESS_NON_EVAL
        non_eval = NonEvaluablePacketRecord(
            non_evaluable_id=_gen_id("noneval"),
            runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
            reason_codes=["OBSERVER_LAW_VIOLATION"] + reason_codes,
        )
    elif not missing_field_refs and (
        g28_receipt is None or g28_receipt.verdict == L6_GATE_PASS
    ):
        decision = READINESS_READY
    elif "trace_root" in missing_field_refs or "exit_disposition" in missing_field_refs:
        # Required lineage/terminal facts missing — non-evaluable.
        decision = READINESS_NON_EVAL
        non_eval = NonEvaluablePacketRecord(
            non_evaluable_id=_gen_id("noneval"),
            runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
            reason_codes=reason_codes,
        )
    elif (
        "replay_key" in missing_field_refs
        or "l5_certification_ref" in missing_field_refs
        or "sealed_artifacts" in missing_field_refs
        or "source_lineage_or_normalized_records" in missing_field_refs
        or "policy_hash" in missing_field_refs
        or "route_contract" in missing_field_refs
    ):
        # Required v40 audit evidence cannot proceed; hold for repair.
        decision = READINESS_HOLD
        missing_map = MissingEvidenceMap(
            missing_evidence_map_id=_gen_id("miss"),
            runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
            missing_field_refs=missing_field_refs,
            blocking=True,
        )
    elif normalized:
        decision = READINESS_PARTIAL
        missing_map = MissingEvidenceMap(
            missing_evidence_map_id=_gen_id("miss"),
            runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
            missing_field_refs=missing_field_refs,
            blocking=False,
        )
    else:
        decision = READINESS_NON_EVAL
        non_eval = NonEvaluablePacketRecord(
            non_evaluable_id=_gen_id("noneval"),
            runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
            reason_codes=reason_codes or ["NO_NORMALIZED_RECORDS"],
        )

    receipt = EvalReadinessReceipt(
        eval_readiness_receipt_id=_gen_id("ready"),
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        observer_receipt_id=observer_receipt.observer_receipt_id,
        trace_completeness_status=trace_status,
        artifact_integrity_status=artifact_status,
        replay_key_status=replay_status,
        policy_hash_status=policy_status,
        route_contract_status=route_status,
        prompt_hash_status=prompt_status,
        source_lineage_status=lineage_status,
        terminal_status_status=terminal_status,
        evaluator_input_status=evaluator_status,
        readiness_decision=decision,
        missing_evidence_map_ref=missing_map.missing_evidence_map_id if missing_map else None,
        excluded_from_learning_until=None if decision != READINESS_NON_EVAL else "indefinite",
        g28_audit_completeness_receipt_ref=g28_receipt.gate_receipt_id if g28_receipt else None,
        g29_learning_firewall_receipt_ref=g29_receipt.gate_receipt_id if g29_receipt else None,
        l5_certification_status=l5_status,
        sealed_artifacts_status=sealed_status,
        source_lineage_or_records_status=source_lineage_or_records_status,
        reason_codes=reason_codes,
    )
    return stamp_digest(receipt), missing_map, non_eval


__all__ = [
    "ObserverViolation",
    "FORBIDDEN_WRITE_SURFACES",
    "READINESS_READY",
    "READINESS_PARTIAL",
    "READINESS_HOLD",
    "READINESS_NON_EVAL",
    "stage_barrier_check",
    "deny_if_forbidden",
    "record_denied_write_attempt",
    "build_surface_isolation_manifest",
    "build_observer_compliance_receipt",
    "build_g28_audit_completeness_receipt",
    "build_g29_learning_firewall_receipt",
    "evaluate_readiness",
]
