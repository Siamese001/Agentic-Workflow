# constants.py
"""
Shared Constants — v10_9
"""

from __future__ import annotations
from enum import Enum
from typing import Dict


class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    SKIPPED = "skipped"
    PENDING = "pending"


class WorkflowPhase(Enum):
    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


CANONICAL_MODEL_DEFAULT = "gpt-4.1"

LEGACY_MODEL_ALIASES: Dict[str, str] = {
    "gpt-4": "gpt-4.1",
    "gpt-4-turbo": "gpt-4.1",
    "claude-2": "claude-3-sonnet",
    "gemini-pro": "gemini-1.5-pro",
}
