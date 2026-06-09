from dataclasses import replace

from apps_lic.engines.message_type_requirement_gate import MESSAGE_ROLE_SPECIFIC
from apps_lic.engines.validation_exit import (
    ANTHROPIC_MESSAGES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    EXIT_CLEAR_DRAFT,
    JUDGE_AVAILABLE,
    JUDGE_EVIDENCE_SUPPORT,
    LIVE_CLAUDE_API_CALL,
    STATUS_X1D_BLOCKED,
    STATUS_X1D_REVIEW_REQUIRED,
    STATUS_X2_BLOCKED,
    X1DJudgeResult,
    run_validation_exit,
)
from apps_lic.engines.whole_message_generation import (
    GENERATOR_MODEL_ID,
    GENERATOR_PROVIDER_ID,
    NO_DURABLE_WRITE_RECEIPT,
    WholeMessageCandidate,
    generate_whole_message_candidates,
)
import apps_lic.engines.x1d_judge_feedback_regeneration as x1d_regen
from apps_lic.engines.x1d_judge_feedback_regeneration import (
    STOP_REPAIR_CANDIDATE_CLEAR,
    STOP_REPAIR_CANDIDATE_X2_FAILED,
    STOP_REPAIR_SAME_AS_PARENT,
    STOP_X1D_BLOCKED_NO_REGENERATION,
    run_x1d_judge_feedback_regeneration,
)
from tests.apps_lic.test_w7_validation_exit import _store_for, _w7_request


def _request_and_selected():
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
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )
    batch = generate_whole_message_candidates(request)
    return request, batch, batch.candidates[0]


def _live_judge(
    judge_id: str = JUDGE_EVIDENCE_SUPPORT,
    *,
    score: float,
    passed: bool,
    issue: str = "generic_draft",
    repair: str = "make_specific",
) -> X1DJudgeResult:
    return X1DJudgeResult(
        judge_id=judge_id,
        model=DEFAULT_X1D_JUDGE_MODEL,
        provider=DEFAULT_X1D_JUDGE_PROVIDER,
        score=score,
        passed=passed,
        availability_status=JUDGE_AVAILABLE,
        transport_provenance=LIVE_CLAUDE_API_CALL,
        transport_provider=ANTHROPIC_MESSAGES_API,
        transport_call_id=f"test-call-{score}",
        raw_response_digest="sha256:" + "a" * 64,
        issues=(issue,),
        required_repairs=(repair,),
    )


def _repair_candidate(
    parent: WholeMessageCandidate,
    *,
    text: str,
    candidate_id: str = "repair_candidate_1",
    claims: tuple[str, ...] | None = None,
) -> WholeMessageCandidate:
    return WholeMessageCandidate(
        candidate_id=candidate_id,
        draft_text=text,
        attempt_seed="sha256:" + "b" * 64,
        model_id=GENERATOR_MODEL_ID,
        provider_id=GENERATOR_PROVIDER_ID,
        temperature=0.3,
        top_p=0.9,
        word_count=len(text.split()),
        sentence_count=3,
        char_count=len(text),
        claims_used=claims if claims is not None else parent.claims_used,
        is_whole_message=True,
        no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
        generation_receipt="x1d_feedback_repair:prov:test:mref:test",
    )


