"""ValidatorAgent behavior tests."""



class StubQAValidator:
    def __init__(self, responses):
        self._responses = iter(responses)

    def validate(self, draft, artifacts, pii_placeholders):
        return next(self._responses)


def test_validator_passes_with_subject_and_artifact():
    draft = """Subject: Hello\n\nHello there,\nBody with [artifact_id:123] token\nCTA: Let me know if next week works.\nBest regards,\nLIC Outreach Bot"""
    verdict = ValidatorAgent().check(
        draft, route_decision=None, pii_map={}, artifacts={"123": "token"}
    )
    assert isinstance(verdict, ValidationResult)
    assert verdict.passed
    assert verdict.reasons == ()


def test_validator_flags_missing_placeholders():
    draft = """Subject: Hi\n\nHello there,\nBody with [artifact_id:123] token\nCTA: Can we connect?\nBest regards,\nLIC Outreach Bot"""
    verdict = ValidatorAgent().check(
        draft,
        route_decision=None,
        pii_map={"<PII_1>": "alice@example.com"},
        artifacts={"123": "token"},
    )
    assert not verdict.passed
    assert any("Placeholder <PII_1>" in reason for reason in verdict.reasons)


def test_validator_retry_inserts_cta_before_signature():
    draft = """Subject: Hi\n\nHello there,\nBest regards,\nLIC Outreach Bot"""
    verdict = ValidatorAgent(max_retries=1).check(
        draft,
        route_decision=None,
        pii_map={},
        artifacts={"aid": "Grounded"},
    )
    assert verdict.passed
    assert "CTA:" in verdict.final_draft
    assert verdict.final_draft.strip().endswith("LIC Outreach Bot")


def test_validator_without_artifacts_flags_missing_value_wedge():
    draft = """Subject: Hi\n\nHello there,\nCTA: Talk soon?\nBest regards,\nLIC Outreach Bot"""
    verdict = ValidatorAgent().check(draft, route_decision=None, pii_map={}, artifacts={})
    assert not verdict.passed
    assert any("evidence" in reason.lower() for reason in verdict.reasons)


def test_validator_adds_signature_when_missing():
    draft = """Subject: Hi\n\nHello there,\n[artifact_id:aid] detail"""
    verdict = ValidatorAgent(max_retries=1).check(
        draft,
        route_decision=None,
        pii_map={},
        artifacts={"aid": "detail"},
    )
    assert verdict.passed
    assert verdict.final_draft.strip().endswith("LIC Outreach Bot")


def test_validator_inserts_missing_artifacts():
    draft = """Subject: Hi\n\nHello there,\nCTA: Talk soon?\nBest regards,\nLIC Outreach Bot"""
    verdict = ValidatorAgent(max_retries=1).check(
        draft,
        route_decision=None,
        pii_map={},
        artifacts={"aid": "Summary"},
    )
    assert "[artifact_id:aid]" in verdict.final_draft


def test_validator_retry_repairs_all_missing_sections():
    failing = QAResult(
        ok=False,
        reasons=("Missing subject",),
        missing_sections=("subject", "opener", "value_wedge", "cta", "signature"),
        missing_artifacts=("aid",),
    )
    passing = QAResult(ok=True, reasons=())
    agent = ValidatorAgent(qa_validator=StubQAValidator([failing, passing]), max_retries=2)
    verdict = agent.check("", route_decision=None, pii_map={}, artifacts={"aid": "Summary"})
    assert verdict.passed
    assert verdict.attempts == 2
    assert verdict.final_draft.startswith("Subject: Quick idea for you")
    assert "Hello there," in verdict.final_draft
    assert "CTA:" in verdict.final_draft
    assert verdict.final_draft.strip().endswith("LIC Outreach Bot")
    assert "[artifact_id:aid]" in verdict.final_draft


def test_find_signature_index_detects_keywords():
    agent = ValidatorAgent()
    lines = ["Body line", "Best regards,"]
    assert agent._find_signature_index(lines) == 1
    assert agent._find_signature_index(["Body line"]) is None


def test_estimate_token_drift_caps_value():
    agent = ValidatorAgent()
    assert agent._estimate_token_drift(100) == 0
    assert agent._estimate_token_drift(300) == 0.1