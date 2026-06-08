from pathlib import Path

import yaml

from apps_lic.engines.governed_opportunity_ingestion import (
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityIngestionInput,
    run_governed_opportunity_ingestion,
)
from apps_lic.engines.message_type_requirement_gate import (
    evaluate_message_requirements_from_store,
)
from apps_lic.engines.recipient_classification import (
    derive_recipient_class,
    derive_recipient_class_from_store,
)
from apps_lic.engines.sender_proof_graph import (
    PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT,
    REASON_CLAIM_NOT_IN_PACKET,
    REASON_CLAIM_PERMISSION_NOT_ALLOW,
    REASON_MESSAGE_REQUIREMENTS_NOT_PASSED,
    REASON_NOT_ALLOWED_FOR_SCOPE,
    REASON_RECIPIENT_CLASS_NOT_DERIVED,
    STATUS_CLAIMS_BLOCKED,
    STATUS_CLAIMS_PASS,
    STATUS_PROOF_GRAPH_BLOCKED,
    STATUS_PROOF_GRAPH_READY,
    build_pa_sender_proof_envelope,
    build_sender_proof_graph_packet,
    build_sender_proof_graph_packet_from_store,
    validate_l2_sender_claims_against_packet,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W5_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "sender_proof_graph.v1.yaml"
)


def _store_for(
    *,
    title: str = "Senior Technical Recruiter",
    company: object | None = None,
    jd: object | None = None,
    company_trigger: object | None = None,
    role_ownership: object | None = None,
) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id=f"req-w5-{title}",
        trace_root="trace-w5",
        idempotency_key=f"idem-w5-{title}",
        contact={
            "name": "Jane Target",
            "title": title,
            "headline": title,
            "company": "AIG",
            "linkedin_url": "https://www.linkedin.com/in/jane-target",
        },
        company=company,
        jd=jd,
        company_trigger=company_trigger,
        role_ownership=role_ownership,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def _gate(
    store: InMemoryOpportunityFactStore,
    *,
    message_type_hint: str,
    intent_text: str = "",
):
    derivation = derive_recipient_class_from_store(store)
    gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=message_type_hint,
        intent_text=intent_text,
    )
    return derivation, gate


def test_w5_config_freezes_sender_proof_graph_contract() -> None:
    with W5_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["authority"] == "C0_3_PROOF_GRAPH"
    assert config["standing_corpus"]["namespace"] == "apps_lic_sender_facts"
    assert config["standing_corpus"]["approved_proof_points_min"] == 1
    assert config["standing_corpus"]["approved_proof_points_max"] == 3
    assert "claim_not_in_c03_packet" in config["permission_decisions"]["block_reasons"]
    assert "apps_lic.pa_sender_proof_envelope.v1" == config["pa_envelope"]["schema_version"]


def test_role_specific_recruiter_gets_one_to_three_approved_proofs_and_pa_envelope() -> None:
    store = _store_for(
        title="Senior Technical Recruiter",
        company={"company": "AIG", "context": "Regulated insurer expanding agentic AI governance."},
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    derivation, gate = _gate(store, message_type_hint="role_specific")

    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
        company_context="AIG regulated insurance AI platform work.",
        desired_next_step="resume review",
    )
    envelope = build_pa_sender_proof_envelope(packet)

    assert packet.status == STATUS_PROOF_GRAPH_READY
    assert packet.ready is True
    assert 1 <= len(packet.selected_proof_points) <= 3
    assert "sp_agentic_platform" in packet.proof_ids
    assert packet.proof_packet_id.startswith("sha256:")
    assert packet.claim_permission_map_hash.startswith("sha256:")
    for proof_id in packet.proof_ids:
        assert packet.source_lineage[proof_id]
        assert packet.graph_links[proof_id]
    assert envelope["allowed_claim_ids"] == list(packet.proof_ids)
    assert envelope["instruction_data_boundary_receipt"] == PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT
    assert envelope["pa_component_hash"].startswith("sha256:")


def test_ceo_trigger_context_prioritizes_executive_value_creation_proofs() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company={"company": "AIG", "context": "Enterprise value creation from AI platform productization."},
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    derivation, gate = _gate(store, message_type_hint="trigger_based_insight")

    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        company_context="Productization, platform economics, risk-aware governance.",
        desired_next_step="quick executive chat",
    )

    assert packet.status == STATUS_PROOF_GRAPH_READY
    assert packet.proof_ids[0] == "sp_platform_commercialization"
    assert packet.proof_to_target_relevance_score["sp_platform_commercialization"] > packet.proof_to_target_relevance_score["sp_agentic_platform"]


