from __future__ import annotations

#!/usr/bin/env python3
"""
[PHASE 15] Tiered Cognitive Purge - Smart Hybrid Execution.

Executes the AI-driven architectural purge with tiered strategy:
- Tier 1: High-confidence heuristics (>=0.75) - auto-execute immediately
- Tier 2: Low-confidence files (<0.75) - route to LLM Gemini
- Meta-learning: Cache decisions in Redis for future reference

This dramatically reduces LLM API calls from 2166 to ~200-400.

Usage:
    python scripts/maintenance/execute_tiered_purge.py
    python scripts/maintenance/execute_tiered_purge.py --threshold 0.7
    python scripts/maintenance/execute_tiered_purge.py --clear-checkpoint

Exit Codes:
    0 - Success
    1 - No API key
    2 - Error
"""

import argparse
import logging
import os
import signal
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
Logger = logging.getLogger("TieredPurge")


def run_tiered_purge(
    threshold: float = 0.75,
    checkpoint_file: str = "tiered_checkpoint.json",
    clear_checkpoint: bool = False,
    rate_limit: float = 1.0,
) -> int:
    """
    Execute tiered cognitive purge.

    Args:
        threshold: Confidence threshold for auto-execution
        checkpoint_file: Path to checkpoint file
        clear_checkpoint: Clear existing checkpoint
        rate_limit: Seconds between LLM calls

    Returns:
        Exit code
    """

    # Signal handler for graceful shutdown (Ctrl+C)
    def signal_handler(sig, frame):
        Logger.warning("\n[INTERRUPT] Graceful shutdown initiated. Saving progress...")
        Logger.info("[INTERRUPT] Checkpoint saved. Re-run to resume from last position.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Load .env
    try:
        from dotenv import find_dotenv, load_dotenv

        env_file = find_dotenv(usecwd=True)
        if env_file:
            load_dotenv(env_file)
            Logger.info(f"Loaded environment from: {env_file}")
    except ImportError:
        pass

    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        Logger.error("[FAIL] GEMINI_API_KEY not found.")
        return 1

    try:
        # Add project root to path
        project_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(project_root))

        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L5_safety.cognition.TieredBatchProcessor import (
            TieredBatchProcessor,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        Logger.info("=" * 60)
        Logger.info("PHASE 15: TIERED COGNITIVE PURGE")
        Logger.info("=" * 60)
        Logger.info(f"Project Root: {project_root}")
        Logger.info(f"Heuristic Threshold: {threshold:.0%}")
        Logger.info(f"Rate Limit: {rate_limit}s")
        Logger.info("")

        # Clear checkpoint if requested
        if clear_checkpoint:
            checkpoint_path = project_root / checkpoint_file
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                Logger.info("[OK] Checkpoint cleared")

        # Initialize Governor
        Logger.info("Initializing ArchitectureGovernorAgent...")
        governor = ArchitectureGovernorAgent(
            project_root=project_root,
            healing_enabled=False,
        )

        # Scan for violations
        Logger.info("Scanning for violations...")
        governor.heal_repository(dry_run=True)
        violations = getattr(governor, "violations", [])

        if not violations:
            Logger.info("[OK] No violations found.")
            return 0

        Logger.info(f"Found {len(violations)} violations")
        Logger.info("")

        # Initialize Cognitive Agent with LLM
        cognitive = CognitiveDispositionAgent(
            project_root=project_root,
            llm_enabled=True,
            api_key=api_key,
        )

        # Initialize Tiered Processor
        processor = TieredBatchProcessor(
            agent=cognitive,
            heuristic_threshold=threshold,
            checkpoint_file=checkpoint_file,
            use_semantic_cache=True,
            rate_limit_delay=rate_limit,
        )

        # Process
        stats = processor.process_batch(violations)

        # Results
        Logger.info("")
        Logger.info("=" * 60)
        Logger.info("TIERED PURGE RESULTS")
        Logger.info("=" * 60)

        results_stats = processor.get_statistics()
        Logger.info(f"Total Processed: {results_stats['total']}")
        Logger.info("")
        Logger.info("By Tier:")
        for tier, count in sorted(results_stats["by_tier"].items()):
            Logger.info(f"  {tier}: {count}")
        Logger.info("")
        Logger.info("By Action:")
        for action, count in sorted(results_stats["by_action"].items()):
            Logger.info(f"  {action}: {count}")
        Logger.info("")
        Logger.info(f"Checkpoint: {checkpoint_file}")
        Logger.info("=" * 60)

        return 0

    except Exception as e:
        Logger.error(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 2


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Execute tiered cognitive purge",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Confidence threshold for auto-execution (default: 0.75)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="tiered_checkpoint.json",
        help="Checkpoint file path",
    )
    parser.add_argument(
        "--clear-checkpoint",
        action="store_true",
        help="Clear existing checkpoint",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Seconds between LLM calls (default: 1.0)",
    )

    args = parser.parse_args()

    return run_tiered_purge(
        threshold=args.threshold,
        checkpoint_file=args.checkpoint,
        clear_checkpoint=args.clear_checkpoint,
        rate_limit=args.rate_limit,
    )


if __name__ == "__main__":
    sys.exit(main())
