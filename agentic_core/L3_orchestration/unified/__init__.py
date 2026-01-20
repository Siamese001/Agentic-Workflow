"""
Unified L3 Orchestration Agents

Phase 1 Consolidation: 20 orchestrators → 4 unified cores

This module provides consolidated orchestration agents that merge functionality
from multiple legacy agents while maintaining backward compatibility.

Unified Agents:
- CoreOrchestrationAgent: Caching + Self-Recovery + Intelligent Routing
- AppWorkflowOrchestratorAgent: Phase-based workflow execution for LIC/RG
"""
from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import (
    CoreOrchestrationAgent,
    create_legacy_cached_orchestrator,
    create_legacy_self_recovering_orchestrator,
    create_legacy_intelligent_orchestrator,
)
from agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent import (
    AppWorkflowOrchestratorAgent,
    WorkflowPhase,
    PhaseConfig,
)

__all__ = [
    "CoreOrchestrationAgent",
    "AppWorkflowOrchestratorAgent",
    "WorkflowPhase",
    "PhaseConfig",
    "create_legacy_cached_orchestrator",
    "create_legacy_self_recovering_orchestrator",
    "create_legacy_intelligent_orchestrator",
]
