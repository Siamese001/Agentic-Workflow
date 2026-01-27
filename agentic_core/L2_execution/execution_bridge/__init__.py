#!/usr/bin/env python3
from __future__ import annotations

"""
L2 Execution Unified Agents

Phase 4 Hard Migration: Consolidated routing agents.
"""


from agentic_core.L2_execution.execution_bridge.ModelRouterAgent import (
    ModelConfig,
    ModelTier,
    RouterConfig,
    RoutingDecision,
    TaskComplexity,
    ModelRouterAgent,
    create_legacy_dynamic_router,
    create_legacy_model_router,
)

__all__ = [
    "ModelRouterAgent",
    "ModelConfig",
    "ModelTier",
    "TaskComplexity",
    "RoutingDecision",
    "RouterConfig",
    "create_legacy_model_router",
    "create_legacy_dynamic_router",
]
