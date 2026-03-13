"""
§Wave2.4 — Tool Enforcement Artifact Types.

Typed artifacts for the LawSlotHandler enforcement gate at tool choke points.
All artifacts are frozen dataclasses with deterministic serialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LawSlotOutcome(Enum):
    """§Wave2.4 — Enforcement outcomes at the tool choke point."""

    PASS = "pass"
    BLOCK = "block"
    MODIFY = "modify"


@dataclass(frozen=True)
class ToolEnforcementArtifact:
    """§Wave2.4 — Enforcement record emitted exactly once per tool call.

    Captures the enforcement decision, applied law slots, argument hashes,
    and rationale for audit trail.
    """

    enforcement_id: str
    timestamp_utc: str
    trace_id: str
    agent_id: str
    tool_name: str
    outcome: LawSlotOutcome
    applied_law_slots: tuple[str, ...]
    rationale: str
    original_args_hash: str
    modified_args_hash: str = ""
    policy_context_hash: str = ""

    def __post_init__(self) -> None:
        if not self.enforcement_id:
            raise ValueError("ToolEnforcementArtifact: enforcement_id must be non-empty")
        if not self.trace_id:
            raise ValueError("ToolEnforcementArtifact: trace_id must be non-empty")
        if not self.tool_name:
            raise ValueError("ToolEnforcementArtifact: tool_name must be non-empty")
        if not isinstance(self.outcome, LawSlotOutcome):
            raise TypeError(
                f"ToolEnforcementArtifact: outcome must be LawSlotOutcome, got {type(self.outcome).__name__}"
            )
        if not self.original_args_hash:
            raise ValueError("ToolEnforcementArtifact: original_args_hash must be non-empty")
        if self.outcome == LawSlotOutcome.MODIFY and (not self.modified_args_hash):
            raise ValueError("ToolEnforcementArtifact: modified_args_hash required when outcome is MODIFY")


class ToolPolicyBlocked(Exception):
    """§Wave2.4 — Raised when a tool call is blocked by enforcement policy.

    Preserves the enforcement rationale and artifact for upstream handling.
    """

    def __init__(self, tool_name: str, rationale: str, artifact: ToolEnforcementArtifact) -> None:
        self.tool_name = tool_name
        self.rationale = rationale
        self.artifact = artifact
        super().__init__(f"Tool '{tool_name}' blocked by policy: {rationale}")


__all__ = ["LawSlotOutcome", "ToolEnforcementArtifact", "ToolPolicyBlocked"]
