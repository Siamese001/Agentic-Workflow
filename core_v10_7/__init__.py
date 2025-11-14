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
from types import ModuleType
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
from .agents import *      # noqa: F401,F403
from .clients import *     # noqa: F401,F403
from .config import *      # noqa: F401,F403
from .constants import *   # noqa: F401,F403
from .context import *     # noqa: F401,F403
from .exceptions import *  # noqa: F401,F403
from .mcp import *         # noqa: F401,F403
from .models import *      # noqa: F401,F403
from .resilience import *  # noqa: F401,F403
from .services import *    # noqa: F401,F403


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
