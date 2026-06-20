"""Healing-cascade SSOT registry — control_surface = "healing".

Per operator directive 2026-05-01 14:15 UTC-04:00, this module is the
single source of truth for the healing/remediation ladder. It is
deliberately SEPARATE from the RTC-REQ-056 judge panel registry in
``tools/certification/safety/rtc_req_056_panel.py``.

Hard rules (see .codex/rules/closed-loop-router-enforcement.md and
the control-surface separation directive):

  - Healing outputs may propose, repair, or generate remediation
    candidates; they are NEVER certification evidence.
  - Healing outputs MUST stamp ``control_surface = "healing"`` on every
    emission. The RTC-REQ-056 gate rejects any artifact with that
    surface.
  - The healing evidence tree is ``artifacts/healing/`` — never
    ``artifacts/certification/``.
  - ``GEMINI_PRO_MODEL_ID`` appears in BOTH this registry (as a healing
    tier) AND the judge panel (as a juror). The same model string serves
    both surfaces; separation is enforced by ``control_surface`` at the
    artifact level, not by model-id uniqueness.

This module imports low-level model-id strings from
``agentic_core.L0_routing.config.model_registry`` (which is a pure
string table with no control-surface semantics). It does NOT import
anything from ``tools/certification/``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

from agentic_core.L0_routing.config.model_registry import (  # guardian: allow-layer-violation -- model_registry SSOT at L0 config; healing registry reads canonical model-id strings only
    DETERMINISTIC_MODEL_SENTINEL,
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)

__all__ = [
    # Surface labels
    "CONTROL_SURFACE",
    "PURPOSE",
    "HEALING_EVIDENCE_ROOT",
    "HEALING_GEMINI_PRO_ENV_OVERRIDE",
    # Cascade
    "HEALING_CASCADE",
    "HealingTier",
    "DETERMINISTIC_TIER",
    "QWEN_TIER",
    "GEMINI_FLASH_TIER",
    "GEMINI_PRO_TIER",
    # Re-exported model-id strings (so healers source them from this SSOT,
    # not directly from L0 model_registry). Keeping them here means the
    # healing surface owns its own identity table while still pointing at
    # the same low-level string SSOT under the hood.
    "DETERMINISTIC_MODEL_SENTINEL",
    "GEMINI_FLASH_MODEL_ID",
    "GEMINI_PRO_MODEL_ID",
    "QWEN_LOCAL_MODEL_ID",
    # Helpers
    "get_healing_tier",
    "get_tier_by_model_id",
    "is_healing_model_id",
    "resolve_healing_gemini_pro_model_id",
    # Evidence stamp helper
    "build_healing_evidence_stamp",
]


# ---------------------------------------------------------------------------
# Surface labels — stamped on every healing emission
# ---------------------------------------------------------------------------

CONTROL_SURFACE: Final[str] = "healing"
PURPOSE: Final[str] = "remediation"

# On-disk evidence root. NEVER collides with artifacts/certification/.
HEALING_EVIDENCE_ROOT: Final[str] = "artifacts/healing"


# ---------------------------------------------------------------------------
# Healing-surface env-var override (isolated from judge panel)
# ---------------------------------------------------------------------------

HEALING_GOOGLE_AI_PRO_ENV_OVERRIDE: Final[str] = "HEALING_GOOGLE_AI_PRO_MODEL"
HEALING_GEMINI_PRO_ENV_OVERRIDE: Final[str] = "HEALING_GEMINI_MODEL"
"""Healing-only override for the Google AI pro tier's model id.

