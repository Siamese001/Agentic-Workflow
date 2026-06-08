from dataclasses import replace
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
from apps_lic.engines.sender_proof_graph import build_sender_proof_graph_packet_from_store
from apps_lic.engines.validation_exit import (
    ANTHROPIC_MESSAGES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    EXIT_BLOCKED,
    EXIT_CLEAR_DRAFT,
    GATE_CANDIDATE_SELECTION,
    GATE_JD_REQUIRED,
    GATE_NO_SEND,
    GATE_POSITION_NAME,
    GATE_REQUISITION_NUMBER,
    GATE_ROLE_OWNERSHIP_FIT,
    GATE_SCHEMA,
    GATE_UNSUPPORTED_CLAIM,
    GATE_WHOLE_MESSAGE_SHAPE,
    INDEPENDENT_JUDGE,
    JUDGE_CEO_EVIDENCE_RISK,
    JUDGE_CEO_ORIGINALITY,
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_UNAVAILABLE,
    LIVE_CLAUDE_API_CALL,
    NON_INDEPENDENT_JUDGE,
    STATUS_X1D_BLOCKED,
    STATUS_X1D_NOT_REQUIRED,
    STATUS_X2_BLOCKED,
    STATUS_X2_PASS,
    X1DJudgeResult,
    required_x1d_profiles,
    run_validation_exit,
)
from apps_lic.engines.whole_message_generation import (
    GENERATOR_MODEL_ID,
    GENERATOR_PROVIDER_ID,
    build_whole_message_generation_request_from_store,
    generate_whole_message_candidates,
)
from apps_lic.engines.x1d_claude_judge_adapter import (
    parse_claude_x1d_response,
    run_claude_x1d_judges,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W7_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "validation_exit.v1.yaml"
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
        request_id=f"req-w7-{title}",
        trace_root="trace-w7",
        idempotency_key=f"idem-w7-{title}",
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


def _w7_request(
    store: InMemoryOpportunityFactStore,
    *,
    message_type_hint: str,
    campaign_objective: str,
    desired_next_step: str = "a quick resume review",
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
    return build_whole_message_generation_request_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        sender_proof_packet=proof_packet,
        request_id="req-w7",
        trace_root="trace-w7",
        campaign_objective=campaign_objective,
        desired_next_step=desired_next_step,
    )


def _passing_judge(judge_id: str, *, score: float = 0.95) -> X1DJudgeResult:
    return X1DJudgeResult(
        judge_id=judge_id,
        model=DEFAULT_X1D_JUDGE_MODEL,
        provider=DEFAULT_X1D_JUDGE_PROVIDER,
        score=score,
        passed=True,
    )


def test_w7_config_freezes_validation_exit_policy() -> None:
    with W7_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["governance"]["x1d_runs_only_after_x2_pass"] is True
    assert config["governance"]["x1d_can_override_x2"] is False
    assert config["governance"]["exit_is_final_clearance_authority"] is True
    assert "clear_draft" in config["exit"]["allowed_dispositions"]
    assert "schema_gate" in config["x2_gates"]["universal"]
    assert "candidate_selection_gate" in config["x2_gates"]["conditional"]
    assert config["x1d"]["default_model"] == DEFAULT_X1D_JUDGE_MODEL
    assert config["x1d"]["depth_labels"] == {"none": 0, "one": 1, "two": 2}
    assert config["x1d"]["availability_policy"]["missing_or_unavailable_required_judge"] == "blocked"
    assert config["x1d"]["availability_policy"]["non_live_required_judge"] == "blocked"
    assert config["x1d"]["live_call_policy"]["required_for_clearance"] is True
    assert config["x1d"]["live_call_policy"]["required_transport_provenance"] == LIVE_CLAUDE_API_CALL
    assert config["x1d"]["live_call_policy"]["required_transport_provider"] == ANTHROPIC_MESSAGES_API
    assert config["x1d"]["live_call_policy"]["required_raw_response_digest"] is True
    assert config["x1d"]["live_call_policy"]["mock_or_fake_transport_allowed"] is False
    assert config["x1d"]["preflight_policy"]["modes"] == ["fake", "live", "unavailable-expected"]
    assert config["x1d"]["preflight_policy"]["fake_mode_can_clear_exit"] is False


def test_recruiter_general_intro_can_clear_with_x2_only() -> None:
    store = _store_for(title="Senior Technical Recruiter")
    request = _w7_request(
        store,
        message_type_hint="general_intro",
        campaign_objective="Explore fit for AI platform leadership roles.",
        desired_next_step="a quick connection",
    )
    batch = generate_whole_message_candidates(request)

    bundle = run_validation_exit(request, batch)

    assert bundle.disposition == EXIT_CLEAR_DRAFT
    assert bundle.x2_result.status == STATUS_X2_PASS
    assert bundle.x1d_result.status == STATUS_X1D_NOT_REQUIRED
    assert bundle.x1d_result.judge_results == ()
    assert bundle.x2_result.gate(GATE_NO_SEND).passed is True
    assert bundle.final_user_visible_draft_id == bundle.candidate_id


def test_role_specific_recruiter_sc2_blocks_direct_non_live_judge_artifact() -> None:
    store = _store_for(
        title="Senior Technical Recruiter",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )
    batch = generate_whole_message_candidates(request)

    missing_selection = run_validation_exit(request, batch)

    assert missing_selection.disposition == EXIT_BLOCKED
    assert missing_selection.x2_result.status == STATUS_X2_BLOCKED
    assert missing_selection.x2_result.gate(GATE_CANDIDATE_SELECTION).passed is False
    assert missing_selection.x1d_result.status == STATUS_X1D_BLOCKED

    selected = batch.candidates[0]
    bundle = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_passing_judge(JUDGE_EVIDENCE_SUPPORT),),
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert bundle.x1d_result.status == STATUS_X1D_BLOCKED
    assert bundle.x1d_result.judge_results[0].judge_id == JUDGE_EVIDENCE_SUPPORT
    assert bundle.x1d_result.judge_results[0].independence_status == INDEPENDENT_JUDGE
    assert "non_live_claude_judge:evidence_claim_support_x1d" in bundle.x1d_result.reason_codes


