"""apps_rg U0 reflection adapter — contract-first ingress hardening.

This adapter is the canonical bridge between raw apps_rg ingress JSON and the
core ``ValidatedRequest`` contract. It proves every input JSON Pointer is
accounted for via the field-map SSOT, and fails closed on any of:

    - Pydantic schema validation failure
    - missing required field
    - missing jd_hash
    - invalid jd_payload structure
    - unknown generation_mode
    - missing policy refs (any field under /profile_manifest/*)
    - missing replay_key
    - silently dropped field (input pointer with no field-map entry)
    - unknown mapping (field-map status outside MAPPED/DERIVED/REJECTED/DEFERRED)

CORE RULE: a field may be deferred. A field may not disappear.

Adapter contract:
    ``apps_rg_u0_adapt(raw_json: dict) -> tuple[ValidatedRequest, AppsRgU0ReflectionReceipt]``

The adapter:
    1. Validates raw JSON against ``AppsRgIngressContractV1`` (Pydantic + JSON schema)
    2. Performs constraint checks (jd_hash, replay_key, policy refs, generation_mode)
    3. Enumerates JSON Pointers from the input payload
    4. Looks up each pointer in ``apps_rg_ingress_field_map.v1.yaml``
    5. Emits ``AppsRgU0ReflectionReceipt`` with deterministic digests
    6. Builds a ``ValidatedRequest`` preserving the full apps_rg payload under ``app_payload``
    7. Returns the tuple — or raises one of the named exceptions

The adapter does NOT execute any apps_rg business logic. It does not call the
L1/L0/C0/PA/L2/Exit layers. It is a pure validator + reflector.

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md (W2.P2.2)
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml
from pydantic import ValidationError

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.u0.reflection_receipt import AppsRgU0ReflectionReceipt
from apps_rg.contracts.apps_rg_ingress_contract_v1 import (
    APPS_RG_INGRESS_CONTRACT_VERSION,
    AppsRgIngressContractV1,
    GenerationMode,
)


# ---------------------------------------------------------------------------
# Exceptions — all derive from AppsRgU0AdapterError so callers can catch
# either a specific failure or "any reflection failure".
# ---------------------------------------------------------------------------


class AppsRgU0AdapterError(Exception):
    """Base class for all apps_rg U0 adapter failures (fail-closed signals)."""


class AppsRgU0ReflectionFailure(AppsRgU0AdapterError):
    """Reflection check failed — silently dropped fields or unknown mappings.

    This exception is the canonical signal that a field disappeared between
    apps_rg ingress and U0. Carries the offending pointers so the caller can
    update either the contract, the field map, or the input payload.
    """

    def __init__(self, message: str, *, silently_dropped: tuple[str, ...] = (),
                 unknown_mappings: tuple[str, ...] = (), receipt: AppsRgU0ReflectionReceipt | None = None) -> None:
        super().__init__(message)
        self.silently_dropped = silently_dropped
        self.unknown_mappings = unknown_mappings
        self.receipt = receipt


class MissingRequiredFieldError(AppsRgU0AdapterError):
    """A field declared required in the contract is missing from the input."""


class MissingJdHashError(AppsRgU0AdapterError):
    """``/jd_payload/jd_hash`` is missing or empty."""


class InvalidJdPayloadError(AppsRgU0AdapterError):
    """``/jd_payload`` is malformed (missing required substructure)."""


class UnknownGenerationModeError(AppsRgU0AdapterError):
    """``/generation_mode`` value is not in the GenerationMode enum."""


class MissingPolicyRefsError(AppsRgU0AdapterError):
    """One or more required fields under ``/profile_manifest/*`` are missing or empty."""


class MissingReplayKeyError(AppsRgU0AdapterError):
    """``/replay/replay_key`` is missing or empty."""


class SilentlyDroppedFieldError(AppsRgU0ReflectionFailure):
    """Specific reflection-failure subclass for silently dropped fields."""


class UnknownFieldMappingError(AppsRgU0ReflectionFailure):
    """Specific reflection-failure subclass for unknown field-map status."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


_PERMITTED_STATUSES: frozenset[str] = frozenset({"MAPPED", "DERIVED", "REJECTED", "DEFERRED"})
"""Statuses that are valid in the field-map. Anything else → UNKNOWN_MAPPING."""

_REQUIRED_POLICY_REFS: tuple[str, ...] = (
    "manifest_digest",
    "prompt_registry_ref",
    "hitl_policy_ref",
    "l0_policy_ref",
    "agent_spec_ref",
    "thresholds_ref",
)
"""Sub-keys under /profile_manifest that must be non-empty. ``profile_refs`` is
intentionally NOT in this list because it may be empty (no profiles bound)."""

_APPS_RG_U0_ADAPTER_CERT_REF: str = "u0-apps-rg-reflection-adapter-79d032"
"""L5 certification reference identifying this adapter as the producer of the
ValidatedRequest. Per ``verify_certification_ref``, any non-empty string is
structurally valid."""

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_FIELD_MAP_PATH: Path = _REPO_ROOT / "apps_rg" / "contracts" / "apps_rg_ingress_field_map.v1.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _canonical_json_bytes(obj: Any) -> bytes:
    """Canonical JSON encoding for digest computation: sorted keys, UTF-8, no whitespace."""

    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_hex(obj: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(obj)).hexdigest()


def _enumerate_pointers(obj: Any, prefix: str = "") -> list[str]:
    """Walk a dict/list-of-leaves payload and emit every JSON Pointer.

    Per RFC 6901: '/foo/0/bar'. The root pointer is '' (empty string). For
    the apps_rg contract we never emit the empty root — every key under the
    root has its own pointer.

    Tuples and lists are treated structurally identically — index pointers
    are emitted (`/formats/0`, `/formats/1`). For inputs that are tuples of
    homogeneous strings (e.g. ``capability_requirements``), the element
    pointers are returned so the field map can either enumerate them
    individually or accept the parent pointer as DEFERRED.

    To keep field-map size tractable, we treat homogeneous primitive
    sequences (tuple/list of int|float|str|bool|None) as opaque — we emit
    the parent pointer only and skip element pointers. Sequences containing
    objects (dict items) get full element walking.
    """

    pointers: list[str] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            child_prefix = f"{prefix}/{key}"
            pointers.append(child_prefix)
            pointers.extend(_enumerate_pointers(value, child_prefix))
    elif isinstance(obj, (list, tuple)):
        # Determine if homogeneous primitive sequence
        is_primitive_seq = all(
            isinstance(item, (str, int, float, bool, type(None))) for item in obj
        )
        if is_primitive_seq:
            return pointers  # parent pointer only — elements are opaque
        for idx, item in enumerate(obj):
            child_prefix = f"{prefix}/{idx}"
            pointers.append(child_prefix)
            pointers.extend(_enumerate_pointers(item, child_prefix))
    # Primitives are leaves — no further pointers below this level.

    return pointers


def _load_field_map() -> Mapping[str, Any]:
    """Load and minimally validate the field-map YAML."""

    if not _FIELD_MAP_PATH.exists():
        raise AppsRgU0AdapterError(
            f"Field-map SSOT missing at {_FIELD_MAP_PATH}. The harness cannot "
            "operate without it — fail closed."
        )
    with open(_FIELD_MAP_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise AppsRgU0AdapterError(f"Field-map at {_FIELD_MAP_PATH} did not parse as a mapping.")
    if "mappings" not in data or not isinstance(data["mappings"], dict):
        raise AppsRgU0AdapterError("Field-map missing 'mappings' section.")
    if "version" not in data:
        raise AppsRgU0AdapterError("Field-map missing 'version' field.")
    return data


def _check_required_policy_refs(profile_manifest: Mapping[str, Any]) -> None:
    missing: list[str] = []
    for key in _REQUIRED_POLICY_REFS:
        value = profile_manifest.get(key)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(f"/profile_manifest/{key}")
    if missing:
        raise MissingPolicyRefsError(
            f"Required policy refs missing or empty: {missing}. "
            "These are MANDATORY per AG-1.d manifest-bundled boundary."
        )


def _check_jd_payload(jd: Mapping[str, Any]) -> None:
    if not isinstance(jd, Mapping):
        raise InvalidJdPayloadError(
            f"/jd_payload must be a JSON object; got {type(jd).__name__}."
        )
    jd_hash = jd.get("jd_hash")
    if jd_hash is None or (isinstance(jd_hash, str) and jd_hash.strip() == ""):
        raise MissingJdHashError("/jd_payload/jd_hash is missing or empty.")
    jd_text = jd.get("jd_text")
    if jd_text is None or (isinstance(jd_text, str) and jd_text.strip() == ""):
        raise InvalidJdPayloadError("/jd_payload/jd_text is missing or empty.")
    if isinstance(jd_text, str) and jd_text == "<empty>":
        raise InvalidJdPayloadError(
            "/jd_payload/jd_text is the '<empty>' placeholder — the JD ref file "
            "was not found or could not be read. Pass a valid --jd file path."
        )


def _check_replay_key(replay: Mapping[str, Any]) -> None:
    rk = replay.get("replay_key")
    if rk is None or (isinstance(rk, str) and rk.strip() == ""):
        raise MissingReplayKeyError("/replay/replay_key is missing or empty.")


def _check_generation_mode(value: Any) -> GenerationMode:
    if not isinstance(value, str):
        raise UnknownGenerationModeError(
            f"/generation_mode must be a string; got {type(value).__name__}."
        )
    try:
        return GenerationMode(value)
    except ValueError as exc:
        valid = sorted(m.value for m in GenerationMode)
        raise UnknownGenerationModeError(
            f"/generation_mode={value!r} is not a recognized mode. Valid: {valid}."
        ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def apps_rg_u0_adapt(
    raw_json: Mapping[str, Any],
    *,
    request_id: str | None = None,
    run_id: str | None = None,
) -> tuple[ValidatedRequest, AppsRgU0ReflectionReceipt]:
    """Validate raw apps_rg JSON and emit a ValidatedRequest plus reflection receipt.

    Args:
        raw_json: The raw apps_rg ingress payload as a Python dict (already
            JSON-decoded). Will be validated against ``AppsRgIngressContractV1``.
        request_id: Optional override for the ``ValidatedRequest.request_id``.
            If omitted, derived from ``raw_json['transport']['request_id']``.
        run_id: Optional override for the ``ValidatedRequest.run_id``. If
            omitted, derived from ``raw_json['transport']['run_id']``.

    Returns:
        Tuple ``(ValidatedRequest, AppsRgU0ReflectionReceipt)``. The receipt
        always has ``pass_status=True`` when returned — any failure raises.

    Raises:
        AppsRgU0AdapterError: subclass-specific. See module-level exception
            hierarchy. All are fail-closed signals — the caller MUST treat
            any exception as terminal at U0.
    """

    # 1. Domain-specific pre-checks on raw input (raise pointed exceptions
    #    BEFORE Pydantic shape validation so the specific failure mode is
    #    visible to callers — e.g. an empty jd_hash surfaces as
    #    MissingJdHashError rather than a generic Pydantic string_too_short).
    if not isinstance(raw_json, Mapping):
        raise AppsRgU0AdapterError(
            f"raw_json must be a mapping; got {type(raw_json).__name__}."
        )
    _check_jd_payload(raw_json.get("jd_payload", {}))
    _check_replay_key(raw_json.get("replay", {}))
    if "generation_mode" in raw_json:
        # Only run the enum check if the field is present — Pydantic handles
        # the "missing required field" case with a MissingRequiredFieldError.
        _check_generation_mode(raw_json["generation_mode"])
    _check_required_policy_refs(raw_json.get("profile_manifest", {}))

    # 2. Pydantic validation (catches schema-shape errors, missing required, etc.)
    try:
        contract = AppsRgIngressContractV1.model_validate(raw_json)
    except ValidationError as exc:
        # Surface a more pointed message for the most common case: missing required field.
        first_error = exc.errors()[0] if exc.errors() else None
        if first_error and first_error.get("type") == "missing":
            loc = ".".join(str(p) for p in first_error.get("loc", ()))
            raise MissingRequiredFieldError(
                f"Required field missing: {loc}. (pydantic: {first_error.get('msg')})"
            ) from exc
        raise AppsRgU0AdapterError(f"Schema validation failed: {exc.errors()}") from exc

    if contract.apps_rg_contract_version != APPS_RG_INGRESS_CONTRACT_VERSION:
        raise AppsRgU0AdapterError(
            f"apps_rg_contract_version mismatch: got {contract.apps_rg_contract_version!r}, "
            f"expected {APPS_RG_INGRESS_CONTRACT_VERSION!r}."
        )

    # 3. Reflection — enumerate every JSON Pointer in the input
    field_map = _load_field_map()
    field_map_version: str = field_map.get("version", "unknown")
    mappings: Mapping[str, Mapping[str, Any]] = field_map["mappings"]
    section_aggregations: Mapping[str, Mapping[str, Any]] = field_map.get("section_aggregations", {})
    pattern_mappings: Mapping[str, Mapping[str, Any]] = field_map.get("pattern_mappings", {})

    # Walk the contract dump (canonical, deterministic).
    contract_dump = contract.model_dump(mode="python")
    pointers = _enumerate_pointers(contract_dump)

    silently_dropped: list[str] = []
    unknown_mappings: list[str] = []
    counts: dict[str, int] = {"MAPPED": 0, "DERIVED": 0, "REJECTED": 0, "DEFERRED": 0}
    deferred_reasons: list[tuple[str, str]] = []

    def _resolve_entry(pointer: str) -> Mapping[str, Any] | None:
        """Resolve a pointer to a field-map entry.

        Resolution order (first hit wins):
            1. exact match in ``mappings``
            2. exact match in ``section_aggregations``
            3. longest-prefix match in ``pattern_mappings`` where the key
               ends with ``/`` and is a strict prefix of the pointer

        Returning ``None`` means the pointer is uncovered → silently dropped.
        """

        if pointer in mappings:
            return mappings[pointer]
        if pointer in section_aggregations:
            return section_aggregations[pointer]
        # Longest-prefix wins so e.g. "/profile_manifest/profile_refs/foo" picks
        # "/profile_manifest/profile_refs/" over a shorter "/profile_manifest/".
        best_prefix: str | None = None
        for prefix in pattern_mappings:
            if not prefix.endswith("/"):
                continue
            if pointer.startswith(prefix) and (best_prefix is None or len(prefix) > len(best_prefix)):
                best_prefix = prefix
        if best_prefix is not None:
            return pattern_mappings[best_prefix]
        return None

    for pointer in pointers:
        entry = _resolve_entry(pointer)
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
                # DEFERRED without an explicit reason is treated as UNKNOWN_MAPPING
                unknown_mappings.append(pointer)
                continue
            deferred_reasons.append((pointer, reason.strip()))

    # 4. Build deterministic digests
    input_digest = _sha256_hex(contract_dump)

    # 5. Build ValidatedRequest BEFORE the receipt so we can include the
    #    validated_request_digest in the receipt. The digest is computed over
    #    the canonical fields (excluding the receipt itself, which doesn't
    #    appear on ValidatedRequest).
    transport = raw_json["transport"]
    effective_request_id = request_id or transport["request_id"]
    effective_run_id = run_id or transport["run_id"]

    # Build authority validation receipt — for v1 contract there are no
    # forbidden fields possible (Pydantic extra=forbid + the contract has no
    # authority field shape). We construct a passing receipt to satisfy the
    # ValidatedRequest contract.
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AuthorityValidationReceipt,
    )
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    auth_receipt = AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        request_id=effective_request_id,
        checked_fields=tuple(sorted(contract_dump.keys())),
        forbidden_fields_detected=(),
        matched_rule="apps_rg_ingress_contract_v1_extra_forbid",
        reason="apps_rg ingress contract v1 forbids unknown top-level keys via Pydantic extra='forbid'",
        timestamp_iso=timestamp_iso,
        policy_version="1.0",
    )

    validated_request = ValidatedRequest(
        request_id=effective_request_id,
        run_id=effective_run_id,
        app_id="apps_rg",
        task_class=contract.transport.task_class,
        payload_digest=input_digest,
        authority_validation_receipt=auth_receipt,
        trace_id=contract.transport.trace_id,
        tenant_id=contract.transport.tenant_id,
        target_level=contract.target.level,
        replay_key=contract.replay.replay_key,
        l5_certification_ref=_APPS_RG_U0_ADAPTER_CERT_REF,
        app_payload=contract_dump,
    )

    # Compute validated_request_digest over a canonical, JSON-safe projection.
    validated_request_canonical = {
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
    validated_request_digest = _sha256_hex(validated_request_canonical)

    pass_status = not silently_dropped and not unknown_mappings

    receipt = AppsRgU0ReflectionReceipt(
        contract_version=contract.apps_rg_contract_version,
        schema_version=APPS_RG_INGRESS_CONTRACT_VERSION,
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
        msg_parts: list[str] = []
        if silently_dropped:
            msg_parts.append(f"silently_dropped={list(silently_dropped)}")
        if unknown_mappings:
            msg_parts.append(f"unknown_mappings={list(unknown_mappings)}")
        message = (
            "apps_rg U0 reflection failed. CORE RULE violated: a field may be "
            "deferred but a field may not disappear. " + "; ".join(msg_parts)
        )
        if silently_dropped and not unknown_mappings:
            raise SilentlyDroppedFieldError(
                message, silently_dropped=tuple(silently_dropped),
                unknown_mappings=(), receipt=receipt,
            )
        if unknown_mappings and not silently_dropped:
            raise UnknownFieldMappingError(
                message, silently_dropped=(),
                unknown_mappings=tuple(unknown_mappings), receipt=receipt,
            )
        raise AppsRgU0ReflectionFailure(
            message, silently_dropped=tuple(silently_dropped),
            unknown_mappings=tuple(unknown_mappings), receipt=receipt,
        )

    return validated_request, receipt


__all__ = [
    "AppsRgU0AdapterError",
    "AppsRgU0ReflectionFailure",
    "InvalidJdPayloadError",
    "MissingJdHashError",
    "MissingPolicyRefsError",
    "MissingReplayKeyError",
    "MissingRequiredFieldError",
    "SilentlyDroppedFieldError",
    "UnknownFieldMappingError",
    "UnknownGenerationModeError",
    "apps_rg_u0_adapt",
]
