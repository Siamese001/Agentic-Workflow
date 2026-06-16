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
from apps_lic.engines.recipient_classification import derive_recipient_class_from_store
from apps_lic.engines.sender_proof_graph import (
    STATUS_PROOF_GRAPH_BLOCKED,
    build_sender_proof_graph_packet_from_store,
)
from apps_lic.engines.whole_message_generation import (
    GENERATOR_PROVIDER_ID,
    INSTRUCTION_DATA_BOUNDARY_RECEIPT,
    NO_DURABLE_WRITE_RECEIPT,
    NO_SEND_RECEIPT,
    REASON_CANDIDATE_MISSING_CTA,
    REASON_CANDIDATE_MISSING_SIGNATURE,
    REASON_CANDIDATE_MISSING_SUBJECT,
    REASON_CANDIDATE_NOT_WHOLE_MESSAGE,
    REASON_CANDIDATE_SUBJECT_TOO_LONG,
    REASON_CANDIDATE_UNAPPROVED_CLAIM,
    REASON_MESSAGE_REQUIREMENTS_NOT_PASSED,
    REASON_SEND_MODE_FORBIDDEN,
    REASON_SENDER_PROOF_NOT_READY,
    SC_1,
    SC_2,
    SC_3,
    STATUS_CANDIDATES_BLOCKED,
    STATUS_CANDIDATES_READY,
    STATUS_CANDIDATE_SHAPE_BLOCKED,
    STATUS_CANDIDATE_SHAPE_PASS,
    STATUS_GENERATION_REQUEST_BLOCKED,
    STATUS_GENERATION_REQUEST_READY,
    WholeMessageCandidate,
    build_whole_message_generation_request_from_store,
    generate_whole_message_candidates,
    resolve_length_budget,
    resolve_reasoning_policy,
    validate_whole_message_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W6_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "whole_message_generation.v1.yaml"
)


def _store_for(
    *,
    title: str = "Senior Technical Recruiter",
    company: object | None = None,
    jd: object | None = None,
    company_trigger: object | None = None,
    referral: object | None = None,
    relationship: object | None = None,
    prior_thread: object | None = None,
) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id=f"req-w6-{title}",
        trace_root="trace-w6",
        idempotency_key=f"idem-w6-{title}",
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
        referral=referral,
        relationship=relationship,
        prior_thread=prior_thread,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def _w6_request(
    store: InMemoryOpportunityFactStore,
    *,
    message_type_hint: str,
    campaign_objective: str,
    desired_next_step: str = "a quick resume review",
    send_mode: str = "draft_only",
    channel: str = "linkedin",
):
    derivation = derive_recipient_class_from_store(store)
    gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=message_type_hint,
    )
    proof_packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective=campaign_objective,
        desired_next_step=desired_next_step,
    )
    request = build_whole_message_generation_request_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        sender_proof_packet=proof_packet,
        request_id="req-w6",
        trace_root="trace-w6",
        channel=channel,
        send_mode=send_mode,
        campaign_objective=campaign_objective,
        desired_next_step=desired_next_step,
    )
    return derivation, gate, proof_packet, request


def test_w6_config_freezes_whole_message_generation_contract() -> None:
    with W6_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["governance"]["generation_unit"] == "whole_message"
    assert config["governance"]["provider_calls_in_w6_scaffold"] is False
    assert config["governance"]["durable_writes_allowed"] is False
    assert config["reasoning_policy"]["sc_levels"]["SC-2"]["candidate_count"] == 2
    assert config["reasoning_policy"]["sc_levels"]["SC-3"]["candidate_count"] == 3
    assert "body_fragment" in config["governance"]["forbidden_units"]
    assert config["recipient_archetype_policy"]["class_to_archetype"]["CEO"] == "C_LEVEL"
    assert config["length_control_policy"]["hard_controls"] == [
        "max_sentences",
        "hard_cap_chars",
    ]
    assert config["length_control_policy"]["advisory_controls"] == [
        "min_words",
        "max_words",
    ]


