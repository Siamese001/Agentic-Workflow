"""Canonical apps_rg L2 E1-E5 runtime over signed upstream authority.

This module composes the existing v4 execution stages with the signed
``RouteContract``/``ValidatedRequest`` authority packet. Product callers use
this entrypoint; the CPA-only envelope remains a compatibility/test surface.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from apps_rg.runtime.bindings.l2_authority import (
    L2AuthorityError,
    build_signed_execution_packet,
    freeze_execution_room,
    validate_execution_packet,
)
from apps_rg.runtime.bindings.l2_receipt_bundle import (
    build_authority_rejection_seal,
    compute_attempt_output_digest,
    finalize_content_addressed_bundle,
    write_authority_rejection_bundle,
)


def _authority_error(code: str, reason: str, field_name: str = "") -> L2AuthorityError:
    return L2AuthorityError(code, reason, field_name=field_name)


def _execution_prompt(prompt_artifact: Any, packet: Any, frozen_room: Any) -> Any:
    """Bind E3-visible metadata to the verified packet without changing prompt text."""
    audit_refs = tuple(getattr(prompt_artifact, "audit_refs", ()) or ()) + (
        f"l2_packet:{packet.packet_digest}",
        f"frozen_execution_room:{frozen_room.room_digest}",
    )
    snapshot_refs = tuple(getattr(prompt_artifact, "snapshot_refs", ()) or ()) + (
        packet.packet_digest,
        frozen_room.room_digest,
    )
    return replace(
        prompt_artifact,
        target_provider=packet.canonical_provider,
        target_model=packet.target_model,
        allowed_tools=packet.allowed_tools,
        allowed_models=packet.allowed_models,
        allowed_networks=packet.allowed_networks,
        allowed_file_roots=packet.allowed_file_roots,
        sandbox_required=packet.sandbox_required,
        egress_policy_ref=packet.egress_policy_ref,
        max_tokens=int(packet.budget.get("max_tokens", 0)),
        replay_key=packet.replay_key,
        compilation_hash=packet.prompt_hash,
        audit_refs=tuple(dict.fromkeys(audit_refs)),
        snapshot_refs=tuple(dict.fromkeys(snapshot_refs)),
    )


def _bind_authority_to_validation(validation_output: Any, packet: Any, gate_receipts: Any) -> Any:
    """Replace permissive legacy work-order metadata with packet-derived authority."""
    gate_refs = tuple(receipt.ref for receipt in gate_receipts)
    if validation_output.validation_status != "PASS" or validation_output.approved_work_order is None:
        return replace(validation_output, gate_refs=gate_refs)

    from apps_rg.runtime.bindings.l2_envelope_contracts import (
        BudgetSnapshot,
        CapabilityScopeSummary,
    )

    capability_scope = CapabilityScopeSummary(
        capability_token_id=f"sha256:{packet.capability_scope_digest}",
        granted_tools=packet.allowed_tools,
        granted_actions=(),
        granted_models=packet.allowed_models,
        side_effect_envelope=packet.side_effect_class,
        tenant_scope=packet.tenant_id,
    )
    budget = BudgetSnapshot(
        timeout_ms=int(packet.budget.get("timeout_ms", 0)),
        retry_ceiling=int(packet.budget.get("retry_ceiling", 0)),
        repair_ceiling=int(packet.budget.get("repair_ceiling", 0)),
        token_limit=int(packet.budget.get("max_tokens", 0)),
        compute_limit=int(packet.budget.get("compute_limit", 1)),
        memory_limit_mb=int(packet.budget.get("memory_limit_mb", 0)),
        io_quota_bytes=int(packet.budget.get("max_output_bytes", 0)),
        circuit_breaker_open=bool(packet.budget.get("circuit_breaker_open", False)),
    )
    approved = replace(
        validation_output.approved_work_order,
        decisive_rule_id="V_AUTHORITY_PACKET_PASS",
        capability_scope=capability_scope,
        budget_snapshot=budget,
        side_effect_class=packet.side_effect_class,
    )
    return replace(
        validation_output,
        approved_work_order=approved,
        gate_refs=gate_refs,
    )


def _stamp_attempt_digest(attempt: Any) -> Any:
    digest = compute_attempt_output_digest(attempt)
    if str(getattr(attempt, "output_digest", "") or "") == digest:
        return attempt
    return replace(attempt, output_digest=digest)


def run_apps_rg_authorized_l2(
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
    *,
    artifact_dir: str | Path | None,
    attempt_number: int = 1,
    enable_heal: bool = False,
    max_heal_attempts: int = 3,
    resume_artifact_contract_mode: Any | None = None,
) -> Any:
    """Run E1→E2→(E3↔E4)→E5 from signed U0/L0/PA authority.

    Authority failures are sealed before E3 and never create provider receipts.
    Product execution requires an artifact directory so the canonical receipt
    bundle is part of the result rather than optional diagnostics.
    """
    root = Path(artifact_dir) if artifact_dir is not None else None
    try:
        if route_contract is None:
            raise _authority_error(
                "V0_MISSING_ROUTE",
                "product L2 requires an upstream RouteContract",
                "route_contract",
            )
        if validated_request is None:
            raise _authority_error(
                "V0_MISSING_REQUEST",
                "product L2 requires an upstream ValidatedRequest",
                "validated_request",
            )
        if root is None:
            raise _authority_error(
                "V0_ARTIFACT_DIR_REQUIRED",
                "product L2 requires artifact_dir for the canonical receipt bundle",
                "artifact_dir",
            )
        packet = build_signed_execution_packet(
            prompt_artifact,
            route_contract,
            validated_request,
            attempt_number=attempt_number,
        )
        gate_receipts = validate_execution_packet(
            packet,
            prompt_artifact,
            route_contract,
            validated_request,
        )
        frozen_room = freeze_execution_room(packet)
    except L2AuthorityError as error:
        sealed = build_authority_rejection_seal(prompt_artifact, error)
        if root is not None:
            write_authority_rejection_bundle(root, sealed, error)
        return sealed

    from apps_rg.runtime.bindings.l2_envelope_adapter import (
        _apply_heal_repair_patch,
        _build_prep_output,
        _execute_approved_work_order,
        _heal_attempt_failure,
        _seal_e2_rejection,
        _seal_l2_artifact,
        _validate_work_order,
    )

    active_prompt = _execution_prompt(prompt_artifact, packet, frozen_room)
    prep_output = _build_prep_output(active_prompt, route_contract, validated_request)
    validation_output = _bind_authority_to_validation(
        _validate_work_order(prep_output, active_prompt),
        packet,
        gate_receipts,
    )

    if validation_output.validation_status != "PASS" or validation_output.approved_work_order is None:
        sealed = _seal_e2_rejection(
            cpa=active_prompt,
            prep_output=prep_output,
            validation_output=validation_output,
        )
        return finalize_content_addressed_bundle(
            artifact_dir=root,
            packet=packet,
            frozen_room=frozen_room,
            gate_receipts=gate_receipts,
            prep_output=prep_output,
            validation_output=validation_output,
            attempt_receipt=None,
            heal_receipt=None,
            sealed=sealed,
        ).sealed

    attempt = _execute_approved_work_order(
        cpa=active_prompt,
        approved_work_order=validation_output.approved_work_order,
        prep_output=prep_output,
        attempt_number=attempt_number,
        resume_artifact_contract_mode=resume_artifact_contract_mode,
        artifact_dir=str(root),
    )
    attempt = _stamp_attempt_digest(attempt)

    heal_receipt: Any | None = None
    heals_used = 0
    repair_ceiling = min(
        max(0, int(max_heal_attempts)),
        max(0, int(packet.budget.get("repair_ceiling", 0))),
    )
    while (
        enable_heal
        and str(getattr(attempt.result_class, "value", attempt.result_class)) == "SOFT_REPAIRABLE"
        and heals_used < repair_ceiling
    ):
        heal_receipt = _heal_attempt_failure(
            failed_attempt=attempt,
            prep_output=prep_output,
            approved_work_order=validation_output.approved_work_order,
            cpa=active_prompt,
            repair_count=heals_used + 1,
        )
        heals_used += 1
        if str(getattr(heal_receipt, "next_action", "")) != "RETURN_TO_E3":
            break
        active_prompt = _apply_heal_repair_patch(active_prompt, heal_receipt)
        attempt = _execute_approved_work_order(
            cpa=active_prompt,
            approved_work_order=validation_output.approved_work_order,
            prep_output=prep_output,
            attempt_number=attempt_number + heals_used,
            resume_artifact_contract_mode=resume_artifact_contract_mode,
            artifact_dir=str(root),
        )
        attempt = _stamp_attempt_digest(attempt)

    sealed = _seal_l2_artifact(
        cpa=active_prompt,
        prep_output=prep_output,
        validation_output=validation_output,
        attempt_receipt=attempt,
        heal_receipt=heal_receipt,
    )
    return finalize_content_addressed_bundle(
        artifact_dir=root,
        packet=packet,
        frozen_room=frozen_room,
        gate_receipts=gate_receipts,
        prep_output=prep_output,
        validation_output=validation_output,
        attempt_receipt=attempt,
        heal_receipt=heal_receipt,
        sealed=sealed,
    ).sealed


__all__ = ["run_apps_rg_authorized_l2"]
