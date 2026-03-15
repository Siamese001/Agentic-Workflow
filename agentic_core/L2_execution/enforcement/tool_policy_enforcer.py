"""
§Wave2.4 — ToolPolicyEnforcer: LawSlot enforcement gate for tool calls.

Resolves applicable law slots and enforces policy constraints before
tool execution. Default behavior is PASS with empty slots if no policy
is configured.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
    ToolEnforcementArtifact,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "tool_policy_enforcer", "state_snapshot")

_log = logging.getLogger(__name__)


def _stable_args_hash(args: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of tool arguments.

    Uses sorted-key JSON serialization with default=str for non-serializable
    values, ensuring identical args always produce the same hash.
    """
    serialized = json.dumps(args, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ToolPolicyEnforcer:
    """§Wave2.4 — Minimal law-slot enforcement handler.

    Resolves applicable law slots for a given tool + context and returns
    an enforcement decision (PASS / BLOCK / MODIFY).

    Default behavior (no policy rules configured): PASS with empty slots.

    Subclass or configure `_policy_rules` to implement real enforcement.
    """

    def __init__(self) -> None:
        self._policy_rules: dict[str, dict[str, Any]] = {}

    def register_rule(
        self,
        tool_name: str,
        *,
        outcome: LawSlotOutcome,
        law_slots: tuple[str, ...] = (),
        rationale: str = "",
        arg_transform: dict[str, Any] | None = None,
    ) -> None:
        """Register a policy rule for a specific tool.

        Used primarily for testing and configuration.
        """
        self._policy_rules[tool_name] = {
            "outcome": outcome,
            "law_slots": law_slots,
            "rationale": rationale,
            "arg_transform": arg_transform,
        }

    def resolve_slots(
        self,
        tool_name: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[str, ...]:
        """Resolve applicable law slot IDs for this tool + context."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ToolPolicyEnforcer.resolve_slots"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolPolicyEnforcer.resolve_slots".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        rule = self._policy_rules.get(tool_name)
        if rule:
            return rule.get("law_slots", ())
        return ()

    def enforce(
        self,
        tool_name: str,
        args: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[LawSlotOutcome, dict[str, Any], str, tuple[str, ...]]:
        """Enforce policy for a tool call.

        Returns:
            (outcome, new_args, rationale, applied_slots)
            - outcome: PASS, BLOCK, or MODIFY
            - new_args: original args if PASS/BLOCK; transformed args if MODIFY
            - rationale: human-readable explanation
            - applied_slots: tuple of law slot IDs that were applied
        """
        rule = self._policy_rules.get(tool_name)
        if not rule:
            return (LawSlotOutcome.PASS, args, "No policy rules configured", ())

        outcome = rule["outcome"]
        slots = rule.get("law_slots", ())
        rationale = rule.get("rationale", f"Policy rule: {outcome.value}")

        if outcome == LawSlotOutcome.MODIFY and rule.get("arg_transform"):
            new_args = {**args, **rule["arg_transform"]}
            return (outcome, new_args, rationale, slots)

        return (outcome, args, rationale, slots)

    def build_artifact(
        self,
        tool_name: str,
        outcome: LawSlotOutcome,
        applied_slots: tuple[str, ...],
        rationale: str,
        original_args_hash: str,
        modified_args_hash: str = "",
        trace_id: str = "",
        agent_id: str = "",
    ) -> ToolEnforcementArtifact:
        """Build a ToolEnforcementArtifact for emission."""
        return ToolEnforcementArtifact(
            enforcement_id=str(uuid.uuid4()),
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            trace_id=trace_id or str(uuid.uuid4())[:16],
            agent_id=agent_id or "unknown",
            tool_name=tool_name,
            outcome=outcome,
            applied_law_slots=applied_slots,
            rationale=rationale,
            original_args_hash=original_args_hash,
            modified_args_hash=modified_args_hash,
        )


# Module-level default enforcer (singleton pattern matching MCPToolServer)
_TOOL_POLICY_ENFORCER: ToolPolicyEnforcer | None = None


def get_tool_policy_enforcer() -> ToolPolicyEnforcer:
    """Get or create the global ToolPolicyEnforcer instance."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_tool_policy_enforcer", "L2_EXECUTION")
    global _TOOL_POLICY_ENFORCER
    if _TOOL_POLICY_ENFORCER is None:
        _TOOL_POLICY_ENFORCER = ToolPolicyEnforcer()
    return _TOOL_POLICY_ENFORCER


def set_tool_policy_enforcer(enforcer: ToolPolicyEnforcer | None) -> None:
    """Replace the global enforcer (for testing or reconfiguration)."""
    global _TOOL_POLICY_ENFORCER
    _TOOL_POLICY_ENFORCER = enforcer


__all__ = [
    "ToolPolicyEnforcer",
    "_stable_args_hash",
    "get_tool_policy_enforcer",
    "set_tool_policy_enforcer",
]
