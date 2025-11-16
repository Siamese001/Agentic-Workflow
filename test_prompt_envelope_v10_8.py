"""
Test Suite — Prompt Envelope v10.8

Responsibilities:
    • Validate construction and metadata handling within the prompt envelope layer.
    • Ensure compatibility between envelopes, templates, and rendering components.
    • Prepare regression coverage for safety annotations and orchestration hooks.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from prompt_envelope import PromptEnvelope
from prompt_renderer import PromptRenderer
from prompt_templates import envelope_from_template


def test_prompt_envelope_serialization():
    envelope = PromptEnvelope(
        framing="Test framing",
        context="Context",
        reasoning="Reasoning",
        instructions="Do it",
        safety_signals="Stay safe",
        output_schema="text",
        metadata={"mode": "demo"},
    )

    data = envelope.to_dict()
    assert data["sections"]["Framing"] == "Test framing"
    assert data["metadata"]["mode"] == "demo"


def test_prompt_renderer_renders_sections_in_order():
    envelope = envelope_from_template(overrides={"framing": "Hello", "context": "World"})
    renderer = PromptRenderer()

    prompt = renderer.render(envelope, runtime_context={"name": "Agent"})

    assert "[Framing]\nHello" in prompt
    assert prompt.strip().split("\n\n")[0].startswith("[Framing]")
