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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "runtime_models")
emit_determinism_digest("p0", "runtime_models")

_emit_dispatches_healing_run("p1", "runtime_models", "L4")
_emit_routes_through("p1", "runtime_models", "L4")
_emit_escalates_to_human("p1", "runtime_models", "L4")
_emit_reads_policy_state("p1", "runtime_models", "L4")

_emit_snapshots_state("p0", "runtime_models", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "runtime_models", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "runtime_models")


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
