from __future__ import annotations

from apps_rg.runtime.ibm_narrative_proof_accounting import (
    build_clean_x3_allow_readiness_document,
    classify_certification_class,
    classify_generation_class,
    classify_judge_class,
    classify_proof_class,
    compute_decisive_accounting_label,
)


def test_generation_judge_proof_and_certification_classification_matrix() -> None:
    assert classify_generation_class(
        runtime_generation_status="REAL_LLM",
        offline_contract_stub_active=False,
        test_only_mock_provider=False,
    ) == "real_llm"
    assert classify_generation_class(
        runtime_generation_status="REAL_LLM",
        offline_contract_stub_active=True,
        test_only_mock_provider=False,
    ) == "offline_stub"
    assert classify_judge_class([{"evaluator_mode": "MODEL_BACKED"}]) == "model_backed"
    assert classify_judge_class([{"evaluator_mode": "MOCKED"}, {"evaluator_mode": "BLOCKED_PARSE"}]) == "mixed"
    assert classify_judge_class([]) == "blocked"
    assert classify_proof_class(bundle={}, x3_code="X3_ALLOW", x3_pass=True) == "allow_class"
    assert classify_proof_class(bundle={"proof_scope": "plumbing_only"}, x3_code="", x3_pass=False) == "plumbing_only"
    assert classify_certification_class(
        bundle={"proof_eligible": True},
        x3_code="X3_ALLOW",
        x3_pass=True,
    ) == "runtime_slice_allow"
    assert classify_certification_class(
        bundle={"proof_eligible": False, "proof_scope": "plumbing_only"},
        x3_code="X3_BLOCK",
        x3_pass=False,
    ) == "runtime_slice_review"


def test_decisive_accounting_label_separates_shell_success_from_authorization() -> None:
    base = {
        "command_fault": False,
        "runtime_generation_status": "REAL_LLM",
        "x2_failure_count": 0,
        "x3_code": "X3_ALLOW",
        "x3_pass": True,
        "proceed_to_runtime": True,
        "mock_judges_active": False,
        "proof_eligible": True,
        "preflight_blocked": False,
        "bundle_proof_scope": "runtime_slice",
    }

    assert compute_decisive_accounting_label(**base) == "PASS_ALLOW_CLASS"
    assert compute_decisive_accounting_label(**{**base, "x2_failure_count": 1}) == "FAIL"
    assert compute_decisive_accounting_label(**{**base, "mock_judges_active": True}) == "PASS_PLUMBING_ONLY"
    assert compute_decisive_accounting_label(**{**base, "x3_code": "X3_REVIEW"}) == "PASS_REVIEW_CLASS"
    assert compute_decisive_accounting_label(**{**base, "preflight_blocked": True}) == "BLOCKED"


def test_clean_x3_allow_readiness_document_preserves_boolean_and_count_fields() -> None:
    doc = build_clean_x3_allow_readiness_document(
        section_id="ibm_narrative",
        run_id="run-1",
        clean_allow_possible_at_start=False,
        required_judges=["openai_chatgpt"],
        provider_preflight_status_by_judge={"openai_chatgpt": {"status": "ok"}},
        mocked_judges_present=False,
        blocked_judges_present=True,
        mocked_judge_flags_active=False,
        x2_hard_gates_required=3,
        x2_hard_gates_passed=2,
        x3_code="X3_REVIEW",
        proceed_to_runtime=False,
        product_authorized=False,
        proof_eligible=True,
        proof_scope="runtime_slice",
        decisive_blockers=["blocked_judge"],
        recommended_next_action="configure provider",
        preflight_artifact_written=True,
    )

    assert doc["section_id"] == "ibm_narrative"
    assert doc["x2_hard_gates_required"] == 3
    assert doc["x2_hard_gates_passed"] == 2
    assert doc["blocked_judges_present"] is True
    assert doc["decisive_blockers"] == ["blocked_judge"]
