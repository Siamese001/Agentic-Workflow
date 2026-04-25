"""G1 GOVERNANCE INVOCATION — Front Desk Triage (spec lines 53–88).

Maps a validated ``GovernanceReviewRequest`` plus declared
``risk_tier_hint`` to a ``TriageReport`` carrying:

- governance_mode (5 modes per spec line 83)
- risk_tier_band incl. CRITICAL (line 84)
- review_depth (line 85)
- triage_flags (line 86)
- next_lane (line 87)

The mapping is deterministic; no I/O.
"""

from __future__ import annotations

import re
from typing import Iterable, Mapping

from agentic_core.L5_safety.v5.contracts import GovernanceReviewRequest, TriageReport
from agentic_core.L5_safety.v5.types import (
    GovernanceMode,
    NextLane,
    PacketKind,
    ReviewDepth,
    RiskTierBandV5,
    SideEffectClass,
    TriageFlag,
)


# Patterns that flip ``injection_suspected`` (spec line 79–80).
_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+|previous\s+|prior\s+)+(?:\w+\s+)*instructions", re.IGNORECASE),
    re.compile(r"system\s*[:=]", re.IGNORECASE),
    re.compile(r"<\s*script\b", re.IGNORECASE),
    re.compile(r"data:\s*text/html", re.IGNORECASE),
    re.compile(r"\{\{\s*[^}]+\s*\}\}"),  # template-injection markers
    re.compile(r"javascript\s*:", re.IGNORECASE),
)


# Spec line 80 — shadow_discovery_probe. Detects attempts to evade governance
# through alternate tools, "just do it" framing, hidden text, markdown
# injection, or connector smuggling.
_SHADOW_DISCOVERY_PATTERNS = (
    re.compile(r"\bjust\s+do\s+it\b", re.IGNORECASE),
    re.compile(r"\b(?:bypass|skip|disable|override)\s+(?:the\s+)?(?:guardrail|policy|safety|governance|review)", re.IGNORECASE),
    re.compile(r"\b(?:use|call|invoke)\s+(?:any|another|alternate|different)\s+tool", re.IGNORECASE),
    re.compile(r"<!--\s*hidden", re.IGNORECASE),
    re.compile(r"\[//\]:\s*#"),  # markdown-comment smuggling
    re.compile(r"\\u200[bcdef]"),  # zero-width chars used for hidden text
    re.compile(r"\bunregistered\s+(?:tool|connector|mcp|model)\b", re.IGNORECASE),
)


def _scan_shadow_discovery(samples: Iterable[str]) -> bool:
    """Spec G1 line 80 shadow_discovery_probe."""
    for s in samples:
        if not s:
            continue
        for pat in _SHADOW_DISCOVERY_PATTERNS:
            if pat.search(s):
                return True
    return False


# Mode dispatch by packet kind. Spec lines 24–31 map packet kinds → modes
# fairly directly; HITL re-entry and Exit-disposition are explicit.
_PACKET_MODE: Mapping[PacketKind, GovernanceMode] = {
    PacketKind.REQUEST_ENVELOPE: GovernanceMode.RUNTIME_CHECK,
    PacketKind.L1_PLAN_CONTRACT: GovernanceMode.RUNTIME_CHECK,
    PacketKind.L0_ROUTE_CONTRACT: GovernanceMode.RUNTIME_CHECK,
    PacketKind.L3_STEP_CONTRACT: GovernanceMode.RUNTIME_CHECK,
    PacketKind.L2_EXECUTION_REQUEST: GovernanceMode.RUNTIME_CHECK,
    PacketKind.HITL_REENTRY_PACKET: GovernanceMode.HUMAN_REENTRY,
    PacketKind.EXIT_DISPOSITION_REQUEST: GovernanceMode.COMMIT_REVIEW,
}


