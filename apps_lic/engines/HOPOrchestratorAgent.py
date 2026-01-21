"""
HOPOrchestrator - HOP-based Workflow Orchestrator for LIC (LinkedIn Canonical)

Extracted from workflow_LIC.py v13.0

This orchestrator coordinates the HOP (Hop-based Orchestration Pipeline) agents
for outreach message generation with:
- S6→S2 meta-loop for factual failures
- S5 retry with temperature escalation for creative failures
- Configuration-driven, agent-agnostic execution
"""

__version__ = "13.0"

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class HOPOrchestratorAgent:
    """
    v13.0: HOP-based Workflow Orchestrator

    BREAKING CHANGE from v12.0:
    - OLD: Monolithic workflow with hardcoded steps
    - NEW: Configuration-driven HOP execution with meta-loops

    Features:
    - Implements S6→S2 meta-loop (Factual failure)
    - Implements S5 retry (Creative failure)
    - Configuration-driven and agent-agnostic
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        agents: dict[str, Any] | None = None,
        state_manager_class: type | None = None,
    ):
        """
        Initialize orchestrator with dependencies.

        Args:
            config: Configuration dict (or loads from config/agent_specs_LIC.json)
            agents: Dict of HOP agents keyed by hop_id (e.g., "HOP-2", "HOP-5")
            state_manager_class: Class to use for state management
        """
        self.config = config or self._load_default_config()
        self.agents = agents or {}
        self.state_manager_class = state_manager_class

        # Get HOP execution order from config
        self.hop_execution_order = self.config.get("hop_execution_order", {}).get("hops", [])

        # Loop limits
        self.max_factual_loops = self.config.get("max_factual_loops", 2)
        self.max_creative_retries = self.config.get("max_creative_retries", 3)

    def _load_default_config(self) -> dict[str, Any]:
        """Load default configuration from file."""
        config_path = Path("config/agent_specs_LIC.json")
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            "hop_execution_order": {"hops": []},
            "max_factual_loops": 2,
            "max_creative_retries": 3,
        }

    def register_agent(self, hop_id: str, agent: Any) -> None:
        """Register a HOP agent."""
        self.agents[hop_id] = agent

    async def execute_workflow(self, mission: Any) -> dict[str, Any]:
        """
        Execute complete workflow using HOP architecture.

        Args:
            mission: Mission specification (OutreachMission or similar)

        Returns:
            Workflow result dictionary with status, message, metrics
        """
        mission_id = getattr(mission, "mission_id", str(mission))

        print(f"\n{'=' * 80}")
        print(f"HOP WORKFLOW ORCHESTRATOR v{__version__}")
        print(f"Mission ID: {mission_id}")
        print(f"{'=' * 80}")

        start_time = datetime.now()

        # Initialize state manager
        if self.state_manager_class:
            state_mgr = self.state_manager_class(mission_id=mission_id)
        else:
            state_mgr = _DummyStateManager(mission_id=mission_id)

        # Track loop counts
        factual_loop_count = 0
        creative_retry_count = 0

        try:
            # Main execution loop
            while True:
                # Execute HOPs in sequence
                for hop_spec in self.hop_execution_order:
                    hop_id = hop_spec.get("hop_id") if isinstance(hop_spec, dict) else hop_spec

                    # Skip if agent not implemented
                    if hop_id not in self.agents:
                        print(f"\n⚠ {hop_id} - Agent not implemented, skipping")
                        continue

                    agent = self.agents[hop_id]

                    try:
                        # Execute agent
                        await agent.execute(state_mgr)

                    except FactualGapError as e:
                        # S6→S2 Meta-Loop triggered
                        factual_loop_count += 1

                        if factual_loop_count >= self.max_factual_loops:
                            print(f"\n✗ Max factual loops ({self.max_factual_loops}) reached - HALTING")
                            raise ValueError(f"Max factual loops exceeded: {e}")

                        print(f"\n⚠ Factual gap detected: {e}")
                        print(f"→ Triggering S6→S2 meta-loop (attempt {factual_loop_count}/{self.max_factual_loops})")

                        # Loop back to HOP-2 (research)
                        break

                    except Exception as e:
                        print(f"\n✗ Error in {hop_id}: {e}")
                        raise

                # Check if we need to retry due to creative failure
                if state_mgr.state_exists("HOP-7"):
                    gate = state_mgr.read_state("HOP-7")
                    decision = gate.get("decision")

                    if decision == "CREATIVE_FAILURE":
                        creative_retry_count += 1

                        if creative_retry_count >= self.max_creative_retries:
                            print(f"\n✗ Max creative retries ({self.max_creative_retries}) reached - HALTING")
                            raise ValueError("Max creative retries exceeded")

                        print("\n⚠ Creative failure detected")
                        print(f"→ Retrying HOP-5 with escalated temperature (attempt {creative_retry_count}/{self.max_creative_retries})")

                        # Escalate temperature
                        base_temp = 0.50
                        new_temp = min(0.95, base_temp + (creative_retry_count * 0.15))

                        # Re-run HOP-5 with higher temperature
                        if "HOP-5" in self.agents:
                            await self.agents["HOP-5"].execute(state_mgr, temperature=new_temp)

                        # Re-run HOP-6 validation
                        if "HOP-6" in self.agents:
                            await self.agents["HOP-6"].execute(state_mgr)

                        continue

                    elif decision == "PASS":
                        # Workflow complete
                        break
                else:
                    # No gate decision yet, continue
                    break

        except Exception as e:
            print(f"\n✗ Workflow failed: {e}")

            return {
                "mission_id": mission_id,
                "status": "failed",
                "error": str(e),
                "workflow_time": (datetime.now() - start_time).total_seconds(),
            }

        # Get workflow results
        workflow_time = (datetime.now() - start_time).total_seconds()

        validation = state_mgr.read_state("HOP-6") if state_mgr.state_exists("HOP-6") else {}
        generation = state_mgr.read_state("HOP-5") if state_mgr.state_exists("HOP-5") else {}

        passed = validation.get("passed", False)
        draft = generation.get("selected_draft", {})

        print(f"\n{'=' * 80}")
        print("WORKFLOW COMPLETE")
        print(f"Status: {'PASS' if passed else 'FAIL'}")
        print(f"Time: {workflow_time:.1f}s")
        print(f"Factual loops: {factual_loop_count}")
        print(f"Creative retries: {creative_retry_count}")
        print(f"{'=' * 80}\n")

        return {
            "mission_id": mission_id,
            "status": "success" if passed else "failed_validation",
            "production_ready": passed,
            "message": draft.get("text", ""),
            "word_count": draft.get("word_count", 0),
            "workflow_time": workflow_time,
            "factual_loop_count": factual_loop_count,
            "creative_retry_count": creative_retry_count,
            "validation_summary": {
                "passed": passed,
                "critical_issues": validation.get("critical_issues", 0),
                "high_issues": validation.get("high_issues", 0),
            },
        }


class FactualGapError(Exception):
    """Raised when a factual gap is detected during validation."""
    pass


class _DummyStateManager:
    """Dummy state manager for testing without real state persistence."""

    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self._states: dict[str, dict] = {}

    def write_state(self, hop_id: str, state: dict) -> None:
        self._states[hop_id] = state

    def read_state(self, hop_id: str) -> dict:
        return self._states.get(hop_id, {})

    def state_exists(self, hop_id: str) -> bool:
        return hop_id in self._states


# Test function
def test_hop_orchestrator():
    """Basic test for HOPOrchestratorAgent."""
    import asyncio

    class MockAgent:
        def __init__(self, hop_id: str):
            self.hop_id = hop_id

        async def execute(self, state_mgr, **kwargs):
            print(f"  [MockAgent] Executing {self.hop_id}")
            state_mgr.write_state(self.hop_id, {"status": "complete"})

    async def run_test():
        config = {
            "hop_execution_order": {
                "hops": [
                    {"hop_id": "HOP-1"},
                    {"hop_id": "HOP-2"},
                    {"hop_id": "HOP-5"},
                    {"hop_id": "HOP-6"},
                    {"hop_id": "HOP-7"},
                ]
            },
            "max_factual_loops": 2,
            "max_creative_retries": 3,
        }

        orchestrator = HOPOrchestratorAgent(config=config)

        # Register mock agents
        for hop_id in ["HOP-1", "HOP-2", "HOP-5", "HOP-6"]:
            orchestrator.register_agent(hop_id, MockAgent(hop_id))

        # Create mock mission
        class MockMission:
            mission_id = "test_001"

        result = await orchestrator.execute_workflow(MockMission())
        print(f"\nResult: {result}")

        assert result["status"] in ("success", "failed_validation")
        print("✓ HOPOrchestratorAgent test passed")

    asyncio.run(run_test())


if __name__ == "__main__":
    test_hop_orchestrator()
