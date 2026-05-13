"""S8: Manual Section Review Harness for apps_rg resume shipping.

Produces a human-readable review packet for generated or candidate resume
sections before sending. This is an OPERATIONAL review artifact for
local/dev resume shipping — NOT HITL governance and does NOT re-enter
runtime authority.

BOUNDARY (enforced by test suite):
- No model calls. No provider calls. No PA/C0/L2 invocation.
- No cache writes. No L4 writes. No L6 execution.
- No external egress. No automatic sending.
- No mutation of the input resume artifact.
- No auto-approval of sections.
- Missing/UNKNOWN support or exit checks are NOT treated as PASS.
- Does not import: section_agentic_pipeline, write_section_to_semantic_cache,
  l6_shadow_learning, fact_vectors, openai, anthropic, vllm, httpx,
  pa_binding, c0_binding, l2_binding, agentic_core.

FORBIDDEN IMPORTS (enforced by boundary guard tests):
- section_agentic_pipeline
- write_section_to_semantic_cache
- l6_shadow_learning
- fact_vectors
- openai / anthropic / qwen / vllm
- requests.post / httpx
- pa_binding / l2_binding / c0_binding
- agentic_core

Only stdlib + pathlib + json + dataclasses + datetime + hashlib + re allowed.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    / "resume_manual_section_review_profile.v1.json"
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
# Constants
# ---------------------------------------------------------------------------

_REVIEWER_DECISION_UNREVIEWED = "UNREVIEWED"
_REVIEWER_DECISION_APPROVE = "APPROVE"
_REVIEWER_DECISION_EDIT = "EDIT"
_REVIEWER_DECISION_RETRY = "RETRY"
_REVIEWER_DECISION_REJECT = "REJECT"

_PLACEHOLDER_PATTERNS = (
    re.compile(r"\[.*?\]"),
    re.compile(r"<.*?>"),
    re.compile(r"TODO", re.IGNORECASE),
    re.compile(r"PLACEHOLDER", re.IGNORECASE),
    re.compile(r"INSERT\s+HERE", re.IGNORECASE),
)


def _has_placeholder(text: str) -> bool:
    return any(p.search(text) for p in _PLACEHOLDER_PATTERNS)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SectionReview:
    """Review record for a single resume section or sub-element."""
    section_id: str
    role_id: str = ""
    employer: str = ""
    bullet_ordinal: int | None = None
    treatment_tier: str = ""
    generated_text: str = ""
    original_source_text: str = ""
    source_span_ref: str = ""
    support_status: str = ""
    deterministic_exit_check_status: str = ""
    issues: list[str] = field(default_factory=list)
    reviewer_decision: str = _REVIEWER_DECISION_UNREVIEWED
    reviewer_notes: str = ""
    safe_to_send: bool = False


@dataclass
class ReviewPacket:
    """Top-level manual review packet for a resume artifact."""
    review_packet_id: str
    created_at: str
    source_resume_digest: str = ""
    jd_digest: str = ""
    jd_ref: str = ""
    section_reviews: list[SectionReview] = field(default_factory=list)
    overall_status: str = "UNREVIEWED"
    reviewer_decision: str = _REVIEWER_DECISION_UNREVIEWED
    unresolved_issues: list[str] = field(default_factory=list)
    next_action: str = ""
    profile_ref: str = "resume_manual_section_review_profile.v1.json"


# ---------------------------------------------------------------------------
# Issue detection helpers
# ---------------------------------------------------------------------------

_BLOCKING_SUPPORT_STATUSES_DEFAULT: frozenset[str] = frozenset({
    "INSUFFICIENT_SOURCE_SUPPORT",
    "BLOCKED",
    "UNKNOWN",
    "CONFLICTED",
    "EMPTY",
    "WEAK",
    "WEAK_WITH_CAVEATS",
})

_BLOCKING_EXIT_CHECK_STATUSES_DEFAULT: frozenset[str] = frozenset({
    "FAIL", "BLOCKED", "UNKNOWN",
})


def _eval_support_status(
    support_status: str,
    blocking_set: frozenset[str],
) -> list[str]:
    issues: list[str] = []
    if not support_status or not support_status.strip():
        issues.append("MISSING_SUPPORT_STATUS: support_status absent — treated as UNKNOWN, not PASS")
    elif support_status.upper() in blocking_set:
        issues.append(f"BLOCKING_SUPPORT_STATUS: support_status={support_status!r} blocks safe_to_send")
    return issues


def _eval_exit_check(
    exit_check_status: str,
    blocking_set: frozenset[str],
) -> list[str]:
    issues: list[str] = []
    if not exit_check_status or not exit_check_status.strip():
        issues.append("MISSING_EXIT_CHECK: exit check not provided — treated as UNKNOWN, not PASS")
    elif exit_check_status.upper() in blocking_set:
        issues.append(f"FAILING_EXIT_CHECK: exit check verdict={exit_check_status!r} blocks safe_to_send")
    return issues


def _is_safe_to_send(
    reviewer_decision: str,
    issues: list[str],
    profile: dict[str, Any],
) -> bool:
    """safe_to_send=True requires explicit APPROVE and no blocking issues."""
    decisions = profile.get("reviewer_decisions", {})
    approve_cfg = decisions.get(_REVIEWER_DECISION_APPROVE, {})
    if reviewer_decision != _REVIEWER_DECISION_APPROVE:
        return False
    if not approve_cfg.get("requires_explicit_set", True):
        return False
    # Any issue mentioning BLOCKING or MISSING blocks even an APPROVE
    blocking_keywords = ("BLOCKING_SUPPORT_STATUS", "FAILING_EXIT_CHECK", "MISSING_SUPPORT_STATUS", "MISSING_EXIT_CHECK")
    for issue in issues:
        if any(kw in issue for kw in blocking_keywords):
            return False
    return True


# ---------------------------------------------------------------------------
# Section review builders
# ---------------------------------------------------------------------------

def _build_section_review(
    section_id: str,
    generated_text: str,
    original_source_text: str = "",
    support_status: str = "",
    deterministic_exit_check_status: str = "",
    treatment_tier: str = "",
    role_id: str = "",
    employer: str = "",
    bullet_ordinal: int | None = None,
    source_span_ref: str = "",
    reviewer_decision: str = _REVIEWER_DECISION_UNREVIEWED,
    reviewer_notes: str = "",
    blocking_support: frozenset[str] = _BLOCKING_SUPPORT_STATUSES_DEFAULT,
    blocking_exit: frozenset[str] = _BLOCKING_EXIT_CHECK_STATUSES_DEFAULT,
    profile: dict[str, Any] | None = None,
) -> SectionReview:
    _profile = profile or {}
    issues: list[str] = []

    if not generated_text or not generated_text.strip():
        issues.append("EMPTY_SECTION: generated_text is empty")

    if _has_placeholder(generated_text):
        issues.append("PLACEHOLDER_DETECTED: generated_text contains placeholder pattern")

    issues.extend(_eval_support_status(support_status, blocking_support))
    issues.extend(_eval_exit_check(deterministic_exit_check_status, blocking_exit))

    safe = _is_safe_to_send(reviewer_decision, issues, _profile)

    return SectionReview(
        section_id=section_id,
        role_id=role_id,
        employer=employer,
        bullet_ordinal=bullet_ordinal,
        treatment_tier=treatment_tier,
        generated_text=generated_text,
        original_source_text=original_source_text,
        source_span_ref=source_span_ref,
        support_status=support_status,
        deterministic_exit_check_status=deterministic_exit_check_status,
        issues=issues,
        reviewer_decision=reviewer_decision,
        reviewer_notes=reviewer_notes,
        safe_to_send=safe,
    )


# ---------------------------------------------------------------------------
# Overall status computation
# ---------------------------------------------------------------------------

def _compute_overall_status(
    section_reviews: list[SectionReview],
    profile: dict[str, Any],
) -> tuple[str, list[str], str]:
    """Compute overall_status, unresolved_issues, next_action."""
    blocking_exit = frozenset(profile.get("blocking_exit_check_statuses", ["FAIL", "BLOCKED", "UNKNOWN"]))

    unresolved: list[str] = []
    any_unreviewed = False
    any_blocking = False
    any_needs_edit = False
    all_approved = True

    for sr in section_reviews:
        if sr.reviewer_decision == _REVIEWER_DECISION_UNREVIEWED:
            any_unreviewed = True
            all_approved = False
        elif sr.reviewer_decision in (_REVIEWER_DECISION_EDIT, _REVIEWER_DECISION_RETRY):
            any_needs_edit = True
            all_approved = False
        elif sr.reviewer_decision == _REVIEWER_DECISION_REJECT:
            any_blocking = True
            all_approved = False

        for issue in sr.issues:
            if any(kw in issue for kw in ("BLOCKING", "FAILING", "EMPTY_SECTION")):
                unresolved.append(f"{sr.section_id}: {issue}")
                any_blocking = True

    if any_blocking:
        status = "BLOCKED"
        next_action = "Resolve blocking issues before sending"
    elif any_needs_edit:
        status = "NEEDS_EDIT"
        next_action = "Edit or retry flagged sections before sending"
    elif any_unreviewed:
        if not section_reviews:
            status = "UNREVIEWED"
        else:
            status = "PARTIAL_REVIEW"
        next_action = "Complete review of all sections"
    elif all_approved and section_reviews:
        status = "ALL_APPROVED"
        next_action = "All sections approved — ready to send after final check"
    else:
        status = "UNREVIEWED"
        next_action = "Begin section review"

    return status, unresolved, next_action


# ---------------------------------------------------------------------------
# Main harness: build_review_packet
# ---------------------------------------------------------------------------

def build_review_packet(
    resume_artifact: dict[str, Any],
    *,
    exit_check_summary: dict[str, Any] | None = None,
    jd_text: str = "",
    jd_ref: str = "",
    profile_override: dict[str, Any] | None = None,
) -> ReviewPacket:
    """Build a manual review packet from a resume artifact.

    Args:
        resume_artifact: The resume as a plain dict. Expected top-level keys:
            headline, executive_summary, roles, competencies,
            education, certifications, early_career.
            Each section may carry support_status, treatment_tier,
            original_source_text, source_span_ref.
        exit_check_summary: Optional dict mapping section_id -> exit check verdict.
            Keys: headline, executive_summary, roles, competencies,
            education, certifications, early_career, per_role_{i}, per_bullet_{i}_{j}.
        jd_text: Optional job description text for digest.
        jd_ref: Optional JD reference string.
        profile_override: Optional profile dict for testing.

    Returns:
        ReviewPacket with section_reviews populated.

    Invariants:
        - Input resume_artifact is NOT mutated.
        - All reviewer_decisions default to UNREVIEWED.
        - All safe_to_send default to False.
        - Missing support_status treated as UNKNOWN, not PASS.
        - Missing exit_check treated as UNKNOWN, not PASS.
        - No model calls. No provider calls. No cache writes.
    """
    profile = _load_profile(profile_override)

    blocking_support: frozenset[str] = frozenset(
        s.upper() for s in profile.get("blocking_support_statuses", [])
    )
    if not blocking_support:
        blocking_support = _BLOCKING_SUPPORT_STATUSES_DEFAULT

    blocking_exit: frozenset[str] = frozenset(
        s.upper() for s in profile.get("blocking_exit_check_statuses", [])
    )
    if not blocking_exit:
        blocking_exit = _BLOCKING_EXIT_CHECK_STATUSES_DEFAULT

    exit_checks: dict[str, str] = exit_check_summary or {}

    # Digests
    raw_src = json.dumps(resume_artifact, sort_keys=True, ensure_ascii=False)
    source_resume_digest = _digest(raw_src)
    jd_digest = _digest(jd_text) if jd_text else ""

    packet_id = f"review-{source_resume_digest}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    created_at = datetime.now(timezone.utc).isoformat()

    section_reviews: list[SectionReview] = []

    def _ec(key: str) -> str:
        return exit_checks.get(key, "")

    # ------------------------------------------------------------------
    # HEADLINE
    # ------------------------------------------------------------------
    hl = resume_artifact.get("headline", {})
    if isinstance(hl, str):
        hl_text = hl
        hl_source = ""
        hl_support = ""
        hl_tier = ""
    elif isinstance(hl, dict):
        hl_text = hl.get("text", "")
        hl_source = hl.get("original_source_text", "")
        hl_support = hl.get("support_status", "")
        hl_tier = hl.get("treatment_tier", "")
    else:
        hl_text = str(hl) if hl else ""
        hl_source = ""
        hl_support = ""
        hl_tier = ""

    section_reviews.append(_build_section_review(
        section_id="headline",
        generated_text=hl_text,
        original_source_text=hl_source,
        support_status=hl_support,
        deterministic_exit_check_status=_ec("headline"),
        treatment_tier=hl_tier,
        blocking_support=blocking_support,
        blocking_exit=blocking_exit,
        profile=profile,
    ))

    # ------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ------------------------------------------------------------------
    es = resume_artifact.get("executive_summary", {})
    if isinstance(es, str):
        es_text = es
        es_source = ""
        es_support = ""
        es_tier = ""
    elif isinstance(es, dict):
        es_text = es.get("text", "")
        es_source = es.get("original_source_text", "")
        es_support = es.get("support_status", "")
        es_tier = es.get("treatment_tier", "")
    else:
        es_text = str(es) if es else ""
        es_source = ""
        es_support = ""
        es_tier = ""

    section_reviews.append(_build_section_review(
        section_id="executive_summary",
        generated_text=es_text,
        original_source_text=es_source,
        support_status=es_support,
        deterministic_exit_check_status=_ec("executive_summary"),
        treatment_tier=es_tier,
        blocking_support=blocking_support,
        blocking_exit=blocking_exit,
        profile=profile,
    ))

    # ------------------------------------------------------------------
    # COMPETENCIES
    # ------------------------------------------------------------------
    comp_raw = resume_artifact.get("competencies", {})
    if isinstance(comp_raw, dict):
        comp_items: list[str] = comp_raw.get("items", [])
        comp_support = comp_raw.get("support_status", "")
        comp_tier = comp_raw.get("treatment_tier", "")
    elif isinstance(comp_raw, list):
        comp_items = comp_raw
        comp_support = ""
        comp_tier = ""
    else:
        comp_items = []
        comp_support = ""
        comp_tier = ""

    comp_text = " | ".join(str(c) for c in comp_items)
    section_reviews.append(_build_section_review(
        section_id="competencies",
        generated_text=comp_text,
        support_status=comp_support,
        deterministic_exit_check_status=_ec("competencies"),
        treatment_tier=comp_tier,
        blocking_support=blocking_support,
        blocking_exit=blocking_exit,
        profile=profile,
    ))

    # ------------------------------------------------------------------
    # ROLES — narrative + per-bullet
    # ------------------------------------------------------------------
    roles_raw = resume_artifact.get("roles", [])
    if not isinstance(roles_raw, list):
        roles_raw = []

    for role_idx, role in enumerate(roles_raw):
        if not isinstance(role, dict):
            continue
        employer = role.get("employer", f"role_{role_idx}")
        title = role.get("title", "")
        role_id = f"role_{role_idx}"
        narrative = role.get("narrative", "")
        narrative_source = role.get("narrative_original_source_text", "")
        narrative_support = role.get("support_status", "")
        narrative_tier = role.get("treatment_tier", "")
        narrative_ec_key = f"role_{role_idx}_narrative"

        section_reviews.append(_build_section_review(
            section_id=f"role_{role_idx}_narrative",
            generated_text=narrative,
            original_source_text=narrative_source,
            support_status=narrative_support,
            deterministic_exit_check_status=_ec(narrative_ec_key),
            treatment_tier=narrative_tier,
            role_id=role_id,
            employer=employer,
            blocking_support=blocking_support,
            blocking_exit=blocking_exit,
            profile=profile,
        ))

        bullets = role.get("bullets", [])
        if not isinstance(bullets, list):
            bullets = []

        ordinals_seen: list[int] = []
        for bullet in bullets:
            if not isinstance(bullet, dict):
                continue
            ordinal = bullet.get("ordinal")
            if isinstance(ordinal, int):
                ordinals_seen.append(ordinal)
            bullet_text = bullet.get("source_text", bullet.get("text", ""))
            bullet_source = bullet.get("original_source_text", "")
            bullet_support = bullet.get("support_status", "")
            bullet_tier = bullet.get("treatment_tier", "")
            bullet_ec_key = f"role_{role_idx}_bullet_{ordinal}"

            bullet_review = _build_section_review(
                section_id=f"role_{role_idx}_bullet_{ordinal}",
                generated_text=bullet_text,
                original_source_text=bullet_source,
                support_status=bullet_support,
                deterministic_exit_check_status=_ec(bullet_ec_key),
                treatment_tier=bullet_tier,
                role_id=role_id,
                employer=employer,
                bullet_ordinal=ordinal if isinstance(ordinal, int) else None,
                blocking_support=blocking_support,
                blocking_exit=blocking_exit,
                profile=profile,
            )
            section_reviews.append(bullet_review)

        # Check for ordinal gaps
        if ordinals_seen:
            sorted_ords = sorted(ordinals_seen)
            for i in range(len(sorted_ords) - 1):
                if sorted_ords[i + 1] - sorted_ords[i] > 1:
                    # Add gap issue to the role narrative review
                    for sr in section_reviews:
                        if sr.section_id == f"role_{role_idx}_narrative":
                            sr.issues.append(
                                f"BULLET_ORDINAL_GAP: ordinals {sorted_ords[i]}->{sorted_ords[i+1]} skipped"
                            )
                            break

    # ------------------------------------------------------------------
    # VERBATIM SECTIONS: education, certifications, early_career
    # ------------------------------------------------------------------
    verbatim_sections = profile.get("verbatim_sections", ["education", "certifications", "early_career"])
    for vsec in verbatim_sections:
        vsec_raw = resume_artifact.get(vsec)
        if vsec_raw is None:
            vsec_text = ""
        elif isinstance(vsec_raw, str):
            vsec_text = vsec_raw
        elif isinstance(vsec_raw, dict):
            vsec_text = vsec_raw.get("text", vsec_raw.get("content", ""))
        elif isinstance(vsec_raw, list):
            vsec_text = " | ".join(str(x) for x in vsec_raw)
        else:
            vsec_text = str(vsec_raw)

        issues: list[str] = []
        if not vsec_text or not vsec_text.strip():
            issues.append(f"EMPTY_SECTION: {vsec} text is empty")

        # Verbatim hash check
        if isinstance(vsec_raw, dict):
            expected_hash = vsec_raw.get("source_hash", "")
            if not expected_hash:
                issues.append(
                    f"VERBATIM_MISMATCH_WARNING: {vsec} missing source_hash — cannot verify verbatim preservation (WARN)"
                )

        exit_v = _ec(vsec)
        exit_issues = _eval_exit_check(exit_v, blocking_exit)
        issues.extend(exit_issues)

        sr = SectionReview(
            section_id=vsec,
            treatment_tier="VERBATIM",
            generated_text=vsec_text,
            original_source_text=(
                vsec_raw.get("original_source_text", "") if isinstance(vsec_raw, dict) else ""
            ),
            support_status="NOT_APPLICABLE",
            deterministic_exit_check_status=exit_v,
            issues=issues,
            reviewer_decision=_REVIEWER_DECISION_UNREVIEWED,
            reviewer_notes="",
            safe_to_send=False,
        )
        section_reviews.append(sr)

    # ------------------------------------------------------------------
    # Overall status
    # ------------------------------------------------------------------
    overall_status, unresolved, next_action = _compute_overall_status(section_reviews, profile)

    return ReviewPacket(
        review_packet_id=packet_id,
        created_at=created_at,
        source_resume_digest=source_resume_digest,
        jd_digest=jd_digest,
        jd_ref=jd_ref,
        section_reviews=section_reviews,
        overall_status=overall_status,
        reviewer_decision=_REVIEWER_DECISION_UNREVIEWED,
        unresolved_issues=unresolved,
        next_action=next_action,
    )


# ---------------------------------------------------------------------------
# JSON serialisation
# ---------------------------------------------------------------------------

def review_packet_to_dict(packet: ReviewPacket) -> dict[str, Any]:
    """Serialize a ReviewPacket to a plain dict (JSON-safe)."""
    return {
        "review_packet_id": packet.review_packet_id,
        "created_at": packet.created_at,
        "source_resume_digest": packet.source_resume_digest,
        "jd_digest": packet.jd_digest,
        "jd_ref": packet.jd_ref,
        "overall_status": packet.overall_status,
        "reviewer_decision": packet.reviewer_decision,
        "unresolved_issues": packet.unresolved_issues,
        "next_action": packet.next_action,
        "profile_ref": packet.profile_ref,
        "section_reviews": [
            {
                "section_id": sr.section_id,
                "role_id": sr.role_id,
                "employer": sr.employer,
                "bullet_ordinal": sr.bullet_ordinal,
                "treatment_tier": sr.treatment_tier,
                "generated_text": sr.generated_text,
                "original_source_text": sr.original_source_text,
                "source_span_ref": sr.source_span_ref,
                "support_status": sr.support_status,
                "deterministic_exit_check_status": sr.deterministic_exit_check_status,
                "issues": sr.issues,
                "reviewer_decision": sr.reviewer_decision,
                "reviewer_notes": sr.reviewer_notes,
                "safe_to_send": sr.safe_to_send,
            }
            for sr in packet.section_reviews
        ],
    }


# ---------------------------------------------------------------------------
# Markdown formatter
# ---------------------------------------------------------------------------

def _fmt_verdict(verdict: str) -> str:
    v = (verdict or "").upper()
    if v in ("PASS",):
        return "✅ PASS"
    if v in ("WARN",):
        return "⚠️ WARN"
    if v in ("FAIL", "BLOCKED"):
        return "❌ FAIL/BLOCKED"
    if v in ("UNKNOWN", ""):
        return "❓ UNKNOWN/MISSING"
    return v


def _fmt_support(status: str) -> str:
    s = (status or "").upper()
    if s in ("PASS", "PARTIAL"):
        return f"✅ {s}"
    if s in ("NOT_APPLICABLE",):
        return f"— {s}"
    if s == "":
        return "❓ MISSING"
    return f"⚠️ {s}"


def _fmt_decision(decision: str) -> str:
    if decision == _REVIEWER_DECISION_APPROVE:
        return "✅ APPROVED"
    if decision == _REVIEWER_DECISION_UNREVIEWED:
        return "[ ] UNREVIEWED"
    if decision == _REVIEWER_DECISION_EDIT:
        return "[E] NEEDS EDIT"
    if decision == _REVIEWER_DECISION_RETRY:
        return "[R] RETRY"
    if decision == _REVIEWER_DECISION_REJECT:
        return "[X] REJECTED"
    return decision


def format_review_packet_markdown(packet: ReviewPacket) -> str:
    """Render the review packet as a human-readable Markdown string."""
    lines: list[str] = []

    lines.append("# Manual Section Review")
    lines.append(f"\n**Packet ID:** `{packet.review_packet_id}`")
    lines.append(f"**Created:** {packet.created_at}")
    if packet.source_resume_digest:
        lines.append(f"**Resume Digest:** `{packet.source_resume_digest}`")
    if packet.jd_digest:
        lines.append(f"**JD Digest:** `{packet.jd_digest}`")
    if packet.jd_ref:
        lines.append(f"**JD Ref:** {packet.jd_ref}")
    lines.append(f"\n**Overall Status:** {packet.overall_status}")
    lines.append(f"**Reviewer Decision (packet):** {_fmt_decision(packet.reviewer_decision)}")
    if packet.unresolved_issues:
        lines.append("\n**Unresolved Issues:**")
        for issue in packet.unresolved_issues:
            lines.append(f"- {issue}")
    lines.append(f"\n**Next Action:** {packet.next_action}")

    lines.append("\n---\n")

    # Group: header sections first, then roles, then verbatim
    header_ids = {"headline", "executive_summary", "competencies"}
    verbatim_ids = {"education", "certifications", "early_career"}

    def _render_section(sr: SectionReview) -> None:
        role_label = f" ({sr.employer})" if sr.employer else ""
        bullet_label = f" — bullet #{sr.bullet_ordinal}" if sr.bullet_ordinal is not None else ""
        lines.append(f"## {sr.section_id}{role_label}{bullet_label}")
        if sr.treatment_tier:
            lines.append(f"**Treatment:** {sr.treatment_tier}")
        lines.append(f"**Support Status:** {_fmt_support(sr.support_status)}")
        lines.append(f"**Exit Check:** {_fmt_verdict(sr.deterministic_exit_check_status)}")
        lines.append(f"**Safe to Send:** {'✅ YES' if sr.safe_to_send else '❌ NO'}")
        lines.append(f"\n**Reviewer Decision:** {_fmt_decision(sr.reviewer_decision)}")
        if sr.reviewer_notes:
            lines.append(f"**Reviewer Notes:** {sr.reviewer_notes}")
        else:
            lines.append("**Reviewer Notes:** _(none)_")
        if sr.generated_text:
            lines.append(f"\n**Generated Text:**\n```\n{sr.generated_text[:500]}\n```")
        else:
            lines.append("\n**Generated Text:** _(empty)_")
        if sr.original_source_text:
            lines.append(f"\n**Original Source:**\n```\n{sr.original_source_text[:200]}\n```")
        if sr.issues:
            lines.append("\n**Issues:**")
            for issue in sr.issues:
                lines.append(f"- ⚠️ {issue}")
        else:
            lines.append("\n**Issues:** _(none)_")
        lines.append("")

    # Render header sections
    for section_id in ("headline", "executive_summary", "competencies"):
        for sr in packet.section_reviews:
            if sr.section_id == section_id:
                _render_section(sr)

    # Render roles (grouped by role)
    role_sections = [
        sr for sr in packet.section_reviews
        if sr.section_id not in header_ids and sr.section_id not in verbatim_ids
    ]
    if role_sections:
        lines.append("---\n")
        lines.append("## Roles\n")
        for sr in role_sections:
            _render_section(sr)

    # Render verbatim sections
    for vsec in ("education", "certifications", "early_career"):
        for sr in packet.section_reviews:
            if sr.section_id == vsec:
                lines.append("---\n")
                _render_section(sr)

    lines.append("---")
    lines.append(f"\n_Review packet generated by manual_section_review.py — S8 ops/dev harness only._")
    lines.append("_Not HITL governance. Does not send. Does not auto-approve. Does not run models._")

    return "\n".join(lines)


__all__ = [
    "SectionReview",
    "ReviewPacket",
    "build_review_packet",
    "review_packet_to_dict",
    "format_review_packet_markdown",
]
