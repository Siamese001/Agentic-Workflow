"""Core constants and enumerations for the v10.7 runtime layer."""
from __future__ import annotations

from enum import Enum
from typing import Dict


class NodeStatus(Enum):
    """Lifecycle status for node execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class WorkflowPhase(Enum):
    """Phases for workflow execution surfaces."""

    INIT = "init"
    EXECUTION = "execution"
    POST_PROCESS = "post_process"
    COMPLETE = "complete"
    FAILED = "failed"


LEGACY_MODEL_ALIASES: Dict[str, str] = {
    "gpt-4": "gpt-4o",
    "gpt-4-0613": "gpt-4o",
    "gpt-3.5-turbo": "gpt-4o-mini",
    "claude-2": "claude-3-sonnet",
    "gemini-pro": "gemini-1.5-pro",
}


CANONICAL_MODEL_DEFAULT = "gpt-4o"
