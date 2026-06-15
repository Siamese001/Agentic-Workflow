from __future__ import annotations

from apps_rg.runtime.judges import competencies_x1d


def test_build_prompt_marks_companion_context_read_only_and_compacts_ledger() -> None:
    prompt = competencies_x1d._build_prompt(
        '[{"label":"Cloud","terms":["AWS"]}]',
        [{"fact_id": "F1", "claim_text": "Scaled cloud controls."}],
        "Executive summary companion text.",
    )

    assert "READ_ONLY_GENERATED_SECTIONS" in prompt
    assert "Executive summary companion text." in prompt
    assert "companion_context_used_as_proof must remain false" in prompt
    assert '"fact_id":"F1"' in prompt
    assert "Return JSON only" in prompt


def test_run_competencies_judges_mocked_provider_contract() -> None:
    outputs = competencies_x1d.run_competencies_judges(
        competencies=[{"label": "Cloud", "terms": ["AWS", "Kubernetes"]}],
        claim_ledger=[{"fact_id": "F1", "claim_text": "Scaled cloud controls."}],
        judge_keys=["openai_chatgpt"],
        companion_context="",
        mode="mocked",
    )

    assert len(outputs) == 1
    out = outputs[0]
    assert out.judge_id == "x1d_openai_chatgpt_competencies"
    assert out.provider_key == "openai_chatgpt"
    assert out.evaluator_mode == "MOCKED"
    assert out.provider_status == "MOCKED"
    assert out.rubric_version == competencies_x1d.JUDGE_RUBRIC_VERSION
    assert out.pass_ is True
    assert out.findings == ["MOCKED plumbing judge. Not valid for X3_ALLOW."]


def test_unknown_competencies_provider_blocks_with_section_specific_judge_id() -> None:
    outputs = competencies_x1d.run_competencies_judges(
        competencies=[],
        claim_ledger=[],
        judge_keys=["missing_provider"],
        mode="mocked",
    )

    assert len(outputs) == 1
    out = outputs[0]
    assert out.judge_id == "x1d_missing_provider_competencies"
    assert out.provider_key == "missing_provider"
    assert out.provider_blocked is True
    assert out.provider_available is False
    assert out.provider_status == "BLOCKED_PROVIDER_UNAVAILABLE"
    assert "Unknown judge provider key" in str(out.exact_provider_error)