def test_x1d_feedback_repair_can_clear_after_live_judge_review_failure() -> None:
    request, batch, selected = _request_and_selected()
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_live_judge(score=0.40, passed=False),),
    )
    assert initial.x1d_result.status == STATUS_X1D_REVIEW_REQUIRED
    repaired_text = (
        "Hi Jane, AIG's Director, AI Platforms role needs governed agentic AI delivery "
        "that can stand up inside regulated workflows. I designed and operationalized "
        "a governed agentic AI platform for regulated enterprise workflows. Would a "
        "quick resume review for JR-12345 be useful?\n\nAmit"
    )
    judge_calls: list[str] = []

    def repair_runner(req, parent, failed, iteration):
        assert req is request
        assert parent.candidate_id == selected.candidate_id
        assert failed[0].required_repairs == ("make_specific",)
        assert iteration == 1
        return _repair_candidate(parent, text=repaired_text)

    def judge_runner(req, candidate):
        judge_calls.append(candidate.candidate_id)
        return (_live_judge(score=0.96, passed=True, issue="", repair=""),)

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=judge_runner,
        repair_runner=repair_runner,
    )

    assert result.attempted is True
    assert result.iteration_count == 1
    assert result.stop_reason == STOP_REPAIR_CANDIDATE_CLEAR
    assert result.final_proof.disposition == EXIT_CLEAR_DRAFT
    assert result.final_selected_candidate_id == "repair_candidate_1"
    assert judge_calls == ["repair_candidate_1"]
    assert result.attempts[0].failed_judge_ids == (JUDGE_EVIDENCE_SUPPORT,)
    assert result.attempts[0].post_repair_scores[0]["passed"] is True


def test_x1d_blocked_result_does_not_trigger_regeneration() -> None:
    request, batch, selected = _request_and_selected()
    initial = run_validation_exit(
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
    assert initial.x1d_result.status == STATUS_X1D_BLOCKED

    def repair_runner(_req, _parent, _failed, _iteration):
        raise AssertionError("blocked X1D must not call Qwen repair")

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=None,
        repair_runner=repair_runner,
    )

    assert result.attempted is False
    assert result.stop_reason == STOP_X1D_BLOCKED_NO_REGENERATION
    assert result.final_proof is initial


def test_x1d_feedback_same_text_repair_stops_without_second_judge() -> None:
    request, batch, selected = _request_and_selected()
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_live_judge(score=0.40, passed=False),),
    )

    def repair_runner(_req, parent, _failed, _iteration):
        return _repair_candidate(parent, text=parent.draft_text)

    def judge_runner(_req, _candidate):
        raise AssertionError("same-text repair must not run X1D again")

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=judge_runner,
        repair_runner=repair_runner,
    )

    assert result.attempted is True
    assert result.stop_reason == STOP_REPAIR_SAME_AS_PARENT
    assert result.iteration_count == 1
    assert result.final_proof is initial


def test_x1d_feedback_repair_reruns_x2_before_second_judge() -> None:
    request, batch, selected = _request_and_selected()
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_live_judge(score=0.40, passed=False),),
    )

    def repair_runner(_req, parent, _failed, _iteration):
        return _repair_candidate(
            parent,
            text="Hi Jane, this repaired draft is missing its required signature?",
        )

    def judge_runner(_req, _candidate):
        raise AssertionError("X2-failed repair must not run X1D again")

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=judge_runner,
        repair_runner=repair_runner,
    )

    assert result.attempted is True
    assert result.stop_reason == STOP_REPAIR_CANDIDATE_X2_FAILED
    assert result.final_proof.x2_result.status == STATUS_X2_BLOCKED
    assert result.final_proof.x1d_result.status == STATUS_X1D_BLOCKED


def test_qwen_repair_candidate_forces_terminal_amit_signature(monkeypatch) -> None:
    request, _batch, selected = _request_and_selected()

    def _fake_repair(**kwargs):
        _ = kwargs
        text = (
            "Hi Jane, AIG's role needs governed agentic AI delivery across "
            "claims and underwriting. Would a quick resume review be useful?"
        )
        return {
            "message_text": text,
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "draft_text": text,
                    "claims_used": list(selected.claims_used),
                    "model_call_ref": "mref:test",
                    "provider_receipt": "prov:test",
                }
            ],
            "model": GENERATOR_MODEL_ID,
            "target_provider": GENERATOR_PROVIDER_ID,
            "generation_temperature": 0.3,
            "top_p": 0.9,
        }

    monkeypatch.setattr(x1d_regen, "generate_judge_feedback_repair_draft", _fake_repair)

    repaired = x1d_regen.qwen_judge_feedback_repair_candidate(
        request,
        selected,
        (_live_judge(score=0.4, passed=False),),
        1,
    )

    assert repaired is not None
    assert repaired.draft_text.endswith("\n\nAmit")