def test_ceo_trigger_blocks_direct_non_live_judge_artifacts() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company={"company": "AIG", "context": "Enterprise AI platform economics."},
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a brief executive exchange",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]

    one_judge = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_passing_judge(JUDGE_CEO_ORIGINALITY),),
    )

    assert one_judge.disposition == EXIT_BLOCKED
    assert one_judge.x1d_result.status == STATUS_X1D_BLOCKED
    assert JUDGE_CEO_EVIDENCE_RISK in one_judge.x1d_result.missing_judge_ids

    two_judges = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(
            _passing_judge(JUDGE_CEO_ORIGINALITY, score=0.93),
            _passing_judge(JUDGE_CEO_EVIDENCE_RISK, score=0.94),
        ),
    )

    assert two_judges.disposition == EXIT_BLOCKED
    assert two_judges.x1d_result.status == STATUS_X1D_BLOCKED
    assert two_judges.x1d_result.required_depth == "two"
    assert len(two_judges.x1d_result.required_profiles) == 2
    assert len(two_judges.x1d_result.judge_results) == 2
    assert "non_live_claude_judge:ceo_attention_originality_x1d" in two_judges.x1d_result.reason_codes
    assert "non_live_claude_judge:ceo_evidence_overclaim_risk_x1d" in two_judges.x1d_result.reason_codes


