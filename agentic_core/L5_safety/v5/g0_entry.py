"""G0 GOVERNANCE ENTRY CONTRACT (spec lines 21–49).

Validates the inbound packet, applies fast-reject conditions, and
returns either a normalized ``GovernanceReviewRequest`` or a list of
fast-reject failure codes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.L5_safety.v5.contracts import GovernanceReviewRequest
from agentic_core.L5_safety.v5.types import (
    PacketKind,
    ReasonCode,
    SideEffectClass,
)


# Side-effect classes that demand a route contract HMAC (spec line 41).
_AUTHORITY_REQUIRED_SIDE_EFFECTS = frozenset(
    {
        SideEffectClass.MODEL_CALL,
        SideEffectClass.TOOL_CALL,
        SideEffectClass.NETWORK,
        SideEffectClass.MEMORY,
        SideEffectClass.WRITE_PROPOSAL,
        SideEffectClass.EXTERNAL_COMMIT,
    }
)

# Side-effect classes that imply write intent — must not be claimed
# read-only (spec line 45).
_WRITE_INTENT_SIDE_EFFECTS = frozenset(
    {
        SideEffectClass.MEMORY,
        SideEffectClass.WRITE_PROPOSAL,
        SideEffectClass.EXTERNAL_COMMIT,
    }
)


@dataclass(frozen=True)
class EntryValidationFailure:
    """One fast-reject finding (spec lines 40–45)."""

    code: ReasonCode
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code.value, "detail": self.detail}


@dataclass(frozen=True)
class EntryValidationResult:
    """Outcome of G0 validation."""

    accepted: bool
    request: GovernanceReviewRequest | None
    failures: tuple[EntryValidationFailure, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "failures": [f.to_dict() for f in self.failures],
            "request": self.request.to_dict() if self.request else None,
        }


def _required_present(value: str, name: str, failures: list[EntryValidationFailure]) -> None:
    if not value:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.MISSING_AUTHORITY,
                detail=f"required field missing: {name}",
            ),
        )


def validate_entry_packet(
    raw: Mapping[str, Any],
    *,
    declared_read_only: bool = False,
) -> EntryValidationResult:
    """Validate a raw inbound packet dict.

    Spec lines 33–46. The function is strict in what it requires and
    tolerant of extra unknown keys (passed through into the constructed
    request). All eight fast-reject conditions are mapped to
    ``ReasonCode`` values for downstream uniformity.
    """
    failures: list[EntryValidationFailure] = []

    # --- Required scalar fields --------------------------------------
    request_id = str(raw.get("request_id", ""))
    trace_id = str(raw.get("trace_id", ""))
    run_id = str(raw.get("run_id", ""))
    tenant_id = str(raw.get("tenant_id", ""))
    caller_id = str(raw.get("caller_id", ""))
    _required_present(request_id, "request_id", failures)
    _required_present(trace_id, "trace_id", failures)
    _required_present(run_id, "run_id", failures)
    _required_present(tenant_id, "tenant_id", failures)
    _required_present(caller_id, "caller_id", failures)

    # --- Packet kind --------------------------------------------------
    packet_kind_raw = raw.get("packet_kind", "")
    try:
        packet_kind = PacketKind(packet_kind_raw)
    except ValueError:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.MISSING_AUTHORITY,
                detail=f"unknown packet_kind: {packet_kind_raw!r}",
            ),
        )
        packet_kind = PacketKind.REQUEST_ENVELOPE  # placeholder for downstream

    # --- Side-effect class -------------------------------------------
    side_effect_raw = raw.get("side_effect_class", "")
    try:
        side_effect_class = SideEffectClass(side_effect_raw)
    except ValueError:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.MISSING_AUTHORITY,
                detail=f"unknown side_effect_class: {side_effect_raw!r}",
            ),
        )
        side_effect_class = SideEffectClass.NONE

    # --- Origin manifest required for content entering prompt assembly or L2
    origin_raw = raw.get("origin_trust_manifest_raw") or {}
    if not origin_raw and side_effect_class in {
        SideEffectClass.MODEL_CALL,
        SideEffectClass.TOOL_CALL,
    }:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.INJECTION_DETECTED,
                detail="missing origin_trust_manifest for prompt-assembly or L2 packet",
            ),
        )

    # --- Route contract required when authority requested ------------
    requested_authority = tuple(raw.get("requested_authority") or ())
    route_contract_hmac = str(raw.get("route_contract_hmac", ""))
    if requested_authority and not route_contract_hmac:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.ROUTE_MISMATCH,
                detail="missing route_contract_hmac when authority requested",
            ),
        )

    # --- Registry digest required for any side-effect-bearing packet -
    registry_digest_set = tuple(raw.get("registry_digest_set") or ())
    if side_effect_class in _AUTHORITY_REQUIRED_SIDE_EFFECTS and not registry_digest_set:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.REGISTRY_MISMATCH,
                detail="missing registry_digest_set for authority-requesting packet",
            ),
        )

    # --- Principal chain required for any delegated invocation -------
    principal_chain_id = str(raw.get("principal_chain_id", ""))
    if side_effect_class != SideEffectClass.NONE and not principal_chain_id:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.MISSING_AUTHORITY,
                detail="missing principal_chain_id for non-NONE side_effect packet",
            ),
        )

    # --- Read-only claim mismatch ------------------------------------
    if declared_read_only and side_effect_class in _WRITE_INTENT_SIDE_EFFECTS:
        failures.append(
            EntryValidationFailure(
                code=ReasonCode.POLICY_VIOLATION,
                detail=(
                    f"declared read-only but side_effect_class={side_effect_class.value} implies write intent"
                ),
            ),
        )

    # --- Build request ------------------------------------------------
    if failures:
        return EntryValidationResult(accepted=False, request=None, failures=tuple(failures))

    origin_manifest_normalized: dict[str, tuple[str, ...]] = {
        str(label): tuple(str(p) for p in (paths or ())) for label, paths in (origin_raw or {}).items()
    }

    request = GovernanceReviewRequest(
        request_id=request_id,
        trace_id=trace_id,
        run_id=run_id,
        tenant_id=tenant_id,
        caller_id=caller_id,
        packet_kind=packet_kind,
        side_effect_class=side_effect_class,
        requested_authority=tuple(str(s) for s in requested_authority),
        policy_hash=str(raw.get("policy_hash", "")),
        blueprint_hash=str(raw.get("blueprint_hash", "")),
        registry_digest_set=tuple(str(s) for s in registry_digest_set),
        route_contract_hmac=route_contract_hmac,
        replay_key=str(raw.get("replay_key", "")),
        origin_trust_manifest_raw=origin_manifest_normalized,
        principal_chain_id=principal_chain_id,
        payload_digest=str(raw.get("payload_digest", "")),
    )
    return EntryValidationResult(accepted=True, request=request, failures=())


__all__ = [
    "EntryValidationFailure",
    "EntryValidationResult",
    "validate_entry_packet",
]
