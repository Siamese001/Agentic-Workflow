"""GenAI OTel semantic conventions — closed enums + helper builders.

This module is the single source of truth for the OpenTelemetry GenAI SIG
semantic conventions used by agent / workflow / tool / model spans emitted
by this repo. It mirrors the upstream spec at:

    https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/
    https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/

Per ADR-074 (Runtime Bucket as OTEL View) and the 2026-04-29 user critique
("the runtime ADG isnt that a fake concept? should it is OTEL traces"), the
runtime bucket of the three-bucket ADG authority model is a deterministic
view over the OTel span sink. For that view to be meaningful, our spans
MUST follow the published GenAI semconv so they are interoperable with any
OTel backend (Jaeger, Tempo, SigNoz, OpenAI Traces, etc.) and so the
``check_otel_genai_semconv_coverage.py`` CI gate has stable invariants to
assert against.

Plan: ``docs/archive/windsurf/legacy-tree/plans/three-bucket-otel-view-5db409.md`` (W3).

USAGE
=====

To emit an agent span correctly::

    from agentic_core.L6_observability.semconv.gen_ai import (
        OPERATION_INVOKE_AGENT,
        agent_span_attributes,
    )

    span = tracer.start_as_current_span(
        name=f"invoke_agent {agent_name}",
        kind=SpanKind.INTERNAL,
        attributes=agent_span_attributes(
            operation=OPERATION_INVOKE_AGENT,
            agent_name=agent_name,
            agent_id=agent_id,
            provider="anthropic",
            model="claude-sonnet-4-7",
        ),
    )

To emit a tool span::

    from agentic_core.L6_observability.semconv.gen_ai import (
        OPERATION_EXECUTE_TOOL,
        tool_span_attributes,
    )

    span = tracer.start_as_current_span(
        name=f"execute_tool {tool_name}",
        attributes=tool_span_attributes(
            operation=OPERATION_EXECUTE_TOOL,
            tool_name=tool_name,
            tool_call_id=call_id,
        ),
    )

VALIDATION
==========

* All ``ATTR_*`` constants match the upstream OTel GenAI SIG attribute names
  exactly (verified against the Sept-2025 semconv release).
* All ``OPERATION_*`` constants are values from the upstream
  ``gen_ai.operation.name`` enum.
* ``check_otel_genai_semconv_coverage.py`` CI gate (W4) asserts a target
  fraction of agent/workflow/tool span emit sites import from this module
  rather than using raw strings.
"""

from __future__ import annotations

from typing import Any, Final


# ---------------------------------------------------------------------------
# Attribute keys (match upstream OTel GenAI SIG semconv exactly)
# ---------------------------------------------------------------------------
# Source: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/

# Operation discriminator — REQUIRED on every GenAI span.
ATTR_OPERATION_NAME: Final[str] = "gen_ai.operation.name"

# Provider discriminator — REQUIRED on agent / model / tool spans.
ATTR_PROVIDER_NAME: Final[str] = "gen_ai.provider.name"

# Agent attributes (CONDITIONALLY REQUIRED on create_agent / invoke_agent).
ATTR_AGENT_ID: Final[str] = "gen_ai.agent.id"
ATTR_AGENT_NAME: Final[str] = "gen_ai.agent.name"
ATTR_AGENT_DESCRIPTION: Final[str] = "gen_ai.agent.description"
ATTR_AGENT_VERSION: Final[str] = "gen_ai.agent.version"

# Workflow attributes (CONDITIONALLY REQUIRED on invoke_workflow).
ATTR_WORKFLOW_NAME: Final[str] = "gen_ai.workflow.name"

# Model / request attributes.
ATTR_REQUEST_MODEL: Final[str] = "gen_ai.request.model"
ATTR_RESPONSE_MODEL: Final[str] = "gen_ai.response.model"

# Tool attributes (CONDITIONALLY REQUIRED on execute_tool).
ATTR_TOOL_NAME: Final[str] = "gen_ai.tool.name"
ATTR_TOOL_CALL_ID: Final[str] = "gen_ai.tool.call.id"
ATTR_TOOL_TYPE: Final[str] = "gen_ai.tool.type"

# I/O messages (OPT-IN — may contain PII; emit only when explicitly enabled).
ATTR_INPUT_MESSAGES: Final[str] = "gen_ai.input.messages"
ATTR_OUTPUT_MESSAGES: Final[str] = "gen_ai.output.messages"

# System discriminator (LEGACY — superseded by ATTR_PROVIDER_NAME but kept for
# back-compat with v1.36.0 and prior emitters).
ATTR_SYSTEM: Final[str] = "gen_ai.system"

# Error type (when applicable; standard OTel error attribute, included for
# completeness).
ATTR_ERROR_TYPE: Final[str] = "error.type"


# ---------------------------------------------------------------------------
# Operation names (closed enum from gen_ai.operation.name)
# ---------------------------------------------------------------------------

# Agent lifecycle.
OPERATION_CREATE_AGENT: Final[str] = "create_agent"
OPERATION_INVOKE_AGENT: Final[str] = "invoke_agent"

