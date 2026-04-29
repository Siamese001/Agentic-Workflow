"""Tests for agentic_core/L6_observability/semconv/gen_ai.py.

Tier: unit
Plan: .windsurf/plans/three-bucket-otel-view-5db409.md (W3)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

__adg_consumer_mode__ = "inventory"

from agentic_core.L6_observability.semconv.gen_ai import (
    ALIGNMENT_MARKERS,
    ALL_OPERATIONS,
    ALL_PROVIDERS,
    ATTR_AGENT_ID,
    ATTR_AGENT_NAME,
    ATTR_OPERATION_NAME,
    ATTR_PROVIDER_NAME,
    ATTR_TOOL_NAME,
    ATTR_WORKFLOW_NAME,
    OPERATION_CHAT,
    OPERATION_CREATE_AGENT,
    OPERATION_EXECUTE_TOOL,
    OPERATION_INVOKE_AGENT,
    OPERATION_INVOKE_WORKFLOW,
    PROVIDER_ANTHROPIC,
    PROVIDER_OPENAI,
    agent_span_attributes,
    is_aligned_with_genai_semconv,
    model_span_attributes,
    span_name_create_agent,
    span_name_execute_tool,
    span_name_invoke_agent,
    span_name_invoke_workflow,
    tool_span_attributes,
    workflow_span_attributes,
)


class TestAttributeKeysMatchUpstreamSpec:
    """Attribute keys MUST equal the upstream OTel GenAI SIG spec strings."""

    def test_operation_name(self) -> None:
        assert ATTR_OPERATION_NAME == "gen_ai.operation.name"

    def test_provider_name(self) -> None:
        assert ATTR_PROVIDER_NAME == "gen_ai.provider.name"

    def test_agent_name(self) -> None:
        assert ATTR_AGENT_NAME == "gen_ai.agent.name"

    def test_workflow_name(self) -> None:
        assert ATTR_WORKFLOW_NAME == "gen_ai.workflow.name"

    def test_tool_name(self) -> None:
        assert ATTR_TOOL_NAME == "gen_ai.tool.name"


class TestOperationsClosedEnum:
    def test_operations_match_upstream_values(self) -> None:
        assert OPERATION_CREATE_AGENT == "create_agent"
        assert OPERATION_INVOKE_AGENT == "invoke_agent"
        assert OPERATION_INVOKE_WORKFLOW == "invoke_workflow"
        assert OPERATION_EXECUTE_TOOL == "execute_tool"
        assert OPERATION_CHAT == "chat"

    def test_all_operations_includes_canonical_set(self) -> None:
        for op in (
            OPERATION_CREATE_AGENT,
            OPERATION_INVOKE_AGENT,
            OPERATION_INVOKE_WORKFLOW,
            OPERATION_EXECUTE_TOOL,
            OPERATION_CHAT,
        ):
            assert op in ALL_OPERATIONS


class TestProvidersClosedEnum:
    def test_providers_match_upstream_values(self) -> None:
        assert PROVIDER_ANTHROPIC == "anthropic"
        assert PROVIDER_OPENAI == "openai"

    def test_all_providers_includes_canonical_set(self) -> None:
        assert PROVIDER_ANTHROPIC in ALL_PROVIDERS
        assert PROVIDER_OPENAI in ALL_PROVIDERS


class TestSpanNameBuilders:
    def test_create_agent(self) -> None:
        assert span_name_create_agent("Math Tutor") == "create_agent Math Tutor"

    def test_invoke_agent(self) -> None:
        assert span_name_invoke_agent("ResearchBot") == "invoke_agent ResearchBot"

    def test_invoke_workflow(self) -> None:
        assert (
            span_name_invoke_workflow("multi_agent_rag")
            == "invoke_workflow multi_agent_rag"
        )

    def test_execute_tool(self) -> None:
        assert span_name_execute_tool("search") == "execute_tool search"


class TestAgentSpanAttributes:
    def test_invoke_agent_full(self) -> None:
        attrs = agent_span_attributes(
            operation=OPERATION_INVOKE_AGENT,
            agent_name="research",
            agent_id="ag_123",
            provider=PROVIDER_ANTHROPIC,
            request_model="claude-sonnet-4-7",
        )
        assert attrs[ATTR_OPERATION_NAME] == "invoke_agent"
        assert attrs[ATTR_AGENT_NAME] == "research"
        assert attrs[ATTR_PROVIDER_NAME] == "anthropic"

    def test_create_agent_minimal(self) -> None:
        attrs = agent_span_attributes(
            operation=OPERATION_CREATE_AGENT,
            agent_name="x",
        )
        assert attrs[ATTR_OPERATION_NAME] == "create_agent"
        assert ATTR_AGENT_ID not in attrs  # optional, omitted

    def test_empty_strings_dropped(self) -> None:
        attrs = agent_span_attributes(
            operation=OPERATION_INVOKE_AGENT,
            agent_name="x",
            agent_id="",
            provider=None,
        )
        assert ATTR_AGENT_ID not in attrs
        assert ATTR_PROVIDER_NAME not in attrs

    def test_rejects_wrong_operation(self) -> None:
        with pytest.raises(ValueError, match="must be create_agent or invoke_agent"):
            agent_span_attributes(operation="invalid_op", agent_name="x")


class TestWorkflowSpanAttributes:
    def test_minimal(self) -> None:
        attrs = workflow_span_attributes(workflow_name="customer_support_pipeline")
        assert attrs[ATTR_OPERATION_NAME] == "invoke_workflow"
        assert attrs[ATTR_WORKFLOW_NAME] == "customer_support_pipeline"

    def test_with_provider(self) -> None:
        attrs = workflow_span_attributes(
            workflow_name="x",
            provider=PROVIDER_OPENAI,
        )
        assert attrs[ATTR_PROVIDER_NAME] == "openai"


class TestToolSpanAttributes:
    def test_minimal(self) -> None:
        attrs = tool_span_attributes(tool_name="search")
        assert attrs[ATTR_OPERATION_NAME] == "execute_tool"
        assert attrs[ATTR_TOOL_NAME] == "search"

    def test_with_call_id(self) -> None:
        attrs = tool_span_attributes(tool_name="x", tool_call_id="call_42")
        assert attrs["gen_ai.tool.call.id"] == "call_42"


class TestModelSpanAttributes:
    def test_chat(self) -> None:
        attrs = model_span_attributes(
            operation=OPERATION_CHAT,
            provider=PROVIDER_ANTHROPIC,
            request_model="claude-sonnet-4-7",
        )
        assert attrs[ATTR_OPERATION_NAME] == "chat"
        assert attrs[ATTR_PROVIDER_NAME] == "anthropic"
        assert attrs["gen_ai.request.model"] == "claude-sonnet-4-7"

    def test_rejects_non_model_operation(self) -> None:
        with pytest.raises(ValueError, match="chat / generate_content"):
            model_span_attributes(
                operation=OPERATION_INVOKE_AGENT,  # wrong op
                provider="x",
                request_model="y",
            )


class TestAlignmentDetector:
    def test_imports_marker_aligned(self) -> None:
        src = "from agentic_core.L6_observability.semconv import gen_ai\n"
        assert is_aligned_with_genai_semconv(src) is True

    def test_raw_attribute_string_aligned(self) -> None:
        # Even raw strings count as aligned — they ARE the spec.
        src = '''span.set_attribute("gen_ai.operation.name", "invoke_agent")\n'''
        assert is_aligned_with_genai_semconv(src) is True

    def test_unrelated_source_not_aligned(self) -> None:
        src = "import os\nprint('hello')\n"
        assert is_aligned_with_genai_semconv(src) is False

    def test_alignment_markers_nonempty(self) -> None:
        assert len(ALIGNMENT_MARKERS) >= 5
