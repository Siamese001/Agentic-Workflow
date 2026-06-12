"""W2 / G11+G14: base-resume + JD are identity/targeting context only, never proof authority.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

Base-resume / JD prose is excluded from PROOF by the source-prefix scheme (resume_payload /
jd_payload are not in PROOF_RETRIEVAL_SOURCE_PREFIXES). This locks the declared-but-unenforced
``base_resume_static_anchors_only`` constraint: inline items are explicitly tagged
NON_PROOF_CONTEXT, and assert_base_resume_identity_only fails loud if a future change mistags them
as proof. Pure product-mode unit test.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem
from apps_rg.runtime.c0.c0_section_authority import (
    AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
    AUTHORITY_CLASS_NON_PROOF_CONTEXT,
    NON_PROOF_CONTEXT_PREFIXES,
    PROOF_RETRIEVAL_SOURCE_PREFIXES,
    assert_base_resume_identity_only,
    is_non_proof_context_source,
    proof_support_target,
)


def test_non_proof_context_source_detection() -> None:
    assert is_non_proof_context_source("resume_payload") is True
    assert is_non_proof_context_source("jd_payload") is True
    assert is_non_proof_context_source("briefing_payload") is True
    assert is_non_proof_context_source("chromadb:candidate_profile:doc1") is False
    assert is_non_proof_context_source("fact:abc") is False
    assert is_non_proof_context_source("") is False


def test_base_resume_and_jd_excluded_from_proof_prefixes() -> None:
    for prefix in ("resume_payload", "jd_payload", "briefing_payload"):
        assert prefix not in PROOF_RETRIEVAL_SOURCE_PREFIXES
        assert prefix in NON_PROOF_CONTEXT_PREFIXES
    # proof_support_target is built strictly from the proof prefixes (fact/ledger/proof_pool/srfs).
    assert "fact:" in PROOF_RETRIEVAL_SOURCE_PREFIXES
    assert proof_support_target() is not None


def test_evidence_item_accepts_non_proof_authority_tag() -> None:
    """The inline-ingestion tagging compiles: EvidenceItem carries authority_class + owner."""
    item = EvidenceItem(
        source="resume_payload",
        content="Amit Ayer — VP Engineering",
        authority_class=AUTHORITY_CLASS_NON_PROOF_CONTEXT,
        source_owner_or_authority="base_resume_identity_non_authoritative",
    )
    assert item.authority_class == AUTHORITY_CLASS_NON_PROOF_CONTEXT


def test_assert_passes_for_non_proof_tagged_context() -> None:
    items = [
        EvidenceItem(
            source="resume_payload",
            content="resume prose",
            authority_class=AUTHORITY_CLASS_NON_PROOF_CONTEXT,
        ),
        EvidenceItem(
            source="jd_payload",
            content="jd prose",
            authority_class=AUTHORITY_CLASS_NON_PROOF_CONTEXT,
        ),
        EvidenceItem(source="fact:competency:1", content="proof"),
    ]
    # No raise.
    assert assert_base_resume_identity_only(items) is None


def test_assert_raises_when_base_resume_mistagged_as_proof() -> None:
    items = [
        EvidenceItem(
            source="resume_payload",
            content="resume prose smuggled as proof",
            authority_class=AUTHORITY_CLASS_LEDGER_GRAPH_PROOF,
        ),
    ]
    with pytest.raises(ValueError) as excinfo:
        assert_base_resume_identity_only(items)
    assert "identity only" in str(excinfo.value)
    assert "resume_payload" in str(excinfo.value)
