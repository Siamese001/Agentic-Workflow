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

import os
import re
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
        raise ValueError(f"Unknown severity {severity!r}; expected one of {list(SEVERITY_TO_BAND)}") from exc


def band_to_severity(band: str) -> str:
    """Map a priority band string to its canonical ADG severity.

    Raises:
        ValueError: if the band is not one of the canonical values.
    """
    try:
        return BAND_TO_SEVERITY[band]
    except KeyError as exc:
        raise ValueError(f"Unknown band {band!r}; expected one of {list(BAND_TO_SEVERITY)}") from exc


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


# =============================================================================
# ADR-024 Part B — SURFACE_OVERRIDE (W15, 2026-04-24)
#
# Surface/layer-aware severity promotions. Applied AFTER the base band lookup
# when SURFACE_OVERRIDE_ENABLED is truthy.
#
# OQ resolutions (ADR-024, 2026-04-24, confidence=0.81, gap=0.42):
#   OQ#1: heuristic file-path markers (not ADG graph labels)
#   OQ#2: env-flag P1_RATCHET_POLICY_V2 defaults OFF, flips ON after W5 burndown
#   OQ#3: SC-1 deferred to sibling ADR-025
#
# When the feature flag is OFF, effective_severity() returns the base severity
# unchanged — zero behavior change. When ON, (pattern_kind, surface_marker)
# pairs in SURFACE_OVERRIDE promote the severity.
# =============================================================================

# Feature-flag env var. ``1``/``true``/``yes``/``on`` (case-insensitive) = ON.
# Any other value (incl. missing) = OFF. Read once at module import; callers
# that need dynamic toggling should use is_surface_override_enabled().
_FLAG_ENV_VAR: Final[str] = "P1_RATCHET_POLICY_V2"


def is_surface_override_enabled() -> bool:
    """Return True iff the ADR-024 Part B feature flag is active.

    Reads ``P1_RATCHET_POLICY_V2`` from the environment each call so test
    harnesses can toggle the flag via ``monkeypatch.setenv``.
    """
    raw = os.environ.get(_FLAG_ENV_VAR, "")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# Heuristic surface markers derived from file path (OQ#1 resolution).
#
# Each marker is a set of regex patterns; a file matches the marker if ANY
# pattern matches. A file may match multiple markers (e.g. an L5 safety file
# is also "prod").
#
# Markers:
#   write          — Write Surface (mutates state of record)
#   prod           — not under tests/, tools/, ops_scripts/, docs/
#   L0_critical    — high fan_in in L0_routing (hotspot; see SURFACE_OVERRIDE)
#   L5_critical    — high fan_in in L5_safety (hotspot; see SURFACE_OVERRIDE)
#   L0             — any L0_routing file
#   L5             — any L5_safety file
#
# Note: L0_critical / L5_critical use the same regex as L0/L5 in this heuristic
# implementation because fan_in is not available at severity-lookup time. The
# full graph-label upgrade is deferred per OQ#1 resolution.
_NON_PROD_PATH_RE: Final[re.Pattern[str]] = re.compile(
    r"(^|[/\\])(tests?|tools|ops_scripts|docs|archives?)[/\\]",
)
_WRITE_PATH_RES: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"agentic_core[/\\]L4_state[/\\]"),
    re.compile(r"write_gateway"),
    re.compile(r"memory_authority"),
    re.compile(r"checkpoint"),
    re.compile(r"commit_versioned"),
)
_L0_PATH_RE: Final[re.Pattern[str]] = re.compile(r"agentic_core[/\\]L0_routing[/\\]")
_L5_PATH_RE: Final[re.Pattern[str]] = re.compile(r"agentic_core[/\\]L5_safety[/\\]")


def resolve_surface_markers(file_path: str) -> frozenset[str]:
    """Return the set of heuristic surface markers that apply to ``file_path``.

    Pure function, no I/O. Accepts both forward- and back-slash separators.
    Empty/None-like input returns an empty set.
    """
    if not file_path:
        return frozenset()
    markers: set[str] = set()
    # Write surface
    if any(p.search(file_path) for p in _WRITE_PATH_RES):
        markers.add("write")
    # Prod (inverse match on non-prod roots)
    if not _NON_PROD_PATH_RE.search(file_path):
        markers.add("prod")
    # L0 / L5 layer markers (file-path heuristic)
    if _L0_PATH_RE.search(file_path):
        markers.add("L0")
        markers.add("L0_critical")  # see header note on heuristic equivalence
    if _L5_PATH_RE.search(file_path):
        markers.add("L5")
        markers.add("L5_critical")
    return frozenset(markers)


