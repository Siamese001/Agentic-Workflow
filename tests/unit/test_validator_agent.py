from src.lic_agentic.agents.k7_validator_agent import ValidationResult, ValidatorAgent


def test_validator_passes_with_complete_sections():
    draft = """Subject: Hello\n\nHello there and thanks for your time\n[artifact_id:123] Proof point\nCTA: Shall we chat tomorrow?\nBest regards,\nLIC Outreach Bot"""
    agent = ValidatorAgent()
    verdict = agent.check(
        draft,
        route_decision=None,
        pii_map={},
        artifacts={"123": "Proof point"},
        token_count=len(draft.split()),
        latency_ms=250,
    )
    assert isinstance(verdict, ValidationResult)
    assert verdict.passed
    assert verdict.final_draft.endswith("LIC Outreach Bot")
    assert agent.metrics.latency_samples_ms == [250]
    assert ValidatorAgent().metrics.latency_samples_ms == []  # ensure per-instance tracking


def test_validator_flags_missing_placeholders():
    draft = """Subject: Hi\n\nHello\n[artifact_id:123] token\nCTA: Are you available next week?\nBest regards,\nLIC Outreach Bot"""
    verdict = ValidatorAgent().check(
        draft,
        route_decision=None,
        pii_map={"<PII_1>": "alice@example.com"},
        artifacts={"123": "token"},
    )
    assert not verdict.passed
    assert any("Placeholder <PII_1>" in reason for reason in verdict.reasons)


def test_default_retry_returns_none_when_no_changes_required():
    agent = ValidatorAgent()
    draft = """Subject: Ready\n\nHello there\n[artifact_id:123] win\nCTA: Talk soon?\nBest regards,\nLIC Outreach Bot"""
    qa_result = agent.qa_validator.validate(draft, {"123": "win"})
    assert qa_result.ok
    assert agent._default_retry(qa_result, draft, {"123": "win"}) is None


def test_custom_retry_function_is_used():
    agent = ValidatorAgent(max_retries=1)
    draft = "Subject: Hello\n\nHello there"

    def _retry(_, current_draft, current_artifacts):
        return (
            current_draft + "\n[artifact_id:123] detail\nCTA: Meet soon?\nBest regards,\nLIC Outreach Bot",
            {"123": "detail"},
        )

    verdict = agent.check(
        draft,
        route_decision=None,
        pii_map={},
        artifacts={},
        retry_fn=_retry,
    )
    assert verdict.passed
    assert "[artifact_id:123]" in verdict.final_draft


def test_helper_methods_identify_signature_and_body():
    agent = ValidatorAgent()
    lines = [
        "Subject: Hello",
        "",
        "Hello there",
        "[artifact_id:1] detail",
        "CTA: Meet?",
        "Best regards,",
        "LIC Outreach Bot",
    ]
    assert agent._locate_signature_line(lines) == 5
    assert agent._first_body_index(lines) == 2


def test_default_retry_adds_signature_when_missing():
    agent = ValidatorAgent()
    draft = """Subject: Hello\n\nHello there\n[artifact_id:1] detail\nCTA: Meet soon?"""
    qa_result = agent.qa_validator.validate(draft, {"1": "detail"})
    assert not qa_result.ok
    assert "signature" in qa_result.missing_sections
    updated, _ = agent._default_retry(qa_result, draft, {"1": "detail"})
    assert "LIC Outreach Bot" in updated


def test_default_retry_inserts_missing_artifacts():
    agent = ValidatorAgent()
    draft = """Subject: Hello\n\nHello there\nCTA: Meet soon?\nBest regards,\nLIC Outreach Bot"""
    qa_result = agent.qa_validator.validate(draft, {"aid": "detail"})
    assert "value_wedge" in qa_result.missing_sections
    updated, _ = agent._default_retry(qa_result, draft, {"aid": "detail"})
    assert "[artifact_id:aid]" in updated


def test_default_retry_handles_absent_cta_and_signature():
    agent = ValidatorAgent()
    draft = """Subject: Hello\n\nHello there\n[artifact_id:1] detail"""
    qa_result = agent.qa_validator.validate(draft, {"1": "detail"})
    assert "cta" in qa_result.missing_sections
    assert "signature" in qa_result.missing_sections
    updated, _ = agent._default_retry(qa_result, draft, {"1": "detail"})
    assert "CTA:" in updated
    assert "LIC Outreach Bot" in updated


def test_validator_passes_with_pii_placeholders_present():
    agent = ValidatorAgent()
    draft = """Subject: Hello\n\nHello <PII_1>\n[artifact_id:1] detail\nCTA: Meet soon?\nBest regards,\nLIC Outreach Bot"""
    verdict = agent.check(
        draft,
        route_decision=None,
        pii_map={"<PII_1>": "alice@example.com"},
        artifacts={"1": "detail"},
    )
    assert verdict.passed


def test_validator_respects_max_retries_zero():
    agent = ValidatorAgent(max_retries=0)
    draft = "Subject: Hello\n\nHello there"
    verdict = agent.check(draft, route_decision=None, pii_map={}, artifacts={})
    assert not verdict.passed


def test_validator_metrics_capture_failure_breakdown():
    agent = ValidatorAgent()
    draft = "Subject: Hello\n\nHello there"
    agent.check(draft, route_decision=None, pii_map={}, artifacts={})
    breakdown = agent.metrics.failure_breakdown()
    assert breakdown
    assert agent.metrics.retry_attempts >= 1