def test_qwen_repair_applies_generic_citi_recruiter_feedback_plan(monkeypatch) -> None:
    request, _batch, selected = _request_and_selected()
    request = replace(
        request,
        target_context={"name": "Dee Morgan", "title": "Recruiter", "company": "Citi"},
        jd_fields={
            "position_name": "Head of AI Strategy - Firmwide AI",
            "job_title": "Head of AI Strategy - Firmwide AI",
            "company": "Citi",
        },
        recipient_class="RECRUITER",
    )
    parent_style_text = (
        "Hi Dee, Citi's Head of AI Strategy role needs governed AI that can survive risk controls. "
        "I designed and operationalized a governed agentic AI platform for regulated enterprise workflows. "
        "That maps to Head of AI Strategy - Firmwide AI. "
        "The bridge is implementation detail: policy-gated retrieval, validation controls, and replayable traces matched to the role scope. "
        "Would a quick screen on that firmwide AI governance fit be useful?\n\nAmit"
    )

    def _fake_repair(**kwargs):
        _ = kwargs
        return {
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "draft_text": parent_style_text,
                    "claims_used": ["sp_agentic_platform"],
                    "model_call_ref": "mref:test",
                    "provider_receipt": "prov:test",
                }
            ],
            "model": GENERATOR_MODEL_ID,
            "target_provider": GENERATOR_PROVIDER_ID,
        }

    monkeypatch.setattr(x1d_regen, "generate_judge_feedback_repair_draft", _fake_repair)

    repaired = x1d_regen.qwen_judge_feedback_repair_candidate(
        request,
        selected,
        (
            _live_judge(
                score=0.81,
                passed=False,
                issue="sentence4_bridge_clause_is_redundant_restatement_not_new_evidence; commercialization_claim_lacks_context_for_regulated_finance_relevance; opening_sentence_generic_role_restatement_adds_no_signal",
                repair="replace_sentence4_bridge_with_one_concrete_citi_regulated_ai_fit_detail",
            ),
        ),
        1,
    )

    assert repaired is not None
    assert repaired.draft_text.startswith("Hi Dee,")
    assert "The bridge is implementation detail" not in repaired.draft_text
    assert "Citi's Head of AI Strategy - Firmwide AI search" in repaired.draft_text
    assert "multi-agent orchestration" in repaired.draft_text
    assert "policy gating" in repaired.draft_text
    assert "financial-services controls" not in repaired.draft_text
    assert "sp_platform_commercialization" in repaired.claims_used
    assert repaired.draft_text.endswith("\n\nAmit")


