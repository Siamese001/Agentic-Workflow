"""apps_lic U0 reflection adapter — contract-first ingress hardening.

This adapter is the canonical bridge between raw apps_lic ingress JSON and the
shared ``ValidatedRequest`` contract. It proves every input JSON Pointer is
accounted for via the field-map SSOT, and fails closed on any of:

    - Pydantic schema validation failure (E1)
    - app_id != 'apps_lic' or task_class != 'outreach_message' (E4)
    - side_effect_class != 'read_only' (E5)
    - workflow_required != 'managed_workflow_hop' (E6)
    - grounding_required=False for non-dry_run request (E7)
    - forbidden_send_modes missing any of the hardcoded three (E2)
    - missing identity (no lead_profile AND no lead_ref for non-dry_run) (E3)
    - governance field disabled (pii_detection, governance_shield, antipattern) (E8)
    - bypass_hitl_freeze=True without HITL_FREEZE_BYPASS env var (E9)
    - silently dropped field (input pointer with no field-map entry)
    - unknown mapping (field-map status outside MAPPED/DERIVED/REJECTED/DEFERRED)

CORE RULE: a field may be deferred. A field may not disappear.

Adapter contract:
    ``apps_lic_u0_adapt(raw_json: dict) -> tuple[ValidatedRequest, AppsLicU0ReflectionReceipt]``

The adapter:
    1. Validates raw JSON against ``AppsLicIngressContractV1`` (Pydantic)
    2. Performs U0 E1-E9 domain checks
    3. Enumerates JSON Pointers from the contract dump
    4. Looks up each pointer in ``apps_lic_ingress_field_map.v1.yaml``
    5. Emits ``AppsLicU0ReflectionReceipt`` with deterministic digests
    6. Builds a ``ValidatedRequest`` preserving the full apps_lic payload
       under ``app_payload``
    7. Returns the tuple — or raises one of the named exceptions

The adapter does NOT execute any apps_lic business logic. It does not call
L1/L0/C0/PA/L2/Exit layers. It is a pure validator + reflector.

No business logic. No routing. No retrieval. No L4 writes. No I/O beyond
loading the field-map YAML once from disk.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W3)
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml
from pydantic import ValidationError

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AuthorityValidationReceipt,
)
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY
from apps_lic.contracts.apps_lic_ingress_contract_v1 import (
    APPS_LIC_INGRESS_CONTRACT_VERSION,
    AppsLicIngressContractV1,
)


# ---------------------------------------------------------------------------
# Receipt dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AppsLicU0ReflectionReceipt:
    """Proof that every input JSON Pointer is accounted for at apps_lic U0.

    A receipt with ``pass_status=True`` requires:
      - ``silently_dropped == ()``
      - ``unknown_mappings == ()``
      - every DEFERRED pointer carries an explicit reason
      - deterministic ``input_payload_digest`` (sha256 over canonical input JSON)
      - deterministic ``validated_request_digest`` (sha256 over canonical
        ValidatedRequest projection)

    A receipt with ``pass_status=False`` MUST never accompany a returned
    ValidatedRequest — the adapter raises instead.
    """

    contract_version: str
    schema_version: str
    field_map_version: str
    input_payload_digest: str
    validated_request_digest: str
    pointers_total: int
    pointers_mapped: int
    pointers_derived: int
    pointers_rejected: int
    pointers_deferred: int
    deferred_reasons: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    silently_dropped: tuple[str, ...] = field(default_factory=tuple)
    unknown_mappings: tuple[str, ...] = field(default_factory=tuple)
    pass_status: bool = False
    timestamp_iso: str = ""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AppsLicU0AdapterError(Exception):
    """Base class for all apps_lic U0 adapter failures (fail-closed signals)."""


class AppsLicU0ReflectionFailure(AppsLicU0AdapterError):
    """Reflection check failed — silently dropped fields or unknown mappings."""

    def __init__(
        self,
        message: str,
        *,
        silently_dropped: tuple[str, ...] = (),
        unknown_mappings: tuple[str, ...] = (),
        receipt: AppsLicU0ReflectionReceipt | None = None,
    ) -> None:
        super().__init__(message)
        self.silently_dropped = silently_dropped
        self.unknown_mappings = unknown_mappings
        self.receipt = receipt


class SilentlyDroppedFieldError(AppsLicU0ReflectionFailure):
    """Specific subclass for silently dropped fields."""


class UnknownFieldMappingError(AppsLicU0ReflectionFailure):
    """Specific subclass for unknown field-map status."""


class AppsLicSchemaValidationError(AppsLicU0AdapterError):
    """Pydantic schema validation failed (E1)."""


class AppsLicIdentityError(AppsLicU0AdapterError):
    """app_id or task_class mismatch (E4)."""


class AppsLicSideEffectError(AppsLicU0AdapterError):
    """side_effect_class != 'read_only' (E5)."""


class AppsLicWorkflowError(AppsLicU0AdapterError):
    """workflow_required != 'managed_workflow_hop' (E6)."""


class AppsLicGroundingError(AppsLicU0AdapterError):
    """grounding_required=False for non-dry_run (E7)."""


class AppsLicForbiddenSendModeError(AppsLicU0AdapterError):
    """forbidden_send_modes missing hardcoded three (E2)."""


class AppsLicMissingIdentityError(AppsLicU0AdapterError):
    """No lead_profile and no lead_ref for non-dry_run (E3)."""


class AppsLicGovernanceFieldError(AppsLicU0AdapterError):
    """A governance field has been disabled (E8)."""


class AppsLicHitlBypassError(AppsLicU0AdapterError):
    """bypass_hitl_freeze=True without HITL_FREEZE_BYPASS env var (E9)."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PERMITTED_STATUSES: frozenset[str] = frozenset({"MAPPED", "DERIVED", "REJECTED", "DEFERRED"})
