import pytest
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.agents import PIISanitizerAgent, QAAgent  # INVALID: Cannot import from path with hyphens


@pytest.mark.data
def test_structure_preserved_after_sanitization() -> None:
    inp = {"email": "a@b.com", "name": "John"}
    out = PIISanitizerAgent().sanitize(inp)
    assert set(inp.keys()) == set(out.keys())


@pytest.mark.data
def test_analyzer_adds_confidence_field() -> None:
    out = QAAgent().evaluate("sample")
    assert "confidence" in out


@pytest.mark.xfail(
    reason="Add 13 transformation tests on Analyzer, Enricher, Validator, Aggregator",
    strict=False,
)
def test_placeholder() -> None:
    pytest.xfail(
        "Add 13 transformation tests on Analyzer, Enricher, Validator, Aggregator"
    )
