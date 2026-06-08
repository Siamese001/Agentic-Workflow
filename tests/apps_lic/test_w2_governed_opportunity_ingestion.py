from datetime import datetime, timezone
from pathlib import Path

import yaml

from apps_lic.engines.governed_opportunity_ingestion import (
    BASELINE_VECTOR_COLLECTIONS,
    C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS,
    NAMESPACE_COMPANY,
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_CONTACT,
    NAMESPACE_JD,
    NAMESPACE_PRIOR_THREAD,
    NAMESPACE_REFERRAL,
    NAMESPACE_RELATIONSHIP,
    NAMESPACE_ROLE_OWNERSHIP,
    NAMESPACE_STANDING_SENDER,
    STATUS_BLOCKED,
    STATUS_CONFLICTED,
    STATUS_MISSING,
    STATUS_READY,
    STATUS_STALE,
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityFactDocument,
    OpportunityIngestionInput,
    ProfileEvidenceInputRecord,
    baseline_vector_collections,
    build_profile_opportunity_ingestion_input,
    check_opportunity_evidence_readiness,
    check_profile_evidence_readiness,
    ensure_profile_c0_readiness,
    normalize_jd_facts,
    run_governed_opportunity_ingestion,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W2_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "opportunity_ingestion.v1.yaml"
)


def _full_payload() -> OpportunityIngestionInput:
    return OpportunityIngestionInput(
        request_id="req-w2",
        trace_root="trace-w2",
        idempotency_key="idem-w2",
        contact={
            "name": "Jane Recruiter",
            "title": "Senior Technical Recruiter",
            "company": "AIG",
            "linkedin_url": "https://www.linkedin.com/in/jane-recruiter",
        },
        company={
            "company": "AIG",
            "context": "Global insurer investing in AI-enabled operating platforms.",
            "url": "https://www.aig.com/",
        },
        jd={
            "title": "VP, Global Head of Agentic AI",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "location": "New York, NY",
            "description": "Lead agentic AI platform strategy for enterprise insurance workflows.",
        },
        company_trigger={
            "trigger_text": "AIG is expanding enterprise AI governance.",
            "url": "https://example.com/aig-ai",
        },
        role_ownership={
            "ownership_signal": "Owns recruiting for AI platform leadership roles.",
            "source_id": "profile:role-ownership",
        },
        relationship={
            "relationship_context": "User-approved prior exchange at industry event.",
            "permission_scope": "may_reference_context_not_name",
        },
        referral={
            "referrer_name": "Sam Referrer",
            "permission_scope": "may_mention_name",
        },
        prior_thread={
            "thread_summary": "Recruiter asked for a concise follow-up.",
            "last_touch_date": "2026-06-01T00:00:00+00:00",
        },
        collected_at="2026-06-08T00:00:00+00:00",
    )


def _profile_record(*, collected_at: str = "2026-06-08T00:00:00+00:00") -> ProfileEvidenceInputRecord:
    return ProfileEvidenceInputRecord(
        profile_id="aig-jane-recruiter",
        name="Jane Recruiter",
        title_headline_seed="Senior Technical Recruiter at AIG",
        linkedin_public_url="https://www.linkedin.com/in/jane-recruiter",
        company="AIG",
        expected_opportunity_scope="AIG role-specific recruiter outreach for JR-12345",
        role_ownership_seed="Owns recruiting for AI platform leadership roles.",
        source_lineage=("linkedin:public-profile-snippet", "search:public-result"),
        confidence=0.86,
        collected_at=collected_at,
    )


def test_w2_config_defines_apps_lic_namespaces_and_write_gate() -> None:
    with W2_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["governance"]["inference_may_write"] is False
    assert config["governance"]["uncontrolled_web_search_allowed"] is False
    assert config["governance"]["write_authority_required"] == WRITE_AUTHORITY_GOVERNED_INGESTION
    assert config["namespaces"]["contact"]["collection"] == NAMESPACE_CONTACT
    assert config["namespaces"]["company"]["collection"] == NAMESPACE_COMPANY
    assert config["namespaces"]["jd"]["collection"] == NAMESPACE_JD
    assert "requisition_number" in config["jd_normalization"]["extended_fields"]
    assert config["governance"]["on_demand_ingestion_outside_inference"] is True
    assert config["profile_evidence_input"]["required_fields"] == [
        "profile_id",
        "name",
        "title_headline_seed",
        "linkedin_public_url",
        "company",
        "expected_opportunity_scope",
    ]
    assert config["baseline_vector_collections"]["standing_sender_corpus"]["collection"] == NAMESPACE_STANDING_SENDER
    assert config["baseline_vector_collections"]["aig_company_facts"]["collection"] == NAMESPACE_COMPANY
    assert config["baseline_vector_collections"]["aig_jd_facts"]["collection"] == NAMESPACE_JD
    assert config["profile_readiness_receipt"]["required_fields"] == [
        "profile_id",
        "status",
        "vector_collection_name",
        "source_count",
        "source_snapshot_ids",
        "ingestion_required_reason",
    ]


