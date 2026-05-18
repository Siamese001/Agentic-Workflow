"""W10b — R1B UWG receipt field parity and governance ref validation (apps_rg)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_rg.cache.r1b_constants import R1B_UWG_TARGET_SURFACE

REQUIRED_SOURCE_SURFACE = "Exit"

REQUIRED_COMMIT_REQUEST_FIELDS: tuple[str, ...] = (
    "source_surface",
    "l5_certification_ref",
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
    """apps_rg-sidecar governance refs preserved across UWG promotion."""

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
    uwg_commit_receipt_id: str = ""
    blocked_commit_receipt_id: str = ""
    core_receipt_l5_present: bool = False
    core_receipt_gate_verdict_present: bool = False

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
            "uwg_commit_receipt_id": self.uwg_commit_receipt_id,
            "blocked_commit_receipt_id": self.blocked_commit_receipt_id,
            "core_receipt_l5_present": self.core_receipt_l5_present,
            "core_receipt_gate_verdict_present": self.core_receipt_gate_verdict_present,
        }


def validate_commit_request_governance(commit_request: Any) -> R1BGovernanceRefValidation:
    """Fail-closed validation before UWG durable admission."""
    missing: list[str] = []
    reasons: list[str] = []

    if str(getattr(commit_request, "source_surface", "") or "") != REQUIRED_SOURCE_SURFACE:
        missing.append("source_surface")
        reasons.append("source_surface_must_be_exit")

    l5 = str(getattr(commit_request, "l5_certification_ref", "") or "").strip()
    if not l5:
        missing.append("l5_certification_ref")
        reasons.append("missing_l5_certification_ref")

    gate_refs = tuple(getattr(commit_request, "gate_verdict_refs", ()) or ())
    if not gate_refs:
        missing.append("gate_verdict_refs")
        reasons.append("missing_gate_verdict_refs")

    replay = str(getattr(commit_request, "replay_key", "") or "").strip()
    if not replay:
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

    for fld in ("cleared_exit_review_packet_ref", "request_id", "run_id", "trace_root", "tenant_id"):
        if not str(getattr(commit_request, fld, "") or "").strip():
            missing.append(fld)
            reasons.append(f"missing::{fld}")

    return R1BGovernanceRefValidation(
        valid=not missing,
        missing_fields=tuple(missing),
        reason_codes=tuple(reasons),
    )


def build_governance_receipt_bundle(
    *,
    commit_request: Any,
    state_diffs: list[Any],
    commit_receipt: Any | None = None,
    blocked_receipt: Any | None = None,
) -> R1BGovernanceReceiptBundle:
    sd = state_diffs[0] if state_diffs else None
    core_l5 = ""
    if commit_receipt is not None:
        core_l5 = str(getattr(commit_receipt, "l5_certification_ref", "") or "")
    return R1BGovernanceReceiptBundle(
        source_surface=str(commit_request.source_surface),
        l5_certification_ref=str(commit_request.l5_certification_ref),
        gate_verdict_refs=tuple(commit_request.gate_verdict_refs),
        replay_key=str(commit_request.replay_key),
        policy_hash=str(commit_request.policy_hash),
        blueprint_hash=str(commit_request.blueprint_hash),
        affected_state_surfaces=tuple(commit_request.affected_state_surfaces),
        cleared_exit_review_packet_ref=str(commit_request.cleared_exit_review_packet_ref),
        commit_request_id=str(commit_request.commit_request_id),
        state_diff_id=str(sd.state_diff_id) if sd else "",
        target_surface=str(sd.target_surface) if sd else R1B_UWG_TARGET_SURFACE,
        operation_type=str(sd.operation_type) if sd else "memory_promotion",
        uwg_commit_receipt_id=str(getattr(commit_receipt, "commit_receipt_id", "") or "")
        if commit_receipt
        else "",
        blocked_commit_receipt_id=str(
            getattr(blocked_receipt, "blocked_commit_receipt_id", "") or ""
        )
        if blocked_receipt
        else "",
        core_receipt_l5_present=bool(core_l5),
        core_receipt_gate_verdict_present=False,
    )


def build_receipt_field_parity_matrix() -> list[dict[str, Any]]:
    """Field-level parity: CommitRequest vs StateDiff vs core receipt vs apps_rg sidecar."""
    return [
        {
            "field": "source_surface",
            "commit_request": True,
            "state_diff": "proposed_by_surface=Exit",
            "uwg_commit_receipt_core": False,
            "apps_rg_governance_sidecar": True,
            "notes": "Must be Exit on CommitRequest; core receipt has committed_by_surface=UWG only",
        },
        {
            "field": "l5_certification_ref",
            "commit_request": True,
            "state_diff": False,
            "uwg_commit_receipt_core": "shim_patched",
            "apps_rg_governance_sidecar": True,
            "notes": "Core gateway omits l5 on receipt; AppsRgR1BUwgGateway patches construction",
        },
        {
            "field": "gate_verdict_refs",
            "commit_request": True,
            "state_diff": False,
            "uwg_commit_receipt_core": False,
            "apps_rg_governance_sidecar": True,
            "notes": "Not a UWGCommitReceipt field; preserved in apps_rg sidecar only",
        },
        {
            "field": "replay_key",
            "commit_request": True,
            "state_diff": "replay_refs on StateDiff",
            "uwg_commit_receipt_core": False,
            "apps_rg_governance_sidecar": True,
        },
        {
            "field": "policy_hash",
            "commit_request": True,
            "state_diff": "policy_refs optional",
            "uwg_commit_receipt_core": False,
            "apps_rg_governance_sidecar": True,
        },
        {
            "field": "blueprint_hash",
            "commit_request": True,
            "state_diff": False,
            "uwg_commit_receipt_core": False,
            "apps_rg_governance_sidecar": True,
        },
        {
            "field": "affected_state_surfaces",
            "commit_request": True,
            "state_diff": "target_surface",
            "uwg_commit_receipt_core": True,
            "apps_rg_governance_sidecar": True,
        },
        {
            "field": "cleared_exit_review_packet_ref",
            "commit_request": True,
            "state_diff": False,
            "uwg_commit_receipt_core": False,
            "apps_rg_governance_sidecar": True,
        },
    ]


def document_shim_core_gaps() -> dict[str, Any]:
    return {
        "shim_module": "apps_rg.cache.r1b_uwg_gateway_shim.AppsRgR1BUwgGateway",
        "core_gap_summary": (
            "Stock DurableWriteGateway.commit constructs UWGCommitReceipt without "
            "l5_certification_ref; apps_rg shim patches receipt __new__ to inject l5 from "
            "CommitRequest. gate_verdict_refs, replay_key, policy_hash, blueprint_hash, and "
            "source_surface are NOT fields on UWGCommitReceipt — apps_rg durable projection "
            "stores them in governance_receipt sidecar."
        ),
        "fields_core_cannot_carry": [
            "gate_verdict_refs",
            "replay_key",
            "policy_hash",
            "blueprint_hash",
            "source_surface",
            "cleared_exit_review_packet_ref",
        ],
        "fields_shim_patches": ["l5_certification_ref"],
        "fields_core_carries": ["affected_state_surfaces", "state_diff_refs", "audit_refs"],
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
    "document_shim_core_gaps",
    "validate_commit_request_governance",
]