Judge panel MUST NOT consult this env var. Canonical: ``HEALING_GOOGLE_AI_PRO_MODEL``;
legacy alias: ``HEALING_GEMINI_MODEL``.
"""


def resolve_healing_gemini_pro_model_id() -> str:
    """Resolve the gemini_pro healing tier's model_id.

    Precedence:
      1. ``HEALING_GOOGLE_AI_PRO_MODEL`` (canonical healing override)
      2. ``HEALING_GEMINI_MODEL`` (deprecated alias)
      3. ``GEMINI_PRO_MODEL_ID`` registry default (from ``GOOGLE_AI_PRO_MODEL``)
    """
    from agentic_core.config.google_ai_env import healing_google_ai_pro_model_id

    model_id, _ = healing_google_ai_pro_model_id(registry_default=GEMINI_PRO_MODEL_ID)
    return model_id


# ---------------------------------------------------------------------------
# Cascade entries
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HealingTier:
    """One tier of the healing cascade.

    Attributes:
        tier: Canonical short name — one of deterministic / qwen /
            gemini_flash / gemini_pro.
        model_id: Model identifier used by this tier. ``None`` for the
            deterministic tier (rule-based, no model).
        confidence_band: Declared confidence band for the tier —
            high / medium_high / medium / low_confidence_escalation.
    """

    tier: str
    model_id: str | None
    confidence_band: str


DETERMINISTIC_TIER: Final[HealingTier] = HealingTier(
    tier="deterministic",
    model_id=None,
    confidence_band="high",
)

QWEN_TIER: Final[HealingTier] = HealingTier(
    tier="qwen",
    model_id=QWEN_LOCAL_MODEL_ID,
    confidence_band="medium_high",
)

GEMINI_FLASH_TIER: Final[HealingTier] = HealingTier(
    tier="gemini_flash",
    model_id=GEMINI_FLASH_MODEL_ID,
    confidence_band="medium",
)

GEMINI_PRO_TIER: Final[HealingTier] = HealingTier(
    tier="gemini_pro",
    model_id=GEMINI_PRO_MODEL_ID,
    confidence_band="low_confidence_escalation",
)


HEALING_CASCADE: Final[tuple[HealingTier, ...]] = (
    DETERMINISTIC_TIER,
    QWEN_TIER,
    GEMINI_FLASH_TIER,
    GEMINI_PRO_TIER,
)


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_healing_tier(tier_name: str) -> HealingTier | None:
    """Return the HealingTier matching ``tier_name`` (case-insensitive)."""
    if not tier_name:
        return None
    t = tier_name.strip().lower()
    for entry in HEALING_CASCADE:
        if entry.tier.lower() == t:
            return entry
    return None


def is_healing_model_id(model_id: str | None) -> bool:
    """True iff ``model_id`` matches any model used by the healing
    cascade. Note: ``GEMINI_PRO_MODEL_ID`` is shared with the judge
    panel; this helper returns True for it, so callers must disambiguate
    via ``control_surface`` rather than model_id alone.
    """
    if not model_id:
        return False
    for entry in HEALING_CASCADE:
        if entry.model_id is not None and entry.model_id == model_id:
            return True
    return False


def get_tier_by_model_id(model_id: str | None) -> HealingTier | None:
    """Return the first HealingTier whose ``model_id`` matches.
    Returns ``None`` for unknown / falsy ids. Note that the deterministic
    tier has ``model_id=None`` and is intentionally NOT returned here —
    callers that need the deterministic tier should look it up by name."""
    if not model_id:
        return None
    for entry in HEALING_CASCADE:
        if entry.model_id == model_id:
            return entry
    return None


# ---------------------------------------------------------------------------
# Evidence stamp builder — used by future durable healing emitters
# ---------------------------------------------------------------------------


_VALID_HEALING_ACTIONS: Final[frozenset[str]] = frozenset({
    "propose",
    "repair",
    "escalate",
    "deterministic_fix",
})


def build_healing_evidence_stamp(
    *,
    healing_tier: str,
    healing_action: str,
    healing_evidence_ref: str | None = None,
    confidence_band_override: str | None = None,
) -> dict[str, str | None]:
    """Build the canonical control-surface stamp for a healing evidence
    record. Includes ``control_surface``, ``purpose``, ``healing_tier``,
    ``healing_model_id``, ``healing_confidence_band``, ``healing_action``,
    and (optionally) ``healing_evidence_ref``.

    Raises:
        ValueError: if ``healing_tier`` is unknown or ``healing_action``
            is not in the allowed set.

    The returned dict is intentionally flat and JSON-serializable so it
    can be merged into any durable healing artifact (e.g. via
    ``stamp = build_healing_evidence_stamp(...); record.update(stamp)``).
    """
    tier = get_healing_tier(healing_tier)
    if tier is None:
        raise ValueError(
            f"unknown healing_tier {healing_tier!r}; "
            f"valid: {[t.tier for t in HEALING_CASCADE]}"
        )
    if healing_action not in _VALID_HEALING_ACTIONS:
        raise ValueError(
            f"unknown healing_action {healing_action!r}; "
            f"valid: {sorted(_VALID_HEALING_ACTIONS)}"
        )

    stamp: dict[str, str | None] = {
        "control_surface": CONTROL_SURFACE,
        "purpose": PURPOSE,
        "healing_tier": tier.tier,
        "healing_model_id": tier.model_id,
        "healing_confidence_band": (
            confidence_band_override or tier.confidence_band
        ),
        "healing_action": healing_action,
    }
    if healing_evidence_ref is not None:
        stamp["healing_evidence_ref"] = healing_evidence_ref
    return stamp