def test_validation_exit_rejects_fake_claude_x1d_runner_hook_after_x2_passes() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a brief executive exchange",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]
    observed_payloads = []

    def fake_transport(payload):
        observed_payloads.append(payload)
        return {
            "score": payload["threshold"] + 0.03,
            "passed": True,
            "issues": [],
            "required_repairs": [],
        }

    def live_runner(runner_request, runner_candidate):
        return run_claude_x1d_judges(
            runner_request,
            runner_candidate,
            transport=fake_transport,
        )

    bundle = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        x1d_judge_runner=live_runner,
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert bundle.x1d_result.status == STATUS_X1D_BLOCKED
    assert observed_payloads == []
    assert {
        result.issues[0]
        for result in bundle.x1d_result.judge_results
    } == {"non_live_claude_transport_rejected"}
    assert "non_live_claude_judge:ceo_attention_originality_x1d" in bundle.x1d_result.reason_codes


def test_claude_x1d_response_parser_marks_unparseable_output_unavailable() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a brief executive exchange",
    )
    assert request.reasoning_policy.x1d_llm_judge_depth == 2
    profile = required_x1d_profiles(request)[0]
    required_profile = parse_claude_x1d_response("not json", profile=profile)

    assert required_profile.availability_status == JUDGE_UNAVAILABLE
    assert required_profile.passed is False

    parsed = parse_claude_x1d_response(
        '{"score": 0.91, "passed": true, "issues": [], "required_repairs": []}',
        profile=profile,
    )

    assert parsed.score == 0.91
    assert parsed.transport_provenance == ""


def test_x1d_cannot_run_or_override_when_x2_failed() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a brief executive exchange",
    )
    batch = generate_whole_message_candidates(request)

    bundle = run_validation_exit(
        request,
        batch,
        judge_results=(
            _passing_judge(JUDGE_CEO_ORIGINALITY),
            _passing_judge(JUDGE_CEO_EVIDENCE_RISK),
        ),
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert bundle.x2_result.gate(GATE_CANDIDATE_SELECTION).passed is False
    assert bundle.x1d_result.status == STATUS_X1D_BLOCKED
    assert bundle.x1d_result.judge_results == ()


def test_x1d_provider_independence_and_availability_are_enforced() -> None:
    store = _store_for(
        title="Senior Technical Recruiter",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]

    same_provider = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(
            X1DJudgeResult(
                judge_id=JUDGE_EVIDENCE_SUPPORT,
                model=GENERATOR_MODEL_ID,
                provider=GENERATOR_PROVIDER_ID,
                score=0.99,
                passed=True,
            ),
        ),
    )

    assert same_provider.disposition == EXIT_BLOCKED
    assert same_provider.x1d_result.status == STATUS_X1D_BLOCKED
    assert same_provider.x1d_result.judge_results[0].independence_status == NON_INDEPENDENT_JUDGE
    assert "non_independent_judge:evidence_claim_support_x1d" in same_provider.x1d_result.reason_codes
    assert "non_live_claude_judge:evidence_claim_support_x1d" in same_provider.x1d_result.reason_codes

    unavailable = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(
            X1DJudgeResult(
                judge_id=JUDGE_EVIDENCE_SUPPORT,
                model=DEFAULT_X1D_JUDGE_MODEL,
                provider=DEFAULT_X1D_JUDGE_PROVIDER,
                score=0.99,
                passed=True,
                availability_status=JUDGE_UNAVAILABLE,
            ),
        ),
    )

    assert unavailable.disposition == EXIT_BLOCKED
    assert unavailable.x1d_result.status == STATUS_X1D_BLOCKED
    assert "judge_unavailable:evidence_claim_support_x1d" in unavailable.x1d_result.reason_codes


def test_x2_conditional_jd_gates_fail_closed_even_if_candidate_and_judge_pass() -> None:
    store = _store_for(
        title="Senior Technical Recruiter",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]
    mutated_request = replace(request, jd_fields={})

    bundle = run_validation_exit(
        mutated_request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_passing_judge(JUDGE_EVIDENCE_SUPPORT),),
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert bundle.x2_result.gate(GATE_JD_REQUIRED).passed is False
    assert bundle.x2_result.gate(GATE_POSITION_NAME).passed is False
    assert bundle.x2_result.gate(GATE_REQUISITION_NUMBER).passed is False
    assert bundle.x1d_result.status == STATUS_X1D_BLOCKED