_HARDCODED_FORBIDDEN_SEND_MODES: frozenset[str] = frozenset(
    {"send_now", "auto_send", "connector_send"}
)
_APPS_LIC_U0_ADAPTER_CERT_REF: str = "u0-apps-lic-outreach-message-reflection-f3c2e1"

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_FIELD_MAP_PATH: Path = (
    _REPO_ROOT / "apps_lic" / "contracts" / "apps_lic_ingress_field_map.v1.yaml"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def _sha256_hex(obj: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(obj)).hexdigest()


def _enumerate_pointers(obj: Any, prefix: str = "") -> list[str]:
    """Walk a dict/list payload and emit every JSON Pointer (RFC 6901).

    Homogeneous primitive sequences (tuple/list of str/int/float/bool/None)
    are treated as opaque — the parent pointer is emitted, not individual
    element pointers. This matches the apps_rg adapter behaviour and keeps
    field-map size tractable.
    """
    pointers: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{prefix}/{key}"
            pointers.append(child)
            pointers.extend(_enumerate_pointers(value, child))
    elif isinstance(obj, (list, tuple)):
        is_primitive = all(isinstance(i, (str, int, float, bool, type(None))) for i in obj)
        if not is_primitive:
            for idx, item in enumerate(obj):
                child = f"{prefix}/{idx}"
                pointers.append(child)
                pointers.extend(_enumerate_pointers(item, child))
    return pointers


def _load_field_map() -> Mapping[str, Any]:
    if not _FIELD_MAP_PATH.exists():
        raise AppsLicU0AdapterError(
            f"apps_lic field-map SSOT missing at {_FIELD_MAP_PATH}. "
            "The harness cannot operate without it — fail closed."
        )
    with open(_FIELD_MAP_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise AppsLicU0AdapterError(
            f"apps_lic field-map at {_FIELD_MAP_PATH} did not parse as a mapping."
        )
    if "mappings" not in data or not isinstance(data["mappings"], dict):
        raise AppsLicU0AdapterError("apps_lic field-map missing 'mappings' section.")
    if "version" not in data:
        raise AppsLicU0AdapterError("apps_lic field-map missing 'version' field.")
    return data


# ---------------------------------------------------------------------------
# U0 domain checks (E1-E9)
# ---------------------------------------------------------------------------


def _check_identity(transport: Mapping[str, Any]) -> None:
    """E4: app_id and task_class must match exactly."""
    if transport.get("app_id") != "apps_lic":
        raise AppsLicIdentityError(
            f"app_id must be 'apps_lic'; got {transport.get('app_id')!r} (E4)"
        )
    if transport.get("task_class") != "outreach_message":
        raise AppsLicIdentityError(
            f"task_class must be 'outreach_message'; got {transport.get('task_class')!r} (E4)"
        )


def _check_side_effect_class(campaign: Mapping[str, Any]) -> None:
    """E5: side_effect_class must be 'read_only'."""
    sec = campaign.get("side_effect_class")
    if sec != "read_only":
        raise AppsLicSideEffectError(
            f"side_effect_class must be 'read_only' (NB-3 invariant); got {sec!r} (E5)"
        )


def _check_workflow_required(campaign: Mapping[str, Any]) -> None:
    """E6: workflow_required must be 'managed_workflow_hop'."""
    wr = campaign.get("workflow_required")
    if wr != "managed_workflow_hop":
        raise AppsLicWorkflowError(
            f"workflow_required must be 'managed_workflow_hop'; got {wr!r} (E6)"
        )


def _check_grounding(campaign: Mapping[str, Any]) -> None:
    """E7: grounding_required must be True for non-dry_run."""
    if campaign.get("request_type") != "dry_run":
        if not campaign.get("grounding_required", True):
            raise AppsLicGroundingError(
                "grounding_required cannot be False for non-dry_run requests (E7)"
            )


def _check_forbidden_send_modes(fsm: Mapping[str, Any]) -> None:
    """E2: forbidden_send_modes must contain the three hardcoded values."""
    modes = set(fsm.get("modes", []))
    missing = _HARDCODED_FORBIDDEN_SEND_MODES - modes
    if missing:
        raise AppsLicForbiddenSendModeError(
            f"forbidden_send_modes missing required entries: {sorted(missing)} (E2)"
        )


def _check_identity_fields(entity_refs: Mapping[str, Any], campaign: Mapping[str, Any]) -> None:
    """E3: non-dry_run requests must have lead_profile or lead_ref."""
    if campaign.get("request_type") == "dry_run":
        return
    has_profile = bool(entity_refs.get("lead_profile"))
    has_ref = bool(entity_refs.get("lead_ref"))
    if not has_profile and not has_ref:
        raise AppsLicMissingIdentityError(
            "Non-dry_run request must provide lead_profile or lead_ref (E3)"
        )


def _check_governance_fields(
    pii: Mapping[str, Any],
    shield: Mapping[str, Any],
    antipattern: Mapping[str, Any],
    source_lineage: Mapping[str, Any],
) -> None:
    """E8: governance fields cannot be disabled."""
    if not pii.get("fail_on_pii_detect", True):
        raise AppsLicGovernanceFieldError(
            "pii_policy.fail_on_pii_detect cannot be False — "
            "PII detection is a governance field (E8)"
        )
    if not shield.get("shield_required", True):
        raise AppsLicGovernanceFieldError(
            "governance_shield.shield_required cannot be False — "
            "governance shield is a governance field (E8)"
        )
    if not antipattern.get("enabled", True):
        raise AppsLicGovernanceFieldError(
            "antipattern_policy.enabled cannot be False — "
            "antipattern detection is a governance field (E8)"
        )
    if not source_lineage.get("source_lineage_required", True):
        raise AppsLicGovernanceFieldError(
            "source_lineage.source_lineage_required cannot be False — "
            "source lineage is a governance field (E8)"
        )


def _check_hitl_bypass(hitl: Mapping[str, Any]) -> None:
    """E9: bypass_hitl_freeze=True requires HITL_FREEZE_BYPASS env var."""
    if hitl.get("bypass_hitl_freeze", False):
        if os.environ.get("HITL_FREEZE_BYPASS") != "1":
            raise AppsLicHitlBypassError(
                "hitl_policy.bypass_hitl_freeze=True requires HITL_FREEZE_BYPASS=1 "
                "env var — not set in this process (E9)"
            )


# ---------------------------------------------------------------------------
# Reflection engine
# ---------------------------------------------------------------------------


def _resolve_entry(
    pointer: str,
    mappings: Mapping[str, Any],
    section_aggregations: Mapping[str, Any],
    pattern_mappings: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    """Resolve a pointer to its field-map entry.

    Resolution order (first hit wins):
      1. exact match in ``mappings``
      2. exact match in ``section_aggregations``
      3. longest-prefix match in ``pattern_mappings`` (key ends with ``/``)
    """
    if pointer in mappings:
        return mappings[pointer]
    if pointer in section_aggregations:
        return section_aggregations[pointer]
    best: str | None = None
    for prefix in pattern_mappings:
        if not prefix.endswith("/"):
            continue
        if pointer.startswith(prefix) and (best is None or len(prefix) > len(best)):
            best = prefix
    if best is not None:
        return pattern_mappings[best]
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def apps_lic_u0_adapt(
    raw_json: Mapping[str, Any],
    *,
    request_id: str | None = None,
    run_id: str | None = None,
) -> tuple[ValidatedRequest, AppsLicU0ReflectionReceipt]:
    """Validate raw apps_lic ingress JSON and emit ValidatedRequest + reflection receipt.

    Args:
        raw_json: The raw apps_lic ingress payload as a Python dict.
        request_id: Optional override for ValidatedRequest.request_id.
            If omitted, derived from raw_json['transport']['request_id'].
        run_id: Optional override for ValidatedRequest.run_id.

    Returns:
        Tuple (ValidatedRequest, AppsLicU0ReflectionReceipt).
        The receipt always has pass_status=True when returned — any failure raises.

    Raises:
        AppsLicU0AdapterError subclass for any domain, governance, or reflection
        failure. All are fail-closed — caller MUST treat any exception as terminal
        at U0. No business logic, routing, retrieval, execution, or L4 write occurs
        inside this function.
    """
    if not isinstance(raw_json, Mapping):
        raise AppsLicU0AdapterError(
            f"raw_json must be a mapping; got {type(raw_json).__name__}."
        )

    # 1. Pre-checks on raw input before Pydantic (pointed exceptions surface
    #    the specific failure mode rather than a generic ValidationError).
    transport_raw = raw_json.get("transport", {})
    campaign_raw = raw_json.get("campaign", {})
    fsm_raw = raw_json.get("forbidden_send_modes", {})
    entity_refs_raw = raw_json.get("entity_refs", {})
    pii_raw = raw_json.get("pii_policy", {})
    shield_raw = raw_json.get("governance_shield", {})
    antipattern_raw = raw_json.get("antipattern_policy", {})
    source_lineage_raw = raw_json.get("source_lineage", {})
    hitl_raw = raw_json.get("hitl_policy", {})

    _check_identity(transport_raw)
    _check_side_effect_class(campaign_raw)
    _check_workflow_required(campaign_raw)
    _check_grounding(campaign_raw)
    _check_forbidden_send_modes(fsm_raw)
    _check_identity_fields(entity_refs_raw, campaign_raw)
    _check_governance_fields(pii_raw, shield_raw, antipattern_raw, source_lineage_raw)
    _check_hitl_bypass(hitl_raw)

    # 2. Pydantic validation — catches shape errors, missing required fields,
    #    governed-value enum mismatches, and extra keys (extra='forbid').
    try:
        contract = AppsLicIngressContractV1.model_validate(raw_json)
    except ValidationError as exc:
        first = exc.errors()[0] if exc.errors() else None
        if first and first.get("type") == "missing":
            loc = ".".join(str(p) for p in first.get("loc", ()))
            raise AppsLicSchemaValidationError(
                f"Required field missing: {loc}. (E1 schema validation failure)"
            ) from exc
        raise AppsLicSchemaValidationError(
            f"Schema validation failed (E1): {exc.errors()}"
        ) from exc

    if contract.apps_lic_contract_version != APPS_LIC_INGRESS_CONTRACT_VERSION:
        raise AppsLicSchemaValidationError(
            f"apps_lic_contract_version mismatch: got "
            f"{contract.apps_lic_contract_version!r}, expected "
            f"{APPS_LIC_INGRESS_CONTRACT_VERSION!r}"
        )

    # 3. Canonical dump — deterministic (Pydantic model_dump is stable for
    #    frozen models with sorted-key JSON encoding downstream).
    contract_dump = contract.model_dump(mode="python")

    # 4. Reflection — enumerate every JSON Pointer from the validated dump.
    field_map = _load_field_map()
    field_map_version: str = field_map.get("version", "unknown")
    mappings: Mapping[str, Any] = field_map["mappings"]
    section_aggregations: Mapping[str, Any] = field_map.get("section_aggregations", {})
    pattern_mappings: Mapping[str, Any] = field_map.get("pattern_mappings", {})

    pointers = _enumerate_pointers(contract_dump)

    silently_dropped: list[str] = []
    unknown_mappings: list[str] = []
    counts: dict[str, int] = {"MAPPED": 0, "DERIVED": 0, "REJECTED": 0, "DEFERRED": 0}
    deferred_reasons: list[tuple[str, str]] = []

    for pointer in pointers:
        entry = _resolve_entry(pointer, mappings, section_aggregations, pattern_mappings)
        if entry is None:
            silently_dropped.append(pointer)
            continue
        status = entry.get("status")
        if status not in _PERMITTED_STATUSES:
            unknown_mappings.append(pointer)
            continue
        counts[status] += 1
        if status == "DEFERRED":
            reason = entry.get("reason", "")
            if not reason or not isinstance(reason, str) or reason.strip() == "":
                unknown_mappings.append(pointer)
                continue
            deferred_reasons.append((pointer, reason.strip()))

    # 5. Deterministic digests.
    input_digest = _sha256_hex(contract_dump)

    # 6. Build ValidatedRequest.
    transport = contract.transport
    effective_request_id = request_id or transport.request_id
    effective_run_id = run_id or transport.run_id
    timestamp_iso = datetime.now(timezone.utc).isoformat()

    auth_receipt = AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        request_id=effective_request_id,
        checked_fields=tuple(sorted(contract_dump.keys())),
        forbidden_fields_detected=(),
        matched_rule="apps_lic_ingress_contract_v1_extra_forbid",
        reason=(
            "apps_lic ingress contract v1 forbids unknown top-level keys via "
            "Pydantic extra='forbid'; governance fields validated by U0 domain checks"
        ),
        timestamp_iso=timestamp_iso,
        policy_version="1.0",
    )

    replay_audit = contract.replay_audit
    replay_refs_list = replay_audit.replay_refs if replay_audit.replay_refs else []
    replay_key = replay_refs_list[0] if replay_refs_list else ""
    snapshot_refs = tuple(replay_refs_list[1:]) if len(replay_refs_list) > 1 else ()
    audit_refs = tuple(replay_audit.audit_refs) if replay_audit.audit_refs else ()

    validated_request = ValidatedRequest(
        request_id=effective_request_id,
        run_id=effective_run_id,
        app_id="apps_lic",
        task_class="outreach_message",
        payload_digest=input_digest,
        authority_validation_receipt=auth_receipt,
        trace_id=transport.trace_id,
        tenant_id=transport.tenant_id,
        target_level="",
        replay_key=replay_key,
        snapshot_refs=snapshot_refs,
        audit_refs=audit_refs,
        posture=POSTURE_READ_ONLY,
        l5_certification_ref=_APPS_LIC_U0_ADAPTER_CERT_REF,
        app_payload=contract_dump,
        reflection_receipt=None,  # will be replaced via dataclasses.replace below
    )

    # 7. Compute validated_request_digest over a canonical projection (mirrors
    #    apps_rg adapter shape — excludes reflection_receipt to avoid circular
    #    dependency in the digest).
    vr_canonical = {
        "request_id": validated_request.request_id,
        "run_id": validated_request.run_id,
        "app_id": validated_request.app_id,
        "task_class": validated_request.task_class,
        "payload_digest": validated_request.payload_digest,
        "trace_id": validated_request.trace_id,
        "tenant_id": validated_request.tenant_id,
        "target_level": validated_request.target_level,
        "replay_key": validated_request.replay_key,
        "schema_version": validated_request.schema_version,
        "l5_certification_ref": validated_request.l5_certification_ref,
        "app_payload": contract_dump,
    }
    validated_request_digest = _sha256_hex(vr_canonical)

    pass_status = not silently_dropped and not unknown_mappings

    receipt = AppsLicU0ReflectionReceipt(
        contract_version=contract.apps_lic_contract_version,
        schema_version=APPS_LIC_INGRESS_CONTRACT_VERSION,
        field_map_version=field_map_version,
        input_payload_digest=input_digest,
        validated_request_digest=validated_request_digest,
        pointers_total=len(pointers),
        pointers_mapped=counts["MAPPED"],
        pointers_derived=counts["DERIVED"],
        pointers_rejected=counts["REJECTED"],
        pointers_deferred=counts["DEFERRED"],
        deferred_reasons=tuple(deferred_reasons),
        silently_dropped=tuple(silently_dropped),
        unknown_mappings=tuple(unknown_mappings),
        pass_status=pass_status,
        timestamp_iso=timestamp_iso,
    )

    if not pass_status:
        parts: list[str] = []
        if silently_dropped:
            parts.append(f"silently_dropped={list(silently_dropped)}")
        if unknown_mappings:
            parts.append(f"unknown_mappings={list(unknown_mappings)}")
        message = (
            "apps_lic U0 reflection failed. CORE RULE violated: a field may be "
            "deferred but a field may not disappear. " + "; ".join(parts)
        )
        if silently_dropped and not unknown_mappings:
            raise SilentlyDroppedFieldError(
                message,
                silently_dropped=tuple(silently_dropped),
                unknown_mappings=(),
                receipt=receipt,
            )
        if unknown_mappings and not silently_dropped:
            raise UnknownFieldMappingError(
                message,
                silently_dropped=(),
                unknown_mappings=tuple(unknown_mappings),
                receipt=receipt,
            )
        raise AppsLicU0ReflectionFailure(
            message,
            silently_dropped=tuple(silently_dropped),
            unknown_mappings=tuple(unknown_mappings),
            receipt=receipt,
        )

    # 8. Thread reflection_receipt into the ValidatedRequest.
    from dataclasses import replace
    validated_request = replace(validated_request, reflection_receipt=receipt)

    return validated_request, receipt


__all__ = [
    "AppsLicGovernanceFieldError",
    "AppsLicGroundingError",
    "AppsLicHitlBypassError",
    "AppsLicIdentityError",
    "AppsLicMissingIdentityError",
    "AppsLicForbiddenSendModeError",
    "AppsLicSchemaValidationError",
    "AppsLicSideEffectError",
    "AppsLicU0AdapterError",
    "AppsLicU0ReflectionFailure",
    "AppsLicU0ReflectionReceipt",
    "AppsLicWorkflowError",
    "SilentlyDroppedFieldError",
    "UnknownFieldMappingError",
    "apps_lic_u0_adapt",
]
