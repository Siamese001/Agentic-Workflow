import json
from dataclasses import replace
from pathlib import Path

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
    STOP_REPAIR_BUDGET_EXHAUSTED,
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
    assert result.attempts[0].x1d_repair_effective is True
    assert result.attempts[0].x1d_repair_resolved_issue_ids == ("generic_draft",)
    assert result.attempts[0].x1d_repair_unresolved_issue_ids == ()
    assert result.attempts[0].repair_candidate_sanitization_passed is True
    assert result.to_packet()["x1d_repair_effective"] is True
    assert result.to_packet()["x1d_repair_resolved_issue_ids"] == ["generic_draft"]
    assert result.to_packet()["repair_candidate_sanitization_passed"] is True


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
    assert result.attempts[0].x1d_repair_effective is False
    assert result.attempts[0].x1d_repair_unresolved_issue_ids == ("generic_draft",)


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
    assert result.attempts[0].repair_candidate_sanitization_passed is False


def test_w3_sc3_repair_loop_can_use_second_iteration() -> None:
    request, batch, selected = _request_and_selected()
    request = replace(
        request,
        reasoning_policy=replace(
            request.reasoning_policy,
            sc_level="SC-3",
            repair_budget=2,
        ),
    )
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_live_judge(score=0.40, passed=False),),
    )
    repaired_texts = {
        1: (
            "Hi Jane, AIG's Director, AI Platforms role needs governed agentic AI "
            "delivery. I designed and operationalized a governed agentic AI platform "
            "for regulated enterprise workflows. Would a quick resume review for "
            "JR-12345 be useful?\n\nAmit"
        ),
        2: (
            "Hi Jane, AIG's Director, AI Platforms role needs governed agentic AI "
            "delivery with validation controls and replayable traces. I designed "
            "and operationalized a governed agentic AI platform for regulated "
            "enterprise workflows. Would a quick resume review for JR-12345 be useful?\n\nAmit"
        ),
    }
    repair_iterations: list[int] = []
    judge_calls = 0

    def repair_runner(_req, parent, _failed, iteration):
        repair_iterations.append(iteration)
        return _repair_candidate(
            parent,
            text=repaired_texts[iteration],
            candidate_id=f"repair_candidate_{iteration}",
        )

    def judge_runner(_req, _candidate):
        nonlocal judge_calls
        judge_calls += 1
        if judge_calls == 1:
            return (_live_judge(score=0.50, passed=False),)
        return (_live_judge(score=0.96, passed=True, issue="", repair=""),)

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=judge_runner,
        repair_runner=repair_runner,
    )

    assert repair_iterations == [1, 2]
    assert result.iteration_count == 2
    assert result.stop_reason == STOP_REPAIR_CANDIDATE_CLEAR
    assert result.final_selected_candidate_id == "repair_candidate_2"


def test_w3_sc2_single_judge_repair_stays_one_iteration() -> None:
    request, batch, selected = _request_and_selected()
    assert request.reasoning_policy.sc_level == "SC-2"
    assert request.reasoning_policy.repair_budget == 1
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_live_judge(score=0.40, passed=False),),
    )
    repair_iterations: list[int] = []

    def repair_runner(_req, parent, _failed, iteration):
        repair_iterations.append(iteration)
        return _repair_candidate(
            parent,
            text=(
                "Hi Jane, AIG's Director, AI Platforms role needs governed agentic AI "
                "delivery. I designed and operationalized a governed agentic AI platform "
                "for regulated enterprise workflows. Would a quick resume review for "
                "JR-12345 be useful?\n\nAmit"
            ),
        )

    def judge_runner(_req, _candidate):
        return (_live_judge(score=0.50, passed=False),)

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=judge_runner,
        repair_runner=repair_runner,
    )

    assert repair_iterations == [1]
    assert result.iteration_count == 1
    assert result.stop_reason == STOP_REPAIR_BUDGET_EXHAUSTED


