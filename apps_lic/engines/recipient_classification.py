"""C0-A recipient classification for apps_lic W3.

The classifier derives recipient_class from evidence documents. U0 can supply
hints, but hints are never scoring authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_CONTACT,
    NAMESPACE_JD,
    NAMESPACE_REFERRAL,
    NAMESPACE_RELATIONSHIP,
    NAMESPACE_ROLE_OWNERSHIP,
    OpportunityFactDocument,
    OpportunityFactStore,
)


CLASS_RECRUITER = "RECRUITER"
CLASS_SENIOR_TA = "SENIOR_TA"
CLASS_HIRING_MANAGER = "HIRING_MANAGER"
CLASS_EXECUTIVE = "EXECUTIVE"
CLASS_C_LEVEL = "C_LEVEL"
CLASS_CEO = "CEO"
CLASS_CTO = "CTO"
CLASS_VP_ENG = "VP_ENG"
CLASS_REFERRAL_CONTACT = "REFERRAL_CONTACT"
CLASS_UNKNOWN = "UNKNOWN"

STATUS_DERIVED = "RECIPIENT_CLASS_DERIVED"
STATUS_LOW_CONFIDENCE = "RECIPIENT_CLASS_LOW_CONFIDENCE"
STATUS_CONFLICTED = "RECIPIENT_CLASS_CONFLICTED"
STATUS_MISSING_EVIDENCE = "C0_OPPORTUNITY_INGESTION_REQUIRED"

TARGET_ELIGIBLE = "ELIGIBLE"
TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE = "ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE"
TARGET_NOT_TARGETABLE = "NOT_TARGETABLE"
TARGET_C0_EVIDENCE_REQUIRED = "C0_EVIDENCE_REQUIRED"

ALT_GENERAL_INTRO_NO_JD = "general_intro_no_jd"
ALT_COMPANY_CONTEXT_INTRO = "company_context_intro"
ALT_PEER_NETWORKING_INTRO = "peer_networking_intro"
MESSAGE_ROLE_SPECIFIC = "role_specific"
MESSAGE_GENERAL_INTRO = "general_intro"

DRAFT_EXPOSURE_ALLOWED = "USER_VISIBLE_DRAFT_ALLOWED"
DRAFT_EXPOSURE_BLOCKED = "USER_VISIBLE_DRAFT_BLOCKED"

_CLASS_PRIORITY: tuple[str, ...] = (
    CLASS_CEO,
    CLASS_CTO,
    CLASS_VP_ENG,
    CLASS_C_LEVEL,
    CLASS_SENIOR_TA,
    CLASS_HIRING_MANAGER,
    CLASS_EXECUTIVE,
    CLASS_RECRUITER,
    CLASS_REFERRAL_CONTACT,
)

_CONFIDENCE_THRESHOLDS: dict[str, float] = {
    CLASS_RECRUITER: 0.60,
    CLASS_SENIOR_TA: 0.65,
    CLASS_HIRING_MANAGER: 0.60,
    CLASS_EXECUTIVE: 0.62,
    CLASS_C_LEVEL: 0.66,
    CLASS_CEO: 0.66,
    CLASS_CTO: 0.66,
    CLASS_VP_ENG: 0.66,
    CLASS_REFERRAL_CONTACT: 0.60,
}

_MIN_CONFLICT_SIGNAL = 2.5


@dataclass(frozen=True)
class RecipientClassRule:
    recipient_class: str
    pattern: str
    reason_code: str
    weight: float

    def matches(self, text: str) -> bool:
        return re.search(self.pattern, text, flags=re.IGNORECASE) is not None


@dataclass(frozen=True)
class RecipientClassEvidenceSignal:
    recipient_class: str
    reason_code: str
    matched_text: str
    source_snapshot_id: str
    source_id: str
    weight: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipient_class": self.recipient_class,
            "reason_code": self.reason_code,
            "matched_text": self.matched_text,
            "source_snapshot_id": self.source_snapshot_id,
            "source_id": self.source_id,
            "weight": self.weight,
        }


@dataclass(frozen=True)
class RecipientClassDerivation:
    status: str
    derived_recipient_class: str
    recipient_class_confidence: float
    class_reason_codes: tuple[str, ...]
    source_snapshot_ids: tuple[str, ...]
    supporting_facts: tuple[RecipientClassEvidenceSignal, ...]
    contradicted_facts: tuple[RecipientClassEvidenceSignal, ...]
    contradiction_status: str
    hitl_required: bool
    u0_hint: str
    u0_hint_used_as_authority: bool
    evidence_packet_id: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.recipient_class_derivation.v1",
            "status": self.status,
            "derived_recipient_class": self.derived_recipient_class,
            "recipient_class_confidence": self.recipient_class_confidence,
            "class_reason_codes": list(self.class_reason_codes),
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "supporting_facts": [signal.to_dict() for signal in self.supporting_facts],
            "contradicted_facts": [signal.to_dict() for signal in self.contradicted_facts],
            "contradiction_status": self.contradiction_status,
            "hitl_required": self.hitl_required,
            "u0_hint": self.u0_hint,
            "u0_hint_used_as_authority": self.u0_hint_used_as_authority,
            "evidence_packet_id": self.evidence_packet_id,
        }


@dataclass(frozen=True)
class TargetEligibilityResult:
    """W3 target eligibility decision for the requested opportunity scope."""

    target_eligibility: str
    recipient_class: str
    requested_message_type: str
    alternate_message_mode: str
    no_send_required: bool
    user_visible_draft_allowed: bool
    strict_jd_user_visible_draft_allowed: bool
    reason_codes: tuple[str, ...]
    required_c0_namespaces: tuple[str, ...]
    blocked_copy_terms: tuple[str, ...]
    source_snapshot_ids: tuple[str, ...]
    eligibility_packet_id: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.target_eligibility.v1",
            "target_eligibility": self.target_eligibility,
            "recipient_class": self.recipient_class,
            "requested_message_type": self.requested_message_type,
            "alternate_message_mode": self.alternate_message_mode,
            "no_send_required": self.no_send_required,
            "user_visible_draft_allowed": self.user_visible_draft_allowed,
            "strict_jd_user_visible_draft_allowed": self.strict_jd_user_visible_draft_allowed,
            "reason_codes": list(self.reason_codes),
            "required_c0_namespaces": list(self.required_c0_namespaces),
            "blocked_copy_terms": list(self.blocked_copy_terms),
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "eligibility_packet_id": self.eligibility_packet_id,
        }


@dataclass(frozen=True)
class DraftExposureDecision:
    """No-send decision for whether draft copy may be shown to the user."""

    status: str
    allowed: bool
    user_visible_text: str
    reason_codes: tuple[str, ...]
    blocked_terms: tuple[str, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.draft_exposure_decision.v1",
            "status": self.status,
            "allowed": self.allowed,
            "user_visible_text": self.user_visible_text,
            "reason_codes": list(self.reason_codes),
            "blocked_terms": list(self.blocked_terms),
        }


_RULES: tuple[RecipientClassRule, ...] = (
    RecipientClassRule(CLASS_CEO, r"\b(chief executive officer|founder\s*&?\s*ceo|ceo)\b", "ceo_title_signal", 7.5),
    RecipientClassRule(CLASS_CTO, r"\b(chief technology officer|cto)\b", "cto_title_signal", 7.0),
    RecipientClassRule(CLASS_VP_ENG, r"\b(vp|vice president)\s+(of\s+)?engineering\b", "vp_eng_title_signal", 6.5),
    RecipientClassRule(CLASS_C_LEVEL, r"\bchief\s+(?!executive\b)(?!technology\b)[a-z&,\s]+\s+officer\b", "c_level_title_signal", 9.0),
    RecipientClassRule(CLASS_C_LEVEL, r"\b(cio|ciso|cfo|coo|cmo|cpo|cro|chro|cdo)\b", "c_level_abbrev_signal", 2.0),
    RecipientClassRule(CLASS_SENIOR_TA, r"\b(global\s+head|head|director|vp|vice president|leader|lead)\s+(of\s+)?(talent acquisition|recruiting|executive hiring)\b", "senior_ta_leadership_title", 6.5),
    RecipientClassRule(CLASS_SENIOR_TA, r"\b(talent acquisition|recruiting|executive hiring)\s+(manager|leader|lead|director|head)\b", "senior_ta_function_leadership_title", 6.2),
    RecipientClassRule(CLASS_SENIOR_TA, r"\b(owns|leads|directs|runs)\s+(recruiting strategy|talent acquisition|executive hiring)\b", "senior_ta_ownership_signal", 6.0),
    RecipientClassRule(CLASS_RECRUITER, r"\b(technical recruiter|senior recruiter|recruiter|sourcer|sourcing specialist|talent acquisition specialist|recruiting coordinator)\b", "recruiter_title_signal", 4.0),
    RecipientClassRule(CLASS_RECRUITER, r"\bsenior talent acquisition professional\b", "senior_talent_acquisition_professional_signal", 4.2),
    RecipientClassRule(CLASS_RECRUITER, r"\b(?:senior\s+|global\s+)?talent acquisition partner\b", "recruiter_partner_signal", 5.2),
    RecipientClassRule(CLASS_RECRUITER, r"\btalent acquisition strategist\b", "recruiter_ta_strategist_signal", 4.8),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\b(hiring manager|engineering manager|manager,\s*engineering|product manager|platform manager)\b", "hiring_manager_title_signal", 4.5),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\b(director|head)\s+(of\s+)?(engineering|platform|product|data|ai)\b", "hiring_manager_leader_signal", 4.0),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\bhead\s+(of\s+)?(e-?discovery|cyber(?:security)?|cyber investigations|broker services|producer licensing|claims|underwriting|operations|legal|compliance|regulatory technology)\b", "hiring_manager_function_head_signal", 4.8),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\b(owns hiring|building the team|hiring for|role owner)\b", "hiring_owner_signal", 4.0),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\b(ai systems builder|ai platform builder)\b", "hiring_manager_ai_builder_signal", 4.4),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\b(product\s*/\s*hiring|hiring amplifier)\b", "hiring_manager_product_hiring_signal", 4.4),
    RecipientClassRule(CLASS_HIRING_MANAGER, r"\b(ai and data platform product/architecture leader|product/architecture leader|data platform product.*leader)\b", "hiring_manager_product_architecture_leader_signal", 4.8),
    RecipientClassRule(CLASS_EXECUTIVE, r"\b(executive chair(?:man|woman)?|chair(?:man|woman)? of the board|board chair)\b", "executive_chair_signal", 6.0),
    RecipientClassRule(CLASS_EXECUTIVE, r"\b(svp|evp|senior vice president|executive vice president|(?<!vice )president|general manager|managing director)\b", "executive_title_signal", 3.5),
    RecipientClassRule(CLASS_EXECUTIVE, r"\bhead\s+(of\s+)?technology\s+(and|&)\s+business enablement\b", "executive_technology_business_enablement_signal", 4.8),
    RecipientClassRule(CLASS_EXECUTIVE, r"\bvice president\b", "executive_vp_signal", 1.0),
    RecipientClassRule(CLASS_REFERRAL_CONTACT, r"\b(referrer|referral|mutual connection|former colleague|introduced by|warm intro)\b", "referral_contact_signal", 3.5),
)

_AMBIGUOUS_PATTERNS: tuple[str, ...] = (
    r"\btalent partner\s*/\s*business partner\b",
    r"\bpeople partner\b",
    r"\bbusiness partner\b",
)

_FORMER_ROLE_PATTERNS: tuple[str, ...] = (
    r"\bformer\s+(?:chief executive officer|ceo)\b",
    r"\bformer(?:ly)?\b.*\b(?:chief executive officer|ceo)\b",
    r"\bprevious(?:ly)?\s+(?:served\s+as\s+)?(?:chief executive officer|ceo)\b",
    r"\bserved\s+as\s+(?:chief executive officer|ceo)\b",
    r"\bwas\s+(?:the\s+)?(?:chief executive officer|ceo)\b",
    r"\b(?:chief executive officer|ceo)\s+from\s+\d{4}\b",
    r"\b(?:chief executive officer|ceo)\s+until\b",
    r"\bstill\s+says\b.*\b(?:chief executive officer|ceo)\b",
    r"\bstale\b.*\b(?:chief executive officer|ceo)\b",
)

_NEGATED_ROLE_CLAUSE_PATTERN = re.compile(
    r"\b(?:no explicit current|no current|not currently|without explicit current)\b[^|.;\n]*",
    flags=re.IGNORECASE,
)

_US_JD_LOCATION_HINTS = (
    "new york",
    "ny-new york",
    "charlotte",
    "nc-charlotte",
    "atlanta",
    "ga-atlanta",
)
_NON_US_OWNERSHIP_HINTS = (
    "aig japan",
    "japan",
    "tokyo",
)
_IC_TITLE_PATTERN = re.compile(
    r"\b(software engineer|data engineer|business analyst|developer|engineer|analyst|individual contributor)\b",
    flags=re.IGNORECASE,
)
_TARGET_OWNER_PATTERN = re.compile(
    r"\b(recruit|talent acquisition|sourc|hiring manager|owns hiring|role owner|head|director|manager|vp|vice president|chief|executive|president)\b",
    flags=re.IGNORECASE,
)
_JD_REFERENCE_PATTERN = re.compile(
    r"\b(jd|job description|requisition|req(?:uisition)?\s*(?:number|id|#)?|job id|jr[0-9][a-z0-9._-]*)\b",
    flags=re.IGNORECASE,
)

_SPECIFIC_C_SUITE_CLASSES = frozenset(
    {
        CLASS_CEO,
        CLASS_CTO,
        CLASS_C_LEVEL,
        CLASS_VP_ENG,
    }
)


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _evidence_text(document: OpportunityFactDocument) -> str:
    metadata = dict(document.metadata)
    parts = [
        document.fact_text,
        metadata.get("title"),
        metadata.get("headline"),
        metadata.get("name"),
        metadata.get("company"),
        metadata.get("ownership_signal"),
        metadata.get("relationship_context"),
        metadata.get("referrer_name"),
        metadata.get("permission_scope"),
    ]
    return " | ".join(_clean(part) for part in parts if _clean(part))


def _strip_negated_role_clauses(text: str) -> str:
    return _NEGATED_ROLE_CLAUSE_PATTERN.sub(" ", text)


def _is_ambiguous(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in _AMBIGUOUS_PATTERNS)


def _is_former_role_signal(rule: RecipientClassRule, text: str) -> bool:
    if rule.recipient_class != CLASS_CEO:
        return False
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in _FORMER_ROLE_PATTERNS)


def _signal_documents(documents: Iterable[OpportunityFactDocument]) -> tuple[OpportunityFactDocument, ...]:
    allowed = {
        NAMESPACE_CONTACT,
        NAMESPACE_ROLE_OWNERSHIP,
        NAMESPACE_RELATIONSHIP,
        NAMESPACE_REFERRAL,
    }
    return tuple(document for document in documents if document.namespace in allowed)


def _target_eligibility_documents(
    documents: Iterable[OpportunityFactDocument],
) -> tuple[OpportunityFactDocument, ...]:
    allowed = {
        NAMESPACE_CONTACT,
        NAMESPACE_ROLE_OWNERSHIP,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
    }
    return tuple(document for document in documents if document.namespace in allowed)


def _score_documents(
    documents: Iterable[OpportunityFactDocument],
) -> tuple[dict[str, float], tuple[RecipientClassEvidenceSignal, ...], tuple[str, ...]]:
    scores: dict[str, float] = {}
    signals: list[RecipientClassEvidenceSignal] = []
    ambiguous_sources: list[str] = []

    for document in documents:
        text = _strip_negated_role_clauses(_evidence_text(document))
        if not text:
            continue
        if _is_ambiguous(text):
            ambiguous_sources.append(document.source_snapshot_id)
        for rule in _RULES:
            if rule.matches(text):
                confidence = max(0.0, min(1.0, document.confidence))
                demoted = _is_former_role_signal(rule, text)
                weight = round(rule.weight * confidence * (0.15 if demoted else 1.0), 4)
                scores[rule.recipient_class] = scores.get(rule.recipient_class, 0.0) + weight
                signals.append(
                    RecipientClassEvidenceSignal(
                        recipient_class=rule.recipient_class,
                        reason_code=(
                            f"{rule.reason_code}:former_or_stale_role_demotion"
                            if demoted
                            else rule.reason_code
                        ),
                        matched_text=text[:280],
                        source_snapshot_id=document.source_snapshot_id,
                        source_id=document.source_id,
                        weight=weight,
                    )
                )

    return scores, tuple(signals), tuple(ambiguous_sources)


def _apply_specific_c_suite_preference(scores: dict[str, float]) -> dict[str, float]:
    """Prefer exact C-suite titles over generic EVP/SVP/president text."""
    strongest_specific = max(
        (scores.get(recipient_class, 0.0) for recipient_class in _SPECIFIC_C_SUITE_CLASSES),
        default=0.0,
    )
    if strongest_specific >= 6.0 and scores.get(CLASS_EXECUTIVE, 0.0) > 0.0:
        scores = dict(scores)
        scores[CLASS_EXECUTIVE] = min(scores[CLASS_EXECUTIVE], 0.5)
    return scores


def _target_identity_has_non_referral_signal(
    documents: Iterable[OpportunityFactDocument],
) -> bool:
    for document in documents:
        if document.namespace not in {NAMESPACE_CONTACT, NAMESPACE_ROLE_OWNERSHIP}:
            continue
        text = _evidence_text(document)
        if any(
            rule.recipient_class != CLASS_REFERRAL_CONTACT and rule.matches(text)
            for rule in _RULES
        ):
            return True
    return False


def _without_referral_context_class_signals(
    signals: Iterable[RecipientClassEvidenceSignal],
) -> tuple[dict[str, float], tuple[RecipientClassEvidenceSignal, ...]]:
    kept = tuple(
        signal
        for signal in signals
        if not (
            signal.recipient_class == CLASS_REFERRAL_CONTACT
            and (
                signal.source_snapshot_id.startswith(NAMESPACE_REFERRAL)
                or signal.source_snapshot_id.startswith(NAMESPACE_RELATIONSHIP)
            )
        )
    )
    scores: dict[str, float] = {}
    for signal in kept:
        scores[signal.recipient_class] = scores.get(signal.recipient_class, 0.0) + signal.weight
    return scores, kept


def _sort_scores(scores: Mapping[str, float]) -> list[tuple[str, float]]:
    priority = {klass: idx for idx, klass in enumerate(_CLASS_PRIORITY)}
    return sorted(
        scores.items(),
        key=lambda item: (-item[1], priority.get(item[0], 999), item[0]),
    )


def _confidence(top_score: float, runner_up_score: float) -> float:
    if top_score <= 0:
        return 0.0
    return round(min(0.99, top_score / (top_score + runner_up_score + 0.25)), 4)


def _signals_for_class(
    signals: Iterable[RecipientClassEvidenceSignal],
    recipient_class: str,
) -> tuple[RecipientClassEvidenceSignal, ...]:
    return tuple(signal for signal in signals if signal.recipient_class == recipient_class)


def _has_ic_only_signal(documents: Iterable[OpportunityFactDocument]) -> bool:
    text = " | ".join(_evidence_text(document) for document in documents)
    return bool(_IC_TITLE_PATTERN.search(text)) and not bool(_TARGET_OWNER_PATTERN.search(text))


def _has_opportunity_region_mismatch(
    documents: Iterable[OpportunityFactDocument],
) -> bool:
    role_text = " ".join(
        _evidence_text(document)
        for document in documents
        if document.namespace == NAMESPACE_ROLE_OWNERSHIP
    ).lower()
    jd_text = " ".join(
        " ".join(
            (
                _evidence_text(document),
                " ".join(_clean(value) for value in dict(document.metadata).values()),
            )
        )
        for document in documents
        if document.namespace == NAMESPACE_JD
    ).lower()
    return (
        any(hint in role_text for hint in _NON_US_OWNERSHIP_HINTS)
        and any(hint in jd_text for hint in _US_JD_LOCATION_HINTS)
    )


def _jd_blocked_copy_terms(documents: Iterable[OpportunityFactDocument]) -> tuple[str, ...]:
    terms: list[str] = []
    for document in documents:
        if document.namespace != NAMESPACE_JD:
            continue
        metadata = dict(document.metadata)
        for key in ("position_name", "job_title", "title", "requisition_number", "req_id", "job_id"):
            value = _clean(metadata.get(key))
            if len(value) >= 3:
                terms.append(value)
    return tuple(dict.fromkeys(terms))


def _source_snapshot_ids(documents: Iterable[OpportunityFactDocument]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(document.source_snapshot_id for document in documents))


def _target_packet_id(seed: Mapping[str, Any]) -> str:
    return _sha256_canonical(seed)


def _target_result(
    *,
    target_eligibility: str,
    recipient_class: str,
    requested_message_type: str,
    alternate_message_mode: str = "",
    no_send_required: bool,
    user_visible_draft_allowed: bool,
    strict_jd_user_visible_draft_allowed: bool,
    reason_codes: Iterable[str],
    required_c0_namespaces: Iterable[str],
    blocked_copy_terms: Iterable[str],
    source_snapshot_ids: Iterable[str],
) -> TargetEligibilityResult:
    reason_tuple = tuple(dict.fromkeys(_clean(reason) for reason in reason_codes if _clean(reason)))
    required_tuple = tuple(dict.fromkeys(_clean(item) for item in required_c0_namespaces if _clean(item)))
    blocked_terms = tuple(dict.fromkeys(_clean(item) for item in blocked_copy_terms if _clean(item)))
    source_tuple = tuple(dict.fromkeys(_clean(item) for item in source_snapshot_ids if _clean(item)))
    packet_seed = {
        "target_eligibility": target_eligibility,
        "recipient_class": recipient_class,
        "requested_message_type": requested_message_type,
        "alternate_message_mode": alternate_message_mode,
        "reason_codes": reason_tuple,
        "required_c0_namespaces": required_tuple,
        "blocked_copy_terms": blocked_terms,
        "source_snapshot_ids": source_tuple,
    }
    return TargetEligibilityResult(
        target_eligibility=target_eligibility,
        recipient_class=recipient_class,
        requested_message_type=requested_message_type,
        alternate_message_mode=alternate_message_mode,
        no_send_required=no_send_required,
        user_visible_draft_allowed=user_visible_draft_allowed,
        strict_jd_user_visible_draft_allowed=strict_jd_user_visible_draft_allowed,
        reason_codes=reason_tuple,
        required_c0_namespaces=required_tuple,
        blocked_copy_terms=blocked_terms,
        source_snapshot_ids=source_tuple,
        eligibility_packet_id=_target_packet_id(packet_seed),
    )


def _top_class_for_document(document: OpportunityFactDocument) -> tuple[str, float] | None:
    scores, _signals, _ambiguous = _score_documents((document,))
    scores = _apply_specific_c_suite_preference(scores)
    ranked = _sort_scores(scores)
    if not ranked:
        return None
    return ranked[0]


def _contradictions(
    documents: Iterable[OpportunityFactDocument],
    signals: tuple[RecipientClassEvidenceSignal, ...],
    top_class: str,
) -> tuple[RecipientClassEvidenceSignal, ...]:
    source_classes: dict[str, str] = {}
    for document in documents:
        top = _top_class_for_document(document)
        if top is None:
            continue
        klass, score = top
        if score >= _MIN_CONFLICT_SIGNAL:
            source_classes[document.source_snapshot_id] = klass

    unique_classes = set(source_classes.values())
    if len(unique_classes) <= 1:
        return ()
    if unique_classes <= {CLASS_CEO, CLASS_C_LEVEL, CLASS_EXECUTIVE}:
        return ()
    return tuple(
        signal
        for signal in signals
        if signal.recipient_class != top_class
        and source_classes.get(signal.source_snapshot_id) == signal.recipient_class
    )


def derive_recipient_class(
    documents: Iterable[OpportunityFactDocument],
    *,
    u0_recipient_class_hint: str = "",
) -> RecipientClassDerivation:
    """Derive recipient class from C0 evidence documents."""
    evidence_docs = _signal_documents(documents)
    source_snapshot_ids = tuple(document.source_snapshot_id for document in evidence_docs)
    if not evidence_docs:
        return RecipientClassDerivation(
            status=STATUS_MISSING_EVIDENCE,
            derived_recipient_class=CLASS_UNKNOWN,
            recipient_class_confidence=0.0,
            class_reason_codes=("missing_contact_or_role_ownership_evidence",),
            source_snapshot_ids=(),
            supporting_facts=(),
            contradicted_facts=(),
            contradiction_status="NOT_APPLICABLE",
            hitl_required=True,
            u0_hint=_clean(u0_recipient_class_hint),
            u0_hint_used_as_authority=False,
            evidence_packet_id=_sha256_canonical({"status": STATUS_MISSING_EVIDENCE}),
        )

    scores, signals, ambiguous_sources = _score_documents(evidence_docs)
    if _target_identity_has_non_referral_signal(evidence_docs):
        scores, signals = _without_referral_context_class_signals(signals)
    scores = _apply_specific_c_suite_preference(scores)
    ranked = _sort_scores(scores)
    if not ranked:
        reason_codes = ("ambiguous_title_signal",) if ambiguous_sources else ("no_class_signal",)
        contradiction_status = "AMBIGUOUS_LOW_CONFIDENCE" if ambiguous_sources else "LOW_CONFIDENCE"
        return RecipientClassDerivation(
            status=STATUS_LOW_CONFIDENCE,
            derived_recipient_class=CLASS_UNKNOWN,
            recipient_class_confidence=0.0,
            class_reason_codes=reason_codes,
            source_snapshot_ids=source_snapshot_ids,
            supporting_facts=(),
            contradicted_facts=(),
            contradiction_status=contradiction_status,
            hitl_required=True,
            u0_hint=_clean(u0_recipient_class_hint),
            u0_hint_used_as_authority=False,
            evidence_packet_id=_sha256_canonical({"scores": scores, "sources": source_snapshot_ids}),
        )

    top_class, top_score = ranked[0]
    runner_up_score = ranked[1][1] if len(ranked) > 1 else 0.0
    confidence = _confidence(top_score, runner_up_score)
    threshold = _CONFIDENCE_THRESHOLDS.get(top_class, 0.65)
    supporting = _signals_for_class(signals, top_class)
    contradicted = _contradictions(evidence_docs, signals, top_class)
    demotion_reason_codes = tuple(
        signal.reason_code
        for signal in signals
        if "former_or_stale_role_demotion" in signal.reason_code
    )
    reason_codes = tuple(
        dict.fromkeys(
            (
                *(signal.reason_code for signal in supporting),
                *demotion_reason_codes,
            )
        )
    )

    if contradicted:
        status = STATUS_CONFLICTED
        derived_class = CLASS_UNKNOWN
        hitl_required = True
        contradiction_status = "CONFLICTED"
    elif ambiguous_sources and top_score < 4.0:
        status = STATUS_LOW_CONFIDENCE
        derived_class = CLASS_UNKNOWN
        hitl_required = True
        contradiction_status = "AMBIGUOUS_LOW_CONFIDENCE"
        reason_codes = tuple(dict.fromkeys((*reason_codes, "ambiguous_title_signal")))
    elif confidence < threshold:
        status = STATUS_LOW_CONFIDENCE
        derived_class = CLASS_UNKNOWN
        hitl_required = True
        contradiction_status = "LOW_CONFIDENCE"
    else:
        status = STATUS_DERIVED
        derived_class = top_class
        hitl_required = False
        contradiction_status = "CLEAR"

    packet_seed = {
        "status": status,
        "derived": derived_class,
        "scores": scores,
        "sources": source_snapshot_ids,
        "reason_codes": reason_codes,
        "contradictions": [signal.to_dict() for signal in contradicted],
    }
    return RecipientClassDerivation(
        status=status,
        derived_recipient_class=derived_class,
        recipient_class_confidence=confidence,
        class_reason_codes=reason_codes,
        source_snapshot_ids=source_snapshot_ids,
        supporting_facts=supporting,
        contradicted_facts=contradicted,
        contradiction_status=contradiction_status,
        hitl_required=hitl_required,
        u0_hint=_clean(u0_recipient_class_hint),
        u0_hint_used_as_authority=False,
        evidence_packet_id=_sha256_canonical(packet_seed),
    )


def derive_recipient_class_from_store(
    store: OpportunityFactStore,
    *,
    u0_recipient_class_hint: str = "",
) -> RecipientClassDerivation:
    """Read W2 opportunity evidence and derive recipient_class without writes."""
    documents: list[OpportunityFactDocument] = []
    for namespace in (
        NAMESPACE_CONTACT,
        NAMESPACE_ROLE_OWNERSHIP,
        NAMESPACE_RELATIONSHIP,
        NAMESPACE_REFERRAL,
    ):
        documents.extend(store.query_namespace(namespace))
    return derive_recipient_class(
        documents,
        u0_recipient_class_hint=u0_recipient_class_hint,
    )


def evaluate_target_eligibility(
    *,
    recipient_derivation: RecipientClassDerivation,
    documents: Iterable[OpportunityFactDocument],
    requested_message_type: str = MESSAGE_ROLE_SPECIFIC,
    allow_alternate_message_mode: bool = False,
    allow_peer_networking_scope: bool = False,
) -> TargetEligibilityResult:
    """Resolve whether this contact is targetable for apps_lic outreach."""
    document_tuple = _target_eligibility_documents(documents)
    source_ids = _source_snapshot_ids(document_tuple)
    requested_type = _clean(requested_message_type) or MESSAGE_ROLE_SPECIFIC
    recipient_class = recipient_derivation.derived_recipient_class

    if recipient_derivation.status == STATUS_MISSING_EVIDENCE:
        return _target_result(
            target_eligibility=TARGET_C0_EVIDENCE_REQUIRED,
            recipient_class=recipient_class,
            requested_message_type=requested_type,
            no_send_required=True,
            user_visible_draft_allowed=False,
            strict_jd_user_visible_draft_allowed=False,
            reason_codes=("c0_evidence_required:missing_contact_or_role_ownership_evidence",),
            required_c0_namespaces=(NAMESPACE_CONTACT, NAMESPACE_ROLE_OWNERSHIP),
            blocked_copy_terms=(),
            source_snapshot_ids=source_ids,
        )

    if recipient_derivation.status == STATUS_CONFLICTED:
        return _target_result(
            target_eligibility=TARGET_C0_EVIDENCE_REQUIRED,
            recipient_class=recipient_class,
            requested_message_type=requested_type,
            no_send_required=True,
            user_visible_draft_allowed=False,
            strict_jd_user_visible_draft_allowed=False,
            reason_codes=("c0_evidence_required:conflicted_recipient_class_evidence",),
            required_c0_namespaces=(NAMESPACE_CONTACT, NAMESPACE_ROLE_OWNERSHIP),
            blocked_copy_terms=(),
            source_snapshot_ids=source_ids,
        )

    if recipient_derivation.status != STATUS_DERIVED or recipient_class == CLASS_UNKNOWN:
        if _has_ic_only_signal(document_tuple):
            if allow_peer_networking_scope:
                return _target_result(
                    target_eligibility=TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE,
                    recipient_class=recipient_class,
                    requested_message_type=requested_type,
                    alternate_message_mode=ALT_PEER_NETWORKING_INTRO,
                    no_send_required=False,
                    user_visible_draft_allowed=True,
                    strict_jd_user_visible_draft_allowed=False,
                    reason_codes=("alternate_scope:peer_networking_explicitly_allowed",),
                    required_c0_namespaces=(NAMESPACE_CONTACT,),
                    blocked_copy_terms=_jd_blocked_copy_terms(document_tuple),
                    source_snapshot_ids=source_ids,
                )
            return _target_result(
                target_eligibility=TARGET_NOT_TARGETABLE,
                recipient_class=recipient_class,
                requested_message_type=requested_type,
                no_send_required=True,
                user_visible_draft_allowed=False,
                strict_jd_user_visible_draft_allowed=False,
                reason_codes=("not_targetable:ic_profile_out_of_apps_lic_scope",),
                required_c0_namespaces=(),
                blocked_copy_terms=_jd_blocked_copy_terms(document_tuple),
                source_snapshot_ids=source_ids,
            )
        return _target_result(
            target_eligibility=TARGET_NOT_TARGETABLE,
            recipient_class=recipient_class,
            requested_message_type=requested_type,
            no_send_required=True,
            user_visible_draft_allowed=False,
            strict_jd_user_visible_draft_allowed=False,
            reason_codes=("not_targetable:no_current_target_owner_signal",),
            required_c0_namespaces=(),
            blocked_copy_terms=_jd_blocked_copy_terms(document_tuple),
            source_snapshot_ids=source_ids,
        )

    role_specific = requested_type == MESSAGE_ROLE_SPECIFIC
    region_mismatch = role_specific and _has_opportunity_region_mismatch(document_tuple)
    if region_mismatch:
        if allow_alternate_message_mode:
            return _target_result(
                target_eligibility=TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE,
                recipient_class=recipient_class,
                requested_message_type=requested_type,
                alternate_message_mode=ALT_GENERAL_INTRO_NO_JD,
                no_send_required=False,
                user_visible_draft_allowed=True,
                strict_jd_user_visible_draft_allowed=False,
                reason_codes=("alternate_mode:role_ownership_region_mismatch_general_intro_no_jd",),
                required_c0_namespaces=(NAMESPACE_CONTACT, NAMESPACE_COMPANY, NAMESPACE_ROLE_OWNERSHIP),
                blocked_copy_terms=_jd_blocked_copy_terms(document_tuple),
                source_snapshot_ids=source_ids,
            )
        return _target_result(
            target_eligibility=TARGET_NOT_TARGETABLE,
            recipient_class=recipient_class,
            requested_message_type=requested_type,
            no_send_required=True,
            user_visible_draft_allowed=False,
            strict_jd_user_visible_draft_allowed=False,
            reason_codes=("not_targetable:role_ownership_region_mismatch_for_requested_jd",),
            required_c0_namespaces=(),
            blocked_copy_terms=_jd_blocked_copy_terms(document_tuple),
            source_snapshot_ids=source_ids,
        )

    return _target_result(
        target_eligibility=TARGET_ELIGIBLE,
        recipient_class=recipient_class,
        requested_message_type=requested_type,
        no_send_required=False,
        user_visible_draft_allowed=True,
        strict_jd_user_visible_draft_allowed=True,
        reason_codes=("eligible:derived_recipient_class_and_opportunity_fit",),
        required_c0_namespaces=(),
        blocked_copy_terms=(),
        source_snapshot_ids=source_ids,
    )


def evaluate_target_eligibility_from_store(
    *,
    store: OpportunityFactStore,
    recipient_derivation: RecipientClassDerivation,
    requested_message_type: str = MESSAGE_ROLE_SPECIFIC,
    allow_alternate_message_mode: bool = False,
    allow_peer_networking_scope: bool = False,
) -> TargetEligibilityResult:
    """Read W2 facts and resolve W3 target eligibility without writes."""
    documents: list[OpportunityFactDocument] = []
    for namespace in (
        NAMESPACE_CONTACT,
        NAMESPACE_ROLE_OWNERSHIP,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
    ):
        documents.extend(store.query_namespace(namespace))
    return evaluate_target_eligibility(
        recipient_derivation=recipient_derivation,
        documents=documents,
        requested_message_type=requested_message_type,
        allow_alternate_message_mode=allow_alternate_message_mode,
        allow_peer_networking_scope=allow_peer_networking_scope,
    )


def evaluate_user_visible_draft_exposure(
    *,
    target_eligibility: TargetEligibilityResult,
    draft_text: str,
) -> DraftExposureDecision:
    """Apply W3 no-send rule before exposing generated copy to a user."""
    text = _clean(draft_text)
    if not target_eligibility.user_visible_draft_allowed:
        return DraftExposureDecision(
            status=DRAFT_EXPOSURE_BLOCKED,
            allowed=False,
            user_visible_text="",
            reason_codes=("blocked_target_or_strict_jd_scope:no_user_visible_draft",),
            blocked_terms=(),
        )

    blocked_terms = tuple(
        term
        for term in target_eligibility.blocked_copy_terms
        if term and term.lower() in text.lower()
    )
    if (
        target_eligibility.alternate_message_mode == ALT_GENERAL_INTRO_NO_JD
        and (_JD_REFERENCE_PATTERN.search(text) or blocked_terms)
    ):
        return DraftExposureDecision(
            status=DRAFT_EXPOSURE_BLOCKED,
            allowed=False,
            user_visible_text="",
            reason_codes=("alternate_general_intro_no_jd_contains_jd_reference",),
            blocked_terms=blocked_terms,
        )

    return DraftExposureDecision(
        status=DRAFT_EXPOSURE_ALLOWED,
        allowed=True,
        user_visible_text=text,
        reason_codes=("draft_exposure_allowed",),
        blocked_terms=(),
    )


__all__ = [
    "ALT_COMPANY_CONTEXT_INTRO",
    "ALT_GENERAL_INTRO_NO_JD",
    "ALT_PEER_NETWORKING_INTRO",
    "CLASS_CEO",
    "CLASS_CTO",
    "CLASS_C_LEVEL",
    "CLASS_EXECUTIVE",
    "CLASS_HIRING_MANAGER",
    "CLASS_RECRUITER",
    "CLASS_REFERRAL_CONTACT",
    "CLASS_SENIOR_TA",
    "CLASS_UNKNOWN",
    "CLASS_VP_ENG",
    "DRAFT_EXPOSURE_ALLOWED",
    "DRAFT_EXPOSURE_BLOCKED",
    "MESSAGE_GENERAL_INTRO",
    "MESSAGE_ROLE_SPECIFIC",
    "STATUS_CONFLICTED",
    "STATUS_DERIVED",
    "STATUS_LOW_CONFIDENCE",
    "STATUS_MISSING_EVIDENCE",
    "TARGET_C0_EVIDENCE_REQUIRED",
    "TARGET_ELIGIBLE",
    "TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE",
    "TARGET_NOT_TARGETABLE",
    "DraftExposureDecision",
    "RecipientClassDerivation",
    "RecipientClassEvidenceSignal",
    "TargetEligibilityResult",
    "derive_recipient_class",
    "derive_recipient_class_from_store",
    "evaluate_target_eligibility",
    "evaluate_target_eligibility_from_store",
    "evaluate_user_visible_draft_exposure",
]