def test_x2_role_ownership_fit_blocks_clear_regional_jd_mismatch() -> None:
    store = _store_for(
        title="AIG - Head of Talent Acquisition | Inclusion",
        jd={
            "title": "VP, Global Head of Agentic AI Solutions",
            "requisition_number": "JR2601998",
            "company": "AIG",
            "location": "NY-New York, NC-Charlotte, GA-Atlanta",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    payload = OpportunityIngestionInput(
        request_id="req-w7-japan-ta",
        trace_root="trace-w7",
        idempotency_key="idem-w7-japan-ta",
        role_ownership={
            "ownership_signal": "Head of Talent Acquisition for AIG Japan in Tokyo.",
        },
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    request = _w7_request(
        store,
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the VP Global Head of Agentic AI Solutions role.",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]

    bundle = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_passing_judge(JUDGE_EVIDENCE_SUPPORT),),
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert bundle.x2_result.gate(GATE_ROLE_OWNERSHIP_FIT).passed is False
    assert bundle.x2_result.gate(GATE_ROLE_OWNERSHIP_FIT).reason == "role_ownership_region_mismatch"
    assert bundle.x1d_result.status == STATUS_X1D_BLOCKED


def test_exit_proof_bundle_reports_gate_and_judge_audit_fields() -> None:
    store = _store_for(
        title="Chief Executive Officer",
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    request = _w7_request(
        store,
        message_type_hint="trigger_based_insight",
        campaign_objective="Share an executive-native asymmetric insight about AI platform economics.",
        desired_next_step="a brief executive exchange",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]
    bundle = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(
            _passing_judge(JUDGE_CEO_ORIGINALITY, score=0.93),
            _passing_judge(JUDGE_CEO_EVIDENCE_RISK, score=0.94),
        ),
    )
    packet = bundle.to_packet()

    assert packet["disposition"] == EXIT_BLOCKED
    assert packet["no_send_receipt"] == request.no_send_receipt
    assert packet["proof_packet_id"] == request.proof_packet.proof_packet_id
    assert packet["prompt_contract_id"] == request.prompt_contract_id
    gate_packet = packet["x2"]["gate_results"][0]
    assert {"gate_id", "status", "severity", "reason", "clearance"} <= set(gate_packet)
    judge_packet = packet["x1d"]["judge_results"][0]
    assert {
        "judge_id",
        "model",
        "provider",
        "score",
        "threshold",
        "passed",
        "availability_status",
        "independence_status",
        "transport_provenance",
        "transport_provider",
        "transport_call_id",
        "raw_response_digest",
        "clearance",
    } <= set(judge_packet)
    assert judge_packet["model"] == DEFAULT_X1D_JUDGE_MODEL
    assert judge_packet["provider"] == DEFAULT_X1D_JUDGE_PROVIDER
    assert judge_packet["transport_provenance"] == ""
    assert judge_packet["transport_provider"] == ""
    assert judge_packet["threshold"] > 0
    assert packet["x2"]["status"] == STATUS_X2_PASS
    assert packet["x1d"]["status"] == STATUS_X1D_BLOCKED


def test_w7_engine_is_provider_free_and_read_only() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "validation_exit.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "openai",
        "chromadb",
        "SovereignChromaClient",
        "upsert_documents",
        "write_text(",
        "urlopen",
        "requests.",
        "sqlite3.connect",
    ):
        assert forbidden not in source

    assert GATE_SCHEMA in source
    assert GATE_WHOLE_MESSAGE_SHAPE in source
    assert GATE_UNSUPPORTED_CLAIM in source
