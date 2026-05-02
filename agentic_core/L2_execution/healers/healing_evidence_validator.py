"""Healing evidence validator — shape-only, never certifying.

Per operator directive 2026-05-01 14:45 UTC-04:00.

This validator answers ONE question: "is this dict a well-formed
healing evidence record?" It is the symmetric counterpart to
``tools/certification/safety/rtc_req_056_gate.validate_panel_attestation``
for the healing surface — but the two MUST NEVER overlap:

  - This validator NEVER certifies a judge / RTC-REQ-056 panel.
  - It rejects ``control_surface != "healing"`` outright.
  - A document this validator accepts is, by construction, NOT a
    valid panel attestation (the RTC-REQ-056 gate rejects healing
    surface as its first check).

Validation rules:

  1. ``control_surface`` MUST equal ``"healing"`` — anything else is
     ``REJECT_NOT_HEALING_SURFACE`` (a healing-side reject code).
  2. ``purpose`` MUST equal ``"remediation"``.
  3. ``healing_tier`` MUST be one of the four canonical tiers
     (deterministic / qwen / gemini_flash / gemini_pro) — looked up
     via ``get_healing_tier``.
  4. ``healing_action`` MUST be one of: propose / repair / escalate /
     deterministic_fix.
  5. ``healing_confidence_band`` MUST be present and non-empty.
  6. ``healing_model_id`` rules:
     - ``deterministic`` tier: MUST be ``None`` (or absent / null).
     - ``qwen`` / ``gemini_flash`` / ``gemini_pro``: MUST be present
       and non-empty.
  7. ``healing_evidence_ref`` is OPTIONAL (some emitters do not point
     at an upstream chain).

The validator returns a structured ``HealingEvidenceVerdict`` and
never mutates input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.healers.healing_cascade_registry import (
    CONTROL_SURFACE as HEALING_CONTROL_SURFACE,
    PURPOSE as HEALING_PURPOSE,
    HEALING_CASCADE,
    get_healing_tier,
)

__all__ = [
    "HealingEvidenceRejectReason",
    "HealingEvidenceVerdict",
    "validate_healing_evidence",
]


_VALID_HEALING_ACTIONS = frozenset({
    "propose",
    "repair",
    "escalate",
    "deterministic_fix",
})


class HealingEvidenceRejectReason:
    """Healing-side rejection codes.

    DELIBERATELY DISJOINT from
    ``tools.certification.safety.rtc_req_056_panel.RejectReason`` so the
    two validators cannot accidentally share a code namespace.
    """

    REJECT_NOT_HEALING_SURFACE = "HEAL_REJECT_NOT_HEALING_SURFACE"
    REJECT_PURPOSE_MISMATCH = "HEAL_REJECT_PURPOSE_MISMATCH"
    REJECT_UNKNOWN_TIER = "HEAL_REJECT_UNKNOWN_TIER"
    REJECT_TIER_MISSING = "HEAL_REJECT_TIER_MISSING"
    REJECT_UNKNOWN_ACTION = "HEAL_REJECT_UNKNOWN_ACTION"
    REJECT_ACTION_MISSING = "HEAL_REJECT_ACTION_MISSING"
    REJECT_CONFIDENCE_BAND_MISSING = "HEAL_REJECT_CONFIDENCE_BAND_MISSING"
    REJECT_MODEL_ID_MISSING = "HEAL_REJECT_MODEL_ID_MISSING"
    REJECT_DETERMINISTIC_MUST_HAVE_NULL_MODEL = (
        "HEAL_REJECT_DETERMINISTIC_MUST_HAVE_NULL_MODEL"
    )
    REJECT_PAYLOAD_NOT_DICT = "HEAL_REJECT_PAYLOAD_NOT_DICT"


@dataclass(frozen=True)
class HealingEvidenceVerdict:
    accepted: bool
    reason_codes: tuple[str, ...]
    messages: tuple[str, ...]


def _append(
    codes: list[str], msgs: list[str], code: str, msg: str
) -> None:
    codes.append(code)
    msgs.append(f"[{code}] {msg}")


def validate_healing_evidence(payload: Any) -> HealingEvidenceVerdict:
    """Validate a healing evidence record. NEVER certifies judge output.

    Returns a verdict with ``accepted=True`` only when the payload is a
    fully formed healing record.
    """
    codes: list[str] = []
    msgs: list[str] = []

    if not isinstance(payload, dict):
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_PAYLOAD_NOT_DICT,
            f"payload is not a dict: type={type(payload).__name__}",
        )
        return HealingEvidenceVerdict(False, tuple(codes), tuple(msgs))

    # Rule 1: control_surface MUST be "healing"
    surface = payload.get("control_surface")
    if surface != HEALING_CONTROL_SURFACE:
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_NOT_HEALING_SURFACE,
            f"control_surface={surface!r} expected {HEALING_CONTROL_SURFACE!r}",
        )
        # Short-circuit: a non-healing document cannot be salvaged.
        # This is the symmetric mirror of the RTC-REQ-056 gate's
        # surface-first short-circuit.
        return HealingEvidenceVerdict(False, tuple(codes), tuple(msgs))

    # Rule 2: purpose MUST be "remediation"
    purpose = payload.get("purpose")
    if purpose != HEALING_PURPOSE:
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_PURPOSE_MISMATCH,
            f"purpose={purpose!r} expected {HEALING_PURPOSE!r}",
        )

    # Rule 3: healing_tier present + valid
    tier_name = payload.get("healing_tier")
    tier = None
    if not tier_name:
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_TIER_MISSING,
            "healing_tier is missing or empty",
        )
    else:
        tier = get_healing_tier(tier_name)
        if tier is None:
            _append(
                codes, msgs,
                HealingEvidenceRejectReason.REJECT_UNKNOWN_TIER,
                f"healing_tier={tier_name!r} not in "
                f"{[t.tier for t in HEALING_CASCADE]}",
            )

    # Rule 4: healing_action present + valid
    action = payload.get("healing_action")
    if not action:
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_ACTION_MISSING,
            "healing_action is missing or empty",
        )
    elif action not in _VALID_HEALING_ACTIONS:
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_UNKNOWN_ACTION,
            f"healing_action={action!r} not in "
            f"{sorted(_VALID_HEALING_ACTIONS)}",
        )

    # Rule 5: healing_confidence_band present and non-empty
    band = payload.get("healing_confidence_band")
    if not band:
        _append(
            codes, msgs,
            HealingEvidenceRejectReason.REJECT_CONFIDENCE_BAND_MISSING,
            "healing_confidence_band is missing or empty",
        )

    # Rule 6: healing_model_id rules — deterministic must be None, others
    # must be present.
    model_id_present = "healing_model_id" in payload
    model_id_value = payload.get("healing_model_id")

    if tier is not None:
        if tier.tier == "deterministic":
            # deterministic MUST be None (or absent — both treated as null)
            if model_id_present and model_id_value is not None:
                _append(
                    codes, msgs,
                    HealingEvidenceRejectReason.REJECT_DETERMINISTIC_MUST_HAVE_NULL_MODEL,
                    f"deterministic tier requires healing_model_id=None, "
                    f"got {model_id_value!r}",
                )
        else:
            # Non-deterministic tiers MUST have a non-empty model_id
            if not model_id_value:
                _append(
                    codes, msgs,
                    HealingEvidenceRejectReason.REJECT_MODEL_ID_MISSING,
                    f"healing_model_id is required for tier {tier.tier!r}",
                )

    # healing_evidence_ref is optional — no rule needed.

    accepted = not codes
    return HealingEvidenceVerdict(accepted, tuple(codes), tuple(msgs))
