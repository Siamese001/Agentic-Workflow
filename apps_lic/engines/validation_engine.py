"""HOP6 validation for LinkedIn recruiter outreach drafts.

Produces a ``validation_report`` dict with ``passed`` (bool) and
``issues`` (list). The gate_decision stage (HOP7) consumes this report.

Checks are intentionally local: HOP6 validates structure and unsupported-claim
flags on the HOP5 output. Evidence support remains represented by the C0/FEC
bundle and downstream proof receipts.
"""

from __future__ import annotations

import re
from typing import Any

from apps_lic.engines.outreach_antipattern_detector import (
    AntiPattern,
    OutreachAntipatternDetector,
)


_GENERIC_EXTENSION_PATTERNS = [
    AntiPattern(
        pattern_id="AQ_001",
        reason_code="GENERIC_ROLE_OPENER",
        description="Generic role opener without asymmetric insight",
        pattern_text=r"\b(i noticed your role|i saw your role|given your expertise)\b",
    ),
    AntiPattern(
        pattern_id="AQ_002",
        reason_code="GENERIC_ALIGNMENT_CLAIM",
        description="Generic candidate alignment claim",
        pattern_text=r"\b(i believe my (background|experience) (aligns|could contribute)|my background aligns)\b",
    ),
    AntiPattern(
        pattern_id="AQ_003",
        reason_code="GENERIC_SYNERGY_ASK",
        description="Generic synergy/opportunities CTA",
        pattern_text=r"\b(potential synergies|discuss opportunities|explore opportunities|potential opportunities)\b",
    ),
    AntiPattern(
        pattern_id="AQ_004",
        reason_code="GENERIC_ADVANCED_AI_FILLER",
        description="Generic advanced-AI filler with no operating detail",
        pattern_text=r"\b(leverage advanced ai solutions|enhance digital initiatives)\b",
    ),
]

_AIG_OPERATING_TERMS = (
    "underwriting",
    "claims",
    "genai",
    "agentic",
    "governance",
    "workflow",
    "operating-model",
    "operating model",
    "telemetry",
    "evals",
    "aig assist",
)

_CANDIDATE_PROOF_TERMS = (
    "governed",
    "agent workflows",
    "orchestration",
    "evals",
    "telemetry",
    "safety",
    "human control",
    "senior engineering",
    "senior ai engineering",
    "production ai",
)


class ValidationEngine:
    """Lightweight structural validation for the LinkedIn draft contract."""

    MIN_BODY_LENGTH = 20
    MAX_BODY_LENGTH = 600
    ALLOWED_RECIPIENT_CLASSES = {
        "",
        "recruiter",
        "senior_ta",
        "hiring_manager",
        "executive",
        "c_level",
        "vp_eng",
        "cto",
        "referral_contact",
        "RECRUITER",
        "SENIOR_TA",
        "HIRING_MANAGER",
        "EXECUTIVE",
        "C_LEVEL",
        "VP_ENG",
        "CTO",
        "REFERRAL_CONTACT",
    }

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        draft = context.get("draft_message") or {}
        evidence = context.get("evidence_bundle") or {}
        reasoning_policy = (
            context.get("reasoning_policy")
            or draft.get("reasoning_policy")
            or {}
        )

        issues: list[str] = []
        body = str(draft.get("message_text") or draft.get("body") or "")
        support_status = str(evidence.get("support_status", "") or "").upper()
        paragraphs = [
            para.strip()
            for para in re.split(r"\n\s*\n", body.strip())
            if para.strip()
        ]

        if len(body) < self.MIN_BODY_LENGTH:
            issues.append(f"message_too_short (<{self.MIN_BODY_LENGTH} chars)")
        if len(body) > self.MAX_BODY_LENGTH:
            issues.append(f"message_too_long (>{self.MAX_BODY_LENGTH} chars)")
        if not body.strip():
            issues.append("empty_message_text")
        if len(paragraphs) > 2:
            issues.append("too_many_paragraphs (>2)")
        if "—" in body:
            issues.append("em_dash_forbidden")
        if re.search(r"\[[^\]]+\]\([^)]+\)", body):
            issues.append("markdown_link_forbidden")
        if draft.get("channel") not in (None, "", "linkedin"):
            issues.append("channel_not_linkedin")
        if draft.get("recipient_class") not in (None, *self.ALLOWED_RECIPIENT_CLASSES):
            issues.append("recipient_class_unknown")
        if list(draft.get("unsupported_claims") or []):
            issues.append("unsupported_claims_present")
        if not _has_low_friction_ask(body):
            issues.append("low_friction_ask_missing")
        antipattern = OutreachAntipatternDetector(
            extension_patterns=_GENERIC_EXTENSION_PATTERNS
        ).detect(body)
        if not antipattern.is_clean:
            issues.extend(f"antipattern:{code}" for code in antipattern.reason_codes)
        if not _has_aig_operating_insight(body):
            issues.append("aig_operating_insight_missing")
        if not _has_candidate_proof(body):
            issues.append("candidate_proof_missing")
        if _has_unverified_candidate_metric(body):
            issues.append("unverified_candidate_metric")
        if (
            bool(reasoning_policy.get("fail_closed_on_empty_evidence", True))
            and support_status in {"WEAK", "EMPTY"}
        ):
            issues.append(f"evidence_support_{support_status.lower()}_fail_closed")
        if support_status in {"WEAK", "EMPTY"} and int(
            reasoning_policy.get("max_candidates", 1) or 1
        ) > 1:
            issues.append("sc_escalation_forbidden_on_weak_evidence")

        evidence_count = int(evidence.get("count", 0))
        # Non-fatal advisory when evidence bundle is empty — generation was
        # allowed to run, but qa_report will reflect the ungrounded state.
        grounded = evidence_count > 0

        return {
            "validation_report": {
                "passed": len(issues) == 0,
                "issues": issues,
                "grounded": grounded,
                "evidence_count": evidence_count,
                "body_length": len(body),
                "message_text_length": len(body),
                "paragraph_count": len(paragraphs),
                "antipattern_reason_codes": list(antipattern.reason_codes),
                "antipattern_evidence_refs": list(antipattern.evidence_refs),
                "aig_operating_insight": _has_aig_operating_insight(body),
                "candidate_proof": _has_candidate_proof(body),
                "unverified_candidate_metric": _has_unverified_candidate_metric(body),
                "evidence_support_status": support_status,
                "reasoning_policy": dict(reasoning_policy)
                if isinstance(reasoning_policy, dict)
                else {},
            },
        }


def _has_low_friction_ask(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in (
            "chat",
            "call",
            "conversation",
            "connect",
            "discuss",
            "resume review",
            "review this",
            "open to",
            "worth a brief",
            "worth a short",
        )
    )


def _has_aig_operating_insight(text: str) -> bool:
    lowered = text.lower()
    return sum(1 for term in _AIG_OPERATING_TERMS if term in lowered) >= 2


def _has_candidate_proof(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in _CANDIDATE_PROOF_TERMS)


def _has_unverified_candidate_metric(text: str) -> bool:
    lowered = text.lower()
    if not re.search(r"\b(improved|increased|reduced|cut|saved|grew|delivered)\b", lowered):
        return False
    return bool(re.search(r"\b\d+(?:\.\d+)?\s?%", lowered))