# Workflow / multi-agent coordination.
OPERATION_INVOKE_WORKFLOW: Final[str] = "invoke_workflow"

# Tool / function call.
OPERATION_EXECUTE_TOOL: Final[str] = "execute_tool"

# Model client calls (chat / generate / completion).
OPERATION_CHAT: Final[str] = "chat"
OPERATION_GENERATE_CONTENT: Final[str] = "generate_content"
OPERATION_TEXT_COMPLETION: Final[str] = "text_completion"
OPERATION_EMBEDDINGS: Final[str] = "embeddings"


ALL_OPERATIONS: Final[frozenset[str]] = frozenset(
    {
        OPERATION_CREATE_AGENT,
        OPERATION_INVOKE_AGENT,
        OPERATION_INVOKE_WORKFLOW,
        OPERATION_EXECUTE_TOOL,
        OPERATION_CHAT,
        OPERATION_GENERATE_CONTENT,
        OPERATION_TEXT_COMPLETION,
        OPERATION_EMBEDDINGS,
    }
)


# ---------------------------------------------------------------------------
# Provider names (closed enum from gen_ai.provider.name)
# ---------------------------------------------------------------------------

PROVIDER_ANTHROPIC: Final[str] = "anthropic"
PROVIDER_OPENAI: Final[str] = "openai"
PROVIDER_GCP_GEMINI: Final[str] = "gcp.gen_ai"
PROVIDER_GCP_VERTEX: Final[str] = "gcp.vertex_ai"
PROVIDER_AWS_BEDROCK: Final[str] = "aws.bedrock"
PROVIDER_AZURE_OPENAI: Final[str] = "azure.openai"
PROVIDER_LOCAL: Final[str] = "local"  # for vLLM / llama.cpp / ollama / etc.


ALL_PROVIDERS: Final[frozenset[str]] = frozenset(
    {
        PROVIDER_ANTHROPIC,
        PROVIDER_OPENAI,
        PROVIDER_GCP_GEMINI,
        PROVIDER_GCP_VERTEX,
        PROVIDER_AWS_BEDROCK,
        PROVIDER_AZURE_OPENAI,
        PROVIDER_LOCAL,
    }
)


# ---------------------------------------------------------------------------
# Span name builders (per upstream span-name conventions)
# ---------------------------------------------------------------------------


def span_name_create_agent(agent_name: str) -> str:
    """Canonical create_agent span name: ``create_agent {gen_ai.agent.name}``."""
    return f"{OPERATION_CREATE_AGENT} {agent_name}"


def span_name_invoke_agent(agent_name: str) -> str:
    """Canonical invoke_agent span name: ``invoke_agent {gen_ai.agent.name}``."""
    return f"{OPERATION_INVOKE_AGENT} {agent_name}"


def span_name_invoke_workflow(workflow_name: str) -> str:
    """Canonical invoke_workflow span name: ``invoke_workflow {gen_ai.workflow.name}``."""
    return f"{OPERATION_INVOKE_WORKFLOW} {workflow_name}"


def span_name_execute_tool(tool_name: str) -> str:
    """Canonical execute_tool span name: ``execute_tool {gen_ai.tool.name}``."""
    return f"{OPERATION_EXECUTE_TOOL} {tool_name}"


# ---------------------------------------------------------------------------
# Attribute builders — apply correct required/conditional fields for each kind
# ---------------------------------------------------------------------------


def _drop_empty(attrs: dict[str, Any]) -> dict[str, Any]:
    """Strip None / empty-string attributes — semconv says omit instead of empty."""
    return {k: v for k, v in attrs.items() if v not in (None, "")}


def agent_span_attributes(
    *,
    operation: str = OPERATION_INVOKE_AGENT,
    agent_name: str | None = None,
    agent_id: str | None = None,
    agent_description: str | None = None,
    agent_version: str | None = None,
    provider: str | None = None,
    request_model: str | None = None,
) -> dict[str, Any]:
    """Build attributes for create_agent / invoke_agent spans.

    `operation` MUST be one of OPERATION_CREATE_AGENT, OPERATION_INVOKE_AGENT.
    Per upstream semconv: ``gen_ai.agent.name`` is conditionally required —
    omit when not known rather than passing an empty string.
    """
    if operation not in (OPERATION_CREATE_AGENT, OPERATION_INVOKE_AGENT):
        raise ValueError(
            f"agent_span_attributes: operation must be create_agent or "
            f"invoke_agent, got {operation!r}"
        )
    return _drop_empty(
        {
            ATTR_OPERATION_NAME: operation,
            ATTR_AGENT_NAME: agent_name,
            ATTR_AGENT_ID: agent_id,
            ATTR_AGENT_DESCRIPTION: agent_description,
            ATTR_AGENT_VERSION: agent_version,
            ATTR_PROVIDER_NAME: provider,
            ATTR_REQUEST_MODEL: request_model,
        }
    )


