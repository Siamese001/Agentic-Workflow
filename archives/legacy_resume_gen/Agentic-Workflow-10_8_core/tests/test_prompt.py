"""Grouped prompt system tests."""
"""
Test Suite — Prompt Envelope v10.8

Responsibilities:
    • Validate construction and metadata handling within the prompt envelope layer.
    • Ensure compatibility between envelopes, templates, and rendering components.
    • Prepare regression coverage for safety annotations and orchestration hooks.

This test file is scaffolded for Priority 0; implementation comes later.
"""
from prompt_system import PromptEnvelope
from prompt_system import PromptRenderer
from prompt_system import envelope_from_template


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
import pytest

from prompt_system import PromptRenderer
from prompt_system import INSTRUCTIONAL_INJECTION_ALL, PromptSection, SECTION_ORDER


@pytest.fixture
def renderer():
    return PromptRenderer()


def test_render_metadata_sections(renderer):
    renderer.render()
    metadata = renderer.get_last_render_metadata()

    assert set(metadata.keys()) == set(renderer.SECTION_ORDER)
    for section in renderer.SECTION_ORDER:
        assert metadata[section]["section_type"] == section
        assert metadata[section]["instructional_injection_types"] == INSTRUCTIONAL_INJECTION_ALL


def test_render_metadata_contains_all_instructional_injections(renderer):
    renderer.render()
    metadata = renderer.get_last_render_metadata()

    for section in renderer.SECTION_ORDER:
        assert len(metadata[section]["instructional_injection_types"]) == len(INSTRUCTIONAL_INJECTION_ALL)
        assert set(metadata[section]["instructional_injection_types"]) == set(INSTRUCTIONAL_INJECTION_ALL)


def test_render_output_unchanged(renderer):
    rendered = renderer.render()
    expected = (
        "[Framing]\nYou are an orchestrator coordinating deterministic agents.\n\n"
        "[Context]\nUse the provided state to ground your response.\n\n"
        "[Reasoning]\nKeep reasoning minimal; downstream layers handle cognition.\n\n"
        "[Instructions]\nFollow the requested format and stay within scope.\n\n"
        "[Safety Signals]\nRespect safety directives from the gateway.\n\n"
        "[Output Schema]\nReturn plain text content respecting the schema."
    )
    assert rendered == expected


def test_renderer_section_order_matches_taxonomy(renderer):
    expected_order = [section.value for section in SECTION_ORDER]
    assert renderer.SECTION_ORDER == expected_order
import copy

from prompt_system import PromptRenderer
from prompt_utils import validate_sections
from prompt_system import (
    DEFAULT_TEMPLATE_METADATA,
    DEFAULT_TEMPLATE_OUTPUT_INJECTION,
    envelope_from_template,
)
from prompt_system import PromptSection
from prompt_utils import build_prompt_from_plan_and_state
from core.routing import run_model_for_plan
from l3_orchestration import GraphOrchestrator


def test_validate_sections_detects_order_and_missing():
    sections = {
        PromptSection.CONTEXT.value: "context",
        PromptSection.FRAMING.value: "framing",
        PromptSection.REASONING.value: "",
        PromptSection.INSTRUCTIONS.value: "instructions",
    }

    result = validate_sections(sections)

    assert result["valid"] is False
    assert result["missing_sections"] == [
        PromptSection.SAFETY.value,
        PromptSection.OUTPUT_SCHEMA.value,
    ]
    assert set(result["out_of_order"]) == {
        PromptSection.CONTEXT.value,
        PromptSection.FRAMING.value,
    }
    assert result["empty_sections"] == [PromptSection.REASONING.value]


def test_validate_sections_accepts_exact_ordering():
    sections = envelope_from_template().to_sections()

    result = validate_sections(sections)

    assert result == {
        "valid": True,
        "missing_sections": [],
        "out_of_order": [],
        "empty_sections": [],
    }


def test_prompt_metadata_includes_taxonomy_version_and_stability_markers():
    envelope = envelope_from_template()
    data = envelope.to_dict()

    assert data["metadata"].get("taxonomy_version") == "v5"
    assert data["metadata"].get("taxonomy", {}).get("sections") == [
        section.value for section in PromptSection
    ]

    template_metadata = copy.deepcopy(DEFAULT_TEMPLATE_METADATA)
    assert template_metadata.get("stable_ordering") is True


def test_renderer_metadata_preserves_injection_and_adds_taxonomy_validation():
    renderer = PromptRenderer()
    renderer.render()

    metadata = renderer.get_last_render_metadata()

    assert metadata.get("taxonomy_validation", {}).get("valid") is True
    assert metadata.get("injection_reasoning", {}).get("reason_then_answer") is True
    assert metadata.get("injection_output") == DEFAULT_TEMPLATE_OUTPUT_INJECTION
    assert metadata.get("injection_tooling", {}).get("model_switch_awareness") is True


