"""
core_v10_7 – Public API surface for the modular v10.7 core.

This module exposes:
- Data models (ConfigV10_7, MainGraphState)
- Workflow services (CostTracker, ContextBudgetManager, CacheManager, MetricsCollector)
- Factories (create_workflow_context, cleanup_workflow_chroma_collection, get_checkpointer)
- Error types (WorkflowError, FileIOError, ModelAPIError, CostCeilingExceededError)

The internal structure is intentionally modular:
    core_v10_7/
        config.py
        exceptions.py
        state.py
        services.py
        context.py
        checkpointer.py
        clients.py
"""

from __future__ import annotations

import os
import sys
from asyncio import TimeoutError as AsyncTimeoutError

# -------------------------------------------------------------------
# Vendor bootstrap (langgraph, langchain)
# -------------------------------------------------------------------

VENDOR_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "vendor")
)

if os.path.isdir(VENDOR_PATH) and VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

# -------------------------------------------------------------------
# Public API imports
# -------------------------------------------------------------------

# ---- Configuration ----
from .config import ConfigV10_7

# ---- Exception definitions ----
from .exceptions import (
    WorkflowError,
    FileIOError,
    ModelAPIError,
    CostCeilingExceededError,
)

# ---- Graph state model ----
from .state import MainGraphState

# ---- Core services ----
from .services import (
    CostTracker,
    ContextBudgetManager,
    CacheManager,
    MetricsCollector,
)

# ---- Factory methods ----
from .context import create_workflow_context, cleanup_workflow_chroma_collection
from .checkpointer import get_checkpointer

# ---- Export list ----
__all__ = [
    # Config
    "ConfigV10_7",

    # Main state
    "MainGraphState",

    # Exceptions
    "WorkflowError",
    "FileIOError",
    "ModelAPIError",
    "CostCeilingExceededError",

    # Services
    "CostTracker",
    "ContextBudgetManager",
    "CacheManager",
    "MetricsCollector",

    # Factories
    "create_workflow_context",
    "cleanup_workflow_chroma_collection",
    "get_checkpointer",
]