def test_ceo_length_budget_uses_c_level_archetype_and_advisory_words() -> None:
    budget = resolve_length_budget(
        recipient_class="CEO",
        message_type="role_specific",
        modifiers={},
    )

    assert budget.budget_key == "c_level_role_specific"
    assert budget.max_sentences == 3
    assert budget.hard_cap_chars == 550
    assert budget.to_packet()["hard_controls"] == ["max_sentences", "hard_cap_chars"]
    assert budget.to_packet()["advisory_controls"] == ["min_words", "max_words"]


def test_inmail_length_budget_uses_sentence_and_character_hard_controls() -> None:
    budget = resolve_length_budget(
        recipient_class="CEO",
        message_type="trigger_based_insight",
        modifiers={},
        channel="linkedin_inmail",
    )

    assert budget.budget_key == "c_level_trigger_inmail"
    assert budget.max_sentences == 6
    assert budget.hard_cap_chars == 1900
    assert budget.channel == "linkedin_inmail"
    assert budget.route_family == "INMAIL"
    assert budget.subject_required is True
    assert budget.signature_required is True
    assert budget.to_packet()["hard_controls"] == ["max_sentences", "hard_cap_chars"]
    assert budget.to_packet()["advisory_controls"] == ["min_words", "max_words"]
    assert budget.to_packet()["subject_required"] is True


def test_inmail_candidate_requires_subject_line() -> None:
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
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for a quick resume review.",
        channel="linkedin_inmail",
    )
    batch = generate_whole_message_candidates(request)
    candidate = batch.candidates[0]

    assert candidate.subject_line
    assert validate_whole_message_candidate(candidate, request=request).status == STATUS_CANDIDATE_SHAPE_PASS

    missing_subject = WholeMessageCandidate(
        candidate_id=candidate.candidate_id,
        draft_text=candidate.draft_text,
        attempt_seed=candidate.attempt_seed,
        model_id=candidate.model_id,
        provider_id=candidate.provider_id,
        temperature=candidate.temperature,
        top_p=candidate.top_p,
        word_count=candidate.word_count,
        sentence_count=candidate.sentence_count,
        char_count=candidate.char_count,
        claims_used=candidate.claims_used,
        is_whole_message=candidate.is_whole_message,
        no_durable_write_receipt=candidate.no_durable_write_receipt,
        generation_receipt=candidate.generation_receipt,
        subject_line="",
    )
    validation = validate_whole_message_candidate(missing_subject, request=request)

    assert validation.status == STATUS_CANDIDATE_SHAPE_BLOCKED
    assert REASON_CANDIDATE_MISSING_SUBJECT in validation.issues
    assert REASON_CANDIDATE_SUBJECT_TOO_LONG not in validation.issues


def test_role_specific_recruiter_request_packs_w4_w5_jd_policy_and_no_send() -> None:
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
    _derivation, _gate, proof_packet, request = _w6_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )

    assert request.status == STATUS_GENERATION_REQUEST_READY
    assert request.ready is True
    assert request.reasoning_policy.sc_level == SC_2
    assert request.reasoning_policy.candidate_count == 2
    assert request.reasoning_policy.repair_budget == 1
    assert request.reasoning_policy.generator_temperature >= 0.90
    assert request.reasoning_policy.judge_temperature == 0.10
    assert request.length_budget.budget_key == "recruiter_role_specific"
    assert request.jd_fields["position_name"] == "Director, AI Platforms"
    assert request.jd_fields["requisition_number"] == "JR-12345"
    assert request.proof_packet.proof_packet_id == proof_packet.proof_packet_id
    assert request.message_intelligence_packet.packet_id.startswith("sha256:")
    assert request.component_hash_map["message_intelligence_packet"] == request.message_intelligence_packet.packet_id
    assert request.message_intelligence_packet.role_context == "Director, AI Platforms (JR-12345)"
    assert request.no_send_receipt == NO_SEND_RECEIPT
    assert request.no_durable_write_receipt == NO_DURABLE_WRITE_RECEIPT
    assert request.instruction_data_boundary_receipt == INSTRUCTION_DATA_BOUNDARY_RECEIPT
    assert request.prompt_contract_id.startswith("sha256:")