def test_w2_baseline_vector_collections_include_sender_aig_and_profile_facts() -> None:
    baselines = baseline_vector_collections()
    packets = [baseline.to_packet() for baseline in baselines]

    assert tuple(
        (item["baseline_id"], item["collection_name"], item["purpose"])
        for item in packets
    ) == BASELINE_VECTOR_COLLECTIONS
    assert {baseline.collection_name for baseline in baselines} >= {
        NAMESPACE_STANDING_SENDER,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
        NAMESPACE_CONTACT,
        NAMESPACE_ROLE_OWNERSHIP,
    }
    assert C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS == (
        NAMESPACE_CONTACT,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
        NAMESPACE_ROLE_OWNERSHIP,
    )


def test_profile_evidence_record_builds_governed_ingestion_payload() -> None:
    record = _profile_record()
    payload = build_profile_opportunity_ingestion_input(
        record,
        request_id="req-profile",
        trace_root="trace-profile",
        idempotency_key="idem-profile",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production AI platforms.",
        },
    )
    documents = run_governed_opportunity_ingestion(
        payload,
        store=None,
        write_authority="",
        write_enabled=False,
    ).documents

    contact = next(document for document in documents if document.namespace == NAMESPACE_CONTACT)
    role = next(document for document in documents if document.namespace == NAMESPACE_ROLE_OWNERSHIP)
    assert payload.profile_id == record.profile_id
    assert payload.expected_opportunity_scope == record.expected_opportunity_scope
    assert contact.metadata["profile_id"] == record.profile_id
    assert contact.metadata["expected_opportunity_scope"] == record.expected_opportunity_scope
    assert contact.confidence == record.confidence
    assert "linkedin:public-profile-snippet" in contact.source_lineage
    assert role.metadata["profile_id"] == record.profile_id
    assert role.metadata["ownership_signal"] == record.role_ownership_seed


def test_jd_normalizer_extracts_position_name_and_requisition_from_json() -> None:
    facts = normalize_jd_facts(
        {
            "job_title": "Director, AI Platforms",
            "req_id": "AIG-9876",
            "company": "AIG",
            "description": "locations: NY-New York, NC-Charlotte, GA-Atlanta\nBuild production AI platforms.",
        }
    )

    assert facts.position_name == "Director, AI Platforms"
    assert facts.job_title == "Director, AI Platforms"
    assert facts.requisition_number == "AIG-9876"
    assert facts.company == "AIG"
    assert facts.location == "NY-New York, NC-Charlotte, GA-Atlanta"
    assert facts.role_family == "engineering"
    assert len(facts.jd_digest) == 64


def test_jd_normalizer_extracts_position_name_and_requisition_from_text() -> None:
    facts = normalize_jd_facts(
        """
        Job Title: VP, Global Head of Agentic AI
        Company: AIG
        Location: New York, NY
        Requisition Number: JR-12345

        Lead enterprise agentic AI platform strategy.
        """,
    )

    assert facts.position_name == "VP, Global Head of Agentic AI"
    assert facts.requisition_number == "JR-12345"
    assert facts.company == "AIG"
    assert facts.location == "New York, NY"
    assert facts.role_family in {"data_ai", "engineering"}


def test_jd_normalizer_extracts_heading_title_and_parenthetical_req() -> None:
    facts = normalize_jd_facts(
        """
        VP, Global Head of Agentic AI Solutions — AIG (JR2601998)

        locations: NY-New York, NC-Charlotte, GA-Atlanta
        Lead enterprise agentic AI transformation.
        """,
    )

    assert facts.position_name == "VP, Global Head of Agentic AI Solutions"
    assert facts.requisition_number == "JR2601998"
    assert facts.company == "AIG"
    assert facts.location == "NY-New York, NC-Charlotte, GA-Atlanta"