# Side-effect → minimum band (spec lines 68–72).
_SIDE_EFFECT_MIN_BAND: Mapping[SideEffectClass, RiskTierBandV5] = {
    SideEffectClass.NONE: RiskTierBandV5.LOW,
    SideEffectClass.READ: RiskTierBandV5.LOW,
    SideEffectClass.MODEL_CALL: RiskTierBandV5.MODERATE,
    SideEffectClass.TOOL_CALL: RiskTierBandV5.MODERATE,
    SideEffectClass.NETWORK: RiskTierBandV5.MODERATE,
    SideEffectClass.MEMORY: RiskTierBandV5.HIGH,
    SideEffectClass.WRITE_PROPOSAL: RiskTierBandV5.HIGH,
    SideEffectClass.EXTERNAL_COMMIT: RiskTierBandV5.HIGH,
}


# Band → review_depth defaults (spec lines 68–72 implied + line 85).
_BAND_DEFAULT_DEPTH: Mapping[RiskTierBandV5, ReviewDepth] = {
    RiskTierBandV5.LOW: ReviewDepth.FAST_PATH,
    RiskTierBandV5.MODERATE: ReviewDepth.STANDARD,
    RiskTierBandV5.HIGH: ReviewDepth.ENHANCED,
    RiskTierBandV5.CRITICAL: ReviewDepth.LOCKDOWN,
}


_BAND_ORDER: Mapping[RiskTierBandV5, int] = {
    RiskTierBandV5.LOW: 0,
    RiskTierBandV5.MODERATE: 1,
    RiskTierBandV5.HIGH: 2,
    RiskTierBandV5.CRITICAL: 3,
}


def _max_band(a: RiskTierBandV5, b: RiskTierBandV5) -> RiskTierBandV5:
    return a if _BAND_ORDER[a] >= _BAND_ORDER[b] else b


def _scan_for_injection(samples: Iterable[str]) -> bool:
    for sample in samples:
        if not sample:
            continue
        for pat in _INJECTION_PATTERNS:
            if pat.search(sample):
                return True
    return False


