"""
Core constants and enumerations for the v10_9 runtime layer.

This module centralizes:
  • Workflow phases (aligned with Phase enum in utils_types)
  • Execution status codes (L2 tool/executor responses)
  • Canonical model defaults + legacy alias map
  • Shared string constants used across L1–L5

This ensures that all orchestration, safety, planning, and execution
components reference the same deterministic contract.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict


# ======================================================================
# EXECUTION STATUS (L2)
# ======================================================================

class NodeStatus(Enum):
    """Lifecycle status for a node/tool execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    SKIPPED = "skipped"
    PENDING = "pending"


# ======================================================================
# WORKFLOW PHASES (mirrors utils_types.Phase)
# ======================================================================

class WorkflowPhase(Enum):
    """
    High-level workflow lifecycle.

    Must remain in sync with:
      • utils_types.Phase
      • l4_state_machine.StateMachine._TRANSITIONS
      • l3_orchestration phase routing logic
    """

    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


# ======================================================================
# MODEL DEFAULTS + LEGACY ALIASES
# ======================================================================

CANONICAL_MODEL_DEFAULT = "gpt-4.1"

LEGACY_MODEL_ALIASES: Dict[str, str] = {
    # OpenAI historical mappings
    "gpt-4": "gpt-4.1",
    "gpt-4-turbo": "gpt-4.1",
    "gpt-4-0613": "gpt-4.1",
    "gpt-3.5-turbo": "gpt-4.1-mini",

    # Anthropic
    "claude-2": "claude-3-sonnet",
    "claude-instant": "claude-3-haiku",

    # Gemini
    "gemini-pro": "gemini-1.5-pro",
    "gemini-ultra": "gemini-1.5-ultra",
}


# ======================================================================
# STRING CONSTANTS (shared across layers)
# ======================================================================

SYSTEM_ROLE = "system"
USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"

STATE_KEY_MESSAGES = "messages"
STATE_KEY_RAG = "rag_history"
STATE_KEY_SUMMARY = "summary"
STATE_KEY_WORLD = "world"
STATE_KEY_METADATA = "metadata"
STATE_KEY_PHASE = "phase"
