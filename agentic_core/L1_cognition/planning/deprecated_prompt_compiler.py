import logging

# from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.cms.schemas import PromptSchema  # DE...
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.cms.compiler import compile_prompt  #...

def test_compile_prompt_produces_string() -> None:
    """Test that compile_prompt produces a string output."""
    schema = PromptSchema(
        id="test.prompt",
        role="system",
        objective="Test objective",
        instructions="Do the thing.",
        examples=[{"input": "x", "output": "y"}],
        safety_tags=["safety"],
        allowed_tools=["tool1"],
        version="1.0.0",
    )

    rendered = compile_prompt(schema, {"layer": "L2"})
    assert isinstance(rendered, str)
    assert "OBJECTIVE" in rendered
    assert "INSTRUCTIONS" in rendered
