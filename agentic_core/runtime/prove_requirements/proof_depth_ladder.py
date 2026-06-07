"""Proof Depth Ladder — canonical ordering and composition-non-promotion rule.

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``
Source CSV: ``docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv``
Implementation prompt non-negotiables §2 + W0 must-prove "composition proof
cannot promote to integrated runtime proof".

The ladder
----------

The hardened certification matrix uses these proof-depth tiers (numeric order
encodes strict precedence; ``actual_proof_depth >= required_proof_depth`` is
the acceptance gate):

    E0_REQUIREMENT_TEXT             0   Requirement exists as text only
    E1_SOURCE_MAPPING               1   Mapped to canonical source/reference
    E2_STATIC_CHECK                 2   Schema/metadata check exists
    E3_COMPONENT_TEST               3   Unit/component test exists
    E4_NEGATIVE_CONTROL             4   Negative-control / fail-closed test exists
    E5_COMPOSITION_PROOF            5   Production components composed end-to-end
    E6_INTEGRATED_RUNTIME_PROOF     6   Real production entrypoint drove the path
    E7_REAL_OTEL_EXPORT             7   Collector-backed OTEL export proven
    E8_REPLAY_DETERMINISM           8   Original/replay parity + mutation negative
    E9_PRODUCTION_DEPENDENCY_PROOF  9   Production-dependency hash + identity proof

Anti-cheat rules (per implementation prompt non-negotiables)
------------------------------------------------------------

1. ``actual >= required`` is the acceptance test (rule §1).
2. ``E5_COMPOSITION_PROOF`` MUST NOT satisfy ``E6/E7/E8/E9`` claims (rule §2).
   ``can_satisfy(actual=E5, required=E6) == False`` even though 5 < 6 would
   normally be the only failure mode; this function ALSO blocks the case where
   somebody accidentally promotes E5 to count as a higher tier via metadata.

Public API
----------

- ``DEPTH_TO_INDEX``: dict[str, int] — canonical index lookup
- ``INDEX_TO_DEPTH``: dict[int, str] — reverse lookup for reports
- ``parse_depth(value: str) -> int``: tolerant parser with fail-closed default
- ``can_satisfy(actual: str, required: str) -> bool``: TRUE only when the
  actual tier proves at least the required tier AND composition non-promotion
  is honored.
- ``COMPOSITION_NON_PROMOTABLE_TARGETS``: frozenset of tiers E5 cannot satisfy
- ``DEPTHS``: tuple of all valid depth strings (for enum validation)
"""

from __future__ import annotations

from typing import Final, Mapping

# ──────────────────────────────────────────────────────────────────────
# Canonical ladder (DO NOT REORDER without ADR + matrix.csv migration)
# ──────────────────────────────────────────────────────────────────────

# Order MUST match the index numbering in each name; tests assert this.
DEPTHS: Final[tuple[str, ...]] = (
    "E0_REQUIREMENT_TEXT",
    "E1_SOURCE_MAPPING",
    "E2_STATIC_CHECK",
    "E3_COMPONENT_TEST",
    "E4_NEGATIVE_CONTROL",
    "E5_COMPOSITION_PROOF",
    "E6_INTEGRATED_RUNTIME_PROOF",
    "E7_REAL_OTEL_EXPORT",
    "E8_REPLAY_DETERMINISM",
    "E9_PRODUCTION_DEPENDENCY_PROOF",
)

DEPTH_TO_INDEX: Final[Mapping[str, int]] = {d: i for i, d in enumerate(DEPTHS)}
INDEX_TO_DEPTH: Final[Mapping[int, str]] = {i: d for i, d in enumerate(DEPTHS)}

# E5 cannot satisfy any of these targets, even though 5 < 6/7/8/9 would otherwise
# be the only failure mode (rule §2).
COMPOSITION_NON_PROMOTABLE_TARGETS: Final[frozenset[str]] = frozenset({
    "E6_INTEGRATED_RUNTIME_PROOF",
    "E7_REAL_OTEL_EXPORT",
    "E8_REPLAY_DETERMINISM",
    "E9_PRODUCTION_DEPENDENCY_PROOF",
})

# Sentinel returned when an unknown depth value is encountered. Negative so
# `actual_index >= required_index` is always False (fail-closed).
UNKNOWN_DEPTH_INDEX: Final[int] = -1


def parse_depth(value: str | None) -> int:
    """Return canonical index for a depth string. Unknown values return -1.

    Fail-closed: an unknown value can never `can_satisfy` any required depth.
    """
    if value is None:
        return UNKNOWN_DEPTH_INDEX
    v = str(value).strip()
    if not v:
        return UNKNOWN_DEPTH_INDEX
    return DEPTH_TO_INDEX.get(v, UNKNOWN_DEPTH_INDEX)


def can_satisfy(actual: str | None, required: str | None) -> bool:
    """Return True iff ``actual`` proves at least ``required`` AND composition
    non-promotion rule is honored.

    Composition non-promotion (rule §2): when ``actual == E5_COMPOSITION_PROOF``
    and ``required`` is one of the four E6+ runtime tiers, return False even
    though 5 < 6 would already make this False — but this is explicit so the
    rule is unambiguous in the audit log.
    """
    a_idx = parse_depth(actual)
    r_idx = parse_depth(required)
    if a_idx == UNKNOWN_DEPTH_INDEX or r_idx == UNKNOWN_DEPTH_INDEX:
        return False
    if str(actual).strip() == "E5_COMPOSITION_PROOF" and \
            str(required).strip() in COMPOSITION_NON_PROMOTABLE_TARGETS:
        return False
    return a_idx >= r_idx


def is_valid_depth(value: str | None) -> bool:
    """True iff ``value`` is one of the canonical ``DEPTHS``."""
    return parse_depth(value) != UNKNOWN_DEPTH_INDEX


__all__ = [
    "DEPTHS",
    "DEPTH_TO_INDEX",
    "INDEX_TO_DEPTH",
    "COMPOSITION_NON_PROMOTABLE_TARGETS",
    "UNKNOWN_DEPTH_INDEX",
    "parse_depth",
    "can_satisfy",
    "is_valid_depth",
]