def test_prompt_builder_renders_prompt_with_framing():
    plan = {"objective": "demo", "mode": "graph", "routing": {}}
    state = {"summary": "context", "messages": [{"role": "user", "content": "hello"}]}

    rendered = build_prompt_from_plan_and_state(plan, state)

    assert rendered["prompt"].startswith("[Framing]")


def test_run_model_for_plan_updates_routing_and_prompt():
    plan = {
        "objective": "demo-objective",
        "mode": "graph",
        "routing": {"complexity": "medium", "latency_target": 1.5, "cost_ceiling": 0.01},
        "safety_metadata": {"sensitivity": "low"},
    }
    state = {"messages": [{"role": "user", "content": "hi"}]}

    result = run_model_for_plan(plan, state)

    assert plan.get("routing", {}).get("selected_model")
    assert plan.get("routing", {}).get("endpoint")
    assert "completion" in result.get("model_output", {})


def test_orchestrator_state_contains_model_output():
    orchestrator = GraphOrchestrator()
    outcome = orchestrator.orchestrate({"objective": "integration"})

    assert "model_output" in outcome.state
    assert outcome.plan.get("routing", {}).get("selected_model")
from prompt_system import (
    DEFAULT_INJECTION_PATTERNS,
    INSTRUCTIONAL_INJECTION_ALL,
    InjectionType,
    InstructionalInjection,
    PromptSection,
    SECTION_ORDER,
)


def test_prompt_section_taxonomy_count():
    assert len(PromptSection) == 6


def test_injection_type_count():
    assert len(InjectionType) == 4
    assert DEFAULT_INJECTION_PATTERNS == [
        InjectionType.OVERRIDE_SYSTEM.value,
        InjectionType.IGNORE_PREVIOUS.value,
        InjectionType.DISABLE_SAFETY.value,
        InjectionType.RUN_ARBITRARY_CODE.value,
    ]


def test_instructional_injection_count():
    assert len(InstructionalInjection) == 30


EXPECTED_SECTION_ORDER = [
    PromptSection.FRAMING,
    PromptSection.CONTEXT,
    PromptSection.REASONING,
    PromptSection.INSTRUCTIONS,
    PromptSection.SAFETY,
    PromptSection.OUTPUT_SCHEMA,
]


def test_section_order_matches_expected():
    assert SECTION_ORDER == EXPECTED_SECTION_ORDER


def test_instructional_injection_all_contains_all_values():
    assert len(INSTRUCTIONAL_INJECTION_ALL) == 30
    assert set(INSTRUCTIONAL_INJECTION_ALL) == {member.value for member in InstructionalInjection}
import copy

from prompt_system import PromptRenderer
from prompt_system import INSTRUCTIONAL_INJECTION_ALL, PromptSection
from prompt_utils import (
    get_instructional_injection_types,
    get_prompt_taxonomy,
    get_section_names,
    get_section_types,
)


def test_get_section_names_reports_all_sections():
    renderer = PromptRenderer()
    renderer.render()

    section_names = get_section_names(renderer)

    assert section_names == renderer.SECTION_ORDER
    assert set(section_names) == {section.value for section in PromptSection}


def test_get_section_types_returns_taxonomy_mapping():
    renderer = PromptRenderer()
    renderer.render()

    section_types = get_section_types(renderer)

    assert set(section_types.keys()) == set(renderer.SECTION_ORDER)
    for name, section_type in section_types.items():
        assert name == section_type


def test_get_instructional_injection_types_returns_all_entries():
    renderer = PromptRenderer()
    renderer.render()

    injection_types = get_instructional_injection_types(renderer)

    assert len(injection_types) == len(INSTRUCTIONAL_INJECTION_ALL)
    assert set(injection_types) == set(INSTRUCTIONAL_INJECTION_ALL)


def test_get_prompt_taxonomy_returns_full_metadata():
    renderer = PromptRenderer()
    renderer.render()

    expected_metadata = renderer.get_last_render_metadata()
    taxonomy = get_prompt_taxonomy(renderer)

    assert taxonomy == expected_metadata


def test_prompt_views_are_read_only():
    renderer = PromptRenderer()
    renderer.render()

    original_metadata = copy.deepcopy(renderer.get_last_render_metadata())

    _ = get_section_names(renderer)
    _ = get_section_types(renderer)
    _ = get_instructional_injection_types(renderer)
    _ = get_prompt_taxonomy(renderer)

    assert renderer.get_last_render_metadata() == original_metadata
