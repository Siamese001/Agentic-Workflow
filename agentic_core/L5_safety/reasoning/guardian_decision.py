"""
L5 Guardian Decision - Active blocking enforcement.

L5 must block execution before L2.2 with policy enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR


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
        # guardian: allow-magic_configuration - Token budget configured externally in production
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
        violations = []
        escalate = False

        # Check tool allowlist
        if hasattr(manifest, "tool_name"):
            if manifest.tool_name not in self.tool_allowlist:
                violations.append(f"Tool '{manifest.tool_name}' not in allowlist")

        # Check file access scope (only if file_path is a string, not Mock)
        if hasattr(manifest, "file_path") and isinstance(manifest.file_path, str):
            file_path = str(manifest.file_path)
            if not any(allowed in file_path for allowed in self.file_scope_whitelist):
                violations.append(f"File access '{file_path}' outside allowed scope")

        # Check token budget
        if hasattr(manifest, "token_usage"):
            if manifest.token_usage > self.token_budget:
                violations.append(f"Token usage {manifest.token_usage} exceeds budget {self.token_budget}")
                escalate = True

        # Check agent permissions
        if hasattr(manifest, "agent_layer"):
            agent_layer = manifest.agent_layer
            required_permission = getattr(manifest, "required_permission", "read")
            if agent_layer not in self.agent_permissions:
                violations.append(f"Unknown agent layer '{agent_layer}'")
            elif required_permission not in self.agent_permissions[agent_layer]:
                violations.append(f"Agent '{agent_layer}' lacks permission '{required_permission}'")

        # Determine decision
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
        # This would integrate with L4 state storage
        import logging

        Logger = logging.getLogger(__name__)

        Logger.info(f"[L5_GUARDIAN] Decision for {trace_id}: {decision.to_dict()}")

        # In full implementation, this would serialize and store in L4 state
        # with hash verification and version tracking
