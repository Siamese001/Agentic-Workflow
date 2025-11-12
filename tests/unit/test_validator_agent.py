from src.lic_agentic.agents.k7_validator_agent import ValidationResult, ValidatorAgent


def test_validator_passes_with_subject_and_artifact():
    draft = "Subject: Hello\nBody with [artifact_id:123] token"
    verdict = ValidatorAgent().check(draft, route_decision=None, pii_map={})
    assert isinstance(verdict, ValidationResult)
    assert verdict.passed
    assert verdict.reasons == ()


def test_validator_flags_missing_placeholders():
    draft = "Subject: Hi\nBody with [artifact_id:123] token"
    verdict = ValidatorAgent().check(draft, route_decision=None, pii_map={"<PII_1>": "alice@example.com"})
    assert not verdict.passed
    assert any("Placeholder <PII_1>" in reason for reason in verdict.reasons)
