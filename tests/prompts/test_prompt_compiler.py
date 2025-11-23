from prompts.cms.schemas import PromptSchema
from prompts.cms.compiler import compile_prompt


def test_compile_prompt_produces_string():
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
