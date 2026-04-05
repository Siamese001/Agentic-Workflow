"""
TerritoryHealingCoordinator - Simplified coordinator for territory-level healing.

Replaces the complex 7-phase orchestration in execute_ssot.py with a simple,
straightforward approach that allows all agents to heal a territory without
bypasses or complex workarounds.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.base_agents.territory_healer_protocol import (
    HealingContext,
    HealingResult,
    ScanResult,
    TerritoryHealerProtocol,
)

logger = logging.getLogger("TerritoryHealingCoordinator")


@dataclass
class TerritoryHealingReport:
    """Comprehensive report for territory healing."""
    territory: str
    agents_executed: list[str] = field(default_factory=list)
    scan_results: list[ScanResult] = field(default_factory=list)
    healing_results: list[HealingResult] = field(default_factory=list)
    total_violations_found: int = 0
    total_violations_fixed: int = 0
    errors: list[str] = field(default_factory=list)
    success: bool = True


class TerritoryHealingCoordinator:
    """
    Simplified coordinator that orchestrates territory-level healing.

    This replaces the complex phase-based orchestration with a simple approach:
    1. For each agent that can handle the territory:
       - Scan for violations
       - If heal mode enabled: apply healing
    2. Report results

    No cycle detection between agents - only prevent infinite recursion within one agent.
    No SAFETY LOCK - trust the explicit heal flag.
    No complex phase orchestration - just scan and heal.
    """

    def __init__(self, project_root: Path, agents: list[TerritoryHealerProtocol] | None = None):
        self.project_root = Path(project_root).resolve()
        self.agents = agents or []
        self._healing_in_progress: set[str] = set()  # Track agents currently healing (per-territory)

    def register_agent(self, agent: TerritoryHealerProtocol) -> None:
        """Register a healing agent."""
        self.agents.append(agent)
        logger.debug(f"Registered agent: {agent.agent_name}")

    def validate_territory(self, territory: str) -> TerritoryHealingReport:
        """
        Scan a territory for violations without healing.

        Args:
            territory: Territory name to validate

        Returns:
            TerritoryHealingReport with all violations found
        """
        context = HealingContext(
            heal=False,
            project_root=self.project_root,
            verbose=False,
        )
        return self._process_territory(territory, context)

    def heal_territory(self, territory: str, verbose: bool = False) -> TerritoryHealingReport:
        """
        Heal a territory by running all applicable agents.

        Args:
            territory: Territory name to heal
            verbose: Enable verbose logging

        Returns:
            TerritoryHealingReport with healing results
        """
        context = HealingContext(
            heal=True,
            project_root=self.project_root,
            verbose=verbose,
        )
        return self._process_territory(territory, context)

    def _process_territory(
        self,
        territory: str,
        context: HealingContext
    ) -> TerritoryHealingReport:
        """
        Process a territory through all applicable agents.

        Args:
            territory: Territory name
            context: HealingContext with heal flag

        Returns:
            TerritoryHealingReport
        """
        report = TerritoryHealingReport(territory=territory)
        mode = "HEALING" if context.heal else "SCAN-ONLY"

        logger.info(f"=== TERRITORY {mode}: {territory} ===")

        # Find agents that can handle this territory
        applicable_agents = [
            agent for agent in self.agents
            if agent.can_handle(territory)
        ]

        if not applicable_agents:
            logger.warning(f"No agents can handle territory: {territory}")
            report.errors.append(f"No agents registered for territory: {territory}")
            report.success = False
            return report

        logger.info(f"Running {len(applicable_agents)} agents on territory '{territory}'")

        for agent in applicable_agents:
            agent_key = f"{territory}:{agent.agent_name}"

            # Only prevent recursion within the same agent+territory combo
            if agent_key in self._healing_in_progress:
                logger.warning(f"Skipping {agent.agent_name} - already processing {territory}")
                report.errors.append(f"Recursion prevented for {agent.agent_name} on {territory}")
                continue

            try:
                self._healing_in_progress.add(agent_key)

                # Step 1: Scan for violations
                scan_result = agent.scan_territory(territory)
                report.scan_results.append(scan_result)
                report.total_violations_found += scan_result.violations_found

                logger.info(
                    f"  [{agent.agent_name}] Scanned: {scan_result.violations_found} violations"
                )

                # Step 2: Heal if in heal mode and violations exist
                if context.heal and scan_result.violations_found > 0:
                    healing_result = agent.heal_territory(territory, context)
                    report.healing_results.append(healing_result)
                    report.total_violations_fixed += healing_result.violations_fixed
                    report.agents_executed.append(agent.agent_name)

                    logger.info(
                        f"  [{agent.agent_name}] Healed: {healing_result.violations_fixed}/{healing_result.violations_found}"
                    )

                    if healing_result.errors:
                        report.errors.extend(healing_result.errors)
                        logger.warning(f"  [{agent.agent_name}] Errors: {len(healing_result.errors)}")

            except Exception as e:
                error_msg = f"{agent.agent_name} failed on {territory}: {e}"
                logger.exception(error_msg)
                report.errors.append(error_msg)
                report.success = False
            finally:
                self._healing_in_progress.discard(agent_key)

        # Final summary
        if context.heal:
            logger.info(
                f"=== TERRITORY HEALING COMPLETE: {territory} ===\n"
                f"  Agents executed: {len(report.agents_executed)}\n"
                f"  Total violations: {report.total_violations_found}\n"
                f"  Total fixed: {report.total_violations_fixed}"
            )
        else:
            logger.info(
                f"=== TERRITORY SCAN COMPLETE: {territory} ===\n"
                f"  Total violations: {report.total_violations_found}"
            )

        return report

    def heal_all_territories(
        self,
        territories: list[str] | None = None,
        verbose: bool = False
    ) -> dict[str, TerritoryHealingReport]:
        """
        Heal multiple territories.

        Args:
            territories: List of territories to heal (None = auto-detect)
            verbose: Enable verbose logging

        Returns:
            Dict mapping territory name to report
        """
        if territories is None:
            territories = self._auto_detect_territories()

        results = {}
        for territory in territories:
            results[territory] = self.heal_territory(territory, verbose)

        return results

    def _auto_detect_territories(self) -> list[str]:
        """Auto-detect territories from project structure."""
        territories = []

        # Standard territories
        standard_dirs = ["agentic_core", "apps_eval", "apps_exec", "apps_lic",
                        "apps_research", "apps_rfp", "apps_rg", "apps_shared",
                        "system_learning", "tests", "ops_scripts", "tools"]

        for dirname in standard_dirs:
            if (self.project_root / dirname).exists():
                territories.append(dirname)

        return territories
