import copy

from prompt_renderer import PromptRenderer
from prompt_schema_validator import validate_sections
from prompt_templates import (
    DEFAULT_TEMPLATE_METADATA,
    DEFAULT_TEMPLATE_OUTPUT_INJECTION,
    envelope_from_template,
)
from prompt_taxonomy import PromptSection
from prompt_builder import build_prompt_from_plan_and_state
from client_strategy import run_model_for_plan
from l3_graph_orchestrator import GraphOrchestrator


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
