"""
Centralized exceptions for the v10_9 runtime.

This module provides:
  • Layer-aligned exception classes (L1–L5)
  • Unified client/tool error surface
  • Safety, budget, and validation enforcement errors
  • Orchestration and control-flow exceptions
"""

from __future__ import annotations


# ======================================================================
# CONFIGURATION (L0)
# ======================================================================

class RuntimeConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""


# ======================================================================
# L1 — REASONING / COGNITION ERRORS
# ======================================================================

class PlanningError(Exception):
    """Raised when L1 fails to generate a valid plan object."""


class ReasoningError(Exception):
    """Raised when L1 cognitive processing fails."""


# ======================================================================
# L2 — EXECUTION / TOOLING ERRORS
# ======================================================================

class ModelClientError(Exception):
    """Raised when an LLM client invocation fails."""


class ToolExecutionError(Exception):
    """Raised when an L2 tool or action fails."""


class ToolTimeoutError(Exception):
    """Raised when an execution branch exceeds its timeout."""


# ======================================================================
# L3 — ORCHESTRATION ERRORS
# ======================================================================

class OrchestrationError(Exception):
    """General failure within the orchestration layer."""


class IllegalTransitionError(Exception):
    """Raised when state machine transitions are invalid."""


class ControlFlowHalt(Exception):
    """
    Soft halt: orchestrator should gracefully stop execution
    (used for REPLAN, RETRY, HIL escalation).
    """


class ControlFlowAbort(Exception):
    """Hard abort: workflow is unrecoverable and must terminate."""


# ======================================================================
# L4 — STATE / MEMORY / CONTEXT ERRORS
# ======================================================================

class ValidationError(Exception):
    """Raised when structural or semantic validation fails."""


class BudgetExceededError(Exception):
    """Raised when memory or token budgets are exhausted."""


class CacheMiss(Exception):
    """Raised when required cache data is absent."""


class StateIntegrityError(Exception):
    """Raised when L4 state becomes inconsistent or corrupted."""


# ======================================================================
# L5 — SAFETY / POLICY / CONSTITUTIONAL ERRORS
# ======================================================================

class SafetyViolationError(Exception):
    """Raised when safety, constitutional, or policy rules are violated."""


class RedactionFailureError(Exception):
    """Raised when sensitive content cannot be sanitized."""


class ArbitrationError(Exception):
    """Raised when the safety/QA arbitration engine cannot resolve a decision."""


# ======================================================================
# WORKFLOW-LEVEL ERRORS (CROSS-CUTTING)
# ======================================================================

class WorkflowFailed(Exception):
    """Raised when a run terminates in a FAILED state."""


class WorkflowCompleted(Exception):
    """Raised when a workflow ends in a COMPLETE state."""
