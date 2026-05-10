"""AppsRgU0ReflectionReceipt — proof that every input JSON Pointer is accounted for.

Emitted by ``apps_rg_u0_adapt`` after running the apps_rg ingress contract
through the field-map reflection check. The receipt is the canonical artifact
that proves the U0 layer did not silently drop any input field.

A receipt with ``pass_status=True`` requires:
    - ``silently_dropped == ()``
    - ``unknown_mappings == ()``
    - every input pointer accounted for under one of MAPPED/DERIVED/REJECTED/DEFERRED
    - deterministic ``input_payload_digest`` (sha256 over canonical input JSON)
    - deterministic ``validated_request_digest`` (sha256 over canonical ValidatedRequest JSON)

A receipt with ``pass_status=False`` MUST never accompany a returned
``ValidatedRequest`` — the adapter raises ``AppsRgU0ReflectionFailure`` instead.

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md (W2.P2.2)
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AppsRgU0ReflectionReceipt:
    """Receipt produced by the apps_rg U0 reflection adapter."""

    contract_version: str
    """Validated contract version — MUST equal the on-disk contract module version."""

    schema_version: str
    """JSON Schema $id version used for validation."""

    field_map_version: str
    """Field-map YAML version that drove pointer reflection."""

    input_payload_digest: str
    """SHA-256 over canonical (sort_keys=True) JSON of the validated input payload."""

    validated_request_digest: str
    """SHA-256 over canonical JSON of the produced ValidatedRequest (excluding receipt itself)."""

    pointers_total: int
    """Count of distinct JSON Pointers enumerated from the input payload."""

    pointers_mapped: int
    """Count of pointers with status MAPPED in the field map."""

    pointers_derived: int
    """Count of pointers with status DERIVED."""

    pointers_rejected: int
    """Count of pointers with status REJECTED."""

    pointers_deferred: int
    """Count of pointers with status DEFERRED."""

    deferred_reasons: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    """Tuple of (pointer, reason) pairs for every DEFERRED pointer. Required
    for receipt validity — DEFERRED with no reason is treated as
    UNKNOWN_MAPPING."""

    silently_dropped: tuple[str, ...] = field(default_factory=tuple)
    """Tuple of input pointers that have no field-map entry. MUST be empty
    for ``pass_status=True``. Non-empty value is the canonical signal that
    a field disappeared between ingress and U0 — fail closed."""

    unknown_mappings: tuple[str, ...] = field(default_factory=tuple)
    """Tuple of pointers whose field-map entry has an unknown status (not in
    {MAPPED, DERIVED, REJECTED, DEFERRED}). MUST be empty."""

    pass_status: bool = False
    """True iff silently_dropped and unknown_mappings are both empty AND every
    DEFERRED pointer carries an explicit reason."""

    timestamp_iso: str = ""
    """ISO-8601 timestamp at which the receipt was emitted."""


__all__ = ["AppsRgU0ReflectionReceipt"]