def test_governed_ingestion_stores_all_opportunity_fact_namespaces() -> None:
    store = InMemoryOpportunityFactStore()

    receipt = run_governed_opportunity_ingestion(
        _full_payload(),
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )

    expected_namespaces = {
        NAMESPACE_CONTACT,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
        NAMESPACE_COMPANY_TRIGGER,
        NAMESPACE_ROLE_OWNERSHIP,
        NAMESPACE_RELATIONSHIP,
        NAMESPACE_REFERRAL,
        NAMESPACE_PRIOR_THREAD,
    }
    assert receipt.status == STATUS_READY
    assert set(receipt.namespace_counts) == expected_namespaces
    assert set(store.snapshot()) == expected_namespaces
    assert receipt.source_snapshot_ids
    assert receipt.no_inference_write_receipt == "pass:governed_ingestion_write_gate"


def test_inference_style_prepare_does_not_write_to_store() -> None:
    store = InMemoryOpportunityFactStore()

    receipt = run_governed_opportunity_ingestion(
        _full_payload(),
        store=store,
        write_authority="",
        write_enabled=False,
    )

    assert receipt.status == STATUS_READY
    assert receipt.documents
    assert store.snapshot() == {}
    assert receipt.no_inference_write_receipt == "pass:prepared_without_write"


def test_write_enabled_without_governed_authority_is_blocked() -> None:
    store = InMemoryOpportunityFactStore()

    receipt = run_governed_opportunity_ingestion(
        _full_payload(),
        store=store,
        write_authority="inference_runtime",
        write_enabled=True,
    )

    assert receipt.status == STATUS_BLOCKED
    assert store.snapshot() == {}
    assert receipt.skipped[0]["reason"] == "missing_governed_write_authority"


def test_missing_required_namespace_returns_ingestion_required_status() -> None:
    store = InMemoryOpportunityFactStore()

    readiness = check_opportunity_evidence_readiness(
        store=store,
        required_namespaces=(NAMESPACE_CONTACT, NAMESPACE_JD),
    )

    assert readiness.status == STATUS_MISSING
    assert readiness.ready is False
    assert readiness.missing_namespaces == (NAMESPACE_CONTACT, NAMESPACE_JD)
    assert "C0_OPPORTUNITY_INGESTION_REQUIRED" in readiness.ingestion_required_reason
    assert readiness.source_count == 0
    assert readiness.source_count_by_namespace == {
        NAMESPACE_CONTACT: 0,
        NAMESPACE_JD: 0,
    }
    assert readiness.vector_collection_names == (NAMESPACE_CONTACT, NAMESPACE_JD)


def test_profile_readiness_receipt_reports_collections_counts_and_snapshots() -> None:
    store = InMemoryOpportunityFactStore()
    record = _profile_record()
    payload = build_profile_opportunity_ingestion_input(
        record,
        request_id="req-profile-ready",
        trace_root="trace-profile-ready",
        idempotency_key="idem-profile-ready",
        company={"company": "AIG", "context": "AIG enterprise AI context."},
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production AI platforms.",
        },
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )

    receipt = check_profile_evidence_readiness(
        store=store,
        profile_record=record,
        now=datetime(2026, 6, 8, tzinfo=timezone.utc),
    )
    packet = receipt.to_packet()

    assert receipt.status == STATUS_READY
    assert receipt.ready is True
    assert receipt.vector_collection_name == NAMESPACE_CONTACT
    assert receipt.vector_collection_names == C0_PROFILE_REQUIRED_VECTOR_COLLECTIONS
    assert receipt.source_count == 4
    assert receipt.source_count_by_collection == {
        NAMESPACE_CONTACT: 1,
        NAMESPACE_COMPANY: 1,
        NAMESPACE_JD: 1,
        NAMESPACE_ROLE_OWNERSHIP: 1,
    }
    assert len(receipt.source_snapshot_ids) == 4
    assert packet["source_count"] == 4
    assert packet["source_snapshot_ids"]


def test_missing_profile_collection_runs_governed_ingestion_outside_inference() -> None:
    store = InMemoryOpportunityFactStore()
    record = _profile_record()

    before = check_profile_evidence_readiness(store=store, profile_record=record)
    after = ensure_profile_c0_readiness(
        store=store,
        profile_record=record,
        company={"company": "AIG", "context": "AIG enterprise AI context."},
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production AI platforms.",
        },
        now=datetime(2026, 6, 8, tzinfo=timezone.utc),
    )

    assert before.status == STATUS_MISSING
    assert after.status == STATUS_READY
    assert after.ready is True
    assert after.ingestion_action == "governed_ingestion_run"
    assert after.ingestion_receipt_status == STATUS_READY
    assert set(store.snapshot()) >= {
        NAMESPACE_CONTACT,
        NAMESPACE_COMPANY,
        NAMESPACE_JD,
        NAMESPACE_ROLE_OWNERSHIP,
    }


