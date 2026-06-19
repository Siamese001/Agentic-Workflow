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


def test_competencies_rubric_mentions_ta_screen_and_ai_authenticity() -> None:
    rubric = competencies_x1d.COMPETENCIES_RUBRIC.lower()
    assert "head of talent acquisition" in rubric
    assert "ai authenticity" in rubric
    assert "buzzword soup" in rubric
    assert "anti-ai filters" in rubric
    assert "no em dashes" in rubric


def test_run_competencies_judges_uses_pinned_gemini_preview_model(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_credentials(provider_key: str, environ):
        del provider_key, environ
        return "fake-google-key", ["GOOGLE_API_KEY"]

    def fake_call_gemini(api_key: str, prompt: str, model: str, input_hash: str, provider_key: str, **kwargs):
        del api_key, prompt, input_hash, kwargs
        captured["provider_key"] = provider_key
        captured["model"] = model
        return competencies_x1d._mocked(provider_key, "input-hash")

    monkeypatch.setattr(competencies_x1d, "resolve_x1d_provider_credentials", fake_credentials)
    monkeypatch.setattr(competencies_x1d, "_call_gemini", fake_call_gemini)

    outputs = competencies_x1d.run_competencies_judges(
        competencies=[{"category_label": "Cloud", "terms": [{"text": "AWS", "source_fact_id": "bul_001", "source_fact_ids": ["bul_001"]}]}],
        claim_ledger=[{"claim_text": "Scaled cloud controls.", "source_fact_ids": ["bul_001"]}],
        judge_keys=["gemini_pro"],
        companion_context="",
        mode="blocked_if_unavailable",
    )

    assert captured["provider_key"] == "gemini_pro"
    assert captured["model"] == "gemini-3.1-pro-preview"
    assert len(outputs) == 1
    out = outputs[0]
    assert out.provider_key == "gemini_pro"
    assert out.advisory_only is True
    assert out.proof_eligible_judge is False


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
