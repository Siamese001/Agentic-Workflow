from dataclasses import dataclass
"""
LicReflectionAgent - Extracted for one-class-per-file pattern.

Originally from: LeadQualityAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin

@dataclass
class LicReflectionAgent(SubatomicTestingMixin, OutreachAgent, MCPHardenedMixin):
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

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
