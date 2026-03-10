"""Minimal shim: re-exports types required by prompt_assembler.py.

Created by P2/W2.2 to unblock the import chain:
  prompt_assembler.py → from agentic_core.L4_state.memory.runtime_models import InjectionMatch

Only the attributes accessed at runtime are defined:
  InjectionMatch.injection        → InjectionPattern (has .priority, .template)
  InjectionMatch.relevance_score  → float
  InjectionMatch.variable_values  → dict[str, Any]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class InjectionPattern:
    """Minimal representation of an instructional injection pattern."""

    priority: int = 0
    template: str = ""


@dataclass
class InjectionMatch:
    """A matched injection pattern with relevance scoring and variable bindings."""

    injection: InjectionPattern = field(default_factory=InjectionPattern)
    relevance_score: float = 0.0
    variable_values: dict[str, Any] = field(default_factory=dict)
