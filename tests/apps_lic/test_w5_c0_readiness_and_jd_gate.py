"""W5 — C0 recipient-evidence readiness states + JD gate.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W5.1).

apps_lic C0 is governed-ingestion / payload-only BY DESIGN (no ChromaDB / dense
retrieval surface — see apps_lic/runtime/bindings/c0_binding.py). W5's acceptance
is the readiness-state model + the JD gate, both verified here; live
chroma_delegate wiring is design-excluded, not a gap.
"""

from __future__ import annotations

from apps_lic.engines.governed_opportunity_ingestion import (
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityIngestionInput,
    run_governed_opportunity_ingestion,
)
from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_ROLE_SPECIFIC,
    STATUS_REQUIREMENTS_PASS,
    evaluate_message_requirements_from_store,
)
from apps_lic.engines.recipient_classification import derive_recipient_class_from_store
from apps_lic.runtime.bindings import c0_binding


def _recruiter_store(*, with_jd: bool) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id="req-w5",
        trace_root="trace-w5",
        idempotency_key=f"idem-w5-{with_jd}",
        contact={
            "name": "Jane Target",
            "title": "Senior Technical Recruiter",
            "headline": "Senior Technical Recruiter",
            "company": "AIG",
            "linkedin_url": "https://www.linkedin.com/in/jane-target",
        },
        company={"company": "AIG", "context": "Regulated insurer expanding agentic AI."},
        jd=(
            {
                "title": "Director, AI Platforms",
                "requisition_number": "JR-12345",
                "company": "AIG",
                "description": "Build production agentic AI platforms.",
            }
            if with_jd
            else None
        ),
        company_trigger=None,
        role_ownership=None,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def test_c0_exposes_five_distinct_readiness_states() -> None:
    states = {
        c0_binding.C0_READY,
        c0_binding.C0_OPPORTUNITY_INGESTION_REQUIRED,  # missing
        c0_binding.C0_EVIDENCE_STALE,
        c0_binding.C0_EVIDENCE_CONFLICTED,
        c0_binding.C0_EVIDENCE_BLOCKED,
    }
    assert len(states) == 5  # ready / missing / stale / conflicted / blocked


def test_jd_gate_passes_for_recruiter_role_specific_with_jd() -> None:
    store = _recruiter_store(with_jd=True)
    derivation = derive_recipient_class_from_store(store)
    gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        intent_text="Director AI Platforms role.",
    )
    assert derivation.derived_recipient_class == "RECRUITER"
    assert gate.status == STATUS_REQUIREMENTS_PASS
    assert not gate.missing_fields


def test_jd_gate_blocks_recruiter_role_specific_without_jd() -> None:
    store = _recruiter_store(with_jd=False)
    derivation = derive_recipient_class_from_store(store)
    gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        intent_text="Director AI Platforms role.",
    )
    # JD facts (position_name + requisition_number) gate recruiter/Senior-TA
    # role-specific messages: absent JD blocks with explicit missing fields.
    assert gate.status != STATUS_REQUIREMENTS_PASS
    assert gate.missing_fields
