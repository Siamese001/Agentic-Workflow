"""
Run a sovereign healing mission over selected target zones using LocationHealerAgent.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [SovereignMission] - %(message)s",
)
logger = logging.getLogger(__name__)


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _bootstrap(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))  # guardian: allow-global-mutation -- runtime bootstrap


def run_mission(repo_root: Path, dry_run: bool = True) -> int:
    _bootstrap(repo_root)

    from agentic_core.L0_routing.config.path_constants import APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
    from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard
    # MW-9 (2026-04-24): Class body relocated to utils module.
    from agentic_core.L5_safety.utils.location_healer_util import LocationHealerAgent

    logger.info("Initializing Sovereign Healing Mission...")

    agent = LocationHealerAgent(project_root=repo_root)
    state_guard = RuntimeStateGuard(repo_root)
    agent._autonomous_mode = True  # guardian: allow-global-mutation -- mission mode flag

    logger.info("🤖 Autonomous mode ENABLED - No user prompts required")
    initial_upgrades = state_guard.get_metric("upgrade_count", 0)
    logger.info("Initial Upgrade Count: %s", initial_upgrades)
    logger.info("Circuit Breaker Limit: 10 per run")

    target_zones = [repo_root / APPS_RG_DIR, repo_root / APPS_LIC_DIR]
    logger.info("Scanning Target Zones: %s", [zone.name for zone in target_zones])

    files_processed = 0
    violations_found: list[tuple[Path, str]] = []

    for zone in tqdm(target_zones, desc="Processing", unit="zone"):
        if not zone.exists():
            logger.warning("Zone not found: %s", zone)
            continue

        for path in tqdm(sorted(zone.rglob("*.py")), desc="Processing", unit="file"):
            if APPS_SHARED_DIR in str(path):
                continue
            try:
                is_valid, reason = agent.validate_file_location(path)
                files_processed += 1

                if not is_valid:
                    violations_found.append((path, reason))
                    logger.info("Violation found: %s - %s", path.name, reason)

                if files_processed % 100 == 0:
                    logger.info("Progress: %s files scanned...", files_processed)
            except (AttributeError, ImportError, OSError, RuntimeError, ValueError) as exc:
                logger.error("Error processing %s: %s", path.name, exc)

    if violations_found:
        logger.info("Found %s violations, attempting healing...", len(violations_found))
        healing_results = agent.cleanup_violations(violations_found, dry_run=dry_run)
        logger.info("Healing completed: %s actions taken", len(healing_results))
    else:
        logger.info("No violations found - repository is compliant!")

    final_upgrades = state_guard.get_metric("upgrade_count", 0)
    total_scanned = state_guard.get_metric("files_scanned", 0)
    delta_upgrades = final_upgrades - initial_upgrades

    logger.info("=" * 40)
    logger.info("MISSION COMPLETE")
    logger.info("Total Files Scanned (Lifetime): %s", total_scanned)
    logger.info("New Upgrades Performed: %s", delta_upgrades)
    logger.info("Total Shared Upgrades: %s", final_upgrades)
    logger.info("=" * 40)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the sovereign healing mission.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--execute", action="store_true", help="Actually apply healing instead of dry-run.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    return run_mission(repo_root, dry_run=not args.execute)


if __name__ == "__main__":
    raise SystemExit(main())