def test_w5_sc2_effective_sanitized_repair_gets_one_followup_attempt() -> None:
    request, batch, selected = _request_and_selected()
    assert request.reasoning_policy.sc_level == "SC-2"
    assert request.reasoning_policy.repair_budget == 1
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(
            _live_judge(
                score=0.40,
                passed=False,
                issue="old_issue",
                repair="fix_old_issue",
            ),
        ),
    )
    repaired_texts = {
        1: (
            "Hi Jane, AIG's Director, AI Platforms role needs governed agentic AI "
            "delivery with validation controls. I designed and operationalized a "
            "governed agentic AI platform for regulated enterprise workflows. Would "
            "a quick resume review for JR-12345 be useful?\n\nAmit"
        ),
        2: (
            "Hi Jane, AIG's Director, AI Platforms role needs governed agentic AI "
            "delivery with validation controls and replayable traces. I designed "
            "and operationalized a governed agentic AI platform for regulated "
            "enterprise workflows. Would a quick resume review for JR-12345 be useful?\n\nAmit"
        ),
    }
    repair_iterations: list[int] = []
    judge_calls = 0

    def repair_runner(_req, parent, _failed, iteration):
        repair_iterations.append(iteration)
        return _repair_candidate(
            parent,
            text=repaired_texts[iteration],
            candidate_id=f"repair_candidate_{iteration}",
        )

    def judge_runner(_req, _candidate):
        nonlocal judge_calls
        judge_calls += 1
        if judge_calls == 1:
            return (
                _live_judge(
                    score=0.50,
                    passed=False,
                    issue="new_issue",
                    repair="fix_new_issue",
                ),
            )
        return (_live_judge(score=0.96, passed=True, issue="", repair=""),)

    result = run_x1d_judge_feedback_regeneration(
        request=request,
        batch=batch,
        selected_candidate_id=selected.candidate_id,
        initial_proof=initial,
        x1d_judge_runner=judge_runner,
        repair_runner=repair_runner,
    )

    assert repair_iterations == [1, 2]
    assert result.iteration_count == 2
    assert result.stop_reason == STOP_REPAIR_CANDIDATE_CLEAR
    assert result.final_selected_candidate_id == "repair_candidate_2"
    assert result.attempts[0].x1d_repair_effective is True
    assert result.attempts[0].repair_candidate_sanitization_passed is True
    assert result.attempts[0].x1d_repair_resolved_issue_ids == ("old_issue",)
    assert result.attempts[0].x1d_repair_unresolved_issue_ids == ("new_issue",)


def test_w3_multi_judge_failure_can_use_two_iteration_window() -> None:
    request, batch, selected = _request_and_selected()
    initial = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_live_judge(score=0.40, passed=False),),
    )
    multi_judge_proof = replace(
        initial,
        x1d_result=replace(
            initial.x1d_result,
            judge_results=(
                _live_judge(score=0.40, passed=False),
                _live_judge(
                    judge_id="linkedin_tone_non_generic_x1d",
                    score=0.40,
                    passed=False,
                ),
            ),
        ),
    )

    assert x1d_regen._max_repair_iterations(
        request,
        explicit=None,
        initial_proof=multi_judge_proof,
    ) == 2


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
    assert "quick recruiter screen on the role fit" in repaired.draft_text
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
    assert "quick recruiter screen on the role fit" in repaired.draft_text
    for borrowed in ("AIG Assist", "claims", "underwriting", "insurance", "graph-context reliability"):
        assert borrowed.lower() not in repaired.draft_text.lower()
    assert "sp_agentic_platform" in repaired.claims_used
    assert "sp_platform_commercialization" in repaired.claims_used


