from injection_output_profiles import DEFAULT_SAFETY_OUTPUT_PROFILE
from l5_safety_gateway import SafetyGateway
from prompt_envelope import PromptEnvelope
from prompt_renderer import PromptRenderer
from prompt_templates import (
    DEFAULT_TEMPLATE_METADATA,
    DEFAULT_TEMPLATE_OUTPUT_INJECTION,
    envelope_from_template,
)


def test_safety_gateway_includes_injection_safety_metadata():
    gateway = SafetyGateway()
    patch = gateway.evaluate({"content": "safe content"})

    safety_metadata = patch.get("safety_gateway", {}).get("injection_safety", {})

    assert safety_metadata.get("prompt_shield") is DEFAULT_SAFETY_OUTPUT_PROFILE.prompt_shield
    assert (
        safety_metadata.get("data_instruction_separation")
        is DEFAULT_SAFETY_OUTPUT_PROFILE.data_instruction_separation
    )
    assert (
        safety_metadata.get("constitutional_guardrails_enabled")
        is DEFAULT_SAFETY_OUTPUT_PROFILE.constitutional_guardrails_enabled
    )
    assert (
        safety_metadata.get("delegation_guardrails_enabled")
        is DEFAULT_SAFETY_OUTPUT_PROFILE.delegation_guardrails_enabled
    )
    assert (
        safety_metadata.get("adversarial_mode_enabled")
        is DEFAULT_SAFETY_OUTPUT_PROFILE.adversarial_mode_enabled
    )

    assert patch.get("safety_gateway", {}).get("status") == "allowed"


def test_template_and_envelope_expose_output_injection_metadata():
    envelope = envelope_from_template()

    assert envelope.metadata.get("output_injection") == DEFAULT_TEMPLATE_OUTPUT_INJECTION

    env_metadata = envelope.to_dict().get("metadata", {})
    assert env_metadata.get("injection", {}).get("output") == DEFAULT_TEMPLATE_OUTPUT_INJECTION


def test_renderer_exposes_output_injection_metadata():
    renderer = PromptRenderer()
    renderer.render()

    render_metadata = renderer.get_render_metadata()

    assert render_metadata.get("injection_output") == DEFAULT_TEMPLATE_OUTPUT_INJECTION
    for section in renderer.SECTION_ORDER:
        assert section in render_metadata


def test_template_metadata_stability_contracts_intact():
    assert DEFAULT_TEMPLATE_METADATA.get("output_injection") == DEFAULT_TEMPLATE_OUTPUT_INJECTION
