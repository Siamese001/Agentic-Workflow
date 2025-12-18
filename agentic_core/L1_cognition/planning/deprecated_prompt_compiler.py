import logging

_logger = logging.getLogger(__name__)
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.cms.schemas import PromptSchema  # DE...
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.cms.compiler import compile_prompt  #...


def test_compile_prompt_produces_string() -> None:
    """Test that compile_prompt produces a string output."""
    SCHEMA = PromptSchema(
        id="test.prompt",
        ROLE="system",
        OBJECTIVE="Test objective",
        INSTRUCTIONS="Do the thing.",
        EXAMPLES=[{"input": "x", "output": "y"}],
        safety_tags=["safety"],
        allowed_tools=["tool1"],
        VERSION="1.0.0",
    )

    RENDERED = compile_prompt(schema, {"layer": "L2"})
    assert isinstance(rendered, str)
    assert "OBJECTIVE" in rendered
    assert "INSTRUCTIONS" in rendered
