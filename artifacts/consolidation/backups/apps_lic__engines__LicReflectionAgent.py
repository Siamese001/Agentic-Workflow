from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

"""
LicReflectionAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


# STUB: OutreachAgent base class (deprecated)
class OutreachAgent:
    """Legacy base class - use LICAgentBase instead."""

    pass


@dataclass
class LicReflectionAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    Reflects on execution and suggests improvements.

    Analyzes:
    - Passed and failed agents
    - Active signals
    - Campaign readiness
    """

    async def execute(self) -> None:
        """
        Execute reflection on campaign execution.

        Analyzes:
        - Agent results (passed/failed)
        - Active signals
        - Campaign readiness for execution

        Determines if more cycles are needed.
        """
        print(f"   [{self.name}] Reflecting on execution...")

        # Analyze results
        passed_agents: list = []
        failed_agents: list = []

        for agent_name, result in self.ctx.results.items():
            if result.get("passed", False):
                passed_agents.append(agent_name)
            else:
                failed_agents.append(agent_name)

        # Analyze signals
        active_signals: list = list(self.ctx.signals)

        # Determine if more cycles needed
        if active_signals or failed_agents:
            print(f"   [{self.name}] 🔄 More cycles needed (signals: {len(active_signals)})")
        else:
            print(f"   [{self.name}] ✅ Campaign ready for execution")

        self.record_result(True, f"Passed: {len(passed_agents)}, Failed: {len(failed_agents)}")
        print(f"   [{self.name}] ✅ Reflection complete")

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by LicReflectionAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"LicReflectionAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"LicReflectionAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
