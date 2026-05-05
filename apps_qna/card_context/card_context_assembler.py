"""Card Context Assembler — shapes evidence into domain card context.

W3.4: Assembles domain-specific card context from evidence contracts.
This is NOT canonical Prompt Assembly — apps_qna does domain card
context assembly only, not model-level prompt construction.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W3.4
"""

from __future__ import annotations

from typing import Any


def assemble_card_context(
    *,
    evidence_contract: dict[str, Any],
    interview_slug: str,
    route_id: str,
) -> dict[str, Any]:
    """Assemble domain card context from evidence contract.

    Args:
        evidence_contract: The evidence contract (C0 or briefing).
        interview_slug: The interview slug.
        route_id: The selected route id.

    Returns:
        A context dict ready for template rendering.
    """
    return {
        "interview_slug": interview_slug,
        "route_id": route_id,
        "evidence_source": evidence_contract.get("producer", "unknown"),
        "grounded": evidence_contract.get("grounded", False),
        "evidence_sufficiency": evidence_contract.get("evidence_sufficiency", "empty"),
        "retrieval_sources": evidence_contract.get("retrieval_sources", []),
        "company_name": evidence_contract.get("company_name", ""),
        "role_title": evidence_contract.get("role_title", ""),
    }


__all__ = ["assemble_card_context"]
