"""
Run FileClassificationAgent on agentic_core with healing enabled.
Generates detailed JSON report of all healing activities.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

# Add project root to path
project_root = get_validated_project_root()
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent


def run_healing_with_detailed_report():
    """Run FileClassificationAgent healing and generate detailed JSON report."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    # Initialize agent targeting agentic_core
    agent = FileClassificationAgent(
        project_root=project_root,
        dry_run=False,  # Actually perform healing
        validate_only=False,
    )

    logger.info("=" * 70)
    logger.info("FILECLASSIFICATIONAGENT - HEALING RUN ON AGENTIC_CORE")
    logger.info("=" * 70)
    logger.info(f"Project Root: {project_root}")
    logger.info("Target: agentic_core")
    logger.info("Mode: HEALING ENABLED (dry_run=False)")
    logger.info("=" * 70)

    # Capture start time
    start_time = datetime.now()

    # Run healing on agentic_core territory
    result = agent.heal_repository(
        dry_run=False,
        execute=True,
        target_territory=AGENTIC_CORE_DIR,
        auto_approve=True,
    )

    # Capture end time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Build detailed report
    detailed_report = {
        "metadata": {
            "run_timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "target_folder": "agentic_core",
            "healing_mode": "EXECUTE",
            "dry_run": False,
            "agent_version": "v5.1-idempotence-hardened",
        },
        "summary": {
            "violations_found": result.get("violations_found", 0),
            "violations_fixed": result.get("violations_fixed", 0),
            "errors": result.get("errors", 0),
            "skipped": result.get("skipped", 0),
        },
        "action_counters": result.get(
            "action_counters",
            {"renames": 0, "territory_moves": 0, "import_fixes": 0, "deep_refactors": 0, "config_updates": 0},
        ),
        "idempotence_cache": {
            "paths_processed": len(agent.processed_paths),
            "cache_was_cleared": True,  # Always cleared in finally block
        },
        "stats": agent.stats,
        "file_classifications": {},
        "healing_actions": [],
    }

    # Capture file registry classifications
    for path in agent.file_registry:
        try:
            rel_path = str(path.relative_to(project_root))
            file_type = agent.classify_file(path)
            detailed_report["file_classifications"][rel_path] = file_type
        except Exception:
            pass

    # Add idempotence verification
    detailed_report["idempotence_verification"] = {
        "description": "Second run should show zero actions if idempotent",
        "recommendation": "Re-run this script to verify zero violations_fixed",
    }

    # Save report to SSOT-approved location (docs/reports/)
    output_path = project_root / "docs" / "reports" / "file_classification_healing_agentic_core.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(detailed_report, f, indent=2, default=str)

    logger.info("=" * 70)
    logger.info("HEALING RUN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Duration: {duration:.2f}s")
    logger.info(f"Violations Found: {result.get('violations_found', 0)}")
    logger.info(f"Violations Fixed: {result.get('violations_fixed', 0)}")
    logger.info(f"Errors: {result.get('errors', 0)}")
    logger.info(f"Skipped: {result.get('skipped', 0)}")
    logger.info("-" * 70)
    logger.info("Action Counters:")
    for action, count in result.get("action_counters", {}).items():
        logger.info(f"  {action}: {count}")
    logger.info("-" * 70)
    logger.info(f"Detailed JSON report saved to: {output_path}")
    logger.info("=" * 70)

    # Print JSON to stdout for immediate visibility
    print("\n" + "=" * 70)
    print("DETAILED HEALING REPORT (JSON)")
    print("=" * 70)
    print(json.dumps(detailed_report, indent=2, default=str))

    return detailed_report


if __name__ == "__main__":
    run_healing_with_detailed_report()