def test_w2_clean_rebuild_replaces_patchy_duplicate_signature_repair(monkeypatch) -> None:
    request, _batch, selected = _request_and_selected()
    request = replace(
        request,
        target_context={"name": "Jim Young", "title": "Global Chief Data Officer", "company": "AIG"},
        jd_fields={
            "position_name": "VP, Global Head of Agentic AI Solutions",
            "job_title": "VP, Global Head of Agentic AI Solutions",
            "company": "AIG",
        },
        recipient_class="C_LEVEL",
    )
    patchy_repair = (
        "Hi Jim, Given your mandate as the Global Chief Data Officer, ensuring reliable "
        "and auditable AI systems is critical. I've designed and operationalized a "
        "governed agentic AI platform for regulated workflows. Could we discuss how "
        "these insights could enhance AIG's claims and underwriting processes? Amit "
        "That maps to the mandate, where the operating question is how to make "
        "agentic decisions auditable across regulated insurance workflows.\n\nAmit"
    )

    def _fake_repair(**kwargs):
        _ = kwargs
        return {
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "draft_text": patchy_repair,
                    "claims_used": ["sp_agentic_platform", "sp_runtime_reliability"],
                    "model_call_ref": "mref:test",
                    "provider_receipt": "prov:test",
                }
            ],
            "model": GENERATOR_MODEL_ID,
            "target_provider": GENERATOR_PROVIDER_ID,
        }

    monkeypatch.setattr(x1d_regen, "generate_judge_feedback_repair_draft", _fake_repair)
    monkeypatch.setattr(
        x1d_regen,
        "_allowed_claim_ids",
        lambda _request: {
            "sp_agentic_platform",
            "sp_runtime_reliability",
            "sp_platform_commercialization",
        },
    )

    repaired = x1d_regen.qwen_judge_feedback_repair_candidate(
        request,
        selected,
        (
            _live_judge(
                judge_id="ceo_attention_originality_x1d",
                score=0.61,
                passed=False,
                issue="duplicate_closing_signature_and_fragmented_structure; sp_platform_commercialization_claim_omitted_from_draft_despite_approval; generic_phrasing_without_specific_aig_trigger_hook",
                repair="remove_duplicate_amit_signature_and_restructure_as_single_coherent_message; incorporate_22m_revenue_or_margin_outcome_from_sp_platform_commercialization_to_anchor_executive_value",
            ),
            _live_judge(
                judge_id="ceo_evidence_overclaim_risk_x1d",
                score=0.71,
                passed=False,
                issue="duplicate_sign_off_amit_appears_twice_structural_error; second_paragraph_reads_as_unedited_model_reasoning_not_polished_outreach",
                repair="surface_commercial_outcome_metric_from_sp_platform_commercialization_to_substantiate_value_claim",
            ),
        ),
        1,
    )

    assert repaired is not None
    assert repaired.draft_text.count("Amit") == 1
    assert repaired.draft_text.endswith("\n\nAmit")
    assert "That maps to the mandate" not in repaired.draft_text
    # Graph-SSOT for metrics: the judge asked to "incorporate_22m_revenue", but $22M is the
    # apps_lic-authored fabrication the corpus dropped. The rebuild surfaces the graph-grounded
    # $10M and must never reinstate the fabricated number.
    assert "$10M" in repaired.draft_text
    assert "$22M" not in repaired.draft_text
    assert "sp_platform_commercialization" in repaired.claims_used
    assert repaired.word_count <= request.length_budget.max_words
    assert repaired.char_count <= request.length_budget.hard_cap_chars


def test_w2_clean_rebuild_prevents_same_as_parent_repair(monkeypatch) -> None:
    request, _batch, selected = _request_and_selected()
    request = replace(
        request,
        target_context={"name": "Regina Gilligan", "title": "Talent Acquisition Manager", "company": "AIG"},
        jd_fields={
            "position_name": "VP, Global Head of Agentic AI Solutions",
            "job_title": "VP, Global Head of Agentic AI Solutions",
            "company": "AIG",
        },
        recipient_class="SENIOR_TA",
    )

    def _fake_repair(**kwargs):
        _ = kwargs
        return {
            "selected_candidate_id": "repair_candidate_1",
            "candidates": [
                {
                    "candidate_id": "repair_candidate_1",
                    "draft_text": selected.draft_text,
                    "claims_used": list(selected.claims_used),
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
                issue="sp_runtime_reliability_claim_not_surfaced_in_draft; repetitive_phrasing_replayable_traces_validation_controls_appears_twice",
                repair="surface_runtime_reliability_evidence_or_replace_with_stronger_mapped_claim; remove_duplicate_policy_gated_retrieval_validation_controls_replayable_traces_phrase",
            ),
        ),
        1,
    )

    assert repaired is not None
    assert x1d_regen._message_fingerprint(repaired.draft_text) != x1d_regen._message_fingerprint(selected.draft_text)
    assert "validation controls" in repaired.draft_text
    assert "replayable traces" in repaired.draft_text
    assert repaired.draft_text.count("Amit") == 1


