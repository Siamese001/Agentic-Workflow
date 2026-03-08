from __future__ import annotations

"""
HealingStrategy - Tiered Healing Execution Strategy

This strategy encapsulates the healing logic currently in SSOTOrchestratorAgent,
implementing the 5-tier execution flow for repository healing.

TIERS:
    Tier 0: Pre-Flight - Syntax validation (must pass before anything else)
    Tier 1: Structural - Identity collisions, hygiene, naming, location
    Tier 2: Architectural - Gravity enforcement, deep deduplication
    Tier 3: Dynamic - Code SSOT enforcement, runtime checks
    Tier 4: Final Gate - Safety validation, final checks

USAGE:
    from agentic_core.L3_orchestration.unified_orchestrator import Orchestrator

    strategy = HealingStrategy(project_root=Path.cwd())
    orchestrator = Orchestrator(strategy=strategy)
    result = orchestrator.run_mission({"dry_run": True})
"""


import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.config.core.hygiene_registry_config import (
    CORE_HYGIENE_AGENTS,
)

Logger = logging.getLogger(__name__)


class HealingStrategy:
    """
    Tiered healing execution strategy.

    Implements the MissionStrategy protocol for the Orchestrator.
    Encapsulates the 5-tier healing execution flow from SSOTOrchestratorAgent.
    """

    def __init__(self, project_root: Path | None = None, target_tier: int | None = None) -> None:
        """
        Initialize the healing strategy.

        Args:
            project_root: Root path for the project (defaults to cwd)
            target_tier: If specified, only run this tier (0-4). None runs all tiers.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.target_tier = target_tier
        self._agents: dict[str, Any] = {}
        self._dedup_agent: Any | None = None

        # Define the 5-tier execution plan using core registry
        self._tiers: dict[str, list[str]] = {
            "Tier 0: Pre-Flight": CORE_HYGIENE_AGENTS["tier_0_preflight"],
            "Tier 1: Structural": [
                "TwoPhaseDeduplicationAgent_PhaseA",  # Identity collisions (early)
            ]
            + CORE_HYGIENE_AGENTS["tier_1_structural"],
            "Tier 2: Architectural": [
                "StructuralHealerAgent",  # File relocation, fission/fusion (WIRED)
            ]
            + CORE_HYGIENE_AGENTS["tier_2_architectural"]
            + [
                "TwoPhaseDeduplicationAgent_PhaseB",  # Logic duplicates (late)
            ],
            "Tier 3: Dynamic": [
                "CodeEnforcerAgent",
            ]
            + CORE_HYGIENE_AGENTS["tier_3_autonomy"],
            "Tier 4: Final Gate": [
                # Reserved for future safety validators
            ],
        }

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return "HealingStrategy"

    def get_tiers(self) -> dict[str, list[str]]:
        """
        Return the tiered execution plan.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        """
        # Filter out empty tiers
        return {k: v for k, v in self._tiers.items() if v}

    def should_run_tier(self, tier_name: str) -> bool:
        """
        Check if a tier should be executed based on target_tier filter.

        Args:
            tier_name: Name of the tier (e.g., "Tier 0: Pre-Flight")

        Returns:
            True if the tier should run, False to skip
        """
        if self.target_tier is None:
            return True  # No filter, run all tiers

        # Extract tier number from name (e.g., "Tier 0: Pre-Flight" -> 0)
        try:
            tier_num = int(tier_name.split(":")[0].replace("Tier", "").strip())
            return tier_num == self.target_tier
        except (ValueError, IndexError):
            Logger.warning(f"[HealingStrategy] Could not parse tier number from: {tier_name}")
            return False

    def get_tier_skip_message(self, tier_name: str) -> str:
        """
        Get a message explaining why a tier is being skipped.

        Args:
            tier_name: Name of the tier being skipped

        Returns:
            Skip message for logging
        """
        return f"⏭️  SKIPPING {tier_name} (target_tier={self.target_tier})"

    def get_agent(self, agent_name: str) -> Any | None:
        """
        Get or create an agent instance by name.

        Uses lazy loading to instantiate agents only when needed.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        """
        # Handle two-phase deduplication specially (shared instance)
        if agent_name.startswith("TwoPhaseDeduplicationAgent"):
            return self._get_dedup_agent()

        if agent_name in self._agents:
            return self._agents[agent_name]

        try:
            agent = self._load_agent(agent_name)
            if agent:
                self._agents[agent_name] = agent
            return agent
        except Exception as e:
            Logger.error(f"[HealingStrategy] Failed to load {agent_name}: {e}")
            return None

    def _get_dedup_agent(self) -> Any | None:
        """Get or create the shared TwoPhaseDeduplicationAgent instance."""
        if self._dedup_agent is None:
            try:
                from agentic_core.L5_safety.enforcement.TwoPhaseDeduplicationAgent import (
                    TwoPhaseDeduplicationAgent,
                )

                self._dedup_agent = TwoPhaseDeduplicationAgent(project_root=self.project_root)
            except Exception as e:
                Logger.error(f"[HealingStrategy] Failed to load TwoPhaseDeduplicationAgent: {e}")
                return None
        return self._dedup_agent

    def _load_agent(self, agent_name: str) -> Any | None:
        """
        Load an agent by name.

        Args:
            agent_name: Name of the agent to load

        Returns:
            Agent instance or None if not available
        """
        try:
            if agent_name == "CodeValidatorAgent":
                from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (
                    CodeValidatorAgent,
                )

                return CodeValidatorAgent()

            elif agent_name == "HygieneGuardianAgent":
                from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
                    HygieneGuardianAgent,
                )

                return HygieneGuardianAgent(project_root=self.project_root)

            elif agent_name == "StructureEnforcerAgent":
                from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import (
                    StructureEnforcerAgent,
                )

                return StructureEnforcerAgent(project_root=self.project_root)

            elif agent_name == "NamingAgent":
                from agentic_core.L5_safety.reasoning.NamingAgent import NamingAgent

                return NamingAgent(project_root=self.project_root)

            elif agent_name == "LocationAgent":
                from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent

                return LocationAgent(project_root=self.project_root)

            elif agent_name == "CodeEnforcerAgent":
                from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import (
                    CodeEnforcerAgent,
                )

                return CodeEnforcerAgent()

            elif agent_name == "StructuralHealerAgent":
                from agentic_core.L5_safety.enforcement.StructuralHealerAgent import (
                    StructuralHealerAgent,
                )

                return StructuralHealerAgent(project_root=self.project_root)

            # Core Hygiene Agents
            elif agent_name == "ImportAgent":
                # Phase 5 Migration: ImportAgent -> CodeHealerAgent
                from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
                    create_legacy_import_healer,
                )

                return create_legacy_import_healer()

            elif agent_name == "HierarchyAgent":
                from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

                return HierarchyAgent(project_root=self.project_root)

            elif agent_name == "CodeDeduplicationAgent":
                from agentic_core.L5_safety.validators.CodeDeduplicationAgent import (
                    CodeDeduplicationAgent,
                )

                return CodeDeduplicationAgent()

            elif agent_name == "FilesystemSSOTReconcilerAgent":
                from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
                    FilesystemSSOTReconcilerAgent,
                )

                return FilesystemSSOTReconcilerAgent(project_root=self.project_root)

            elif agent_name == "GitHygieneAgent":
                from agentic_core.L5_safety.reasoning.GitHygieneAgent import GitHygieneAgent

                return GitHygieneAgent(project_root=self.project_root, ctx=None)

            elif agent_name == "FileCleanupAgent":
                from agentic_core.L5_safety.enforcement.FileCleanupAgent import FileCleanupAgent

                return FileCleanupAgent(project_root=self.project_root, ctx=None)

            elif agent_name == "AutonomyGuardianAgent":
                from agentic_core.L5_safety.validators.AutonomyGuardianAgent import (
                    AutonomyGuardianAgent,
                )

                return AutonomyGuardianAgent(project_root=self.project_root)

            elif agent_name == "CodeJanitorAgent":
                from agentic_core.L5_safety.validators.CodeJanitorAgent import CodeJanitorAgent

                return CodeJanitorAgent()

            else:
                Logger.warning(f"[HealingStrategy] Unknown agent: {agent_name}")
                return None

        except ImportError as e:
            Logger.error(f"[HealingStrategy] Import error for {agent_name}: {e}")
            return None

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
                route_decision_artifact: audit payload dict from L3 routing
                    (required under V15; ignored otherwise)

        Returns:
            Dictionary with execution results
        """
        # §3.1 — Under V15, require RouteDecisionArtifact before healing
        from agentic_core.L0_routing.types.routing_contracts_types import (
            enforce_route_decision_presence,
        )

        audit_payload = kwargs.get("route_decision_artifact")
        enforce_route_decision_presence(audit_payload)

        start_time = datetime.now()

        try:
            # Handle two-phase deduplication specially
            if agent_name == "TwoPhaseDeduplicationAgent_PhaseA":
                Logger.info("[PHASE A] Running Shallow Duplicate Check...")
                result = agent.heal_repository(dry_run=dry_run, execute=execute, phase="A")
            elif agent_name == "TwoPhaseDeduplicationAgent_PhaseB":
                Logger.info("[PHASE B] Running Deep SSOT Duplicate Check...")
                result = agent.heal_repository(dry_run=dry_run, execute=execute, phase="B")
            elif hasattr(agent, "heal_repository"):
                # [PHASE 33j] Propagate all kwargs to agents for future-proof signal continuity
                result = agent.heal_repository(dry_run=dry_run, execute=execute, **kwargs)
            else:
                return {
                    "status": "ERROR",
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "error_message": f"Agent {agent_name} missing heal_repository()",
                }

            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Normalize result to standard format
            return self._normalize_result(result, execution_time_ms)

        except Exception as e:
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            Logger.error(f"[HealingStrategy] Error executing {agent_name}: {e}")
            return {
                "status": "ERROR",
                "violations_found": 0,
                "violations_fixed": 0,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    def _normalize_result(self, result: dict[str, Any], execution_time_ms: float) -> dict[str, Any]:
        """
        Normalize agent result to standard format.

        Args:
            result: Raw result from agent
            execution_time_ms: Execution time in milliseconds

        Returns:
            Normalized result dictionary
        """
        # Handle various result formats
        violations_found = (
            result.get("violations_found") or result.get("violations") or result.get("errors") or 0
        )

        violations_fixed = result.get("violations_fixed") or result.get("fixed") or 0

        # Determine status
        status = result.get("status")
        if not status:
            if result.get("error_message"):
                status = "ERROR"
            elif violations_found == 0:
                status = "PASS"
            elif violations_fixed >= violations_found:
                status = "PASS"
            else:
                status = "FAIL"

        return {
            "status": status,
            "violations_found": violations_found,
            "violations_fixed": violations_fixed,
            "execution_time_ms": execution_time_ms,
            "error_message": result.get("error_message"),
            "raw_result": result,
        }

    def should_abort_tier(self, tier_name: str, tier_results: list[dict[str, Any]], execute: bool) -> bool:
        """
        Determine if execution should abort after a tier.

        Implements stability gates:
        - Tier 0 (Pre-Flight): Always fatal if failed (syntax must be valid)
        - Tier 1 (Structural): Fatal only during execute mode

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        """
        # Check if any agent failed or errored
        has_failure = any(r.get("status") in ("FAIL", "ERROR") for r in tier_results)

        if not has_failure:
            return False

        # Gate 1: Pre-Flight (Syntax) - Always fatal
        if "Tier 0" in tier_name or "Pre-Flight" in tier_name:
            Logger.error("🛑 CRITICAL GATE: Syntax Validation Failed. Aborting Mission.")
            return True

        # Gate 2: Structural - Fatal only during execute mode
        if ("Tier 1" in tier_name or "Structural" in tier_name) and execute:
            Logger.error("🛑 STABILITY GATE: Structural violations persist. Aborting.")
            return True

        return False


__all__ = [
    "HealingStrategy",
]
