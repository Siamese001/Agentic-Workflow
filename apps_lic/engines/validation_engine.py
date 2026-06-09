"""HOP6 validation for LinkedIn recruiter outreach drafts.

Produces a ``validation_report`` dict with ``passed`` (bool) and
``issues`` (list). The gate_decision stage (HOP7) consumes this report.

Checks are intentionally local: HOP6 validates structure and unsupported-claim
flags on the HOP5 output. Evidence support remains represented by the C0/FEC
bundle and downstream proof receipts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

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
_COMPANY_TRIGGER_CLAIM_RE = re.compile(
    r"\b(announced|launched|released|rolled out|expanded|acquired|ipo|funding|recent news)\b",
    flags=re.IGNORECASE,
)

_VALIDATION_PROFILES_PATH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "domain_contract"
    / "validation_profiles.v1.json"
)
_FALLBACK_PROFILE_CONFIG = {
    "default_profile_id": "generic_company",
    "profiles": {
        "generic_company": {
            "profile_id": "generic_company",
            "companies": [],
            "requires_operating_insight": False,
            "operating_terms": [],
            "minimum_operating_terms": 0,
            "forbidden_terms_without_evidence": (
                "underwriting",
                "claims",
                "aig assist",
            ),
        },
        "aig_operating_insight": {
            "profile_id": "aig_operating_insight",
            "companies": ("aig", "american international group"),
            "requires_operating_insight": True,
            "operating_terms": _AIG_OPERATING_TERMS,
            "minimum_operating_terms": 2,
            "forbidden_terms_without_evidence": (),
        },
    },
}


class ValidationEngine:
    """Lightweight structural validation for the LinkedIn draft contract."""

    MIN_BODY_LENGTH = 20
    MAX_BODY_LENGTH = 600
    ALLOWED_RECIPIENT_CLASSES = {
        "",
        "ceo",
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
        "CEO",
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
        profile_id, validation_profile = _resolve_validation_profile(
            context,
            draft=draft,
            evidence=evidence,
        )
        profile_operating_insight = _has_profile_operating_insight(
            body,
            validation_profile,
        )
        profile_forbidden_terms = _profile_forbidden_terms_without_evidence(
            body,
            validation_profile,
            context,
            evidence,
        )
        unsupported_company_claim = _has_unsupported_company_trigger_claim(
            body,
            context,
            evidence,
        )
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
        if (
            bool(validation_profile.get("requires_operating_insight"))
            and not profile_operating_insight
        ):
            issues.append("aig_operating_insight_missing")
        issues.extend(
            f"profile_forbidden_term:{term}"
            for term in profile_forbidden_terms
        )
        if unsupported_company_claim:
            issues.append("unsupported_company_trigger_claim")
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
                "validation_profile_id": profile_id,
                "profile_operating_insight": profile_operating_insight,
                "profile_forbidden_terms": profile_forbidden_terms,
                "unsupported_company_trigger_claim": unsupported_company_claim,
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


def _load_validation_profiles() -> dict[str, Any]:
    try:
        loaded = json.loads(_VALIDATION_PROFILES_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(_FALLBACK_PROFILE_CONFIG)
    return loaded if isinstance(loaded, dict) else dict(_FALLBACK_PROFILE_CONFIG)


def _clean_company(value: Any) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _company_matches_profile(company: str, aliases: set[str]) -> bool:
    if not company:
        return False
    company_tokens = set(company.split())
    for alias in aliases:
        if not alias:
            continue
        if company == alias:
            return True
        if len(alias) <= 4 and alias in company_tokens:
            return True
        if len(alias) > 4 and (
            company.startswith(f"{alias} ")
            or company.endswith(f" {alias}")
            or f" {alias} " in f" {company} "
        ):
            return True
    return False


def _is_meaningful_company(value: Any) -> bool:
    cleaned = _clean_company(value)
    return bool(cleaned) and cleaned not in {"unknown", "n a", "na", "none", "not available"}


def _explicit_profile_id(
    context: Mapping[str, Any],
    *,
    draft: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> str:
    for source in (
        context,
        draft,
        evidence,
        context.get("profile_features") if isinstance(context.get("profile_features"), Mapping) else {},
    ):
        if not isinstance(source, Mapping):
            continue
        raw = source.get("validation_profile_id") or source.get("profile_id")
        if str(raw or "").strip():
            return str(raw).strip()
        profile = source.get("validation_profile")
        if isinstance(profile, Mapping) and str(profile.get("profile_id") or "").strip():
            return str(profile["profile_id"]).strip()
    return ""


def _target_company(
    context: Mapping[str, Any],
    *,
    draft: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> str:
    profile_features = context.get("profile_features")
    if isinstance(profile_features, Mapping):
        target_contact = profile_features.get("target_contact")
        if isinstance(target_contact, Mapping):
            company = target_contact.get("company_name") or target_contact.get("company")
            if _is_meaningful_company(company):
                return str(company).strip()
    campaign_request = context.get("campaign_request")
    if isinstance(campaign_request, Mapping):
        config = campaign_request.get("config")
        if isinstance(config, Mapping):
            target_contact = config.get("target_contact")
            if isinstance(target_contact, Mapping):
                company = target_contact.get("company_name") or target_contact.get("company")
                if _is_meaningful_company(company):
                    return str(company).strip()
    for source in (draft, evidence):
        company = (
            source.get("target_contact_company")
            or source.get("target_company")
            or source.get("company")
        )
        if _is_meaningful_company(company):
            return str(company).strip()
    return ""


def _resolve_validation_profile(
    context: Mapping[str, Any],
    *,
    draft: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[str, dict[str, Any]]:
    config = _load_validation_profiles()
    profiles = config.get("profiles") if isinstance(config.get("profiles"), Mapping) else {}
    default_profile_id = str(config.get("default_profile_id") or "generic_company")
    explicit = _explicit_profile_id(context, draft=draft, evidence=evidence)
    if explicit and isinstance(profiles.get(explicit), Mapping):
        return explicit, dict(profiles[explicit])

    company = _clean_company(_target_company(context, draft=draft, evidence=evidence))
    if company:
        for profile_id, profile in profiles.items():
            if not isinstance(profile, Mapping):
                continue
            companies = {
                _clean_company(item)
                for item in profile.get("companies", ())
                if _clean_company(item)
            }
            if _company_matches_profile(company, companies):
                return str(profile_id), dict(profile)

    fallback = profiles.get(default_profile_id)
    if isinstance(fallback, Mapping):
        return default_profile_id, dict(fallback)
    return "generic_company", dict(_FALLBACK_PROFILE_CONFIG["profiles"]["generic_company"])


def _has_profile_operating_insight(
    text: str,
    profile: Mapping[str, Any],
) -> bool:
    terms = tuple(str(term).lower() for term in profile.get("operating_terms", ()) if str(term))
    minimum = int(profile.get("minimum_operating_terms") or 0)
    if minimum <= 0:
        return True
    lowered = text.lower()
    return sum(1 for term in terms if term in lowered) >= minimum


def _evidence_text(
    context: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> str:
    parts: list[str] = []
    for item in evidence.get("items", ()) or ():
        if isinstance(item, Mapping):
            parts.append(str(item.get("text") or item.get("content") or ""))
    for item in context.get("retrieval_chunks", ()) or ():
        if isinstance(item, Mapping):
            parts.append(str(item.get("text") or item.get("content") or item.get("body") or ""))
    return "\n".join(parts).lower()


def _profile_forbidden_terms_without_evidence(
    text: str,
    profile: Mapping[str, Any],
    context: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> list[str]:
    lowered = text.lower()
    evidence_corpus = _evidence_text(context, evidence)
    violations: list[str] = []
    for raw_term in profile.get("forbidden_terms_without_evidence", ()) or ():
        term = str(raw_term).lower().strip()
        if term and term in lowered and term not in evidence_corpus:
            violations.append(term)
    return violations


def _has_unsupported_company_trigger_claim(
    text: str,
    context: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> bool:
    if _COMPANY_TRIGGER_CLAIM_RE.search(text) is None:
        return False
    evidence_corpus = _evidence_text(context, evidence)
    if not evidence_corpus:
        return True
    return _COMPANY_TRIGGER_CLAIM_RE.search(evidence_corpus) is None


def _has_candidate_proof(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in _CANDIDATE_PROOF_TERMS)


def _has_unverified_candidate_metric(text: str) -> bool:
    lowered = text.lower()
    if not re.search(r"\b(improved|increased|reduced|cut|saved|grew|delivered)\b", lowered):
        return False
    return bool(re.search(r"\b\d+(?:\.\d+)?\s?%", lowered))
