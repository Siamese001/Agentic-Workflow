"""Shared governed C0 readiness fixtures for apps_lic canonical dispatch tests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_CONTACT,
    NAMESPACE_JD,
    NAMESPACE_ROLE_OWNERSHIP,
)

_FRESH_DATE = "2099-06-08T00:00:00+00:00"


def fact_packet(
    *,
    namespace: str,
    document_id: str,
    fact_text: str,
    metadata: Mapping[str, Any] | None = None,
    freshness_date: str = _FRESH_DATE,
    confidence: float = 0.90,
) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "namespace": namespace,
        "fact_family": namespace,
        "fact_text": fact_text,
        "source_id": f"fixture:{document_id}",
        "source_type": "test_governed_fact",
        "source_lineage": [f"fixture:{document_id}"],
        "freshness_date": freshness_date,
        "confidence": confidence,
        "metadata": dict(metadata or {}),
    }


def ready_governed_opportunity_facts(
    *,
    contact_text: str = "Jane Smith | Senior Technical Recruiter | AIG",
    role_ownership_text: str = "Owns recruiting for AI platform leadership roles.",
    freshness_date: str = _FRESH_DATE,
) -> list[dict[str, Any]]:
    return [
        fact_packet(
            namespace=NAMESPACE_CONTACT,
            document_id="contact-jane",
            fact_text=contact_text,
            freshness_date=freshness_date,
            metadata={
                "title": contact_text,
                "company": "AIG",
                "conflict_key": "contact_identity",
                "canonical_value": contact_text,
            },
        ),
        fact_packet(
            namespace=NAMESPACE_COMPANY,
            document_id="company-aig",
            fact_text="AIG enterprise AI operating context.",
            freshness_date=freshness_date,
            metadata={"company": "AIG"},
        ),
        fact_packet(
            namespace=NAMESPACE_JD,
            document_id="jd-aig-ai",
            fact_text="VP, Global Head of Agentic AI Solutions role, JR2601998.",
            freshness_date=freshness_date,
            metadata={
                "position_name": "VP, Global Head of Agentic AI Solutions",
                "requisition_number": "JR2601998",
                "company": "AIG",
            },
        ),
        fact_packet(
            namespace=NAMESPACE_ROLE_OWNERSHIP,
            document_id="role-owner-jane",
            fact_text=role_ownership_text,
            freshness_date=freshness_date,
            metadata={
                "ownership_signal": role_ownership_text,
                "conflict_key": "role_ownership",
                "canonical_value": role_ownership_text,
            },
        ),
    ]


def company_governed_opportunity_facts(
    *,
    company: str,
    contact_name: str,
    contact_title: str,
    jd_title: str = "Director, AI Platforms",
    requisition_number: str = "JR-12345",
    company_context: str = "",
    trigger_text: str = "",
    role_ownership_text: str = "Owns recruiting for AI platform leadership roles.",
    freshness_date: str = _FRESH_DATE,
) -> list[dict[str, Any]]:
    company_context = company_context or f"{company} enterprise AI platform context."
    facts = [
        fact_packet(
            namespace=NAMESPACE_CONTACT,
            document_id=f"contact-{company.lower()}",
            fact_text=f"{contact_name} | {contact_title} | {company}",
            freshness_date=freshness_date,
            metadata={
                "name": contact_name,
                "title": contact_title,
                "company": company,
                "conflict_key": "contact_identity",
                "canonical_value": f"{contact_name}|{contact_title}|{company}",
            },
        ),
        fact_packet(
            namespace=NAMESPACE_COMPANY,
            document_id=f"company-{company.lower()}",
            fact_text=company_context,
            freshness_date=freshness_date,
            metadata={"company": company},
        ),
        fact_packet(
            namespace=NAMESPACE_JD,
            document_id=f"jd-{company.lower()}",
            fact_text=f"{jd_title} role, {requisition_number}.",
            freshness_date=freshness_date,
            metadata={
                "position_name": jd_title,
                "requisition_number": requisition_number,
                "company": company,
            },
        ),
        fact_packet(
            namespace=NAMESPACE_ROLE_OWNERSHIP,
            document_id=f"role-owner-{company.lower()}",
            fact_text=role_ownership_text,
            freshness_date=freshness_date,
            metadata={
                "ownership_signal": role_ownership_text,
                "conflict_key": "role_ownership",
                "canonical_value": role_ownership_text,
            },
        ),
    ]
    if trigger_text:
        facts.append(
            fact_packet(
                namespace=NAMESPACE_COMPANY_TRIGGER,
                document_id=f"trigger-{company.lower()}",
                fact_text=trigger_text,
                freshness_date=freshness_date,
                metadata={
                    "trigger_text": trigger_text,
                    "company": company,
                },
            )
        )
    return facts


def minimal_recruiter_readiness_facts() -> list[dict[str, Any]]:
    return [
        fact_packet(
            namespace=NAMESPACE_CONTACT,
            document_id="contact-generic-recruiter",
            fact_text="Recruiter | Technical Recruiter",
            metadata={
                "title": "Technical Recruiter",
                "conflict_key": "contact_identity",
                "canonical_value": "Recruiter|Technical Recruiter",
            },
        )
    ]


def low_confidence_recipient_facts() -> list[dict[str, Any]]:
    return ready_governed_opportunity_facts(
        contact_text="Jane Smith | AIG public profile snippet",
        role_ownership_text="Public profile observed without current target-owner signal.",
    )


def conflicted_governed_opportunity_facts() -> list[dict[str, Any]]:
    facts = ready_governed_opportunity_facts()
    facts.append(
        fact_packet(
            namespace=NAMESPACE_CONTACT,
            document_id="contact-jane-conflict",
            fact_text="Jane Smith | Chief Technology Officer | AIG",
            metadata={
                "title": "Chief Technology Officer",
                "company": "AIG",
                "conflict_key": "contact_identity",
                "canonical_value": "Jane Smith|Chief Technology Officer|AIG",
            },
        )
    )
    return facts
