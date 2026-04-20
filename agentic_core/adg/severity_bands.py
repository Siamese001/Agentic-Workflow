"""Single Source of Truth (SSOT) for ADG severity levels and priority bands.

This module is the canonical definition of:
- ADG Severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Priority bands (P0, P1, P2, P3)
- The 1-to-1 mapping between them
- Canonical band labels used in reports

All ADG-related code that needs to map a severity to a band, or vice versa,
MUST import from this module instead of hardcoding strings or inline dicts.

Mapping contract (invariant):
    CRITICAL <-> P0 (layer/architectural violations)
    HIGH     <-> P1 (high-severity anti-patterns)
    MEDIUM   <-> P2 (medium-severity anti-patterns)
    LOW      <-> P3 (style warnings / low-severity)

Usage:
    from agentic_core.adg.severity_bands import (
        Severity, Band,
        SEVERITY_TO_BAND, BAND_TO_SEVERITY,
        BAND_LABELS, BAND_ORDER,
        severity_to_band, band_to_severity,
    )

    band = severity_to_band("CRITICAL")       # -> "P0"
    severity = band_to_severity("P2")         # -> "MEDIUM"
    label = BAND_LABELS["P1"]                 # -> "anti_patterns_high"
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class Severity(str, Enum):
    """Canonical ADG severity levels, stored as strings in the violations table."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Band(str, Enum):
    """Canonical priority bands used in burndown reports and ratchet gates."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


# --- Authoritative 1-to-1 mappings ---

SEVERITY_TO_BAND: Final[dict[str, str]] = {
    Severity.CRITICAL.value: Band.P0.value,
    Severity.HIGH.value: Band.P1.value,
    Severity.MEDIUM.value: Band.P2.value,
    Severity.LOW.value: Band.P3.value,
}

BAND_TO_SEVERITY: Final[dict[str, str]] = {
    Band.P0.value: Severity.CRITICAL.value,
    Band.P1.value: Severity.HIGH.value,
    Band.P2.value: Severity.MEDIUM.value,
    Band.P3.value: Severity.LOW.value,
}

# Canonical human-readable labels per band (used in burndown summary.<band>.label).
BAND_LABELS: Final[dict[str, str]] = {
    Band.P0.value: "layer_violations",
    Band.P1.value: "anti_patterns_high",
    Band.P2.value: "anti_patterns_medium",
    Band.P3.value: "style_warnings",
}

# Canonical descriptions for each band.
BAND_DESCRIPTIONS: Final[dict[str, str]] = {
    Band.P0.value: "Critical layer/architectural violations (SC-1 layer gravity, cycles, dynamic exec, or CRITICAL antipatterns)",
    Band.P1.value: "High-severity anti-patterns (broad exception handling in production layers)",
    Band.P2.value: "Medium-severity anti-patterns (silent swallow, return-none, default masking, retry, etc.)",
    Band.P3.value: "Low-severity style warnings (global mutation, hardcoded paths, throw-for-normal-flow)",
}

# Canonical ordering for iteration and sorting.
BAND_ORDER: Final[tuple[str, ...]] = (Band.P0.value, Band.P1.value, Band.P2.value, Band.P3.value)
SEVERITY_ORDER: Final[tuple[str, ...]] = (
    Severity.CRITICAL.value,
    Severity.HIGH.value,
    Severity.MEDIUM.value,
    Severity.LOW.value,
)

# Top-level burndown field names keyed by band. This is the SSOT for the
# flat-keys section of adg_burndown_table.json so downstream consumers never
# guess string literals.
BAND_TOP_LEVEL_KEYS: Final[dict[str, str]] = {
    Band.P0.value: "P0_layer_violations",
    Band.P1.value: "P1_anti_patterns",
    Band.P2.value: "P2_anti_patterns_medium",
    Band.P3.value: "P3_style",
}


def severity_to_band(severity: str) -> str:
    """Map an ADG severity string to its priority band.

    Raises:
        ValueError: if the severity is not one of the canonical values.
    """
    try:
        return SEVERITY_TO_BAND[severity]
    except KeyError as exc:
        raise ValueError(
            f"Unknown severity {severity!r}; expected one of {list(SEVERITY_TO_BAND)}"
        ) from exc


def band_to_severity(band: str) -> str:
    """Map a priority band string to its canonical ADG severity.

    Raises:
        ValueError: if the band is not one of the canonical values.
    """
    try:
        return BAND_TO_SEVERITY[band]
    except KeyError as exc:
        raise ValueError(
            f"Unknown band {band!r}; expected one of {list(BAND_TO_SEVERITY)}"
        ) from exc


def normalize_band(value: str) -> str:
    """Accept either a severity or a band string and return the band.

    Useful for tolerant parsers of mixed-origin data.
    """
    if value in BAND_TO_SEVERITY:
        return value
    if value in SEVERITY_TO_BAND:
        return SEVERITY_TO_BAND[value]
    raise ValueError(
        f"Unknown severity/band {value!r}; expected severity in "
        f"{list(SEVERITY_TO_BAND)} or band in {list(BAND_TO_SEVERITY)}"
    )


__all__ = [
    "Band",
    "BAND_DESCRIPTIONS",
    "BAND_LABELS",
    "BAND_ORDER",
    "BAND_TO_SEVERITY",
    "BAND_TOP_LEVEL_KEYS",
    "SEVERITY_ORDER",
    "SEVERITY_TO_BAND",
    "Severity",
    "band_to_severity",
    "normalize_band",
    "severity_to_band",
]
