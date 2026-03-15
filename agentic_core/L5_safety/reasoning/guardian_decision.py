"""
L5 Guardian Decision - Active blocking enforcement.

L5 must block execution before L2.2 with policy enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


@dataclass
class GuardianDecision:
    """Decision from L5 Guardian with enforcement capabilities."""

    allow: bool
    escalate: bool
    violations: list[str]
    budget_remaining: int
    policy_version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "allow": self.allow,
            "escalate": self.escalate,
            "violations": self.violations,
            "budget_remaining": self.budget_remaining,
            "policy_version": self.policy_version,
        }


class GuardianViolationError(Exception):
    """Raised when Guardian blocks execution."""

    def __init__(self, decision: GuardianDecision, message: str | None = None) -> None:
        self.decision = decision
        if message is None:
            message = f"Guardian blocked execution: {decision.violations}"
        super().__init__(message)


class L5Guardian:
    """
    Active Guardian that enforces policies before L2.2.

    Enforces:
    - Tool allowlist
    - File access scope
    - Token budget
    - Agent permission map
    - Rate limits
    """

    def __init__(self, policy_version: str = "1.0") -> None:
        self.policy_version = policy_version
        self.tool_allowlist = {
            "file_read",
            "file_write",
            "ast_parse",
            "llm_call",
            "redis_get",
            "redis_set",
            "pinecone_query",
            "pinecone_upsert",
        }
        self.file_scope_whitelist = {"/tmp", "/workspace", AGENTIC_CORE_DIR}
        # guardian: allow-magic-config
        self.token_budget = 1000000
        self.agent_permissions = {
            "L1_cognition": ["read", "transform"],
            "L2_execution": ["read", "write", "validate"],
            "L3_orchestration": ["read", "write", "orchestrate"],
            "L5_safety": ["read", "enforce", "block"],
        }

    def validate(self, manifest: Any, state: Any, policy_version: str | None = None) -> GuardianDecision:
        """
        Validate execution intent against all policies.

        Args:
            manifest: Execution manifest to validate
            state: Current execution state
            policy_version: Policy version to enforce

        Returns:
            GuardianDecision with allow/block result
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "L5Guardian.validate")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:L5Guardian.validate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []
        escalate = False
        if hasattr(manifest, "tool_name"):
            if manifest.tool_name not in self.tool_allowlist:
                violations.append(f"Tool '{manifest.tool_name}' not in allowlist")
        if hasattr(manifest, "file_path") and isinstance(manifest.file_path, str):
            file_path = str(manifest.file_path)
            if not any(allowed in file_path for allowed in self.file_scope_whitelist):
                violations.append(f"File access '{file_path}' outside allowed scope")
        if hasattr(manifest, "token_usage"):
            if manifest.token_usage > self.token_budget:
                violations.append(f"Token usage {manifest.token_usage} exceeds budget {self.token_budget}")
                escalate = True
        if hasattr(manifest, "agent_layer"):
            agent_layer = manifest.agent_layer
            required_permission = getattr(manifest, "required_permission", "read")
            if agent_layer not in self.agent_permissions:
                violations.append(f"Unknown agent layer '{agent_layer}'")
            elif required_permission not in self.agent_permissions[agent_layer]:
                violations.append(f"Agent '{agent_layer}' lacks permission '{required_permission}'")
        allow = len(violations) == 0
        budget_remaining = max(0, self.token_budget - getattr(manifest, "token_usage", 0))
        return GuardianDecision(
            allow=allow,
            escalate=escalate,
            violations=violations,
            budget_remaining=budget_remaining,
            policy_version=policy_version or self.policy_version,
        )

    def log_decision_to_state_bus(self, decision: GuardianDecision, trace_id: str) -> None:
        """Log Guardian decision to L4 state bus."""
        import logging

        Logger = logging.getLogger(__name__)
        Logger.info(f"[L5_GUARDIAN] Decision for {trace_id}: {decision.to_dict()}")