def test_w5_clean_rebuild_varies_for_new_citi_trigger_and_cta_feedback() -> None:
    request, _batch, _selected = _request_and_selected()
    request = replace(
        request,
        target_context={
            "name": "Brian Saluzzo",
            "title": "Chief Information Officer",
            "company": "Citi",
            "company_trigger": (
                "Citi is expanding firmwide AI strategy under senior AI leadership, "
                "with responsible AI, Citi Sky, and global AI adoption signals."
            ),
        },
        jd_fields={
            "position_name": "Head of AI Strategy - Firmwide AI",
            "job_title": "Head of AI Strategy - Firmwide AI",
            "company": "Citi",
        },
        recipient_class="C_LEVEL",
        message_type="trigger_based_insight",
    )
    intents = (
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="ceo_attention_originality_x1d",
            issue_id="opening_sentence_too_dense_and_generic",
            required_repair="make_opening_trigger_specific",
            intent="opening_rewrite",
            required_claim_ids=(),
        ),
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="ceo_attention_originality_x1d",
            issue_id="missing_citi_specific_trigger_hook",
            required_repair="add_citi_specific_trigger_hook",
            intent="trigger_hook",
            required_claim_ids=(),
        ),
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="ceo_attention_originality_x1d",
            issue_id="cta_weak_role_fit_framing",
            required_repair="make_cta_more_executive_specific",
            intent="cta",
            required_claim_ids=(),
        ),
    )

    rebuilt = x1d_regen._clean_rebuild_repair_text(
        request=request,
        normalized_intents=intents,
    )
    subject = x1d_regen._clean_rebuild_subject_line(
        existing="Citi Head of AI Strategy fit",
        request=request,
        normalized_intents=intents,
    )

    # Runtime-derived invariant: the rebuild incorporates the runtime company and
    # the provided company_trigger (which mentions "Citi Sky"), the jd role, a
    # graph-grounded proof, and an executive CTA. No engine-hardcoded Citi copy.
    assert "Citi" in rebuilt
    assert "Citi Sky" in rebuilt  # sourced from the runtime company_trigger
    assert "Head of AI Strategy - Firmwide AI" in rebuilt
    assert "governed agentic AI platform for regulated enterprise workflows" in rebuilt
    assert "Would 15 minutes on Citi's agentic AI operating model be useful?" in rebuilt
    # Subject reflects runtime company + role + executive framing.
    assert subject.startswith("Citi Head of AI Strategy - Firmwide AI")
    assert "governance" in subject.lower()


def test_w5_clean_rebuild_surfaces_cloud_ai_claim_without_fabricated_metric(monkeypatch) -> None:
    request, _batch, _selected = _request_and_selected()
    request = replace(
        request,
        target_context={
            "name": "Firat Tekiner",
            "title": "Director of Product Management",
            "company": "Neo4j",
            "company_trigger": (
                "Neo4j is hiring for Agentic AI product leadership and positioning graph "
                "intelligence as context infrastructure for enterprise agents."
            ),
        },
        jd_fields={
            "position_name": "VP of Product Management, Agentic AI",
            "job_title": "VP of Product Management, Agentic AI",
            "company": "Neo4j",
        },
        recipient_class="HIRING_MANAGER",
        message_type="trigger_based_insight",
    )
    allowed_claim_ids = {
        "sp_agentic_platform",
        "sp_runtime_reliability",
        "sp_cloud_ai_transformation",
    }
    monkeypatch.setattr(
        x1d_regen,
        "_allowed_claim_ids",
        lambda _request: allowed_claim_ids,
    )
    intents = (
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="linkedin_tone_non_generic_x1d",
            issue_id="no_quantified_outcomes_or_metrics_to_anchor_claims",
            required_repair="add_one_concrete_outcome_metric",
            intent="claim_surface",
            required_claim_ids=("sp_cloud_ai_transformation",),
        ),
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="linkedin_tone_non_generic_x1d",
            issue_id="trigger_insight_is_generic_graph_reliability_not_recipient_specific",
            required_repair="make_trigger_recipient_specific",
            intent="trigger_hook",
            required_claim_ids=(),
        ),
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="linkedin_tone_non_generic_x1d",
            issue_id="cta_repeats_role_title_verbatim_twice",
            required_repair="remove_repeated_role_title_from_cta",
            intent="cta",
            required_claim_ids=(),
        ),
    )

    rebuilt = x1d_regen._clean_rebuild_repair_text(
        request=request,
        normalized_intents=intents,
    )
    claims = x1d_regen._claims_from_repaired_text(
        rebuilt,
        existing=(),
        allowed_claim_ids=allowed_claim_ids,
    )

    # Graph-SSOT for metrics: the cloud-AI skills approve NO metric phrase, so the rebuild
    # surfaces the cloud-AI CLAIM but must NOT fabricate a "$30M portfolio" number (the prior
    # apps_lic-authored metric the corpus dropped). Claim surfaced, zero fabricated metric.
    assert "cloud-native AI and analytics platforms" in rebuilt
    assert "$30M" not in rebuilt
    assert "sp_cloud_ai_transformation" in claims
    # Runtime-derived trigger: the opening hook is sourced from the provided
    # company_trigger (graph intelligence as context infrastructure), not from an
    # engine-hardcoded Neo4j phrase.
    assert "Neo4j" in rebuilt
    assert "graph intelligence as context infrastructure for enterprise agents" in rebuilt
    assert "VP of Product Management, Agentic AI" in rebuilt
    assert "VP Product, Agentic AI search be useful" not in rebuilt


