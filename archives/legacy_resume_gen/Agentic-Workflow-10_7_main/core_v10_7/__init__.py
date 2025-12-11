"""
core_v10_7 – Public API surface for the modular v10.7 core.

This package exposes:

- Configuration:
    - ConfigV10_7

- Exceptions:
    - WorkflowError, FileIOError, ModelAPIError,
      CostCeilingExceededError, JSONParsingError, PydanticSchemaError,
      WorkflowTimeoutError, MCPClientInitializationError

- Core services:
    - CostTracker, ContextBudgetManager, CacheManager, MetricsCollector,
      FeedbackLogReader, ProposedRulesLoader, PromptTemplateManager,
      ResponseValidator, SemanticValidator, track_metrics, log_event

- Context & graph state:
    - WorkflowContext
    - create_workflow_context, cleanup_workflow_chroma_collection, detect_bias
    - ResumeContext, JobContext, PromptContext, BulletContext, DraftContext,
      QAContext, ArtifactContext, MetadataContext, SafetyContext,
      FeedbackContext, HILContext
    - A2AMessage, A2AContext, MainGraphState, MetaGraphState

- Agents:
    - BaseAgent, BaseTool (and related helper methods)

- MCP:
    - MCPClientSpec, MCPClientStub, parse_mcp_client_specs,
      instantiate_mcp_client, wrap_mcp

- Models:
    - GeneratedPrompts, StrategyPlan, PlannerAssessment, ScenarioSimulationResult,
      and other Pydantic models used across v10.7

- Resilience:
    - CircuitBreaker, exponential_backoff_retry, workflow_timeout_guard,
      update_context

- Constants:
    - legacy_model_alias, canonical_model_name

- Clients:
    - AsyncBaseModelClient, OpenAIAsyncClient, AnthropicAsyncClient,
      GeminiAsyncClient, MCPToolClient, make_model_client

Imports are intentionally wild-carded from submodules, and __all__ is
assembled dynamically so that “from core_v10_7 import X” works for any
public symbol in the core.
"""

from __future__ import annotations

import os
import sys
from asyncio import TimeoutError as AsyncTimeoutError
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l4.types import ModuleType
from typing import List

# -------------------------------------------------------------------
# Vendor bootstrap (langgraph/langchain in vendor/)
# -------------------------------------------------------------------

VENDOR_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "vendor")
)
if os.path.isdir(VENDOR_PATH):
    # NOTE:
    # The original bootstrap inserted the entire vendor directory at the
    # front of sys.path, which unintentionally allowed vendored stubs
    # (e.g., anthropic_stub) to shadow real SDKs installed in
    # site-packages.  We now scope the bootstrap to the vendored graph
    # dependencies only so langgraph/langchain remain available without
    # overriding any first-party SDKs used elsewhere in the stack.
    vendor_langgraph = os.path.join(VENDOR_PATH, "langgraph")
    vendor_langchain = os.path.join(VENDOR_PATH, "langchain")

    if os.path.isdir(vendor_langgraph) and vendor_langgraph not in sys.path:
        sys.path.insert(0, vendor_langgraph)
    if os.path.isdir(vendor_langchain) and vendor_langchain not in sys.path:
        sys.path.insert(0, vendor_langchain)

# -------------------------------------------------------------------
# Import submodules (as modules and via wildcard)
# -------------------------------------------------------------------

# Import as modules for __all__ aggregation
from . import agents as _agents
from . import clients as _clients
from . import config as _config
from . import constants as _constants
from . import context as _context
from . import exceptions as _exceptions
from . import mcp as _mcp
from . import models as _models
from . import resilience as _resilience
from . import services as _services

# Wildcard imports so public names are available directly on core_v10_7
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.agents import *  # INVALID: Cannot import from path with hyphens
from runtime.shared.clients import *
from shared.config import *
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.constants import *  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.context import *  # INVALID: Cannot import from path with hyphens
from shared.exceptions import *
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.mcp import *  # INVALID: Cannot import from path with hyphens
from shared.models import *
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.resilience import *  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.services import *  # INVALID: Cannot import from path with hyphens


# -------------------------------------------------------------------
# __all__ aggregation helpers
# -------------------------------------------------------------------

def _public_names(mod: ModuleType) -> List[str]:
    """
    Collect public names from a submodule.

    Prefer the module's __all__ if present; otherwise, use a dir()
    fallback and filter out private and module objects.
    """
    if hasattr(mod, "__all__"):
        return list(mod.__all__)  # type: ignore[attr-defined]

    names: List[str] = []
    for name in dir(mod):
        if name.startswith("_"):
            continue
        value = getattr(mod, name)
        # Avoid re-exporting submodules themselves
        if isinstance(value, ModuleType):
            continue
        names.append(name)
    return names


__all__ = sorted(
    set(
        _public_names(_agents)
        + _public_names(_clients)
        + _public_names(_config)
        + _public_names(_constants)
        + _public_names(_context)
        + _public_names(_exceptions)
        + _public_names(_mcp)
        + _public_names(_models)
        + _public_names(_resilience)
        + _public_names(_services)
        + ["AsyncTimeoutError"]
    )
)



__all__ = sorted(
    set(
        __all__
        + [
            "BulletExecutionStackV10_8",
            "DraftingExecutionStackV10_8",
            "HILStackV10_8",
            "QAValidationStackV10_8",
            "RAGExecutionStackV10_8",
            "SafetyStackV10_8",
            "StateAdapterStack",
            "StrategyStackV10_8",
            "RobustnessStack",
        ]
    )
)
