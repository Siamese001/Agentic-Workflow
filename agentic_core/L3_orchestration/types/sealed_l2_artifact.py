from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TerminalClassification(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NEEDS_HELP = "NEEDS_HELP"


@dataclass
class SealedL2Artifact:
    trace_id: str
    run_scope: str = "CURRENT_RUN"
    exec_trace: dict[str, Any] = field(default_factory=dict)
    terminal_classification: TerminalClassification = TerminalClassification.SUCCESS
    escalation_reason: str | None = None
    has_commit_payload: bool = False

    def __post_init__(self) -> None:
        self.trace_id = str(self.trace_id or self.exec_trace.get("trace_id") or "")
        self.run_scope = str(self.run_scope or "CURRENT_RUN")
        self.exec_trace = dict(self.exec_trace or {})
        if self.trace_id and "trace_id" not in self.exec_trace:
            self.exec_trace["trace_id"] = self.trace_id
        if not isinstance(self.terminal_classification, TerminalClassification):
            self.terminal_classification = TerminalClassification(str(self.terminal_classification))
        self.has_commit_payload = bool(self.has_commit_payload)
        if self.escalation_reason is not None:
            self.escalation_reason = str(self.escalation_reason)

    def as_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "run_scope": self.run_scope,
            "exec_trace": deepcopy(self.exec_trace),
            "terminal_classification": self.terminal_classification.value,
            "escalation_reason": self.escalation_reason,
            "has_commit_payload": self.has_commit_payload,
        }
