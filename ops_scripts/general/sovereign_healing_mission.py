#!/usr/bin/env python3
"""
SOVEREIGN HEALING MISSION
-------------------------
Executes the LocationAgent with Shared Alignment Intelligence.
Scans the repository for generic utilities hiding in domain folders
and upgrades them to apps_shared/utils under strict circuit breaker limits.
"""

import logging
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    get_validated_project_root,
)

project_root = get_validated_project_root()

from agentic_core.L4_state.memory.runtime_state_guard import RuntimeStateGuard
from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [SovereignMission] - %(message)s",
)
logger = logging.getLogger(__name__)


def run_mission():
    logger.info("Initializing Sovereign Healing Mission...")

    # 1. Initialize Agent
    agent = LocationHealerAgent(project_root=project_root)
    state_guard = RuntimeStateGuard(project_root)

    # Enable autonomous mode for intelligent decision-making without user prompts
    agent._autonomous_mode = True

    healer = agent

    logger.info("🤖 Autonomous mode ENABLED - No user prompts required")

    # 2. Log Pre-Mission State
    initial_upgrades = state_guard.get_metric("upgrade_count", 0)
    logger.info(f"Initial Upgrade Count: {initial_upgrades}")
    logger.info("Circuit Breaker Limit: 10 per run")

    # 3. Target Territories for Scan
    # We focus on the high-probability drift zones
    target_zones = [project_root / APPS_RG_DIR, project_root / APPS_LIC_DIR]

    logger.info(f"Scanning Target Zones: {[str(z.name) for z in target_zones]}")

    # 4. Execute Scan with Batch Optimization
    # The agent handles the batch context internally for files_scanned,
    # but we wrap the high-level loop for safety.
    files_processed = 0
    violations_found = []

    for zone in target_zones:
        if not zone.exists():
            logger.warning(f"Zone not found: {zone}")
            continue

        for path in zone.rglob("*.py"):
            if APPS_SHARED_DIR in str(path):
                continue

            try:
                # Validate file location (this triggers telemetry internally)
                is_valid, reason = agent.validate_file_location(path)
                files_processed += 1

                if not is_valid:
                    violations_found.append((path, reason))
                    logger.info(f"Violation found: {path.name} - {reason}")

                if files_processed % 100 == 0:
                    logger.info(f"Progress: {files_processed} files scanned...")

            except Exception as e:
                logger.error(f"Error processing {path.name}: {e}")

    # 5. Heal Violations (if any)
    if violations_found:
        logger.info(f"Found {len(violations_found)} violations, attempting healing...")
        healing_results = agent.cleanup_violations(violations_found, dry_run=False)
        logger.info(f"Healing completed: {len(healing_results)} actions taken")
    else:
        logger.info("No violations found - repository is compliant!")

    # 6. Report Telemetry
    final_upgrades = state_guard.get_metric("upgrade_count", 0)
    total_scanned = state_guard.get_metric("files_scanned", 0)
    delta_upgrades = final_upgrades - initial_upgrades

    logger.info("=" * 40)
    logger.info("MISSION COMPLETE")
    logger.info(f"Total Files Scanned (Lifetime): {total_scanned}")
    logger.info(f"New Upgrades Performed: {delta_upgrades}")
    logger.info(f"Total Shared Upgrades: {final_upgrades}")
    logger.info("=" * 40)


if __name__ == "__main__":
    run_mission()