def test_scope_and_permission_map_are_reflected_as_omit_or_block_decisions() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    derivation, gate = _gate(store, message_type_hint="general_intro")

    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Low-claim recruiter intro.",
    )
    decisions = {decision.proof_id: decision for decision in packet.permission_decisions}

    assert decisions["sp_unapproved_placeholder"].decision == "block"
    assert decisions["sp_unapproved_placeholder"].reason == REASON_CLAIM_PERMISSION_NOT_ALLOW
    assert decisions["sp_platform_commercialization"].decision == "omit"
    assert decisions["sp_platform_commercialization"].reason == REASON_NOT_ALLOWED_FOR_SCOPE
    assert any(item["proof_id"] == "sp_unapproved_placeholder" for item in packet.blocked_claims)
    assert any(item["proof_id"] == "sp_platform_commercialization" for item in packet.omitted_claims)


def test_sender_proof_blocks_when_recipient_class_is_not_derived() -> None:
    store = _store_for(
        title="Business Partner",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production AI platforms.",
        },
    )
    derivation, gate = _gate(store, message_type_hint="role_specific")

    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Ask for resume review.",
    )

    assert packet.status == STATUS_PROOF_GRAPH_BLOCKED
    assert packet.ready is False
    assert packet.reason_codes == (REASON_RECIPIENT_CLASS_NOT_DERIVED,)


def test_sender_proof_blocks_when_message_requirements_failed() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    derivation, gate = _gate(store, message_type_hint="role_specific")

    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Ask for resume review.",
    )

    assert packet.status == STATUS_PROOF_GRAPH_BLOCKED
    assert packet.ready is False
    assert packet.reason_codes == (REASON_MESSAGE_REQUIREMENTS_NOT_PASSED,)


def test_l2_sender_claim_validation_detects_claims_not_in_c03_packet() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    derivation, gate = _gate(store, message_type_hint="general_intro")
    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Low-claim recruiter intro about governed AI platforms.",
    )

    passing = validate_l2_sender_claims_against_packet(
        [packet.proof_ids[0]],
        packet=packet,
    )
    failing = validate_l2_sender_claims_against_packet(
        [packet.proof_ids[0], "sp_not_in_packet"],
        packet=packet,
    )

    assert passing.status == STATUS_CLAIMS_PASS
    assert passing.allowed_claim_ids == (packet.proof_ids[0],)
    assert failing.status == STATUS_CLAIMS_BLOCKED
    assert failing.allowed_claim_ids == (packet.proof_ids[0],)
    assert failing.blocked_claims == (
        {"proof_id": "sp_not_in_packet", "reason": REASON_CLAIM_NOT_IN_PACKET},
    )


def test_packet_serialization_carries_permission_decisions_and_lineage() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    derivation, gate = _gate(store, message_type_hint="general_intro")
    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Low-claim recruiter intro about governed AI platforms.",
    ).to_packet()

    assert packet["schema_version"] == "apps_lic.c03_sender_proof_graph_packet.v1"
    assert packet["proof_ids"]
    assert packet["permission_decisions"]
    assert packet["source_lineage"]
    assert packet["graph_links"]
    assert packet["unsupported_claim_policy"] == "block"


def test_direct_packet_builder_accepts_explicit_opportunity_documents() -> None:
    store = _store_for(
        title="Chief Technology Officer",
        jd={
            "title": "Director, AI Platforms",
            "company": "AIG",
            "description": "Build cloud-native AI platforms.",
        },
    )
    derivation, gate = _gate(store, message_type_hint="role_specific")
    documents = []
    for namespace in store.snapshot():
        documents.extend(store.query_namespace(namespace))

    packet = build_sender_proof_graph_packet(
        recipient_derivation=derivation,
        message_gate_result=gate,
        opportunity_documents=documents,
        campaign_objective="Discuss cloud-native AI platform leadership.",
    )

    assert packet.status == STATUS_PROOF_GRAPH_READY
    assert "sp_runtime_reliability" in packet.proof_to_target_relevance_score


def test_standalone_referral_evidence_class_still_selects_no_target_default() -> None:
    derivation = derive_recipient_class([])
    store = _store_for(title="Senior Technical Recruiter")
    _derived, gate = _gate(store, message_type_hint="general_intro")

    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Should block because target class was not derived.",
    )

    assert packet.status == STATUS_PROOF_GRAPH_BLOCKED
    assert packet.reason_codes == (REASON_RECIPIENT_CLASS_NOT_DERIVED,)


def test_w5_engine_is_read_only_and_provider_free() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "sender_proof_graph.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "openai",
        "anthropic",
        "chromadb",
        "SovereignChromaClient",
        "upsert_documents",
        "write_text(",
        "urlopen",
        "requests.",
        "sqlite3.connect",
    ):
        assert forbidden not in source
