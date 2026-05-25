"""Structured regen refusal (terminal heal path)."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L2_execution.regen.regen_types import RegenRefusalCode


@dataclass(frozen=True)
class RegenRefusal:
    """Runner refusal — routes to E5 / NEEDS_HELP without provider dispatch."""

    code: RegenRefusalCode
    message: str
    semantic_regen_attempt_index: int = 0
    max_semantic_regen_attempts: int = 1
    semantic_regen_budget_exhausted: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "refusal_code": self.code.value,
            "message": self.message,
            "semantic_regen_attempt_index": self.semantic_regen_attempt_index,
            "max_semantic_regen_attempts": self.max_semantic_regen_attempts,
            "semantic_regen_budget_exhausted": self.semantic_regen_budget_exhausted,
        }
