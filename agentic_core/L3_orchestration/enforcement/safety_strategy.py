from __future__ import annotations

"""
SafetyStrategy - Consolidated Safety Orchestration Strategy

This module consolidates logic from:
- ComplianceOrchestratorAgent
- GuardianOrchestratorAgent
- HealingOrchestratorAgent

SSOT PRINCIPLE:
    All safety-related orchestration flows through this strategy,
    which is injected into Orchestrator.
"""


import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

Logger = logging.getLogger(__name__)


@dataclass
class SafetyStrategy:
    """
    Strategy for safety-focused orchestration missions.

    Consolidates:
    - Compliance validation (from ComplianceOrchestratorAgent)
    - Guardian protection (from GuardianOrchestratorAgent)
    - Healing coordination (from HealingOrchestratorAgent)

    Usage:
        strategy = SafetyStrategy(project_root=Path.cwd())
        orchestrator = Orchestrator(strategy=strategy)
        result = orchestrator.run_mission({"dry_run": True})
    """

    project_root: Path = field(default_factory=Path.cwd)
    _agent_factory: SafetyAgentFactory | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self._agent_factory is None:
            self._agent_factory = SafetyAgentFactory(self.project_root)

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return "SafetyStrategy"

    def get_tiers(self) -> dict[str, list[str]]:
        """
        Return the tiered execution plan for safety missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        """
        return {
            "Tier 0: Pre-Flight": [
                "CodeValidatorAgent",
            ],
            "Tier 1: Compliance": [
                "HygieneGuardianAgent",
                "NamingAgent",
            ],
            "Tier 2: Safety": [
                "LocationAgent",
                "StructureEnforcerAgent",
            ],
            "Tier 3: Healing": [
                "StructuralHealerAgent",
            ],
        }

    def _get_agent(self, agent_name: str) -> Any | None:
        """
        Get or create an agent instance by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        """
        if agent_name == "CodeValidatorAgent":
            try:
                from agentic_core.L0_routing.utils.subprocess_runner import (
                    invoke_code_validator,
                )

                class CodeValidatorAgentProxy:
                    def __init__(self, project_root):
                        self.project_root = project_root
                        self._invoke = invoke_code_validator

                    def validate_repository(self, **kwargs):
                        return self._invoke(action="validate", project_root=self.project_root)

                    def heal_repository(self, directory=None, **kwargs):
                        if directory:
                            return self._invoke(
                                action="validate_directory",
                                project_root=self.project_root,
                                directory=str(directory),
                            )
                        return self.validate_repository(**kwargs)

                return CodeValidatorAgentProxy(project_root=self.project_root)
            except ImportError as e:
                Logger.warning(f"[SafetyStrategy] Failed to import CodeValidatorAgent: {e}")
                return None
        agent = self._agent_factory.get(agent_name) if self._agent_factory else None
        if agent is None:
            Logger.warning(f"[SafetyStrategy] Unknown or unavailable agent: {agent_name}")
        return agent

    def execute_agent(
        self,
        agent: Any,
        agent_name: str,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters

        Returns:
            Dictionary with execution results
        """
        import time

        start_time = time.time()

        try:
            if hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=dry_run, execute=execute)
                execution_time_ms = (time.time() - start_time) * 1000

                return {
                    "status": "PASS" if result.get("errors", 0) == 0 else "FAIL",
                    "violations_found": result.get("violations", 0),
                    "violations_fixed": result.get("fixed", 0),
                    "execution_time_ms": execution_time_ms,
                    "error_message": None,
                }
            else:
                return {
                    "status": "ERROR",
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "execution_time_ms": 0,
                    "error_message": f"{agent_name} has no heal_repository method",
                }
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            return {
                "status": "ERROR",
                "violations_found": 0,
                "violations_fixed": 0,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    def should_abort_tier(self, tier_name: str, tier_results: list[dict[str, Any]], execute: bool) -> bool:
        """
        Determine if execution should abort after a tier.

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        """
        # Abort on Tier 0 (Pre-Flight) failures
        if "Tier 0" in tier_name:
            for result in tier_results:
                if result.get("status") == "FAIL":
                    return True

        return False