def test_role_specific_recruiter_generates_two_whole_message_candidates() -> None:
    store = _store_for(
        title="Senior Technical Recruiter",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )

    batch = generate_whole_message_candidates(request)

    assert batch.status == STATUS_CANDIDATES_READY
    assert len(batch.candidates) == 2
    for candidate in batch.candidates:
        assert candidate.provider_id == GENERATOR_PROVIDER_ID
        assert candidate.is_whole_message is True
        assert "Director, AI Platforms" in candidate.draft_text
        assert "JR-12345" in candidate.draft_text
        assert "Subject:" not in candidate.draft_text
        assert candidate.draft_text.endswith("\n\nAmit")
        assert candidate.claims_used
        validation = validate_whole_message_candidate(candidate, request=request)
        assert validation.status == STATUS_CANDIDATE_SHAPE_PASS


def test_ceo_trigger_gets_sc3_three_candidates_and_two_judge_depth_marker() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company={"company": "AIG", "context": "Enterprise AI platform economics."},
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a brief executive exchange",
    )
    batch = generate_whole_message_candidates(request)

    assert request.reasoning_policy.sc_level == SC_3
    assert request.reasoning_policy.candidate_count == 3
    assert request.reasoning_policy.repair_budget == 2
    assert request.reasoning_policy.x1d_llm_judge_depth == 2
    assert len(batch.candidates) == 3
    assert all("governance" in candidate.draft_text.lower() for candidate in batch.candidates)
    assert all("deployment caught my attention" not in candidate.draft_text for candidate in batch.candidates)
    assert all("I noticed AIG announced" in candidate.draft_text for candidate in batch.candidates)


def test_inmail_uses_rich_packet_while_connection_request_stays_short() -> None:
    store = _store_for(
        title="Chief Digital Officer",
        company={"company": "AIG", "context": "AIG is scaling governed agentic AI in regulated insurance."},
        company_trigger={
            "trigger_text": (
                "AIG Assist scaled submission and FNOL automation across underwriting, "
                "claims, operations, finance, and corporate functions."
            ),
            "url": "https://example.com/aig-assist",
        },
    )
    _derivation, _gate, _proof_packet, inmail_request = _w6_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native fit note about governed agentic AI.",
        desired_next_step="a brief executive exchange",
        channel="linkedin_inmail",
    )
    packet = inmail_request.message_intelligence_packet
    inmail_candidate = generate_whole_message_candidates(inmail_request).candidates[0]

    assert packet.to_packet()["schema_version"] == "apps_lic.message_intelligence_packet.v1"
    assert packet.company_insight.startswith("AIG Assist scaled")
    assert packet.ask_calibration.recommended_cta.endswith("?")
    assert "15-minute" not in packet.ask_calibration.recommended_cta.lower()
    assert inmail_candidate.subject_line
    assert inmail_candidate.word_count >= inmail_request.length_budget.min_words
    assert 4 <= inmail_candidate.sentence_count <= inmail_request.length_budget.max_sentences
    assert inmail_candidate.draft_text.endswith("\n\nAmit")
    lowered = inmail_candidate.draft_text.lower()
    for banned in ("which maps to", "hard call", "not demo quality", "15-minute"):
        assert banned not in lowered

    _derivation, _gate, _proof_packet, connection_request = _w6_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Send a short connection request.",
        desired_next_step="connecting",
        channel="linkedin_chat",
    )
    connection_candidate = generate_whole_message_candidates(connection_request).candidates[0]

    assert connection_request.length_budget.route_family == "CONNECTION_REQ"
    assert connection_candidate.char_count <= 300
    assert connection_candidate.sentence_count <= 2
    assert not connection_candidate.draft_text.endswith("\n\nAmit")
    assert validate_whole_message_candidate(
        connection_candidate,
        request=connection_request,
    ).status == STATUS_CANDIDATE_SHAPE_PASS


def test_long_trigger_based_insight_candidate_stays_within_exec_length_budget() -> None:
    store = _store_for(
        title="EVP, Chief Digital Officer",
        company={"company": "AIG", "context": "Enterprise AI platform economics."},
        company_trigger={
            "trigger_text": (
                "AIG Assist scaled submission and FNOL automation; AIG is pushing enterprise "
                "agentic AI transformation across underwriting, claims, operations, finance, "
                "and corporate functions."
            ),
            "url": "https://example.com/aig-ai",
        },
    )
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a quick resume review or short conversation",
    )
    batch = generate_whole_message_candidates(request)

    assert request.length_budget.budget_key == "executive_trigger"
    assert batch.candidates
    assert batch.candidates[0].word_count >= 1
    assert batch.candidates[0].draft_text.endswith("\n\nAmit")
    assert batch.candidates[0].sentence_count <= request.length_budget.max_sentences
    assert batch.candidates[0].char_count <= request.length_budget.hard_cap_chars