def _retry16_c_level_fixture() -> dict:
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "x1d_repair_loop_retry16_c_level_red_rows.json"
    )
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def _retry16_intents(row: dict) -> tuple[x1d_regen.X1DNormalizedRepairIntent, ...]:
    return tuple(
        x1d_regen.X1DNormalizedRepairIntent(
            judge_id="ceo_attention_originality_x1d",
            issue_id=str(issue),
            required_repair=str(repair),
            intent=x1d_regen._repair_intent_for_feedback(f"{issue} {repair}".lower()),
            required_claim_ids=x1d_regen._required_claim_ids_for_feedback(
                f"{issue} {repair}".lower()
            ),
        )
        for issue, repair in zip(row["unresolved_issue_ids"], row["required_repairs"])
    )


def _c_level_request(*, company: str, name: str, title: str) -> object:
    request, _batch, _selected = _request_and_selected()
    if company == "AIG":
        return replace(
            request,
            target_context={
                "name": name,
                "title": title,
                "company": "AIG",
                "company_context": (
                    "AIG enterprise AI operating context for regulated insurance, claims, "
                    "underwriting, governance, and GenAI standards."
                ),
                "company_trigger": (
                    "AIG's VP Global Head of Agentic AI Solutions role reports into the "
                    "Global Chief Data Officer and spans agentic AI operating-model work."
                ),
                "role_ownership_signal": (
                    "Global Chief Data Officer tied to AIG data, AI, and agentic AI platform context."
                ),
            },
            jd_fields={
                "position_name": "VP, Global Head of Agentic AI Solutions",
                "company": "AIG",
            },
            recipient_class="C_LEVEL",
            message_type="trigger_based_insight",
        )
    return replace(
        request,
        target_context={
            "name": name,
            "title": title,
            "company": "Citi",
            "company_context": (
                "Citi firmwide AI strategy context across regulated finance, risk controls, "
                "responsible AI, data governance, and platform execution."
            ),
            "company_trigger": (
                "Citi is expanding firmwide AI strategy under senior AI leadership, with "
                "responsible AI, Citi Sky, and global AI adoption signals."
            ),
            "role_ownership_signal": (
                "Chief Information Officer at Citi shaping global technology services and "
                "AI-enabled firmwide technology work."
            ),
        },
        jd_fields={
            "position_name": "Head of AI Strategy - Firmwide AI",
            "company": "Citi",
        },
        recipient_class="C_LEVEL",
        message_type="trigger_based_insight",
    )


def test_w5_retry16_c_level_issue_families_are_classified() -> None:
    rows = {row["row_id"]: row for row in _retry16_c_level_fixture()["red_rows"]}

    aig_families = x1d_regen._c_level_editorial_issue_families(
        " ".join(rows["aig_jim_young"]["unresolved_issue_ids"])
    )
    assert {"subject_specificity", "proof_bridge", "cta_executive_sharpness"} <= aig_families

    citi_families = x1d_regen._c_level_editorial_issue_families(
        " ".join(rows["citi_brian_saluzzo"]["unresolved_issue_ids"])
    )
    assert {"trigger_insight", "credential_dump", "cta_executive_sharpness"} <= citi_families
    assert rows["citi_brian_saluzzo"]["repair_stop_reason"] == "repair_same_as_parent"


