

def test_missing_subject_fails():
    validator = QAValidator()
    draft = "Hello\n\nBody without subject"
    result = validator.validate(draft, {"123": "summary"})
    assert not result.ok
    assert "subject" in " ".join(result.missing_sections)


def test_complete_message_passes():
    validator = QAValidator()
    draft = "Subject: Update\n\nHello there\n[artifact_id:123] summary\nCTA: Can we connect?\nBest regards,\nLIC Outreach Bot"
    result = validator.validate(draft, {"123": "summary"})
    assert result.ok


def test_unknown_and_missing_artifacts_are_reported():
    validator = QAValidator()
    draft = "Subject: Proof\n\nHello\n[artifact_id:known] data\n[artifact_id:unknown] extra\nCTA: Talk soon?\nBest regards,\nLIC Outreach Bot"
    artifacts = {"known": "data", "missing": "oops"}
    result = validator.validate(draft, artifacts)
    assert not result.ok
    assert "missing" in " ".join(result.reasons)
    assert "unknown" in " ".join(result.reasons)


def test_long_body_triggers_style_violation():
    validator = QAValidator(max_body_chars=20)
    draft = "Subject: Length\n\nHello there\n[artifact_id:1] short\nCTA: Meet?\nBest regards,\nLIC Outreach Bot"
    result = validator.validate(draft, {"1": "short"})
    assert not result.ok
    assert any("character" in reason for reason in result.reasons)


def test_qa_package_exports_symbols():
    import importlib

    module = importlib.import_module("src.lic_agentic.qa")
    assert "QAValidator" in module.__all__