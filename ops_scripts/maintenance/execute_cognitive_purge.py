#!/usr/bin/env python3
"""
[PHASE 13] AI-Purge Sentinel - Cognitive Batch Execution Driver.

Executes the AI-driven architectural purge using Gemini LLM with:
- Batch processing for 2,160+ violations
- Rate limiting to respect API quotas
- Progress checkpointing for resumable execution
- Exponential backoff for API errors

This script ties the CognitiveBatchProcessor to the ArchivalGatekeeper,
enabling mass-movement of files based on Gemini's JSON decisions.

Usage:
    # Set API key first
    export GEMINI_API_KEY="your-api-key"

    # Run cognitive purge (analysis only)
    python scripts/maintenance/execute_cognitive_purge.py

    # Run with custom rate limit (default: 1.0s)
    python scripts/maintenance/execute_cognitive_purge.py --rate-limit 2.0

    # Clear checkpoint and start fresh
    python scripts/maintenance/execute_cognitive_purge.py --clear-checkpoint

Exit Codes:
    0 - Purge completed successfully
    1 - No API key found
    2 - Error during execution
"""

import argparse
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
Logger = logging.getLogger("CognitivePurge")


def run_cognitive_purge(
    rate_limit: float = 1.0,
    checkpoint_file: str = "cognitive_checkpoint.json",
    clear_checkpoint: bool = False,
) -> int:
    """
    Execute the AI-driven cognitive purge.

    Args:
        rate_limit: Seconds to wait between API calls
        checkpoint_file: Path to checkpoint file
        clear_checkpoint: If True, clear existing checkpoint

    Returns:
        Exit code (0=success, 1=no API key, 2=error)
    """
    # Load .env file first
    try:
        from dotenv import find_dotenv, load_dotenv

        env_file = find_dotenv(usecwd=True)
        if env_file:
            load_dotenv(env_file)
            Logger.info(f"Loaded environment from: {env_file}")
    except ImportError:
        pass

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        Logger.error("[FAIL] GEMINI_API_KEY not found in environment.")
        Logger.info("Set it with: export GEMINI_API_KEY='your-api-key'")
        return 1

    try:
        # Add project root to path
        project_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(project_root))

        from agentic_core.L5_safety.validators import (
            ArchitectureGovernorAgent,
        )

        Logger.info("=" * 60)
        Logger.info("PHASE 13: AI-PURGE SENTINEL")
        Logger.info("=" * 60)
        Logger.info(f"Project Root: {project_root}")
        Logger.info(f"Rate Limit: {rate_limit}s between API calls")
        Logger.info(f"Checkpoint: {checkpoint_file}")
        Logger.info("")

        # Clear checkpoint if requested
        if clear_checkpoint:
            checkpoint_path = project_root / checkpoint_file
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                Logger.info("[OK] Checkpoint cleared")

        # Initialize Governor
        Logger.info("Initializing ArchitectureGovernorAgent...")
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            healing_enabled=False,  # Analysis only for now
        )

        # Enable LLM in cognitive agent
        cognitive = agent._get_cognitive_agent()
        cognitive.llm_enabled = True
        cognitive.api_key = api_key

        Logger.info("Cognitive agent configured with LLM enabled")
        Logger.info("")

        # Execute cognitive purge
        result = agent.execute_cognitive_purge(
            checkpoint_file=checkpoint_file,
            rate_limit_delay=rate_limit,
        )

        # Display results
        Logger.info("")
        Logger.info("=" * 60)
        Logger.info("COGNITIVE PURGE RESULTS")
        Logger.info("=" * 60)

        violations_found = result.get("violations_found", 0)
        batch_stats = result.get("batch_stats", {})
        results_stats = result.get("results_stats", {})

        Logger.info(f"Violations Found: {violations_found}")
        Logger.info("")
        Logger.info("Batch Statistics:")
        Logger.info(f"  Processed: {batch_stats.get('PROCESSED', 0)}")
        Logger.info(f"  Skipped (cached): {batch_stats.get('SKIPPED', 0)}")
        Logger.info(f"  Errors: {batch_stats.get('ERRORS', 0)}")
        Logger.info(f"  Total: {batch_stats.get('TOTAL', 0)}")
        Logger.info("")
        Logger.info("Results Statistics:")
        Logger.info(f"  Total Analyzed: {results_stats.get('total', 0)}")
        Logger.info(f"  Average Confidence: {results_stats.get('avg_confidence', 0.0):.2%}")
        Logger.info("")
        Logger.info("Actions by Type:")
        for action, count in sorted(results_stats.get("by_action", {}).items()):
            Logger.info(f"  {action}: {count}")
        Logger.info("")
        Logger.info(f"Checkpoint saved to: {result.get('checkpoint_file', checkpoint_file)}")
        Logger.info("=" * 60)

        Logger.info("")
        Logger.info("[OK] Cognitive purge completed successfully.")
        Logger.info("")
        Logger.info("Next Steps:")
        Logger.info("1. Review the checkpoint file for disposition decisions")
        Logger.info("2. Run with --execute flag to apply the decisions (future)")
        Logger.info("3. Or manually review and apply selected decisions")

        return 0

    except ImportError as e:
        Logger.error(f"[ERROR] Import Error: {e}")
        Logger.error("Ensure agentic_core is properly installed.")
        return 2
    except Exception as e:
        raise
        Logger.error(f"[ERROR] Execution Error: {e}")
        import traceback

        traceback.print_exc()
        return 2


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Execute AI-driven cognitive purge with Gemini LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage (requires GEMINI_API_KEY)
    python scripts/maintenance/execute_cognitive_purge.py

    # Custom rate limit (slower = safer)
    python scripts/maintenance/execute_cognitive_purge.py --rate-limit 2.0

    # Clear checkpoint and start fresh
    python scripts/maintenance/execute_cognitive_purge.py --clear-checkpoint
        """,
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Seconds to wait between API calls (default: 1.0)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="cognitive_checkpoint.json",
        help="Path to checkpoint file (default: cognitive_checkpoint.json)",
    )
    parser.add_argument(
        "--clear-checkpoint",
        action="store_true",
        help="Clear existing checkpoint and start fresh",
    )

    args = parser.parse_args()

    return run_cognitive_purge(
        rate_limit=args.rate_limit,
        checkpoint_file=args.checkpoint,
        clear_checkpoint=args.clear_checkpoint,
    )


if __name__ == "__main__":
    sys.exit(main())