# Promotion table — (pattern_kind, surface_marker) → elevated severity.
# Ordering within a row set is NOT significant; the caller iterates all markers
# for a file and applies the highest-severity override that matches.
SURFACE_OVERRIDE: Final[dict[tuple[str, str], str]] = {
    ("partial_side_effects", "write"): Severity.HIGH.value,  # P2 → P1
    ("default_fallback_masking", "write"): Severity.HIGH.value,  # P2 → P1
    ("retry_without_backoff", "prod"): Severity.HIGH.value,  # P2 → P1
    ("global_state_mutation", "L0_critical"): Severity.MEDIUM.value,  # P3 → P2
    ("global_state_mutation", "L5_critical"): Severity.MEDIUM.value,  # P3 → P2
    ("broad_exception_catch", "L5"): Severity.MEDIUM.value,  # P3 → P2
    ("silent_exception_swallow", "L0"): Severity.HIGH.value,  # P3 → P1
    ("silent_exception_swallow", "L5"): Severity.HIGH.value,  # P3 → P1
    ("log_and_swallow", "L0"): Severity.HIGH.value,  # P3 → P1
    ("log_and_swallow", "L5"): Severity.HIGH.value,  # P3 → P1
}


# Rank used to pick the strongest override when multiple markers match.
_SEVERITY_RANK: Final[dict[str, int]] = {
    Severity.LOW.value: 0,
    Severity.MEDIUM.value: 1,
    Severity.HIGH.value: 2,
    Severity.CRITICAL.value: 3,
}


def effective_severity(pattern_kind: str, file_path: str, base_severity: str) -> str:
    """Return the promoted severity for (pattern_kind, file_path, base_severity).

    When the feature flag is OFF, returns ``base_severity`` unchanged.
    When ON, checks each surface marker the file matches; if
    ``(pattern_kind, marker)`` is in :data:`SURFACE_OVERRIDE`, the override
    wins IF it is strictly higher-rank than the base. Never *lowers* severity.

    Args:
        pattern_kind: The antipattern kind string (e.g. ``"broad_exception_catch"``)
            as stored in the violations table.
        file_path: The file path the violation was detected in. May be absolute
            or repo-relative; only path-fragment regex matches are used.
        base_severity: The base severity assigned by the detector (one of
            ``CRITICAL/HIGH/MEDIUM/LOW``).

    Returns:
        Promoted severity if an override applies AND the flag is ON AND the
        override is strictly stronger than ``base_severity``. Otherwise
        ``base_severity`` unchanged.
    """
    if not is_surface_override_enabled():
        return base_severity
    if base_severity not in _SEVERITY_RANK:
        return base_severity
    best = base_severity
    best_rank = _SEVERITY_RANK[base_severity]
    for marker in resolve_surface_markers(file_path):
        promoted = SURFACE_OVERRIDE.get((pattern_kind, marker))
        if promoted is None:
            continue
        promoted_rank = _SEVERITY_RANK.get(promoted, -1)
        if promoted_rank > best_rank:
            best = promoted
            best_rank = promoted_rank
    return best


def effective_band(pattern_kind: str, file_path: str, base_band: str) -> str:
    """Band-level convenience wrapper around :func:`effective_severity`.

    Converts ``base_band`` → severity → applies overrides → converts back.
    Returns ``base_band`` unchanged if the flag is OFF or no override applies.
    """
    if not is_surface_override_enabled():
        return base_band
    base_severity = band_to_severity(base_band)
    promoted_severity = effective_severity(pattern_kind, file_path, base_severity)
    return severity_to_band(promoted_severity)


__all__ = [
    "Band",
    "BAND_DESCRIPTIONS",
    "BAND_LABELS",
    "BAND_ORDER",
    "BAND_TO_SEVERITY",
    "BAND_TOP_LEVEL_KEYS",
    "SEVERITY_ORDER",
    "SEVERITY_TO_BAND",
    "SURFACE_OVERRIDE",
    "Severity",
    "band_to_severity",
    "effective_band",
    "effective_severity",
    "is_surface_override_enabled",
    "normalize_band",
    "resolve_surface_markers",
    "severity_to_band",
]
