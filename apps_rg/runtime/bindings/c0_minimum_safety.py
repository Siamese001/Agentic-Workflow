"""S7: Minimum C0 safety checker for apps_rg resume shipping.

Deterministic, app-local safety checks applied to C0 outputs before
proceeding to PA (prompt assembly). No model calls. No provider calls.
No PA/L2 invocation. No cache writes. No L4 writes. No L6 execution.
No company research retrieval. No fact_vectors. No BM25/sparse retrieval.
No LLM free-text claim verification.

All checks are pure functions over dict/dataclass input.
Returns C0SafetyResult with verdict, decisive_reason, support_status,
missing_fields, blocked_reason, evidence_summary, and safe_to_continue_to_pa.

FORBIDDEN IMPORTS (enforced by TestBoundaryGuard in test suite):
- section_agentic_pipeline
- write_section_to_semantic_cache
- l6_shadow_learning
- fact_vectors
- openai / anthropic / PROVIDER_MODEL / external model
- requests.post / httpx
- pa_binding / l2_binding / c0_binding (circular)
- agentic_core (only stdlib + pathlib + json allowed)
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Profile loader
# ---------------------------------------------------------------------------

_PROFILE_PATH = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "config"
    / "domain_contract"
    / "resume_c0_minimum_safety_profile.v1.json"
)

_DEFAULT_PROFILE: dict[str, Any] | None = None


def _load_profile(override: dict[str, Any] | None = None) -> dict[str, Any]:
    global _DEFAULT_PROFILE  # noqa: PLW0603
    if override is not None:
        return override
    if _DEFAULT_PROFILE is None:
        with _PROFILE_PATH.open(encoding="utf-8") as fh:
            _DEFAULT_PROFILE = json.load(fh)
    return _DEFAULT_PROFILE


# ---------------------------------------------------------------------------
# Verdict enum and result dataclass
# ---------------------------------------------------------------------------

class C0SafetyVerdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    BLOCKED = "BLOCKED"


_VERDICT_PRECEDENCE: dict[str, int] = {
    "FAIL": 5,
    "BLOCKED": 4,
    "UNKNOWN": 3,
    "WARN": 2,
    "PASS": 1,
}


def _worse(a: str, b: str) -> str:
    """Return the higher-severity verdict."""
    return a if _VERDICT_PRECEDENCE.get(a, 0) >= _VERDICT_PRECEDENCE.get(b, 0) else b


@dataclass(frozen=True)
class C0SafetyResult:
    """Deterministic minimum C0 safety result."""
    verdict: str
    decisive_reason: str
    support_status: str
    missing_fields: tuple[str, ...]
    blocked_reason: str
    evidence_summary: str
    safe_to_continue_to_pa: bool
    check_id: str = "C0_MINIMUM_SAFETY"
    profile_ref: str = "resume_c0_minimum_safety_profile.v1.json"


# ---------------------------------------------------------------------------
# Support status constants (mirrored from FEC contract — no import)
# ---------------------------------------------------------------------------

_PASS = "PASS"
_PARTIAL = "PARTIAL"
_WEAK = "WEAK"
_WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
_CONFLICTED = "CONFLICTED"
_EMPTY = "EMPTY"
_BLOCKED_STATUS = "BLOCKED"
_UNKNOWN_STATUS = "UNKNOWN"

_PASSING_SUPPORT_STATUSES: frozenset[str] = frozenset({_PASS, _PARTIAL})

_BLOCKING_SUPPORT_STATUSES: frozenset[str] = frozenset({
    _CONFLICTED,
    _EMPTY,
    _BLOCKED_STATUS,
    _UNKNOWN_STATUS,
    _WEAK,
    _WEAK_WITH_CAVEATS,
})

# Authoritative briefing authority classes that are acceptable
_ALLOWED_AUTHORITY_CLASSES: frozenset[str] = frozenset({
    "AUTHORITATIVE", "PRIMARY", "SECONDARY",
})
_BLOCKING_AUTHORITY_CLASSES: frozenset[str] = frozenset({
    "UNKNOWN", "DENIED", "UNAUTHORIZED",
})


# ---------------------------------------------------------------------------
# Check 1: Grounding required / C0 dispatch proof
# ---------------------------------------------------------------------------

def _check_grounding_dispatch(
    grounding_required: bool,
    fec: dict[str, Any] | None,
    profile: dict[str, Any],
) -> tuple[str, str]:
    """Verify C0 was dispatched when grounding_required=True.

    Returns (verdict, reason).
    """
    policy = profile.get("grounding_required_policy", {})

    if not grounding_required:
        return C0SafetyVerdict.PASS, "grounding_required=False — C0 not required (NOT_APPLICABLE)"

    if fec is None:
        bypass_verdict = policy.get("c0_bypass_when_grounding_required", "BLOCKED")
        return bypass_verdict, (
            "grounding_required=True but no FEC supplied — C0 was bypassed; "
            f"verdict={bypass_verdict}"
        )

    # FEC present and grounding was required — dispatch confirmed
    return C0SafetyVerdict.PASS, "grounding_required=True and FEC present — C0 dispatched"


# ---------------------------------------------------------------------------
# Check 2: FEC required fields completeness
# ---------------------------------------------------------------------------

def _check_fec_completeness(
    fec: dict[str, Any] | None,
    grounding_required: bool,
    profile: dict[str, Any],
) -> tuple[str, str, list[str]]:
    """Check FEC for required field presence.

    Returns (verdict, reason, missing_fields).
    """
    if not grounding_required:
        return C0SafetyVerdict.PASS, "C0 not required — FEC completeness check skipped", []

    if fec is None:
        return C0SafetyVerdict.FAIL, "FEC is None — cannot check completeness", ["fec"]

    field_config: dict[str, Any] = profile.get("fec_required_fields", {})
    missing: list[str] = []
    worst_verdict = C0SafetyVerdict.PASS

    for fname, fcfg in field_config.items():
        required: bool = fcfg.get("required", False)
        absent_verdict: str = fcfg.get("absent_verdict", "WARN")

        val = fec.get(fname)
        # Consider "empty" — empty tuple/list/str/None
        is_empty = (
            val is None
            or (isinstance(val, (list, tuple)) and len(val) == 0)
            or (isinstance(val, str) and not val.strip())
        )

        if is_empty:
            # Special rule for evidence_items: empty allowed with explicit reason
            if fname == "evidence_items":
                empty_allowed = fcfg.get("empty_allowed_with_explicit_reason", False)
                if empty_allowed:
                    empty_reason = fec.get("evidence_items_empty_reason", "")
                    if not empty_reason or not str(empty_reason).strip():
                        missing.append(fname)
                        absent_v = fcfg.get("empty_without_reason_verdict", absent_verdict)
                        worst_verdict = _worse(worst_verdict, absent_v)
                    # else: has explicit reason — acceptable
                elif required:
                    missing.append(fname)
                    worst_verdict = _worse(worst_verdict, absent_verdict)
            elif required:
                missing.append(fname)
                worst_verdict = _worse(worst_verdict, absent_verdict)
            else:
                # Not hard required — use absent_verdict as warning
                worst_verdict = _worse(worst_verdict, absent_verdict)

    if missing:
        reason = f"FEC missing or empty required fields: {missing}"
    else:
        reason = "FEC completeness check passed"

    return worst_verdict, reason, missing


# ---------------------------------------------------------------------------
# Check 3: Support status policy
# ---------------------------------------------------------------------------

def _check_support_status(
    fec: dict[str, Any] | None,
    grounding_required: bool,
    profile: dict[str, Any],
) -> tuple[str, str, str]:
    """Validate support_status against promotion rules.

    Returns (verdict, reason, resolved_support_status).
    UNKNOWN is NEVER PASS.
    WEAK_WITH_CAVEATS / WEAK / CONFLICTED / EMPTY / BLOCKED must not be promoted to PASS.
    """
    if not grounding_required:
        return C0SafetyVerdict.PASS, "grounding_required=False — support status not checked", "NOT_APPLICABLE"

    if fec is None:
        return C0SafetyVerdict.UNKNOWN, "FEC absent — support_status is UNKNOWN", _UNKNOWN_STATUS

    raw_status = fec.get("support_status")

    # Missing support_status → UNKNOWN, never PASS
    if raw_status is None or (isinstance(raw_status, str) and not raw_status.strip()):
        return (
            C0SafetyVerdict.UNKNOWN,
            "support_status field absent — treated as UNKNOWN, not PASS",
            _UNKNOWN_STATUS,
        )

    support_status = str(raw_status).strip()
    rules = profile.get("support_status_rules", {})

    if support_status in _PASSING_SUPPORT_STATUSES:
        # PASS or PARTIAL — check evidence completeness requirement
        rule = rules.get(support_status, {})
        requires_completeness = rule.get("requires_evidence_completeness", False)
        if requires_completeness:
            evidence_items = fec.get("evidence_items")
            has_items = (
                evidence_items is not None
                and isinstance(evidence_items, (list, tuple))
                and len(evidence_items) > 0
            )
            if not has_items:
                return (
                    C0SafetyVerdict.FAIL,
                    f"support_status={support_status} but evidence_items is empty — "
                    "PASS requires evidence completeness",
                    _UNKNOWN_STATUS,
                )
        return C0SafetyVerdict.PASS, f"support_status={support_status} is passing", support_status

    if support_status == _UNKNOWN_STATUS:
        return (
            C0SafetyVerdict.UNKNOWN,
            "support_status=UNKNOWN — UNKNOWN is never PASS",
            support_status,
        )

    if support_status in (_WEAK, _WEAK_WITH_CAVEATS):
        return (
            C0SafetyVerdict.FAIL,
            f"support_status={support_status} — must not be promoted to PASS; "
            "blocks confident output",
            support_status,
        )

    if support_status in (_CONFLICTED, _EMPTY, _BLOCKED_STATUS):
        return (
            C0SafetyVerdict.BLOCKED,
            f"support_status={support_status} — blocks confident output",
            support_status,
        )

    # Unrecognized support_status value → UNKNOWN
    return (
        C0SafetyVerdict.UNKNOWN,
        f"support_status={support_status!r} is unrecognized — treated as UNKNOWN",
        _UNKNOWN_STATUS,
    )


# ---------------------------------------------------------------------------
# Check 4: Authoritative briefing freshness/authority
# ---------------------------------------------------------------------------

def _check_briefing(
    briefing_meta: dict[str, Any] | None,
    profile: dict[str, Any],
) -> tuple[str, str]:
    """Check supplied briefing for authority and freshness markers.

    briefing_meta keys expected:
      authority_class, freshness_status, freshness_timestamp_iso, digest_ref

    Returns (verdict, reason).
    """
    if briefing_meta is None:
        return C0SafetyVerdict.PASS, "No briefing supplied — briefing check not applicable"

    bp = profile.get("briefing_policy", {})
    allowed_authority = set(bp.get("authority_classes_allowed", ["AUTHORITATIVE", "PRIMARY", "SECONDARY"]))
    blocking_authority = set(bp.get("authority_classes_requiring_block", ["UNKNOWN", "DENIED", "UNAUTHORIZED"]))
    freshness_max_hours: int = int(bp.get("freshness_max_age_hours", 72))
    unauthorized_verdict: str = bp.get("unauthorized_briefing_verdict", "BLOCKED")
    missing_authority_verdict: str = bp.get("missing_authority_marker_verdict", "UNKNOWN")
    missing_freshness_verdict: str = bp.get("missing_freshness_marker_verdict", "WARN")
    stale_verdict: str = bp.get("stale_briefing_verdict", "WEAK_WITH_CAVEATS")

    authority_class = briefing_meta.get("authority_class", "")
    freshness_status = briefing_meta.get("freshness_status", "")
    freshness_ts = briefing_meta.get("freshness_timestamp_iso", "")
    digest_ref = briefing_meta.get("digest_ref", "")

    # Missing authority marker
    if not authority_class or not authority_class.strip():
        return (
            missing_authority_verdict,
            "Briefing missing authority_class marker — cannot be clean PASS",
        )

    # Blocking authority class
    if authority_class.upper() in {a.upper() for a in blocking_authority}:
        return (
            unauthorized_verdict,
            f"Briefing authority_class={authority_class!r} is unauthorized — BLOCKED",
        )

    # Authority class not in allowed set
    if authority_class.upper() not in {a.upper() for a in allowed_authority}:
        return (
            missing_authority_verdict,
            f"Briefing authority_class={authority_class!r} not in allowed set — UNKNOWN",
        )

    # Missing freshness marker
    if not freshness_status or not freshness_status.strip():
        return (
            missing_freshness_verdict,
            "Briefing missing freshness_status marker",
        )

    # Stale detection
    if freshness_status.upper() == "STALE":
        # WEAK_WITH_CAVEATS maps to FAIL for safe_to_continue_to_pa gating
        return (
            C0SafetyVerdict.FAIL,
            "Briefing freshness_status=STALE — cannot be clean PASS",
        )

    if freshness_ts:
        try:
            ts = datetime.fromisoformat(freshness_ts.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0
            if age_hours > freshness_max_hours:
                return (
                    C0SafetyVerdict.FAIL,
                    f"Briefing age {age_hours:.1f}h exceeds max {freshness_max_hours}h — "
                    "stale briefing cannot be clean PASS",
                )
        except (ValueError, TypeError):
            return (
                C0SafetyVerdict.WARN,
                f"Briefing freshness_timestamp_iso={freshness_ts!r} is unparseable — WARN",
            )

    # Missing digest ref — WARN only
    if not digest_ref or not digest_ref.strip():
        return C0SafetyVerdict.WARN, "Briefing missing digest_ref — WARN (not hard FAIL)"

    return C0SafetyVerdict.PASS, (
        f"Briefing authority={authority_class!r}, freshness={freshness_status!r} — OK"
    )


# ---------------------------------------------------------------------------
# Check 5: No company research lane guard
# ---------------------------------------------------------------------------

def _check_no_company_research_lane(
    fec: dict[str, Any] | None,
    profile: dict[str, Any],
) -> tuple[str, str]:
    """Assert no company research retrieval path was opened inside apps_rg C0.

    Looks for sentinel markers in FEC retrieval_sources. Company research
    should come from apps_research or a supplied authoritative briefing,
    never from a direct apps_rg C0 retrieval lane.

    Returns (verdict, reason).
    """
    lane_cfg = profile.get("company_research_lane", {})
    if lane_cfg.get("allowed_inside_apps_rg_c0", False):
        return C0SafetyVerdict.PASS, "Company research lane allowed by profile (not default)"

    if fec is None:
        return C0SafetyVerdict.PASS, "No FEC — company research lane check not applicable"

    retrieval_sources = fec.get("retrieval_sources", [])
    if not isinstance(retrieval_sources, (list, tuple)):
        retrieval_sources = []

    _COMPANY_RESEARCH_MARKERS = (
        "company_research",
        "company_brief_kb",
        "company_brief:",
        "company_context",
        "apps_research_direct",
    )

    hits = [
        src for src in retrieval_sources
        if any(marker in str(src).lower() for marker in _COMPANY_RESEARCH_MARKERS)
    ]

    if hits:
        return (
            C0SafetyVerdict.FAIL,
            f"Company research retrieval sources detected inside apps_rg C0: {hits[:3]} — "
            "company research must stay in apps_research or supplied briefing",
        )

    return C0SafetyVerdict.PASS, "No company research retrieval lane detected in apps_rg C0"


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

def run_c0_minimum_safety(
    *,
    grounding_required: bool,
    fec: dict[str, Any] | None,
    briefing_meta: dict[str, Any] | None = None,
    profile_override: dict[str, Any] | None = None,
) -> C0SafetyResult:
    """Run all minimum C0 safety checks and return aggregate result.

    Args:
        grounding_required: Whether the route requires C0 grounding.
        fec: The FinalEvidenceContract as a plain dict (or None if bypassed).
             Keys mirror FinalEvidenceContract fields:
               evidence_items, support_status, final_evidence_digest,
               source_lineage_map, freshness_receipts, acl_verification_receipts,
               contradiction_report, citation_map, retrieval_sources,
               evidence_items_empty_reason.
        briefing_meta: Optional dict with keys:
               authority_class, freshness_status, freshness_timestamp_iso, digest_ref.
        profile_override: Optional profile dict for testing.

    Returns:
        C0SafetyResult with aggregate verdict and safe_to_continue_to_pa flag.

    Invariants:
        - UNKNOWN is NEVER treated as PASS.
        - WEAK_WITH_CAVEATS / WEAK are not promoted to PASS.
        - CONFLICTED / EMPTY / BLOCKED / UNKNOWN block safe_to_continue_to_pa.
        - Stale or unauthorized briefing cannot yield clean PASS.
        - Missing support_status treated as UNKNOWN.
        - No model calls, no provider calls, no cache writes.
    """
    profile = _load_profile(profile_override)

    # Run all checks
    dispatch_v, dispatch_reason = _check_grounding_dispatch(
        grounding_required, fec, profile
    )

    completeness_v, completeness_reason, missing_fields = _check_fec_completeness(
        fec, grounding_required, profile
    )

    support_v, support_reason, resolved_status = _check_support_status(
        fec, grounding_required, profile
    )

    briefing_v, briefing_reason = _check_briefing(briefing_meta, profile)

    company_v, company_reason = _check_no_company_research_lane(fec, profile)

    # Aggregate verdict: worst of all checks
    overall = C0SafetyVerdict.PASS
    for v in (dispatch_v, completeness_v, support_v, briefing_v, company_v):
        overall = _worse(overall, v)

    # Decisive reason: first failing check reason
    decisive = dispatch_reason
    for v, reason in (
        (dispatch_v, dispatch_reason),
        (completeness_v, completeness_reason),
        (support_v, support_reason),
        (briefing_v, briefing_reason),
        (company_v, company_reason),
    ):
        if _VERDICT_PRECEDENCE.get(v, 0) > _VERDICT_PRECEDENCE.get(C0SafetyVerdict.PASS, 0):
            decisive = reason
            break

    # blocked_reason: collect all blocking reasons
    blocking_reasons = []
    for v, reason in (
        (dispatch_v, dispatch_reason),
        (completeness_v, completeness_reason),
        (support_v, support_reason),
        (briefing_v, briefing_reason),
        (company_v, company_reason),
    ):
        if v in (C0SafetyVerdict.FAIL, C0SafetyVerdict.BLOCKED, C0SafetyVerdict.UNKNOWN):
            blocking_reasons.append(reason)

    # safe_to_continue_to_pa
    safe_verdicts = profile.get("safe_to_continue_to_pa_rules", {}).get(
        "required_verdict", ["PASS", "WARN"]
    )
    safe_to_continue = overall in safe_verdicts

    evidence_count = 0
    if fec is not None:
        items = fec.get("evidence_items")
        if isinstance(items, (list, tuple)):
            evidence_count = len(items)

    def _v(v: str) -> str:
        return v.value if hasattr(v, "value") else str(v)

    evidence_summary = (
        f"evidence_items={evidence_count}, "
        f"support_status={resolved_status}, "
        f"dispatch={_v(dispatch_v)} dispatched, "
        f"completeness={_v(completeness_v)}, "
        f"briefing={_v(briefing_v)}, "
        f"company_lane={_v(company_v)}"
    )

    _log.info(
        "[C0Safety] verdict=%s safe_to_continue=%s reason=%r",
        overall,
        safe_to_continue,
        decisive,
    )

    return C0SafetyResult(
        verdict=overall,
        decisive_reason=decisive,
        support_status=resolved_status,
        missing_fields=tuple(missing_fields),
        blocked_reason=" | ".join(blocking_reasons),
        evidence_summary=evidence_summary,
        safe_to_continue_to_pa=safe_to_continue,
    )


_PASSING_SUPPORT_STATUSES_W3: frozenset[str] = frozenset({
    "PASS",
    "WEAK_WITH_CAVEATS",
})


def is_c0_minimum_safe(support_status: str) -> bool:
    """Return True if support_status meets the W3 C0 minimum safety bar (no PARTIAL)."""
    return support_status in _PASSING_SUPPORT_STATUSES_W3


__all__ = [
    "C0SafetyVerdict",
    "C0SafetyResult",
    "run_c0_minimum_safety",
    "is_c0_minimum_safe",
]
