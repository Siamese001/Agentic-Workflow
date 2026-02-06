from __future__ import annotations

"""Phase 1 Integrity Test with L5 Safety Layer Validation.

This script tests the L5 safety layer integration with the NervousSystem.
It should show L5 validation logs during execution.
"""
import asyncio
import logging
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
Logger: Any = logging.getLogger("Phase1_Integrity_With_L5")


async def test_l5_validation() -> Any:
    """Test L5 safety validation directly."""
    safety_layer: Any = create_l5_safety_layer(cost_limit_usd=5.0)
    safe_request: Any = ActionRequest(
        action_type="tool_execution", parameters={"tool_path": "python", "args": ["--version"]}
    )
    Logger.info("Testing SAFE action validation...")
    is_safe: Any = await safety_layer.validate_action(safe_request)
    Logger.info(f"Safe action result: {is_safe}")
    dangerous_request: Any = ActionRequest(
        action_type="tool_execution", parameters={"tool_path": "rm", "args": ["-rf", "/"]}
    )
    Logger.info("Testing DANGEROUS action validation...")
    is_safe: Any = await safety_layer.validate_action(dangerous_request)
    Logger.info(f"Dangerous action result: {is_safe}")
    stats: Any = safety_layer.get_safety_stats()
    Logger.info(f"Safety stats: {stats}")
    safety_layer.cleanup()


async def run_phase1_with_l5() -> Any:
    """Run Phase 1 mission with L5 safety layer enabled."""
    config: Any = OrchestratorConfig(
        mission_id="integrity-scan-with-l5",
        max_phases=None,
        enable_tri_brain=True,
        timeout_seconds=60,
    )
    Logger.info("Initializing Nervous System with L5 Safety Layer...")
    ns: Any = NervousSystem(config=config)
    Logger.info("Starting Phase 1: Integrity Check with L5 validation...")
    result: Any = await ns.run_mission()
    Logger.info(f"Mission Success: {result.success}")
    Logger.info(f"Mission Output: {result.output}")
    if hasattr(ns, "safety_layer"):
        safety_stats: Any = ns.safety_layer.get_safety_stats()
        Logger.info(f"L5 Safety Statistics: {safety_stats}")
    if result.success:
        Logger.info("✅ Phase 1 completed with L5 safety validation active")
    else:
        Logger.error("❌ Phase 1 failed")
    if hasattr(ns, "safety_layer"):
        ns.safety_layer.cleanup()


async def main() -> Any:
    """Main test runner."""
    Logger.info("=" * 60)
    Logger.info("L5 SAFETY LAYER VALIDATION TEST")
    Logger.info("=" * 60)
    Logger.info("\n1. Testing L5 validation directly...")
    await test_l5_validation()
    Logger.info("\n2. Running full Phase 1 mission with L5...")
    await run_phase1_with_l5()
    Logger.info("\n" + "=" * 60)
    Logger.info("L5 SAFETY VALIDATION COMPLETE")
    Logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
