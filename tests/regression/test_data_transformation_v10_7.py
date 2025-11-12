import pytest
from agents import PIISanitizerAgent, QAAgent


@pytest.mark.data
def test_structure_preserved_after_sanitization():
    inp = {"email": "a@b.com", "name": "John"}
    out = PIISanitizerAgent().sanitize(inp)
    assert set(inp.keys()) == set(out.keys())


@pytest.mark.data
def test_analyzer_adds_confidence_field():
    out = QAAgent().evaluate("sample")
    assert "confidence" in out


@pytest.mark.skip("Add 13 transformation tests on Analyzer, Enricher, Validator, Aggregator")
def test_placeholder():
    pass
