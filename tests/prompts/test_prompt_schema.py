from prompts.cms.schemas import PromptSchema, validate_prompt


def test_validate_prompt_happy_path():
    data = {
        "id": "test.prompt",
        "role": "system",
        "objective": "Test objective",
        "instructions": "Do the thing.",
        "examples": [],
        "allowed_tools": [],
        "safety_tags": ["safety"],
        "version": "1.0.0",
    }
    schema = validate_prompt(data)
    assert isinstance(schema, PromptSchema)
    assert schema.id == "test.prompt"


def test_validate_prompt_rejects_empty_fields():
    bad = {
        "id": "",
        "role": "system",
        "objective": "",
        "instructions": "",
    }
    try:
        validate_prompt(bad)
        assert False, "Expected ValueError for invalid schema"
    except ValueError:
        pass
