"""Governed opportunity ingestion for apps_lic W2.

Inference must not browse, scrape, or write vectors. This module provides the
separate governed ingestion path that prepares opportunity facts and writes only
through an explicit write gate supplied by the caller.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, MutableMapping, Protocol


STATUS_READY = "C0_READY"
STATUS_MISSING = "C0_OPPORTUNITY_INGESTION_REQUIRED"
STATUS_STALE = "C0_EVIDENCE_STALE"
STATUS_CONFLICTED = "C0_EVIDENCE_CONFLICTED"
STATUS_BLOCKED = "C0_EVIDENCE_BLOCKED"

WRITE_AUTHORITY_GOVERNED_INGESTION = "governed_opportunity_ingestion"

NAMESPACE_CONTACT = "apps_lic_contact_facts"
NAMESPACE_COMPANY = "apps_lic_company_facts"
NAMESPACE_JD = "apps_lic_jd_facts"
NAMESPACE_COMPANY_TRIGGER = "apps_lic_company_trigger_facts"
NAMESPACE_ROLE_OWNERSHIP = "apps_lic_role_ownership_facts"
NAMESPACE_RELATIONSHIP = "apps_lic_relationship_facts"
NAMESPACE_REFERRAL = "apps_lic_referral_facts"
NAMESPACE_PRIOR_THREAD = "apps_lic_prior_thread_facts"
NAMESPACE_STANDING_SENDER = "apps_lic_sender_facts"

C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS: tuple[str, ...] = (
    NAMESPACE_CONTACT,
    NAMESPACE_COMPANY,
    NAMESPACE_JD,
    NAMESPACE_ROLE_OWNERSHIP,
)

BASELINE_VECTOR_COLLECTIONS: tuple[tuple[str, str, str], ...] = (
    (
        "standing_sender_corpus",
        NAMESPACE_STANDING_SENDER,
        "Reusable Amit sender profile, approved proof points, graph skills, and claim policy.",
    ),
    (
        "aig_company_facts",
        NAMESPACE_COMPANY,
        "Reusable AIG company facts and company context for personalization.",
    ),
    (
        "aig_jd_facts",
        NAMESPACE_JD,
        "AIG JD facts including position name, requisition number, location, and role family.",
    ),
    (
        "per_contact_public_evidence_facts",
        NAMESPACE_CONTACT,
        "Per-contact public profile snippets, title/headline seed, and source lineage.",
    ),
    (
        "role_ownership_facts",
        NAMESPACE_ROLE_OWNERSHIP,
        "Recruiting, TA leadership, hiring-owner, and executive ownership signals.",
    ),
)

FACT_FAMILY_TO_NAMESPACE: dict[str, str] = {
    "contact": NAMESPACE_CONTACT,
    "company": NAMESPACE_COMPANY,
    "jd": NAMESPACE_JD,
    "company_trigger": NAMESPACE_COMPANY_TRIGGER,
    "role_ownership": NAMESPACE_ROLE_OWNERSHIP,
    "relationship": NAMESPACE_RELATIONSHIP,
    "referral": NAMESPACE_REFERRAL,
    "prior_thread": NAMESPACE_PRIOR_THREAD,
}

DEFAULT_FRESHNESS_DAYS: dict[str, int] = {
    NAMESPACE_CONTACT: 90,
    NAMESPACE_COMPANY: 90,
    NAMESPACE_JD: 45,
    NAMESPACE_COMPANY_TRIGGER: 30,
    NAMESPACE_ROLE_OWNERSHIP: 90,
    NAMESPACE_RELATIONSHIP: 180,
    NAMESPACE_REFERRAL: 180,
    NAMESPACE_PRIOR_THREAD: 365,
}

_REQ_RE = re.compile(
    r"(?im)\b(?:requisition|req|job)\s*(?:number|no\.?|id|#)?\s*[:#-]\s*([A-Z0-9][A-Z0-9._-]{2,})"
)
_PAREN_REQ_RE = re.compile(r"\(([A-Z]{1,6}[0-9][A-Z0-9._-]{3,})\)")
_FIELD_RE = re.compile(
    r"(?im)^[ \t]*(?P<name>[A-Za-z][A-Za-z _/-]{1,40})[ \t]*:[ \t]*(?P<value>[^\r\n]+)[ \t]*$"
)


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso_date(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _field_map_from_text(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in _FIELD_RE.finditer(text):
        key = match.group("name").strip().lower().replace(" ", "_").replace("-", "_")
        fields[key] = match.group("value").strip()
    return fields


def _first_non_empty(*values: Any) -> str:
    for value in values:
        cleaned = _clean(value)
        if cleaned:
            return cleaned
    return ""


def _heading_fields_from_text(text: str) -> dict[str, str]:
    first_line = ""
    for line in str(text or "").splitlines():
        cleaned = _clean(line)
        if cleaned:
            first_line = cleaned
            break
    if not first_line:
        return {}

    req_match = _PAREN_REQ_RE.search(first_line)
    req = req_match.group(1).strip() if req_match else ""
    heading = _PAREN_REQ_RE.sub("", first_line).strip()
    parts = re.split(r"\s+[—-]\s+", heading, maxsplit=1)
    title = _clean(parts[0])
    company = _clean(parts[1]) if len(parts) > 1 else ""
    if not title or ":" in title.lower():
        return {"requisition_number": req} if req else {}
    fields = {"position_name": title}
    if company:
        fields["company"] = company
    if req:
        fields["requisition_number"] = req
    return fields


def _derive_role_family(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if any(token in text for token in ("talent", "recruit", "sourc")):
        return "talent_acquisition"
    if any(token in text for token in ("engineering", "engineer", "platform", "architecture")):
        return "engineering"
    if any(token in text for token in ("data", "analytics", "ai", "ml", "machine learning")):
        return "data_ai"
    if "product" in text:
        return "product"
    if any(token in text for token in ("security", "risk", "governance")):
        return "risk_governance"
    return "unknown"


@dataclass(frozen=True)
class JDFacts:
    """Normalized job-description facts for apps_lic."""

    position_name: str
    requisition_number: str
    company: str
    location: str
    role_family: str
    description: str
    source_ref: str
    jd_digest: str

    @property
    def job_title(self) -> str:
        return self.position_name

    def to_metadata(self) -> dict[str, str]:
        return {
            "position_name": self.position_name,
            "job_title": self.job_title,
            "requisition_number": self.requisition_number,
            "company": self.company,
            "location": self.location,
            "role_family": self.role_family,
            "jd_digest": self.jd_digest,
            "source_ref": self.source_ref,
        }


@dataclass(frozen=True)
class OpportunityFactDocument:
    """One opportunity fact prepared for an apps_lic namespace."""

    document_id: str
    namespace: str
    fact_family: str
    fact_text: str
    source_id: str
    source_type: str
    source_lineage: tuple[str, ...]
    freshness_date: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def source_snapshot_id(self) -> str:
        return f"{self.namespace}:{self.document_id}:{self.content_digest[:12]}"

    @property
    def content_digest(self) -> str:
        return _sha256_canonical(
            {
                "namespace": self.namespace,
                "fact_family": self.fact_family,
                "fact_text": self.fact_text,
                "metadata": dict(self.metadata),
            }
        )

    def to_vector_payload(self) -> dict[str, Any]:
        return {
            "id": self.document_id,
            "namespace": self.namespace,
            "text": self.fact_text,
            "metadata": {
                **dict(self.metadata),
                "fact_family": self.fact_family,
                "source_id": self.source_id,
                "source_type": self.source_type,
                "source_lineage": list(self.source_lineage),
                "freshness_date": self.freshness_date,
                "confidence": self.confidence,
                "content_digest": self.content_digest,
            },
        }


@dataclass(frozen=True)
class OpportunityIngestionInput:
    """Seed package for the governed opportunity ingestion path."""

    request_id: str
    trace_root: str
    idempotency_key: str
    profile_id: str = ""
    expected_opportunity_scope: str = ""
    contact: Mapping[str, Any] | None = None
    company: Mapping[str, Any] | None = None
    jd: Mapping[str, Any] | str | None = None
    company_trigger: Mapping[str, Any] | None = None
    role_ownership: Mapping[str, Any] | None = None
    relationship: Mapping[str, Any] | None = None
    referral: Mapping[str, Any] | None = None
    prior_thread: Mapping[str, Any] | None = None
    source_mode: str = "manual_urls_only"
    collected_at: str = ""


@dataclass(frozen=True)
class OpportunityIngestionReceipt:
    """Receipt emitted by governed opportunity ingestion."""

    status: str
    request_id: str
    trace_root: str
    idempotency_key: str
    write_authority: str
    write_enabled: bool
    namespace_counts: Mapping[str, int]
    source_snapshot_ids: tuple[str, ...]
    documents: tuple[OpportunityFactDocument, ...]
    skipped: tuple[Mapping[str, str], ...]
    no_inference_write_receipt: str
    reason: str = ""


@dataclass(frozen=True)
class OpportunityEvidenceReadiness:
    """Readiness status for C0 inference reads."""

    status: str
    ready: bool
    missing_namespaces: tuple[str, ...]
    stale_namespaces: tuple[str, ...]
    conflicted_namespaces: tuple[str, ...]
    blocked_namespaces: tuple[str, ...]
    ingestion_required_reason: str
    source_snapshot_ids: tuple[str, ...]
    source_count: int = 0
    source_count_by_namespace: Mapping[str, int] = field(default_factory=dict)
    vector_collection_names: tuple[str, ...] = ()

    def to_packet(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ready": self.ready,
            "missing_namespaces": list(self.missing_namespaces),
            "stale_namespaces": list(self.stale_namespaces),
            "conflicted_namespaces": list(self.conflicted_namespaces),
            "blocked_namespaces": list(self.blocked_namespaces),
            "ingestion_required_reason": self.ingestion_required_reason,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "source_count": self.source_count,
            "source_count_by_namespace": dict(self.source_count_by_namespace),
            "vector_collection_names": list(self.vector_collection_names),
        }


@dataclass(frozen=True)
class ProfileEvidenceInputRecord:
    """Per-target C0 evidence seed record for governed ingestion."""

    profile_id: str
    name: str
    title_headline_seed: str
    linkedin_public_url: str
    company: str
    expected_opportunity_scope: str
    role_ownership_seed: str = ""
    source_lineage: tuple[str, ...] = ()
    confidence: float = 0.80
    collected_at: str = ""

    @property
    def vector_collection_name(self) -> str:
        return NAMESPACE_CONTACT

    def to_packet(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "title_headline_seed": self.title_headline_seed,
            "linkedin_public_url": self.linkedin_public_url,
            "company": self.company,
            "expected_opportunity_scope": self.expected_opportunity_scope,
            "role_ownership_seed": self.role_ownership_seed,
            "source_lineage": list(self.source_lineage),
            "confidence": self.confidence,
            "collected_at": self.collected_at,
            "vector_collection_name": self.vector_collection_name,
        }


@dataclass(frozen=True)
class VectorCollectionBaseline:
    """Named fact-vector collection expected by the apps_lic C0 path."""

    baseline_id: str
    collection_name: str
    purpose: str

    def to_packet(self) -> dict[str, str]:
        return {
            "baseline_id": self.baseline_id,
            "collection_name": self.collection_name,
            "purpose": self.purpose,
        }


@dataclass(frozen=True)
class ProfileEvidenceReadinessReceipt:
    """Per-profile C0 vector readiness receipt."""

    profile_id: str
    status: str
    ready: bool
    vector_collection_name: str
    vector_collection_names: tuple[str, ...]
    source_count: int
    source_count_by_collection: Mapping[str, int]
    source_snapshot_ids: tuple[str, ...]
    missing_collections: tuple[str, ...]
    stale_collections: tuple[str, ...]
    conflicted_collections: tuple[str, ...]
    blocked_collections: tuple[str, ...]
    ingestion_required_reason: str
    ingestion_action: str = "not_required"
    ingestion_receipt_status: str = ""

    def to_packet(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "status": self.status,
            "ready": self.ready,
            "vector_collection_name": self.vector_collection_name,
            "vector_collection_names": list(self.vector_collection_names),
            "source_count": self.source_count,
            "source_count_by_collection": dict(self.source_count_by_collection),
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "missing_collections": list(self.missing_collections),
            "stale_collections": list(self.stale_collections),
            "conflicted_collections": list(self.conflicted_collections),
            "blocked_collections": list(self.blocked_collections),
            "ingestion_required_reason": self.ingestion_required_reason,
            "ingestion_action": self.ingestion_action,
            "ingestion_receipt_status": self.ingestion_receipt_status,
        }


class OpportunityFactStore(Protocol):
    """Minimal store protocol for governed ingestion."""

    def upsert_documents(self, documents: Iterable[OpportunityFactDocument]) -> int:
        """Upsert documents through the governed ingestion gate."""

    def query_namespace(self, namespace: str) -> tuple[OpportunityFactDocument, ...]:
        """Read documents from a namespace."""


class InMemoryOpportunityFactStore:
    """Test and local dry-run store for W2 opportunity facts."""

    def __init__(self) -> None:
        self._documents: MutableMapping[str, dict[str, OpportunityFactDocument]] = {}

    def upsert_documents(self, documents: Iterable[OpportunityFactDocument]) -> int:
        count = 0
        for document in documents:
            self._documents.setdefault(document.namespace, {})[document.document_id] = document
            count += 1
        return count

    def query_namespace(self, namespace: str) -> tuple[OpportunityFactDocument, ...]:
        return tuple(self._documents.get(namespace, {}).values())

    def snapshot(self) -> dict[str, tuple[OpportunityFactDocument, ...]]:
        return {
            namespace: tuple(docs.values())
            for namespace, docs in sorted(self._documents.items())
        }


def normalize_jd_facts(
    jd: Mapping[str, Any] | str,
    *,
    target_company: str = "",
    target_role: str = "",
    source_ref: str = "inline:jd",
) -> JDFacts:
    """Normalize JD material and expose apps_lic-required fields."""
    if isinstance(jd, Mapping):
        raw = dict(jd)
        description = _first_non_empty(raw.get("description"), raw.get("jd_text"), raw.get("text"))
    else:
        text = str(jd or "").strip()
        raw = {}
        if text.startswith("{"):
            try:
                loaded = json.loads(text)
            except json.JSONDecodeError:
                loaded = None
            if isinstance(loaded, dict):
                raw = loaded
                description = _first_non_empty(
                    loaded.get("description"),
                    loaded.get("jd_text"),
                    loaded.get("text"),
                    text,
                )
            else:
                description = text
        else:
            raw = _field_map_from_text(text)
            raw = {**_heading_fields_from_text(text), **raw}
            description = text

    description_fields = _field_map_from_text(
        str(raw.get("description") or raw.get("jd_text") or raw.get("text") or description)
    )
    heading_fields = _heading_fields_from_text(description)

    title = _first_non_empty(
        raw.get("position_name"),
        raw.get("job_title"),
        raw.get("title"),
        raw.get("role"),
        raw.get("position"),
        heading_fields.get("position_name"),
        target_role,
    )
    company = _first_non_empty(
        raw.get("company"),
        raw.get("organization"),
        heading_fields.get("company"),
        target_company,
    )
    location = _first_non_empty(
        raw.get("location"),
        raw.get("job_location"),
        description_fields.get("location"),
        description_fields.get("locations"),
    )
    req_match = _REQ_RE.search(description)
    paren_req_match = _PAREN_REQ_RE.search(description)
    req_from_text = req_match.group(1).strip() if req_match else ""
    req_from_heading = paren_req_match.group(1).strip() if paren_req_match else ""
    requisition = _first_non_empty(
        raw.get("requisition_number"),
        raw.get("requisition_id"),
        raw.get("req_id"),
        raw.get("job_id"),
        raw.get("job_number"),
        req_from_text,
        heading_fields.get("requisition_number"),
        req_from_heading,
    )
    role_family = _first_non_empty(raw.get("role_family"), _derive_role_family(title, description))
    normalized_seed = {
        "position_name": title,
        "requisition_number": requisition,
        "company": company,
        "location": location,
        "role_family": role_family,
        "description": description,
        "source_ref": source_ref,
    }
    return JDFacts(
        position_name=title,
        requisition_number=requisition,
        company=company,
        location=location,
        role_family=role_family,
        description=description,
        source_ref=source_ref,
        jd_digest=_sha256_canonical(normalized_seed),
    )


def _document_id(seed: Mapping[str, Any]) -> str:
    return _sha256_canonical(seed)[:32]


def _build_document(
    *,
    fact_family: str,
    fact_text: str,
    source_id: str,
    source_type: str,
    source_lineage: Iterable[str],
    freshness_date: str,
    confidence: float = 1.0,
    metadata: Mapping[str, Any] | None = None,
) -> OpportunityFactDocument:
    namespace = FACT_FAMILY_TO_NAMESPACE[fact_family]
    meta = dict(metadata or {})
    seed = {
        "namespace": namespace,
        "fact_family": fact_family,
        "fact_text": fact_text,
        "source_id": source_id,
        "metadata": meta,
    }
    return OpportunityFactDocument(
        document_id=_document_id(seed),
        namespace=namespace,
        fact_family=fact_family,
        fact_text=fact_text,
        source_id=source_id,
        source_type=source_type,
        source_lineage=tuple(str(item) for item in source_lineage if str(item).strip()),
        freshness_date=freshness_date,
        confidence=confidence,
        metadata=meta,
    )


def build_opportunity_fact_documents(
    payload: OpportunityIngestionInput,
) -> tuple[OpportunityFactDocument, ...]:
    """Build opportunity fact documents without storing them."""
    collected_at = payload.collected_at or _now_iso()
    profile_id = _clean(payload.profile_id)
    expected_scope = _clean(payload.expected_opportunity_scope)
    documents: list[OpportunityFactDocument] = []

    if payload.contact:
        contact = dict(payload.contact)
        contact_profile_id = _first_non_empty(contact.get("profile_id"), profile_id)
        contact_scope = _first_non_empty(contact.get("expected_opportunity_scope"), expected_scope)
        name = _clean(contact.get("name") or contact.get("verified_name"))
        title = _clean(contact.get("title") or contact.get("headline"))
        company = _clean(contact.get("company") or contact.get("company_name"))
        if name or title or company:
            contact_lineage = tuple(
                str(item)
                for item in contact.get("source_lineage", ())
                if str(item).strip()
            )
            documents.append(
                _build_document(
                    fact_family="contact",
                    fact_text=f"{name} | {title} | {company}".strip(" |"),
                    source_id=_first_non_empty(contact.get("source_id"), contact.get("linkedin_url"), "u0:contact"),
                    source_type="user_seed_or_public_profile",
                    source_lineage=(
                        contact.get("linkedin_url") or "",
                        contact.get("public_profile_url") or "",
                        *contact_lineage,
                    ),
                    freshness_date=_first_non_empty(contact.get("freshness_date"), collected_at),
                    confidence=float(contact.get("confidence") or 1.0),
                    metadata={
                        "profile_id": contact_profile_id,
                        "name": name,
                        "title": title,
                        "headline": _clean(contact.get("headline")),
                        "company": company,
                        "expected_opportunity_scope": contact_scope,
                        "conflict_key": "contact_identity",
                        "canonical_value": f"{contact_profile_id}|{name}|{title}|{company}",
                    },
                )
            )

    if payload.company:
        company_seed = dict(payload.company)
        company_name = _clean(company_seed.get("company") or company_seed.get("name"))
        context = _clean(company_seed.get("context") or company_seed.get("summary"))
        if company_name or context:
            documents.append(
                _build_document(
                    fact_family="company",
                    fact_text=f"{company_name}: {context}".strip(": "),
                    source_id=_first_non_empty(company_seed.get("source_id"), "u0:company"),
                    source_type="user_seed_or_company_context",
                    source_lineage=(company_seed.get("url") or "",),
                    freshness_date=_first_non_empty(company_seed.get("freshness_date"), collected_at),
                    metadata={
                        "company": company_name,
                        "expected_opportunity_scope": expected_scope,
                        "conflict_key": "company_identity",
                        "canonical_value": company_name,
                    },
                )
            )

    if payload.jd:
        company_seed = dict(payload.company or {})
        company_name = _clean(company_seed.get("company") or company_seed.get("name"))
        jd_facts = normalize_jd_facts(payload.jd, target_company=company_name)
        documents.append(
            _build_document(
                fact_family="jd",
                fact_text=jd_facts.description,
                source_id=jd_facts.source_ref,
                source_type="jd_seed",
                source_lineage=(jd_facts.source_ref,),
                freshness_date=collected_at,
                metadata={
                    **jd_facts.to_metadata(),
                    "expected_opportunity_scope": expected_scope,
                    "conflict_key": "jd_identity",
                    "canonical_value": f"{jd_facts.position_name}|{jd_facts.requisition_number}",
                },
            )
        )

    if payload.company_trigger:
        trigger = dict(payload.company_trigger)
        text = _clean(trigger.get("trigger_text") or trigger.get("text") or trigger.get("summary"))
        if text:
            documents.append(
                _build_document(
                    fact_family="company_trigger",
                    fact_text=text,
                    source_id=_first_non_empty(trigger.get("source_id"), trigger.get("url"), "u0:trigger"),
                    source_type="company_trigger",
                    source_lineage=(trigger.get("url") or "",),
                    freshness_date=_first_non_empty(trigger.get("freshness_date"), collected_at),
                    metadata={"trigger_text": text, "event_date": _clean(trigger.get("event_date"))},
                )
            )

    if payload.role_ownership:
        ownership = dict(payload.role_ownership)
        ownership_profile_id = _first_non_empty(ownership.get("profile_id"), profile_id)
        signal = _clean(
            ownership.get("ownership_signal")
            or ownership.get("text")
            or ownership.get("role_ownership_signal")
        )
        if signal:
            documents.append(
                _build_document(
                    fact_family="role_ownership",
                    fact_text=signal,
                    source_id=_first_non_empty(ownership.get("source_id"), "u0:role_ownership"),
                    source_type="role_ownership_signal",
                    source_lineage=(ownership.get("url") or "",),
                    freshness_date=_first_non_empty(ownership.get("freshness_date"), collected_at),
                    confidence=float(ownership.get("confidence") or 1.0),
                    metadata={
                        "profile_id": ownership_profile_id,
                        "ownership_signal": signal,
                        "expected_opportunity_scope": expected_scope,
                        "conflict_key": "role_ownership",
                        "canonical_value": f"{ownership_profile_id}|{signal}",
                    },
                )
            )

    if payload.relationship:
        relationship = dict(payload.relationship)
        context = _clean(relationship.get("relationship_context") or relationship.get("context"))
        if context:
            documents.append(
                _build_document(
                    fact_family="relationship",
                    fact_text=context,
                    source_id=_first_non_empty(relationship.get("source_id"), "u0:relationship"),
                    source_type="relationship_context",
                    source_lineage=(relationship.get("source_label") or "",),
                    freshness_date=_first_non_empty(relationship.get("freshness_date"), collected_at),
                    metadata={
                        "relationship_context": context,
                        "permission_scope": _clean(relationship.get("permission_scope")),
                    },
                )
            )

    if payload.referral:
        referral = dict(payload.referral)
        referrer = _clean(referral.get("referrer_name") or referral.get("name"))
        permission = _clean(referral.get("permission_scope"))
        if referrer or permission:
            documents.append(
                _build_document(
                    fact_family="referral",
                    fact_text=f"{referrer}: {permission}".strip(": "),
                    source_id=_first_non_empty(referral.get("source_id"), "u0:referral"),
                    source_type="referral_context",
                    source_lineage=(referral.get("source_label") or "",),
                    freshness_date=_first_non_empty(referral.get("freshness_date"), collected_at),
                    metadata={"referrer_name": referrer, "permission_scope": permission},
                )
            )

    if payload.prior_thread:
        thread = dict(payload.prior_thread)
        summary = _clean(thread.get("thread_summary") or thread.get("summary"))
        last_touch = _clean(thread.get("last_touch_date") or thread.get("freshness_date"))
        if summary or last_touch:
            documents.append(
                _build_document(
                    fact_family="prior_thread",
                    fact_text=f"{summary} Last touch: {last_touch}".strip(),
                    source_id=_first_non_empty(thread.get("source_id"), "u0:prior_thread"),
                    source_type="prior_thread_context",
                    source_lineage=(thread.get("thread_id") or "",),
                    freshness_date=_first_non_empty(thread.get("freshness_date"), last_touch, collected_at),
                    metadata={"thread_summary": summary, "last_touch_date": last_touch},
                )
            )

    return tuple(documents)


def run_governed_opportunity_ingestion(
    payload: OpportunityIngestionInput,
    *,
    store: OpportunityFactStore | None,
    write_authority: str,
    write_enabled: bool,
) -> OpportunityIngestionReceipt:
    """Run W2 governed ingestion with an explicit write gate."""
    documents = build_opportunity_fact_documents(payload)
    skipped: list[Mapping[str, str]] = []
    if write_enabled and write_authority != WRITE_AUTHORITY_GOVERNED_INGESTION:
        return OpportunityIngestionReceipt(
            status=STATUS_BLOCKED,
            request_id=payload.request_id,
            trace_root=payload.trace_root,
            idempotency_key=payload.idempotency_key,
            write_authority=write_authority,
            write_enabled=write_enabled,
            namespace_counts={},
            source_snapshot_ids=(),
            documents=documents,
            skipped=({"reason": "missing_governed_write_authority"},),
            no_inference_write_receipt="blocked:no_governed_write_authority",
            reason="Write enabled without governed opportunity ingestion authority.",
        )

    upserted = 0
    if write_enabled:
        if store is None:
            skipped.append({"reason": "write_enabled_but_store_missing"})
        else:
            upserted = store.upsert_documents(documents)

    namespace_counts: dict[str, int] = {}
    for document in documents:
        namespace_counts[document.namespace] = namespace_counts.get(document.namespace, 0) + 1

    status = STATUS_READY if documents and (not write_enabled or upserted == len(documents)) else STATUS_MISSING
    if write_enabled and store is None:
        status = STATUS_BLOCKED

    return OpportunityIngestionReceipt(
        status=status,
        request_id=payload.request_id,
        trace_root=payload.trace_root,
        idempotency_key=payload.idempotency_key,
        write_authority=write_authority,
        write_enabled=write_enabled,
        namespace_counts=namespace_counts,
        source_snapshot_ids=tuple(document.source_snapshot_id for document in documents),
        documents=documents,
        skipped=tuple(skipped),
        no_inference_write_receipt=(
            "pass:governed_ingestion_write_gate"
            if write_enabled
            else "pass:prepared_without_write"
        ),
        reason="",
    )


def _has_stale_document(
    documents: Iterable[OpportunityFactDocument],
    *,
    max_age_days: int,
    now: datetime,
) -> bool:
    for document in documents:
        freshness = _parse_iso_date(document.freshness_date)
        if freshness is None:
            return True
        age_days = (now - freshness).days
        if age_days > max_age_days:
            return True
    return False


def _namespace_has_conflict(documents: Iterable[OpportunityFactDocument]) -> bool:
    values_by_key: dict[str, set[str]] = {}
    for document in documents:
        meta = dict(document.metadata)
        key = _clean(meta.get("conflict_key"))
        if not key:
            continue
        value = _clean(meta.get("canonical_value") or document.fact_text).lower()
        values_by_key.setdefault(key, set()).add(value)
    return any(len(values) > 1 for values in values_by_key.values())


def check_opportunity_evidence_readiness(
    *,
    store: OpportunityFactStore,
    required_namespaces: Iterable[str],
    now: datetime | None = None,
    freshness_days: Mapping[str, int] | None = None,
) -> OpportunityEvidenceReadiness:
    """Read opportunity store readiness for C0 inference without writing."""
    current_time = now or datetime.now(timezone.utc)
    freshness = dict(DEFAULT_FRESHNESS_DAYS)
    freshness.update(dict(freshness_days or {}))

    missing: list[str] = []
    stale: list[str] = []
    conflicted: list[str] = []
    blocked: list[str] = []
    snapshot_ids: list[str] = []
    source_counts: dict[str, int] = {}

    for namespace in tuple(required_namespaces):
        documents = store.query_namespace(namespace)
        source_counts[namespace] = len(documents)
        if not documents:
            missing.append(namespace)
            continue
        snapshot_ids.extend(document.source_snapshot_id for document in documents)
        if any(dict(document.metadata).get("blocked") is True for document in documents):
            blocked.append(namespace)
        if _has_stale_document(
            documents,
            max_age_days=freshness.get(namespace, 90),
            now=current_time,
        ):
            stale.append(namespace)
        if _namespace_has_conflict(documents):
            conflicted.append(namespace)

    if blocked:
        status = STATUS_BLOCKED
    elif conflicted:
        status = STATUS_CONFLICTED
    elif stale:
        status = STATUS_STALE
    elif missing:
        status = STATUS_MISSING
    else:
        status = STATUS_READY

    return OpportunityEvidenceReadiness(
        status=status,
        ready=status == STATUS_READY,
        missing_namespaces=tuple(missing),
        stale_namespaces=tuple(stale),
        conflicted_namespaces=tuple(conflicted),
        blocked_namespaces=tuple(blocked),
        ingestion_required_reason=(
            ""
            if status == STATUS_READY
            else f"{status}: "
            + ", ".join(missing + stale + conflicted + blocked)
        ),
        source_snapshot_ids=tuple(snapshot_ids),
        source_count=sum(source_counts.values()),
        source_count_by_namespace=source_counts,
        vector_collection_names=tuple(required_namespaces),
    )


def baseline_vector_collections() -> tuple[VectorCollectionBaseline, ...]:
    """Return W2 baseline fact-vector collections expected by apps_lic."""
    return tuple(
        VectorCollectionBaseline(
            baseline_id=baseline_id,
            collection_name=collection_name,
            purpose=purpose,
        )
        for baseline_id, collection_name, purpose in BASELINE_VECTOR_COLLECTIONS
    )


def build_profile_opportunity_ingestion_input(
    record: ProfileEvidenceInputRecord,
    *,
    request_id: str,
    trace_root: str,
    idempotency_key: str,
    company: Mapping[str, Any] | None = None,
    jd: Mapping[str, Any] | str | None = None,
    role_ownership: Mapping[str, Any] | None = None,
    collected_at: str = "",
) -> OpportunityIngestionInput:
    """Build a governed ingestion payload from one profile evidence record."""
    contact = {
        "profile_id": record.profile_id,
        "name": record.name,
        "title": record.title_headline_seed,
        "headline": record.title_headline_seed,
        "company": record.company,
        "linkedin_url": record.linkedin_public_url,
        "public_profile_url": record.linkedin_public_url,
        "expected_opportunity_scope": record.expected_opportunity_scope,
        "confidence": record.confidence,
    }
    if record.source_lineage:
        contact["source_lineage"] = list(record.source_lineage)

    role_seed = dict(role_ownership or {})
    if record.role_ownership_seed and not role_seed:
        role_seed = {
            "profile_id": record.profile_id,
            "ownership_signal": record.role_ownership_seed,
            "url": record.linkedin_public_url,
            "confidence": record.confidence,
        }
    elif role_seed:
        role_seed.setdefault("profile_id", record.profile_id)
        role_seed.setdefault("url", record.linkedin_public_url)
        role_seed.setdefault("confidence", record.confidence)

    return OpportunityIngestionInput(
        request_id=request_id,
        trace_root=trace_root,
        idempotency_key=idempotency_key,
        profile_id=record.profile_id,
        expected_opportunity_scope=record.expected_opportunity_scope,
        contact=contact,
        company=company
        or {
            "company": record.company,
            "context": f"{record.company} opportunity context for {record.expected_opportunity_scope}.",
        },
        jd=jd,
        role_ownership=role_seed or None,
        collected_at=collected_at or record.collected_at,
    )


def _profile_matches_document(
    document: OpportunityFactDocument,
    record: ProfileEvidenceInputRecord,
) -> bool:
    metadata = dict(document.metadata)
    document_profile_id = _clean(metadata.get("profile_id"))
    if document_profile_id:
        return document_profile_id == record.profile_id
    if document.namespace == NAMESPACE_CONTACT:
        return (
            _clean(metadata.get("name")).lower() == record.name.lower()
            and _clean(metadata.get("company")).lower() == record.company.lower()
        )
    return False


def _profile_documents_for_namespace(
    *,
    store: OpportunityFactStore,
    record: ProfileEvidenceInputRecord,
    namespace: str,
) -> tuple[OpportunityFactDocument, ...]:
    documents = store.query_namespace(namespace)
    if namespace in {NAMESPACE_CONTACT, NAMESPACE_ROLE_OWNERSHIP}:
        return tuple(
            document for document in documents if _profile_matches_document(document, record)
        )
    return documents


def check_profile_evidence_readiness(
    *,
    store: OpportunityFactStore,
    profile_record: ProfileEvidenceInputRecord,
    required_namespaces: Iterable[str] = C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS,
    now: datetime | None = None,
    freshness_days: Mapping[str, int] | None = None,
    ingestion_action: str = "not_required",
    ingestion_receipt_status: str = "",
) -> ProfileEvidenceReadinessReceipt:
    """Read per-profile C0 readiness without writing to the fact-vector store."""
    current_time = now or datetime.now(timezone.utc)
    freshness = dict(DEFAULT_FRESHNESS_DAYS)
    freshness.update(dict(freshness_days or {}))
    required = tuple(required_namespaces)

    missing: list[str] = []
    stale: list[str] = []
    conflicted: list[str] = []
    blocked: list[str] = []
    snapshot_ids: list[str] = []
    source_counts: dict[str, int] = {}

    for namespace in required:
        documents = _profile_documents_for_namespace(
            store=store,
            record=profile_record,
            namespace=namespace,
        )
        source_counts[namespace] = len(documents)
        if not documents:
            missing.append(namespace)
            continue
        snapshot_ids.extend(document.source_snapshot_id for document in documents)
        if any(dict(document.metadata).get("blocked") is True for document in documents):
            blocked.append(namespace)
        if _has_stale_document(
            documents,
            max_age_days=freshness.get(namespace, 90),
            now=current_time,
        ):
            stale.append(namespace)
        if _namespace_has_conflict(documents):
            conflicted.append(namespace)

    if blocked:
        status = STATUS_BLOCKED
    elif conflicted:
        status = STATUS_CONFLICTED
    elif stale:
        status = STATUS_STALE
    elif missing:
        status = STATUS_MISSING
    else:
        status = STATUS_READY

    return ProfileEvidenceReadinessReceipt(
        profile_id=profile_record.profile_id,
        status=status,
        ready=status == STATUS_READY,
        vector_collection_name=profile_record.vector_collection_name,
        vector_collection_names=required,
        source_count=sum(source_counts.values()),
        source_count_by_collection=source_counts,
        source_snapshot_ids=tuple(snapshot_ids),
        missing_collections=tuple(missing),
        stale_collections=tuple(stale),
        conflicted_collections=tuple(conflicted),
        blocked_collections=tuple(blocked),
        ingestion_required_reason=(
            ""
            if status == STATUS_READY
            else f"{status}: "
            + ", ".join(missing + stale + conflicted + blocked)
        ),
        ingestion_action=ingestion_action,
        ingestion_receipt_status=ingestion_receipt_status,
    )


def ensure_profile_c0_readiness(
    *,
    store: OpportunityFactStore,
    profile_record: ProfileEvidenceInputRecord,
    company: Mapping[str, Any] | None = None,
    jd: Mapping[str, Any] | str | None = None,
    role_ownership: Mapping[str, Any] | None = None,
    required_namespaces: Iterable[str] = C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS,
    now: datetime | None = None,
    write_authority: str = WRITE_AUTHORITY_GOVERNED_INGESTION,
    request_id: str = "",
    trace_root: str = "",
    idempotency_key: str = "",
) -> ProfileEvidenceReadinessReceipt:
    """Run on-demand governed ingestion when profile evidence is missing/stale."""
    before = check_profile_evidence_readiness(
        store=store,
        profile_record=profile_record,
        required_namespaces=required_namespaces,
        now=now,
    )
    if before.status not in {STATUS_MISSING, STATUS_STALE}:
        return before

    payload = build_profile_opportunity_ingestion_input(
        profile_record,
        request_id=request_id or f"req-w2-{profile_record.profile_id}",
        trace_root=trace_root or f"trace-w2-{profile_record.profile_id}",
        idempotency_key=idempotency_key or f"idem-w2-{profile_record.profile_id}",
        company=company,
        jd=jd,
        role_ownership=role_ownership,
        collected_at=profile_record.collected_at,
    )
    ingestion_receipt = run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=write_authority,
        write_enabled=True,
    )
    if ingestion_receipt.status == STATUS_BLOCKED:
        return ProfileEvidenceReadinessReceipt(
            profile_id=profile_record.profile_id,
            status=STATUS_BLOCKED,
            ready=False,
            vector_collection_name=profile_record.vector_collection_name,
            vector_collection_names=tuple(required_namespaces),
            source_count=0,
            source_count_by_collection={namespace: 0 for namespace in required_namespaces},
            source_snapshot_ids=(),
            missing_collections=before.missing_collections,
            stale_collections=before.stale_collections,
            conflicted_collections=before.conflicted_collections,
            blocked_collections=tuple(dict.fromkeys((*before.blocked_collections, "write_gate"))),
            ingestion_required_reason="C0_EVIDENCE_BLOCKED: governed ingestion write authority missing",
            ingestion_action="governed_ingestion_blocked",
            ingestion_receipt_status=ingestion_receipt.status,
        )

    return check_profile_evidence_readiness(
        store=store,
        profile_record=profile_record,
        required_namespaces=required_namespaces,
        now=now,
        ingestion_action="governed_ingestion_run",
        ingestion_receipt_status=ingestion_receipt.status,
    )


__all__ = [
    "DEFAULT_FRESHNESS_DAYS",
    "FACT_FAMILY_TO_NAMESPACE",
    "BASELINE_VECTOR_COLLECTIONS",
    "C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS",
    "NAMESPACE_COMPANY",
    "NAMESPACE_COMPANY_TRIGGER",
    "NAMESPACE_CONTACT",
    "NAMESPACE_JD",
    "NAMESPACE_PRIOR_THREAD",
    "NAMESPACE_REFERRAL",
    "NAMESPACE_RELATIONSHIP",
    "NAMESPACE_ROLE_OWNERSHIP",
    "NAMESPACE_STANDING_SENDER",
    "STATUS_BLOCKED",
    "STATUS_CONFLICTED",
    "STATUS_MISSING",
    "STATUS_READY",
    "STATUS_STALE",
    "WRITE_AUTHORITY_GOVERNED_INGESTION",
    "InMemoryOpportunityFactStore",
    "JDFacts",
    "OpportunityEvidenceReadiness",
    "OpportunityFactDocument",
    "OpportunityIngestionInput",
    "OpportunityIngestionReceipt",
    "ProfileEvidenceInputRecord",
    "ProfileEvidenceReadinessReceipt",
    "VectorCollectionBaseline",
    "baseline_vector_collections",
    "build_profile_opportunity_ingestion_input",
    "build_opportunity_fact_documents",
    "check_opportunity_evidence_readiness",
    "check_profile_evidence_readiness",
    "ensure_profile_c0_readiness",
    "normalize_jd_facts",
    "run_governed_opportunity_ingestion",
]