def test_w5_retry16_c_level_composer_replaces_bad_aig_copy(monkeypatch) -> None:
    row = {
        item["row_id"]: item for item in _retry16_c_level_fixture()["red_rows"]
    }["aig_jim_young"]
    request = _c_level_request(
        company="AIG",
        name="Jim Young",
        title="Global Chief Data Officer",
    )
    allowed_claim_ids = {
        "sp_agentic_platform",
        "sp_platform_commercialization",
        "sp_runtime_reliability",
    }
    monkeypatch.setattr(x1d_regen, "_allowed_claim_ids", lambda _request: allowed_claim_ids)
    intents = _retry16_intents(row)

    old_lint = x1d_regen._c_level_editorial_copy_lint_issues(
        text=row["final_draft_text"],
        subject_line=row["final_subject_line"],
        request=request,
    )
    rebuilt = x1d_regen._clean_rebuild_repair_text(
        request=request,
        normalized_intents=intents,
    )
    subject = x1d_regen._clean_rebuild_subject_line(
        existing=row["final_subject_line"],
        request=request,
        normalized_intents=intents,
    )
    claims = x1d_regen._claims_from_repaired_text(
        rebuilt,
        existing=(),
        allowed_claim_ids=allowed_claim_ids,
    )
    new_lint = x1d_regen._c_level_editorial_copy_lint_issues(
        text=rebuilt,
        subject_line=subject,
        request=request,
    )

    # The bad parent copy still trips the (now company-generic) copy lint via its
    # banned executive-cliche phrases; the runtime-derived rebuild is clean.
    assert any("banned_phrase" in issue for issue in old_lint)
    assert new_lint == ()
    # Subject is runtime-derived from company + role + an executive framing word.
    assert subject == "AIG VP, Global Head of Agentic AI Solutions governance loop"
    # Rebuild incorporates the runtime company, the runtime trigger, a graph-grounded
    # $10M proof, and an executive CTA — no engine-hardcoded AIG copy.
    assert rebuilt.startswith("Hi Jim, the AIG VP, Global Head of Agentic AI Solutions signal")
    assert "Global Chief Data Officer" in rebuilt  # from the runtime company_trigger
    assert "$10M in net-new revenue" in rebuilt
    assert "Would 15 minutes on AIG's agentic AI operating model be useful?" in rebuilt
    assert "which AIG workflow" not in rebuilt
    assert "brief executive exchange" not in rebuilt
    assert {"sp_agentic_platform", "sp_platform_commercialization", "sp_runtime_reliability"} <= set(claims)


def test_w5_retry16_c_level_composer_replaces_same_parent_citi_copy(monkeypatch) -> None:
    row = {
        item["row_id"]: item for item in _retry16_c_level_fixture()["red_rows"]
    }["citi_brian_saluzzo"]
    request = _c_level_request(
        company="Citi",
        name="Brian Saluzzo",
        title="Chief Information Officer",
    )
    allowed_claim_ids = {
        "sp_agentic_platform",
        "sp_platform_commercialization",
        "sp_quant_governance_foundation",
    }
    monkeypatch.setattr(x1d_regen, "_allowed_claim_ids", lambda _request: allowed_claim_ids)
    intents = _retry16_intents(row)

    old_lint = x1d_regen._c_level_editorial_copy_lint_issues(
        text=row["final_draft_text"],
        subject_line=row["final_subject_line"],
        request=request,
    )
    rebuilt = x1d_regen._clean_rebuild_repair_text(
        request=request,
        normalized_intents=intents,
    )
    subject = x1d_regen._clean_rebuild_subject_line(
        existing=row["final_subject_line"],
        request=request,
        normalized_intents=intents,
    )
    claims = x1d_regen._claims_from_repaired_text(
        rebuilt,
        existing=(),
        allowed_claim_ids=allowed_claim_ids,
    )
    new_lint = x1d_regen._c_level_editorial_copy_lint_issues(
        text=rebuilt,
        subject_line=subject,
        request=request,
    )

    # The bad parent copy still trips the (now company-generic) copy lint via its
    # banned phrases (e.g. "pressure-test"); the runtime-derived rebuild is clean.
    assert any("pressure-test" in issue for issue in old_lint)
    assert new_lint == ()
    # Subject is runtime-derived from company + role + an executive framing word.
    assert subject == "Citi Head of AI Strategy - Firmwide AI governance loop"
    # Rebuild incorporates the runtime company + trigger (which mentions "Citi Sky"),
    # the jd role, a graph-grounded $10M proof, and an executive CTA. None of the old
    # engine-hardcoded Citi copy or banned executive cliches survive.
    assert rebuilt.startswith("Hi Brian, the Citi Head of AI Strategy - Firmwide AI signal")
    assert "Citi Sky" in rebuilt  # sourced from the runtime company_trigger
    assert "$10M in net-new revenue" in rebuilt
    assert "Would 15 minutes on Citi's agentic AI operating model be useful?" in rebuilt
    assert "pressure-test" not in rebuilt
    assert "The governance foundation is" not in rebuilt
    assert "My fit is" not in rebuilt
    assert {
        "sp_agentic_platform",
        "sp_platform_commercialization",
    } <= set(claims)


