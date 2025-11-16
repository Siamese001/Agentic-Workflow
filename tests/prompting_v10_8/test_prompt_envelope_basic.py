def test_envelope_shapes():
    from prompting_v10_8 import PromptEnvelope

    env = PromptEnvelope(
        framing="System",
        context={},
        reasoning="hidden",
        instructions="do x",
        tool_context={},
        safety_context={},
        output_schema={},
    )
    assert env.framing and env.instructions
