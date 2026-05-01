"""Section-level temperature resolver — wires MessagePlanner adjustments to HOP5.

W1-P3 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Problem this solves:
    HOP5GenerationAgent currently hardcodes two LLM temperatures:
      - K.3 body generation:        temperature=0.5 (hook section)
      - K.5A synthetic bullet:      temperature=0.7 (value section)
    These values ignore the archetype of the recipient. Industry data shows
    consistent opener temperature (hook ~0.3 for executives) and varied
    value-section temperature (~0.7 for senior audiences) correlates with
    higher reply rates.

Solution:
    MessagePlanner already defines per-(archetype, section) temperature
    adjustments — a delta relative to a base temperature. This module
    surfaces that table through a pure, testable function without
    requiring HOP5 to import MessagePlanner directly (HOP5 has a heavy
    dataclass / config dependency tree that makes direct integration
    awkward in tests).

Public surface:
    - ``resolve_section_temperature(archetype, section, base_temperature)``
    - ``SECTION_TEMPERATURE_CLAMP`` — the valid output range (0.0, 1.0)

The resolver degrades gracefully when the archetype or section is
unknown — returns the base temperature unchanged. This preserves the
HOP5 pre-wiring behaviour for any archetype label MessagePlanner does
not currently enumerate.
"""

from __future__ import annotations

from typing import Final, Mapping, Tuple

# (min, max) clamp for the final temperature returned to the LLM.
# LLM providers generally reject values outside this range; clamping
# inside this resolver centralises the invariant.
SECTION_TEMPERATURE_CLAMP: Final[Tuple[float, float]] = (0.0, 1.0)

# Per-archetype, per-section temperature deltas. Lifted from
# MessagePlanner.temperature_adjustments — duplicated here so the
# resolver does not require instantiating MessagePlanner (which pulls in
# logging + full L1 initialization). Keep in sync with the master table
# in apps_lic/L1_cognition/message_planner.py. The canonicalisation below
# also folds MessagePlanner's lowercase "executive" alias into the
# canonical EXECUTIVE label used by ProfilePlanner.
_SECTION_ADJUSTMENTS: Final[Mapping[str, Mapping[str, float]]] = {
    "RECRUITER": {
        "subject": -0.1,
        "hook": 0.0,
        "value": -0.1,
        "cta": 0.0,
        "signature": 0.0,
    },
    "SENIOR_TA": {
        "subject": 0.0,
        "hook": 0.1,
        "value": 0.0,
        "cta": -0.1,
        "signature": 0.0,
    },
    "EXECUTIVE": {
        "subject": -0.1,
        "hook": 0.0,
        "value": 0.0,
        "cta": 0.1,
        "signature": 0.1,
    },
    "C_LEVEL": {
        "subject": -0.2,
        "hook": -0.1,
        "value": -0.1,
        "cta": -0.1,
        "signature": -0.1,
    },
    "OTHER": {
        "subject": 0.0,
        "hook": 0.0,
        "value": 0.0,
        "cta": 0.0,
        "signature": 0.0,
    },
}


def resolve_section_temperature(
    archetype: str,
    section: str,
    base_temperature: float,
) -> float:
    """Return the archetype-adjusted LLM temperature for a message section.

    Applies the per-(archetype, section) delta from
    ``_SECTION_ADJUSTMENTS`` on top of ``base_temperature``. Unknown
    archetype or section falls back to the base temperature — safe
    default that preserves the pre-W1-P3 HOP5 behaviour.

    Args:
        archetype: One of the canonical ProfilePlanner labels
            (EXECUTIVE, C_LEVEL, SENIOR_TA, RECRUITER, OTHER). The
            lowercase "executive" alias used in MessagePlanner is also
            accepted and normalised. Unknown archetypes return the
            base temperature unchanged.
        section: Message section name. One of {"subject", "hook",
            "value", "cta", "signature"}. Unknown sections return the
            base temperature unchanged.
        base_temperature: The archetype-level baseline temperature
            provided by HOP5 (typically from
            ``generation_agent_config.base_temperatures[archetype]``).
            Must be a non-negative finite float.

    Returns:
        The adjusted temperature, clamped to
        ``SECTION_TEMPERATURE_CLAMP`` (currently ``(0.0, 1.0)``).
        Never raises — invalid inputs fall through to ``base_temperature``
        clamped.

    Examples:
        >>> resolve_section_temperature("EXECUTIVE", "hook", 0.5)
        0.5
        >>> resolve_section_temperature("C_LEVEL", "hook", 0.5)
        0.4
        >>> resolve_section_temperature("SENIOR_TA", "hook", 0.5)
        0.6
    """
    canonical = _canonicalise_archetype(archetype)
    adjustments = _SECTION_ADJUSTMENTS.get(canonical, _SECTION_ADJUSTMENTS["OTHER"])
    delta = adjustments.get(section, 0.0)
    raw = base_temperature + delta
    return _clamp(raw)


def _canonicalise_archetype(archetype: str) -> str:
    """Normalise archetype aliases to the canonical label set."""
    if archetype == "executive":
        return "EXECUTIVE"
    return archetype


def _clamp(value: float) -> float:
    """Clamp ``value`` to ``SECTION_TEMPERATURE_CLAMP``."""
    lo, hi = SECTION_TEMPERATURE_CLAMP
    if value < lo:
        return lo
    if value > hi:
        return hi
    return float(value)


__all__ = [
    "SECTION_TEMPERATURE_CLAMP",
    "resolve_section_temperature",
]