def test_stale_profile_fact_triggers_governed_refresh() -> None:
    store = InMemoryOpportunityFactStore()
    old_record = _profile_record(collected_at="2026-01-01T00:00:00+00:00")
    old_payload = build_profile_opportunity_ingestion_input(
        old_record,
        request_id="req-old-profile",
        trace_root="trace-old-profile",
        idempotency_key="idem-old-profile",
    )
    run_governed_opportunity_ingestion(
        old_payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    fresh_record = _profile_record(collected_at="2026-06-08T00:00:00+00:00")

    before = check_profile_evidence_readiness(
        store=store,
        profile_record=fresh_record,
        required_namespaces=(NAMESPACE_CONTACT,),
        now=datetime(2026, 6, 8, tzinfo=timezone.utc),
    )
    after = ensure_profile_c0_readiness(
        store=store,
        profile_record=fresh_record,
        required_namespaces=(NAMESPACE_CONTACT,),
        now=datetime(2026, 6, 8, tzinfo=timezone.utc),
    )

    assert before.status == STATUS_STALE
    assert before.stale_collections == (NAMESPACE_CONTACT,)
    assert after.status == STATUS_READY
    assert after.ingestion_action == "governed_ingestion_run"
    contact_docs = store.query_namespace(NAMESPACE_CONTACT)
    assert len(contact_docs) == 1
    assert contact_docs[0].freshness_date == "2026-06-08T00:00:00+00:00"


def test_profile_refresh_with_wrong_authority_fails_closed() -> None:
    store = InMemoryOpportunityFactStore()
    record = _profile_record()

    receipt = ensure_profile_c0_readiness(
        store=store,
        profile_record=record,
        required_namespaces=(NAMESPACE_CONTACT,),
        write_authority="inference_runtime",
    )

    assert receipt.status == STATUS_BLOCKED
    assert receipt.ready is False
    assert receipt.ingestion_action == "governed_ingestion_blocked"
    assert "write_gate" in receipt.blocked_collections
    assert store.snapshot() == {}


def test_stale_evidence_returns_stale_status() -> None:
    store = InMemoryOpportunityFactStore()
    old_doc = OpportunityFactDocument(
        document_id="old-trigger",
        namespace=NAMESPACE_COMPANY_TRIGGER,
        fact_family="company_trigger",
        fact_text="Old trigger",
        source_id="source:old",
        source_type="manual",
        source_lineage=("source:old",),
        freshness_date="2026-01-01T00:00:00+00:00",
        confidence=0.8,
        metadata={},
    )
    store.upsert_documents((old_doc,))

    readiness = check_opportunity_evidence_readiness(
        store=store,
        required_namespaces=(NAMESPACE_COMPANY_TRIGGER,),
        now=datetime(2026, 6, 8, tzinfo=timezone.utc),
    )

    assert readiness.status == STATUS_STALE
    assert readiness.stale_namespaces == (NAMESPACE_COMPANY_TRIGGER,)


def test_conflicting_evidence_returns_conflicted_status() -> None:
    store = InMemoryOpportunityFactStore()
    docs = (
        OpportunityFactDocument(
            document_id="contact-1",
            namespace=NAMESPACE_CONTACT,
            fact_family="contact",
            fact_text="Jane | Recruiter | AIG",
            source_id="profile:1",
            source_type="manual",
            source_lineage=("profile:1",),
            freshness_date="2026-06-08T00:00:00+00:00",
            confidence=0.9,
            metadata={"conflict_key": "contact_identity", "canonical_value": "Jane|Recruiter|AIG"},
        ),
        OpportunityFactDocument(
            document_id="contact-2",
            namespace=NAMESPACE_CONTACT,
            fact_family="contact",
            fact_text="Jane | CTO | AIG",
            source_id="profile:2",
            source_type="manual",
            source_lineage=("profile:2",),
            freshness_date="2026-06-08T00:00:00+00:00",
            confidence=0.9,
            metadata={"conflict_key": "contact_identity", "canonical_value": "Jane|CTO|AIG"},
        ),
    )
    store.upsert_documents(docs)

    readiness = check_opportunity_evidence_readiness(
        store=store,
        required_namespaces=(NAMESPACE_CONTACT,),
        now=datetime(2026, 6, 8, tzinfo=timezone.utc),
    )

    assert readiness.status == STATUS_CONFLICTED
    assert readiness.conflicted_namespaces == (NAMESPACE_CONTACT,)


def test_w2_engine_has_no_uncontrolled_web_or_vector_write_surface() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "governed_opportunity_ingestion.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "urlopen",
        "requests.",
        "tavily",
        "browser",
        "chromadb",
        "SovereignChromaClient",
        "get_sovereign_chroma_client",
        "write_text(",
    ):
        assert forbidden not in source
