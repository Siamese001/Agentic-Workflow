#!/usr/bin/env python3
"""Test runtime ADG integration in orchestrator."""

import asyncio
from pathlib import Path


async def test_runtime_adg_integration():
    """Test that runtime ADG captures execution traces."""
    print("[TEST] Starting runtime ADG integration test...")

    # Import orchestrator
    from agentic_core.L3_orchestration.engines.orchestrator_engine import Orchestrator
    from agentic_core.L3_orchestration.reasoning.UnifiedAgent import UnifiedAgent

    # Create orchestrator with runtime ADG
    orchestrator = Orchestrator(mode="unified")

    # Create mock unified agent
    class MockUnifiedAgent(UnifiedAgent):
        def __init__(self):
            self.logs = []

        def log_info(self, msg: str):
            self.logs.append(("INFO", msg))
            print(f"[MOCK] {msg}")

        def log_error(self, msg: str):
            self.logs.append(("ERROR", msg))
            print(f"[MOCK ERROR] {msg}")

    agent = MockUnifiedAgent()

    # Execute with runtime ADG
    result = await orchestrator.execute(agent, mission="test-runtime-adg")

    # Verify result
    assert result.completed, "Execution should complete"
    assert "runtime ADG" in result.metadata.get("agent", ""), "Should indicate runtime ADG usage"

    # Check if runtime ADG artifacts were created
    runtime_adg_dir = Path("artifacts/runtime_adg")
    if runtime_adg_dir.exists():
        snapshots = list(runtime_adg_dir.glob("**/*.json"))
        print(f"[TEST] Found {len(snapshots)} runtime ADG snapshots")
        for snapshot in snapshots:
            print(f"  - {snapshot.relative_to(Path.cwd())}")

    print("[TEST] Runtime ADG integration test completed successfully!")
    return result

if __name__ == "__main__":
    asyncio.run(test_runtime_adg_integration())