def test_general_intro_recruiter_stays_lightweight_sc1() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="general_intro",
        campaign_objective="Explore fit for AI platform leadership roles.",
        desired_next_step="a quick connection",
    )

    assert request.reasoning_policy.sc_level == SC_1
    assert request.reasoning_policy.candidate_count == 1
    assert request.length_budget.budget_key == "recruiter_general_intro"
    assert generate_whole_message_candidates(request).candidates[0].char_count <= request.length_budget.hard_cap_chars


def test_sensitive_modifier_escalates_to_sc3() -> None:
    policy = resolve_reasoning_policy(
        recipient_class="RECRUITER",
        message_type="general_intro",
        modifiers={"uses_sensitive_constraints": True},
    )

    assert policy.sc_level == SC_3
    assert policy.candidate_count == 3
    assert "sensitive_constraints:SC-3" in policy.reason_codes


def test_failed_w4_gate_blocks_generation_request_and_candidates() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    _derivation, gate, proof_packet, request = _w6_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for a missing JD role.",
    )

    assert gate.status != "MESSAGE_REQUIREMENTS_PASS"
    assert proof_packet.status == STATUS_PROOF_GRAPH_BLOCKED
    assert request.status == STATUS_GENERATION_REQUEST_BLOCKED
    assert request.blocking_reasons == (
        REASON_MESSAGE_REQUIREMENTS_NOT_PASSED,
        REASON_SENDER_PROOF_NOT_READY,
    )
    assert generate_whole_message_candidates(request).status == STATUS_CANDIDATES_BLOCKED


def test_forbidden_send_mode_blocks_even_when_evidence_is_ready() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="general_intro",
        campaign_objective="Explore fit for AI platform leadership roles.",
        send_mode="send_now",
    )

    assert request.status == STATUS_GENERATION_REQUEST_BLOCKED
    assert REASON_SEND_MODE_FORBIDDEN in request.blocking_reasons
    assert request.no_send_receipt == ""


def test_candidate_shape_validator_rejects_fragments_and_unapproved_claims() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="general_intro",
        campaign_objective="Explore fit for AI platform leadership roles.",
    )
    bad = WholeMessageCandidate(
        candidate_id="bad",
        draft_text="Subject: Quick intro\nBody: I have an unsupported metric claim.",
        attempt_seed="seed",
        model_id="model",
        provider_id="provider",
        temperature=0.9,
        top_p=0.95,
        word_count=9,
        sentence_count=2,
        char_count=58,
        claims_used=("sp_not_in_packet",),
        is_whole_message=False,
        no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
        generation_receipt="test",
    )

    validation = validate_whole_message_candidate(bad, request=request)

    assert validation.status == STATUS_CANDIDATE_SHAPE_BLOCKED
    assert REASON_CANDIDATE_NOT_WHOLE_MESSAGE in validation.issues
    assert REASON_CANDIDATE_MISSING_CTA in validation.issues
    assert REASON_CANDIDATE_MISSING_SIGNATURE in validation.issues
    assert REASON_CANDIDATE_UNAPPROVED_CLAIM in validation.issues


def test_request_packet_contains_pa_and_l2_required_fields() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    _derivation, _gate, _proof_packet, request = _w6_request(
        store,
        message_type_hint="general_intro",
        campaign_objective="Explore fit for AI platform leadership roles.",
    )
    packet = request.to_packet()

    assert packet["schema_version"] == "apps_lic.whole_message_generation_request.v1"
    assert packet["allowed_claim_ids"]
    assert packet["component_hash_map"]["message_requirement_gate"].startswith("sha256:")
    assert packet["component_hash_map"]["sender_proof_graph"].startswith("sha256:")
    assert packet["length_budget"]["hard_cap_chars"] <= 500
    assert packet["reasoning_policy"]["generator_temperature"] > packet["reasoning_policy"]["judge_temperature"]


def test_w6_engine_is_provider_free_and_read_only() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "whole_message_generation.py"
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
