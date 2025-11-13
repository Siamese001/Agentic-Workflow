from src.lic_agentic.safety.bias_auditor import BiasAssessment, audit_bias


class _Inputs:
    def __init__(self, prompt: str):
        self.prompt = prompt


def test_bias_auditor_empty_prompt():
    assessment = audit_bias(_Inputs(""))
    assert isinstance(assessment, BiasAssessment)
    assert assessment.score == 0.0
    assert "no bias" in assessment.notes.lower()


def test_bias_auditor_detects_inclusive_language():
    assessment = audit_bias(_Inputs("We value diversity and inclusion"))
    assert assessment.score == 0.1
    assert "inclusive" in assessment.notes.lower()