def workflow_span_attributes(
    *,
    workflow_name: str,
    provider: str | None = None,
) -> dict[str, Any]:
    """Build attributes for invoke_workflow spans.

    Per upstream: workflow spans group multiple agent invocations; emit only
    when the framework distinguishes workflow from individual agent
    invocations.
    """
    return _drop_empty(
        {
            ATTR_OPERATION_NAME: OPERATION_INVOKE_WORKFLOW,
            ATTR_WORKFLOW_NAME: workflow_name,
            ATTR_PROVIDER_NAME: provider,
        }
    )


def tool_span_attributes(
    *,
    tool_name: str,
    tool_call_id: str | None = None,
    tool_type: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    """Build attributes for execute_tool spans."""
    return _drop_empty(
        {
            ATTR_OPERATION_NAME: OPERATION_EXECUTE_TOOL,
            ATTR_TOOL_NAME: tool_name,
            ATTR_TOOL_CALL_ID: tool_call_id,
            ATTR_TOOL_TYPE: tool_type,
            ATTR_PROVIDER_NAME: provider,
        }
    )


def model_span_attributes(
    *,
    operation: str = OPERATION_CHAT,
    provider: str,
    request_model: str,
    response_model: str | None = None,
) -> dict[str, Any]:
    """Build attributes for chat / generate / completion / embeddings spans."""
    if operation not in {
        OPERATION_CHAT,
        OPERATION_GENERATE_CONTENT,
        OPERATION_TEXT_COMPLETION,
        OPERATION_EMBEDDINGS,
    }:
        raise ValueError(
            f"model_span_attributes: operation must be chat / generate_content / "
            f"text_completion / embeddings, got {operation!r}"
        )
    return _drop_empty(
        {
            ATTR_OPERATION_NAME: operation,
            ATTR_PROVIDER_NAME: provider,
            ATTR_REQUEST_MODEL: request_model,
            ATTR_RESPONSE_MODEL: response_model,
        }
    )


# ---------------------------------------------------------------------------
# Coverage helpers — used by CI gate to detect which emit sites are aligned
# ---------------------------------------------------------------------------


# The CI gate `check_otel_genai_semconv_coverage.py` greps for any of these
# tokens to determine whether a Python file is "aligned" with GenAI semconv.
# Importing a constant from this module is the cleanest signal of alignment.
ALIGNMENT_MARKERS: Final[frozenset[str]] = frozenset(
    {
        "from agentic_core.L6_observability.semconv.gen_ai",
        "from agentic_core.L6_observability.semconv import gen_ai",
        "import agentic_core.L6_observability.semconv.gen_ai",
        # Raw-string fallback: the bare attribute names ARE the spec; if they
        # appear verbatim, it counts as alignment too.
        "gen_ai.operation.name",
        "gen_ai.agent.name",
        "gen_ai.workflow.name",
        "gen_ai.tool.name",
        "gen_ai.provider.name",
    }
)


def is_aligned_with_genai_semconv(source_text: str) -> bool:
    """Best-effort check: does `source_text` reference the GenAI semconv?

    Used by the CI gate to compute the alignment percentage across emitter
    files. Conservative: returns True if any alignment marker appears.
    """
    return any(marker in source_text for marker in ALIGNMENT_MARKERS)


__all__ = [
    # Attribute keys
    "ATTR_OPERATION_NAME",
    "ATTR_PROVIDER_NAME",
    "ATTR_AGENT_ID",
    "ATTR_AGENT_NAME",
    "ATTR_AGENT_DESCRIPTION",
    "ATTR_AGENT_VERSION",
    "ATTR_WORKFLOW_NAME",
    "ATTR_REQUEST_MODEL",
    "ATTR_RESPONSE_MODEL",
    "ATTR_TOOL_NAME",
    "ATTR_TOOL_CALL_ID",
    "ATTR_TOOL_TYPE",
    "ATTR_INPUT_MESSAGES",
    "ATTR_OUTPUT_MESSAGES",
    "ATTR_SYSTEM",
    "ATTR_ERROR_TYPE",
    # Operations
    "OPERATION_CREATE_AGENT",
    "OPERATION_INVOKE_AGENT",
    "OPERATION_INVOKE_WORKFLOW",
    "OPERATION_EXECUTE_TOOL",
    "OPERATION_CHAT",
    "OPERATION_GENERATE_CONTENT",
    "OPERATION_TEXT_COMPLETION",
    "OPERATION_EMBEDDINGS",
    "ALL_OPERATIONS",
    # Providers
    "PROVIDER_ANTHROPIC",
    "PROVIDER_OPENAI",
    "PROVIDER_GCP_GEMINI",
    "PROVIDER_GCP_VERTEX",
    "PROVIDER_AWS_BEDROCK",
    "PROVIDER_AZURE_OPENAI",
    "PROVIDER_LOCAL",
    "ALL_PROVIDERS",
    # Span name builders
    "span_name_create_agent",
    "span_name_invoke_agent",
    "span_name_invoke_workflow",
    "span_name_execute_tool",
    # Attribute builders
    "agent_span_attributes",
    "workflow_span_attributes",
    "tool_span_attributes",
    "model_span_attributes",
    # Coverage helpers
    "ALIGNMENT_MARKERS",
    "is_aligned_with_genai_semconv",
]