def test_w5_retry17_aig_second_stage_variant_changes_same_parent(monkeypatch) -> None:
    request = _c_level_request(
        company="AIG",
        name="Jim Young",
        title="Global Chief Data Officer",
    )
    allowed_claim_ids = {
        "sp_agentic_platform",
        "sp_platform_commercialization",
        "sp_runtime_reliability",
    }
    monkeypatch.setattr(x1d_regen, "_allowed_claim_ids", lambda _request: allowed_claim_ids)
    parent_text = (
        "Hi Jim, AIG's GCDO trigger is concrete: agentic AI for claims and underwriting "
        "needs release evidence before regulated decisions. The value bridge is insurance "
        "workflow reuse, backed by productized agentic AI services tied to $22M revenue "
        "and 20% margin expansion. My relevant work adds governed agentic AI platforms "
        "with policy gates, evaluation traces, rollback paths, and reusable service patterns. "
        "Would 15 minutes on evidence-backed release controls for AIG's agentic AI operating "
        "model be useful?\n\nAmit"
    )
    row = {
        "unresolved_issue_ids": [
            "value_bridge_lacks_insurance_specificity",
            "cta_too_generic_for_c_level",
            "trigger_framing_restates_jd_not_novel_insight",
        ],
        "required_repairs": [
            "add_insurance_workflow_specificity_to_value_bridge",
            "sharpen_cta_to_name_concrete_decision_or_tradeoff_for_gcdo",
            "reframe_trigger_as_external_signal_not_jd_restatement",
        ],
    }
    intents = _retry16_intents(row)

    rebuilt = x1d_regen._clean_rebuild_repair_text(
        request=request,
        normalized_intents=intents,
    )
    subject = x1d_regen._clean_rebuild_subject_line(
        existing="AIG VP, Global Head of Agentic AI Solutions governance loop",
        request=request,
        normalized_intents=intents,
    )
    lint = x1d_regen._c_level_editorial_copy_lint_issues(
        text=rebuilt,
        subject_line=subject,
        request=request,
    )

    # The second-stage rebuild diverges from the (fabricated-$22M) parent and is
    # entirely runtime-derived: company + role + trigger + graph-grounded proof.
    assert x1d_regen._message_fingerprint(rebuilt) != x1d_regen._message_fingerprint(parent_text)
    # "tradeoff" feedback drives the runtime company + role tradeoff subject framing.
    assert subject == "AIG VP, Global Head of Agentic AI Solutions operating-model tradeoff"
    assert rebuilt.startswith("Hi Jim, the AIG VP, Global Head of Agentic AI Solutions signal")
    assert "Global Chief Data Officer" in rebuilt  # from the runtime company_trigger
    assert "governed agentic AI platform for regulated enterprise workflows" in rebuilt
    assert "Would 15 minutes on AIG's agentic AI operating model be useful?" in rebuilt
    # The fabricated $22M / 20% margin parent metrics must never reappear.
    assert "$22M" not in rebuilt
    assert "20% margin" not in rebuilt
    assert lint == ()