def triage_request(
    request: GovernanceReviewRequest,
    *,
    risk_tier_hint: RiskTierBandV5 = RiskTierBandV5.LOW,
    incident_suspected: bool = False,
    static_only: bool = False,
    text_samples: Iterable[str] = (),
    declared_authority: tuple[str, ...] | None = None,
    declared_mode: GovernanceMode | None = None,
) -> TriageReport:
    """Compute the v5 triage decision for a normalized request.

    Args:
        request: validated ``GovernanceReviewRequest``.
        risk_tier_hint: hint from L0 (spec line 27). Cannot understate the
            actual authority — we ``max(...)`` against the side-effect floor.
        incident_suspected: caller signals an incident posture (spec line 66).
        static_only: caller is running CI / repo-level checks (spec line 62).
        text_samples: free-form strings to scan for injection patterns.
        declared_authority: subset of ``request.requested_authority`` already
            granted upstream — used for ``scope_mismatch`` detection.
    """
    flags: list[TriageFlag] = []

    # --- Mode --------------------------------------------------------
    if incident_suspected:
        mode = GovernanceMode.INCIDENT_REVIEW
    elif static_only:
        mode = GovernanceMode.STATIC_CHECK
    else:
        mode = _PACKET_MODE.get(request.packet_kind, GovernanceMode.RUNTIME_CHECK)

    # --- Risk band ---------------------------------------------------
    side_effect_floor = _SIDE_EFFECT_MIN_BAND.get(request.side_effect_class, RiskTierBandV5.LOW)
    band = _max_band(risk_tier_hint, side_effect_floor)
    if mode == GovernanceMode.INCIDENT_REVIEW:
        band = _max_band(band, RiskTierBandV5.CRITICAL)

    # --- Triage flags ------------------------------------------------
    if _scan_for_injection(text_samples):
        flags.append(TriageFlag.INJECTION_SUSPECTED)
        band = _max_band(band, RiskTierBandV5.HIGH)

    # Spec G1 line 80 — shadow_discovery_probe.
    if _scan_shadow_discovery(text_samples):
        if TriageFlag.INJECTION_SUSPECTED not in flags:
            flags.append(TriageFlag.INJECTION_SUSPECTED)
        band = _max_band(band, RiskTierBandV5.HIGH)

    # Spec G1 line 75 — declared mode must match actual packet content.
    if declared_mode is not None and declared_mode != mode:
        flags.append(TriageFlag.SCOPE_MISMATCH)

    if request.requested_authority and declared_authority is not None:
        requested_set = set(request.requested_authority)
        declared_set = set(declared_authority)
        # widening beyond declared is a scope mismatch
        if requested_set - declared_set:
            flags.append(TriageFlag.SCOPE_MISMATCH)

    if request.side_effect_class != SideEffectClass.NONE and not request.principal_chain_id:
        flags.append(TriageFlag.IDENTITY_GAP)

    if (
        request.side_effect_class
        in {
            SideEffectClass.MODEL_CALL,
            SideEffectClass.TOOL_CALL,
            SideEffectClass.NETWORK,
            SideEffectClass.MEMORY,
            SideEffectClass.WRITE_PROPOSAL,
            SideEffectClass.EXTERNAL_COMMIT,
        }
        and not request.registry_digest_set
    ):
        flags.append(TriageFlag.REGISTRY_GAP)

    # Side-effect mismatch: declared NONE/READ but write authority requested
    write_authority_terms = {"write", "commit", "execute", "mutate", "external"}
    if request.side_effect_class in {SideEffectClass.NONE, SideEffectClass.READ} and any(
        any(term in scope.lower() for term in write_authority_terms) for scope in request.requested_authority
    ):
        flags.append(TriageFlag.SIDE_EFFECT_MISMATCH)

    # HARD_CONSTRAINT_CANDIDATE is set only when CRITICAL coincides with an
    # observed red flag (injection / scope / identity / registry / side-effect
    # mismatch). Pure incident-driven escalation should ESCALATE, not REJECT.
    if band == RiskTierBandV5.CRITICAL and any(
        f
        in {
            TriageFlag.INJECTION_SUSPECTED,
            TriageFlag.SCOPE_MISMATCH,
            TriageFlag.IDENTITY_GAP,
            TriageFlag.REGISTRY_GAP,
            TriageFlag.SIDE_EFFECT_MISMATCH,
        }
        for f in flags
    ):
        flags.append(TriageFlag.HARD_CONSTRAINT_CANDIDATE)

    # --- Review depth ------------------------------------------------
    depth = _BAND_DEFAULT_DEPTH[band]
    if TriageFlag.INJECTION_SUSPECTED in flags and depth == ReviewDepth.FAST_PATH:
        depth = ReviewDepth.STANDARD

    # --- Next lane ---------------------------------------------------
    if (
        TriageFlag.IDENTITY_GAP in flags
        or TriageFlag.SCOPE_MISMATCH in flags
        or TriageFlag.REGISTRY_GAP in flags
        or TriageFlag.SIDE_EFFECT_MISMATCH in flags
    ) and band == RiskTierBandV5.CRITICAL:
        next_lane = NextLane.DECISION_RAIL_REJECT
    elif mode == GovernanceMode.STATIC_CHECK:
        next_lane = NextLane.STATIC_LANE
    elif mode in {GovernanceMode.HUMAN_REENTRY, GovernanceMode.COMMIT_REVIEW}:
        # Human and commit packets need both static (registry) and runtime checks.
        next_lane = NextLane.BOTH_LANES
    elif band in {RiskTierBandV5.HIGH, RiskTierBandV5.CRITICAL}:
        next_lane = NextLane.BOTH_LANES
    else:
        next_lane = NextLane.RUNTIME_LANE

    return TriageReport(
        governance_mode=mode,
        risk_tier_band=band,
        review_depth=depth,
        triage_flags=tuple(flags),
        next_lane=next_lane,
    )


__all__ = ["triage_request"]
