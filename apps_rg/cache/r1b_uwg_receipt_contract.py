"""R1B UWG receipt parity and authenticated L5 admission validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_rg.cache.r1b_constants import R1B_UWG_TARGET_SURFACE

REQUIRED_SOURCE_SURFACE = "Exit"
REQUIRED_COMMIT_REQUEST_FIELDS: tuple[str, ...] = (
    "source_surface",
    "l5_certification_ref",
    "l5_certification_refs",
    "gate_verdict_refs",
    "replay_key",
    "policy_hash",
    "blueprint_hash",
    "affected_state_surfaces",
    "cleared_exit_review_packet_ref",
    "request_id",
    "run_id",
    "trace_root",
    "tenant_id",
    "registry_digest_set",
    "clearance_proof_id",
    "staged_diff_hash",
    "commit_request_signature",
)
FORBIDDEN_PLACEHOLDER_HASHES: frozenset[str] = frozenset({"", "unknown", "UNKNOWN"})


@dataclass(frozen=True)
class R1BGovernanceRefValidation:
    valid: bool
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    reason_codes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "missing_fields": list(self.missing_fields),
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class R1BGovernanceReceiptBundle:
    """apps_rg sidecar governance refs preserved across UWG promotion."""

    source_surface: str
    l5_certification_ref: str
    gate_verdict_refs: tuple[str, ...]
    replay_key: str
    policy_hash: str
    blueprint_hash: str
    affected_state_surfaces: tuple[str, ...]
    cleared_exit_review_packet_ref: str
    commit_request_id: str
    state_diff_id: str
    target_surface: str
    operation_type: str
    l5_certification_packet_digest: str = ""
    l5_certification_status: str = ""
    l5_runtime_binding_digest: str = ""
    l5_certification_verified: bool = False
    l5_certification_verification_digest: str = ""
    uwg_commit_receipt_id: str = ""
    blocked_commit_receipt_id: str = ""
    core_receipt_l5_present: bool = False
    core_receipt_gate_verdict_present: bool = False
    core_receipt_policy_hash_present: bool = False
    core_receipt_blueprint_hash_present: bool = False
    core_receipt_replay_key_present: bool = False
    core_receipt_clearance_proof_present: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_surface": self.source_surface,
            "l5_certification_ref": self.l5_certification_ref,
            "gate_verdict_refs": list(self.gate_verdict_refs),
            "replay_key": self.replay_key,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "affected_state_surfaces": list(self.affected_state_surfaces),
            "cleared_exit_review_packet_ref": self.cleared_exit_review_packet_ref,
            "commit_request_id": self.commit_request_id,
            "state_diff_id": self.state_diff_id,
            "target_surface": self.target_surface,
            "operation_type": self.operation_type,
            "l5_certification_packet_digest": self.l5_certification_packet_digest,
            "l5_certification_status": self.l5_certification_status,
            "l5_runtime_binding_digest": self.l5_runtime_binding_digest,
            "l5_certification_verified": self.l5_certification_verified,
            "l5_certification_verification_digest": (
                self.l5_certification_verification_digest
            ),
            "uwg_commit_receipt_id": self.uwg_commit_receipt_id,
            "blocked_commit_receipt_id": self.blocked_commit_receipt_id,
            "core_receipt_l5_present": self.core_receipt_l5_present,
            "core_receipt_gate_verdict_present": self.core_receipt_gate_verdict_present,
            "core_receipt_policy_hash_present": self.core_receipt_policy_hash_present,
            "core_receipt_blueprint_hash_present": self.core_receipt_blueprint_hash_present,
            "core_receipt_replay_key_present": self.core_receipt_replay_key_present,
            "core_receipt_clearance_proof_present": self.core_receipt_clearance_proof_present,
        }


def _l5_ref_map(commit_request: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in tuple(getattr(commit_request, "l5_certification_refs", ()) or ()):
        key, separator, value = str(item).partition("=")
        if separator and key:
            result[key] = value
    return result


def _is_hex64(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _validate_l5_packet_evidence(commit_request: Any) -> tuple[list[str], list[str]]:
    from apps_rg.runtime.l5.packet_builder import compute_l5_packet_verification_digest

    missing: list[str] = []
    reasons: list[str] = []
    packet_ref = str(getattr(commit_request, "l5_certification_ref", "") or "").strip()
    refs = _l5_ref_map(commit_request)
    packet_digest = refs.get("packet_digest", "")
    status = refs.get("status", "")
    binding_digest = refs.get("runtime_binding_digest", "")
    verified = refs.get("verified", "").lower() == "true"
    verification_digest = refs.get("verification_digest", "")

    if not _is_hex64(packet_digest):
        missing.append("l5_certification_refs.packet_digest")
        reasons.append("missing_or_malformed_l5_packet_digest")
    if packet_ref != f"l5_packet:{packet_digest}":
        missing.append("l5_certification_ref")
        reasons.append("l5_packet_ref_digest_mismatch")
    if status != "L5_CERTIFIED":
        missing.append("l5_certification_refs.status")
        reasons.append("l5_packet_not_certified")
    if not _is_hex64(binding_digest):
        missing.append("l5_certification_refs.runtime_binding_digest")
        reasons.append("missing_or_malformed_l5_runtime_binding_digest")
    if not verified:
        missing.append("l5_certification_refs.verified")
        reasons.append("l5_packet_not_verified_by_exit")
    if not _is_hex64(verification_digest):
        missing.append("l5_certification_refs.verification_digest")
        reasons.append("missing_or_malformed_l5_verification_digest")
    elif _is_hex64(packet_digest) and _is_hex64(binding_digest):
        expected = compute_l5_packet_verification_digest(
            request_id=str(getattr(commit_request, "request_id", "") or ""),
            run_id=str(getattr(commit_request, "run_id", "") or ""),
            trace_id=str(getattr(commit_request, "trace_root", "") or ""),
            packet_ref=packet_ref,
            packet_digest=packet_digest,
            status=status,
            runtime_binding_digest_value=binding_digest,
        )
        if verification_digest != expected:
            missing.append("l5_certification_refs.verification_digest")
            reasons.append("l5_verification_digest_mismatch")
    return missing, reasons


def _expected_commit_request_signature(commit_request: Any) -> str:
    from agentic_core.L4_state.contracts.digests import compute_deterministic_digest

    refs = _l5_ref_map(commit_request)
    return compute_deterministic_digest(
        {
            "commit_request_id": str(
                getattr(commit_request, "commit_request_id", "") or ""
            ),
            "staged_diff_hash": str(
                getattr(commit_request, "staged_diff_hash", "") or ""
            ),
            "clearance_proof_id": str(
                getattr(commit_request, "clearance_proof_id", "") or ""
            ),
            "l5_packet_digest": refs.get("packet_digest", ""),
            "l5_verification_digest": refs.get("verification_digest", ""),
        }
    )


def validate_commit_request_governance(
    commit_request: Any,
) -> R1BGovernanceRefValidation:
    """Fail-closed validation before any UWG durable admission."""

    missing: list[str] = []
    reasons: list[str] = []
    if (
        str(getattr(commit_request, "source_surface", "") or "")
        != REQUIRED_SOURCE_SURFACE
    ):
        missing.append("source_surface")
        reasons.append("source_surface_must_be_exit")

    l5_missing, l5_reasons = _validate_l5_packet_evidence(commit_request)
    missing.extend(l5_missing)
    reasons.extend(l5_reasons)

    gate_refs = tuple(getattr(commit_request, "gate_verdict_refs", ()) or ())
    if not gate_refs:
        missing.append("gate_verdict_refs")
        reasons.append("missing_gate_verdict_refs")
    if not str(getattr(commit_request, "replay_key", "") or "").strip():
        missing.append("replay_key")
        reasons.append("missing_replay_key")

    policy = str(getattr(commit_request, "policy_hash", "") or "").strip()
    if policy in FORBIDDEN_PLACEHOLDER_HASHES:
        missing.append("policy_hash")
        reasons.append("missing_or_placeholder_policy_hash")
    blueprint = str(getattr(commit_request, "blueprint_hash", "") or "").strip()
    if blueprint in FORBIDDEN_PLACEHOLDER_HASHES:
        missing.append("blueprint_hash")
        reasons.append("missing_or_placeholder_blueprint_hash")

    surfaces = tuple(getattr(commit_request, "affected_state_surfaces", ()) or ())
    if not surfaces or R1B_UWG_TARGET_SURFACE not in surfaces:
        missing.append("affected_state_surfaces")
        reasons.append("missing_r1b_target_surface")
    for field_name in (
        "cleared_exit_review_packet_ref",
        "request_id",
        "run_id",
        "trace_root",
        "tenant_id",
    ):
        if not str(getattr(commit_request, field_name, "") or "").strip():
            missing.append(field_name)
            reasons.append(f"missing::{field_name}")
    if not tuple(getattr(commit_request, "registry_digest_set", ()) or ()):
        missing.append("registry_digest_set")
        reasons.append("missing_registry_digest_set")
    if not str(getattr(commit_request, "clearance_proof_id", "") or "").strip():
        missing.append("clearance_proof_id")
        reasons.append("missing_clearance_proof_id")
    if not str(getattr(commit_request, "staged_diff_hash", "") or "").strip():
        missing.append("staged_diff_hash")
        reasons.append("missing_staged_diff_hash")
    signature = str(
        getattr(commit_request, "commit_request_signature", "") or ""
    ).strip()
    if not signature:
        missing.append("commit_request_signature")
        reasons.append("commit_request_signature_invalid")
    elif signature != _expected_commit_request_signature(commit_request):
        missing.append("commit_request_signature")
        reasons.append("commit_request_signature_l5_binding_mismatch")

    return R1BGovernanceRefValidation(
        valid=not missing,
        missing_fields=tuple(dict.fromkeys(missing)),
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def build_governance_receipt_bundle(
    *,
    commit_request: Any,
    state_diffs: list[Any],
    commit_receipt: Any | None = None,
    blocked_receipt: Any | None = None,
) -> R1BGovernanceReceiptBundle:
    state_diff = state_diffs[0] if state_diffs else None
    core_l5 = (
        str(getattr(commit_receipt, "l5_certification_ref", "") or "")
        if commit_receipt
        else ""
    )
    core_gate_refs = (
        tuple(getattr(commit_receipt, "gate_verdict_refs", ()) or ())
        if commit_receipt
        else ()
    )
    refs = _l5_ref_map(commit_request)
    return R1BGovernanceReceiptBundle(
        source_surface=str(commit_request.source_surface),
        l5_certification_ref=str(commit_request.l5_certification_ref),
        gate_verdict_refs=tuple(commit_request.gate_verdict_refs),
        replay_key=str(commit_request.replay_key),
        policy_hash=str(commit_request.policy_hash),
        blueprint_hash=str(commit_request.blueprint_hash),
        affected_state_surfaces=tuple(commit_request.affected_state_surfaces),
        cleared_exit_review_packet_ref=str(
            commit_request.cleared_exit_review_packet_ref
        ),
        commit_request_id=str(commit_request.commit_request_id),
        state_diff_id=str(state_diff.state_diff_id) if state_diff else "",
        target_surface=str(state_diff.target_surface)
        if state_diff
        else R1B_UWG_TARGET_SURFACE,
        operation_type=str(state_diff.operation_type)
        if state_diff
        else "memory_promotion",
        l5_certification_packet_digest=refs.get("packet_digest", ""),
        l5_certification_status=refs.get("status", ""),
        l5_runtime_binding_digest=refs.get("runtime_binding_digest", ""),
        l5_certification_verified=refs.get("verified", "").lower() == "true",
        l5_certification_verification_digest=refs.get("verification_digest", ""),
        uwg_commit_receipt_id=str(
            getattr(commit_receipt, "commit_receipt_id", "") or ""
        ),
        blocked_commit_receipt_id=str(
            getattr(blocked_receipt, "blocked_commit_receipt_id", "") or ""
        ),
        core_receipt_l5_present=bool(core_l5),
        core_receipt_gate_verdict_present=bool(core_gate_refs),
        core_receipt_policy_hash_present=bool(
            str(getattr(commit_receipt, "policy_hash", "") or "")
        )
        if commit_receipt
        else False,
        core_receipt_blueprint_hash_present=bool(
            str(getattr(commit_receipt, "blueprint_hash", "") or "")
        )
        if commit_receipt
        else False,
        core_receipt_replay_key_present=bool(
            str(getattr(commit_receipt, "replay_key", "") or "")
        )
        if commit_receipt
        else False,
        core_receipt_clearance_proof_present=bool(
            str(getattr(commit_receipt, "clearance_proof_id", "") or "")
        )
        if commit_receipt
        else False,
    )


def build_receipt_field_parity_matrix() -> list[dict[str, Any]]:
    fields = (
        "source_surface",
        "l5_certification_ref",
        "gate_verdict_refs",
        "replay_key",
        "policy_hash",
        "blueprint_hash",
        "affected_state_surfaces",
        "cleared_exit_review_packet_ref",
    )
    return [
        {
            "field": field_name,
            "commit_request": True,
            "state_diff": field_name in {"replay_key", "affected_state_surfaces"},
            "uwg_commit_receipt_core": True,
            "apps_rg_governance_sidecar": True,
        }
        for field_name in fields
    ]


def document_r1b_uwg_core_receipt_gaps() -> dict[str, Any]:
    return {
        "promotion_gateway_module": "apps_rg.cache.r1b_uwg_promotion.R1bUwgPromotionGateway",
        "core_gap_summary": "No active core receipt parity gap for R1B UWG provenance.",
        "fields_core_cannot_carry": [],
        "fields_promotion_gateway_enriches": [
            "l5_certification_packet_digest",
            "l5_runtime_binding_digest",
            "l5_certification_verification_digest",
        ],
        "fields_core_carries": [
            "affected_state_surfaces",
            "state_diff_refs",
            "audit_refs",
        ],
        "apps_rg_sidecar_path": "durable/uwg_admitted/intents/<record_id>.json#governance_receipt",
        "agentic_core_edit_required_for_full_parity": False,
    }


__all__ = [
    "R1BGovernanceReceiptBundle",
    "R1BGovernanceRefValidation",
    "REQUIRED_COMMIT_REQUEST_FIELDS",
    "REQUIRED_SOURCE_SURFACE",
    "build_governance_receipt_bundle",
    "build_receipt_field_parity_matrix",
    "document_r1b_uwg_core_receipt_gaps",
    "validate_commit_request_governance",
]