def test_qwen_repair_applies_generic_neo4j_recruiter_feedback_plan(monkeypatch) -> None:
    request, _batch, selected = _request_and_selected()
    request = replace(
        request,
        target_context={"name": "Clint O'Brien", "title": "Recruiter", "company": "Neo4j"},
        jd_fields={
            "position_name": "VP of Product Management, Agentic AI",
            "job_title": "VP of Product Management, Agentic AI",
            "company": "Neo4j",
        },
        recipient_class="RECRUITER",
    )
    parent_style_text = (
        "Hi Clint, Neo4j's Agentic AI product mandate needs graph-backed context that enterprise agents can trust. "
        "I designed and operationalized a governed agentic AI platform for regulated enterprise workflows. "
        "That maps to VP of Product Management, Agentic AI. "
        "The bridge is implementation detail: policy-gated retrieval, validation controls, and replayable traces matched to the role scope. "
        "Would a quick screen on graph-context reliability for the Agentic AI PM role be useful?\n\nAmit"
    )

    def _fake_repair(**kwargs):
        _ = kwargs
        return {
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "draft_text": parent_style_text,
                    "claims_used": ["sp_agentic_platform"],
                    "model_call_ref": "mref:test",
                    "provider_receipt": "prov:test",
                }
            ],
            "model": GENERATOR_MODEL_ID,
            "target_provider": GENERATOR_PROVIDER_ID,
        }

    monkeypatch.setattr(x1d_regen, "generate_judge_feedback_repair_draft", _fake_repair)

    repaired = x1d_regen.qwen_judge_feedback_repair_candidate(
        request,
        selected,
        (
            _live_judge(
                score=0.82,
                passed=False,
                issue="sentence4_bridge_clause_adds_no_new_evidence; recruiter_recipient_mismatch_for_technical_depth; cta_graph_context_reliability_framing_too_narrow",
                repair="simplify_technical_depth_to_recruiter_appropriate_outcome_language",
            ),
        ),
        1,
    )

    assert repaired is not None
    assert repaired.draft_text.startswith("Hi Clint,")
    assert "The bridge is implementation detail" not in repaired.draft_text
    assert "graph-context reliability" not in repaired.draft_text
    assert "Neo4j's VP of Product Management, Agentic AI search" in repaired.draft_text
    assert "quick recruiter screen on the VP of Product Management, Agentic AI fit" in repaired.draft_text
    assert "sp_platform_commercialization" in repaired.claims_used


def test_w6_unseen_company_repair_uses_generic_evidence_plan(monkeypatch) -> None:
    request, _batch, selected = _request_and_selected()
    request = replace(
        request,
        target_context={"name": "Rae Patel", "title": "Recruiter", "company": "Waystar"},
        jd_fields={
            "position_name": "Director, Agentic Automation",
            "job_title": "Director, Agentic Automation",
            "company": "Waystar",
        },
        recipient_class="RECRUITER",
    )
    borrowed_texture_text = (
        "Hi Rae, Waystar needs AIG Assist style claims and underwriting execution. "
        "The bridge is implementation detail: policy-gated retrieval, validation controls, and replayable traces matched to the role scope. "
        "Would a quick screen on graph-context reliability for the role be useful?\n\nAmit"
    )

    def _fake_repair(**kwargs):
        _ = kwargs
        return {
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "draft_text": borrowed_texture_text,
                    "claims_used": ["sp_agentic_platform"],
                    "model_call_ref": "mref:test",
                    "provider_receipt": "prov:test",
                }
            ],
            "model": GENERATOR_MODEL_ID,
            "target_provider": GENERATOR_PROVIDER_ID,
        }

    monkeypatch.setattr(x1d_regen, "generate_judge_feedback_repair_draft", _fake_repair)

    repaired = x1d_regen.qwen_judge_feedback_repair_candidate(
        request,
        selected,
        (
            _live_judge(
                score=0.80,
                passed=False,
                issue="recruiter_recipient_mismatch_for_technical_depth; bridge_clause_redundant; cta_graph_context_reliability_framing_too_narrow; unsupported_cross_company_texture",
                repair="replace_with_generic_evidence_driven_recruiter_plan",
            ),
        ),
        1,
    )

    assert repaired is not None
    assert repaired.draft_text.startswith("Hi Rae,")
    assert "Waystar's Director, Agentic Automation search" in repaired.draft_text
    assert "multi-agent orchestration" in repaired.draft_text
    assert "policy gating" in repaired.draft_text
    assert "quick recruiter screen on the Director, Agentic Automation fit" in repaired.draft_text
    for borrowed in ("AIG Assist", "claims", "underwriting", "insurance", "graph-context reliability"):
        assert borrowed.lower() not in repaired.draft_text.lower()
    assert "sp_agentic_platform" in repaired.claims_used
    assert "sp_platform_commercialization" in repaired.claims_used