def test_w5_retry17_citi_second_stage_variant_drops_medium_quant_claim(monkeypatch) -> None:
    request = _c_level_request(
        company="Citi",
        name="Brian Saluzzo",
        title="Chief Information Officer",
    )
    allowed_claim_ids = {
        "sp_agentic_platform",
        "sp_platform_commercialization",
        "sp_quant_governance_foundation",
    }
    monkeypatch.setattr(x1d_regen, "_allowed_claim_ids", lambda _request: allowed_claim_ids)
    parent_text = (
        "Hi Brian, Citi Sky creates a CIO-specific operating tension: banker-facing AI can scale "
        "only if model controls, data lineage, and support ownership travel with each workflow. "
        "My relevant work is governed agentic AI platform delivery where policy gates and "
        "evaluation evidence made AI usage auditable in production. The quant-governance proof "
        "is forward risk control: decision workflows that expose ownership and audit evidence "
        "before scale. Commercially, the same platform discipline supported productized agentic "
        "AI services tied to $22M revenue and 20% margin expansion. Would 15 minutes on the "
        "Citi Sky governance loop be useful?\n\nAmit"
    )
    row = {
        "unresolved_issue_ids": [
            "quant_governance_claim_is_medium_strength_but_framed_as_forward_risk_proof_without_direct_evidence",
            "opening_tension_framing_is_competent_but_not_sufficiently_differentiated_for_cio_at_global_bank",
            "cta_is_generic_15_minute_ask_without_specific_hook_tied_to_citi_sky_trigger",
            "quant_governance_claim_is_medium_strength_but_presented_as_forward_risk_proof_without_hedging",
            "citi_sky_trigger_referenced_but_no_specific_citi_sky_detail_anchors_the_insight",
        ],
        "required_repairs": [
            "sharpen_cta_to_reference_specific_citi_sky_governance_gap_or_observable_signal_rather_than_generic_15_min_ask",
            "replace_quant_governance_sentence_with_concrete_audit_evidence_example_or_drop_to_avoid_medium_claim_overreach",
            "differentiate_opening_tension_with_citi_specific_detail_such_as_regulated_workflow_scale_or_responsible_ai_mandate",
            "hedge_or_remove_forward_risk_control_framing_for_sp_quant_governance_foundation_given_medium_claim_strength",
            "add_one_specific_citi_sky_or_firmwide_ai_detail_to_differentiate_trigger_from_generic_ai_governance_pitch",
        ],
    }
    intents = _retry16_intents(row)

    rebuilt = x1d_regen._clean_rebuild_repair_text(
        request=request,
        normalized_intents=intents,
    )
    subject = x1d_regen._clean_rebuild_subject_line(
        existing="Citi Sky CIO governance loop",
        request=request,
        normalized_intents=intents,
    )
    claims = x1d_regen._claims_from_repaired_text(
        rebuilt,
        existing=(),
        allowed_claim_ids=allowed_claim_ids,
    )
    lint = x1d_regen._c_level_editorial_copy_lint_issues(
        text=rebuilt,
        subject_line=subject,
        request=request,
    )

    # Runtime-derived rebuild diverges from the (fabricated-$22M) parent and is
    # built from company + role + trigger + a graph-grounded proof.
    assert x1d_regen._message_fingerprint(rebuilt) != x1d_regen._message_fingerprint(parent_text)
    # "governance_gap"/"observable_signal" feedback drives the handoff framing on the
    # runtime company + role subject.
    assert subject == "Citi Head of AI Strategy - Firmwide AI governance handoff"
    assert rebuilt.startswith("Hi Brian, the Citi Head of AI Strategy - Firmwide AI signal")
    assert "Citi Sky" in rebuilt  # sourced from the runtime company_trigger
    assert "Would 15 minutes on Citi's agentic AI operating model be useful?" in rebuilt
    # The medium-strength quant-governance claim is dropped, and the fabricated
    # parent metrics never reappear.
    assert "quant-governance" not in rebuilt
    assert "forward risk control" not in rebuilt
    assert "$22M" not in rebuilt
    assert "20% margin" not in rebuilt
    assert "sp_quant_governance_foundation" not in {
        claim_id for intent in intents for claim_id in intent.required_claim_ids
    }
    assert "sp_quant_governance_foundation" not in claims
    assert lint == ()
