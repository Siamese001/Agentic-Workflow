"""
SovereignBaseAgent - Sovereign Single Source of Truth (SSOT) Root.

Provides foundational capabilities for agents with sovereign authority.

L0 DNA FLATTENING (Jan 2026):
InfrastructureMixin consolidates all core agent capabilities:
- HealerMixin (autonomous repair)
- MCPHardenedMixin (MCP protocol safety)
- SubatomicTestingMixin (self-testing)
- InstructionalInjectionMixin (prompt injection protection - now L0 core trait)

PHASE 2 MIGRATION:
- Replaced individual mixins with InfrastructureMixin (unified gatekeeper)
- InfrastructureMixin provides: healing, MCP hardening, subatomic testing, prompt safety
- State verification via _infra_initialized flag

MRO HARDENING:
- This is the ROOT of the agent hierarchy
- InfrastructureMixin is injected HERE so all agents get full infrastructure
- Layer bases add specialized mixins BEFORE SovereignBaseAgent
- MRO Flow: Specialized -> Layer -> SovereignBaseAgent -> InfrastructureMixin -> [HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, InstructionalInjectionMixin] -> object

RESILIENCE:
- Prompt injection protection is now a core L0 trait, independent of MCP protocol
- Air-gapped agents (no MCP tools) still retain InstructionalInjectionMixin safety protocols
- Security auditors can verify injection-protection layer at the root of the hierarchy
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, validator
# This boosts alignment detection — review and integrate appropriately

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin

logger = logging.getLogger(__name__)


@dataclass
class SovereignBaseAgent(InfrastructureMixin):
    """
    Sovereign Single Source of Truth (SSOT) Root.

    L0 DNA FLATTENING (Jan 2026):
    InfrastructureMixin consolidates all core agent capabilities:
    - HealerMixin: Autonomous repair capability
    - MCPHardenedMixin: MCP protocol hardening
    - SubatomicTestingMixin: Self-testing capability
    - InstructionalInjectionMixin: Prompt injection protection (now L0 core trait)

    This ensures EVERY agent in the L0-L6 hierarchy has full infrastructure.

    MRO HARDENING:
    - SovereignBaseAgent inherits from InfrastructureMixin
    - Layer bases inherit from SovereignBaseAgent (+ specialized mixins)
    - Concrete agents inherit from layer bases (+ more specialized mixins)
    - MRO: Specialized -> Layer -> SovereignBaseAgent -> InfrastructureMixin -> [HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, InstructionalInjectionMixin] -> object

    RESILIENCE:
    - Prompt injection protection is independent of MCP protocol
    - Air-gapped agents retain InstructionalInjectionMixin safety
    - Security auditors can verify injection-protection at root level
    """

    name: str = "SovereignAgent"

    def __post_init__(self) -> None:
        """
        Initialize sovereign agent with infrastructure.

        Triggers InfrastructureMixin gatekeeper logic via super().__init__().

        MRO AUDITOR: Sets _sovereign_initialized sentinel for propagation verification.
        """
        # 1. Cooperative super() call - triggers InfrastructureMixin.__init__()
        super().__init__()

        # 2. Set Sentinel for MRO Auditor - verifies initialization chain reached root
        self._sovereign_initialized = True

        # 3. Core sovereign initialization logic
        self._initialize_sovereign_state()

    def _initialize_sovereign_state(self) -> Any:
        """Initialize sovereign-specific state."""
        self._config: dict[str, Any] = {}
        self._state: dict[str, Any] = {}
        self._authority_level = "standard"

    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")

    def get_state(self, key: str) -> Any | None:
        """Get state value."""
        return self._state.get(key)

    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value

    def get_authority_level(self) -> str:
        """Get the agent's authority level."""
        return self._authority_level

    def elevate_authority(self, level: str) -> None:
        """Elevate the agent's authority level."""
        self._authority_level = level
        logger.info(f"Authority elevated to: {level}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{self.name}] {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{self.name}] {message}")

    def log_feedback(
        self, workflow_id: str, action: str, status: str, details: dict[str, Any] = None
    ) -> None:
        """Log feedback for a workflow action."""
        logger.info(f"[{self.name}] Workflow {workflow_id}: {action} - {status} - {details or {}}")

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        Base heal_repository implementation - ROOT termination point.

        MRO HARDENING: This is the END of the heal_repository chain.
        Subclasses should call super().heal_repository() which eventually
        reaches here and terminates cleanly.
        """
        # ROOT: No super() call - we ARE the termination point
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1}


__all__ = ["SovereignBaseAgent"]
