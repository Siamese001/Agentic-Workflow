#!/usr/bin/env python3
"""
[PHASE 12] Cognitive Subset Tester - LLM Reasoning Validation.

Runs actual Gemini API calls on a random sample of ORPHAN violations
to test the LLM's reasoning without incurring the cost of processing
all 2,160+ files.

Usage:
    # Set API key first
    export GEMINI_API_KEY="your-api-key"
    
    # Run subset test (default: 5 files)
    python scripts/maintenance/test_cognitive_subset.py
    
    # Run with custom sample size
    python scripts/maintenance/test_cognitive_subset.py --sample 10

Exit Codes:
    0 - Test completed successfully
    1 - No API key found
    2 - Error during execution
"""
from __future__ import annotations

import argparse
import logging
import os
import random
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
Logger = logging.getLogger("CognitiveSubsetTest")


def run_subset_test(sample_size: int = 5) -> int:
    """
    Run cognitive disposition test on a random subset of violations.
    
    Args:
        sample_size: Number of files to test
    
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

        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        Logger.info("=" * 60)
        Logger.info("PHASE 12: COGNITIVE SUBSET TEST")
        Logger.info("=" * 60)
        Logger.info(f"Project Root: {project_root}")
        Logger.info(f"Sample Size: {sample_size}")
        Logger.info("")

        # Initialize Governor in audit mode (no healing)
        Logger.info("Initializing ArchitectureGovernorAgent...")
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            healing_enabled=False,
        )

        # Run dry-run audit to get violations
        Logger.info("Running dry-run audit to collect violations...")
        report = agent.heal_repository(dry_run=True)

        # Get violations from the agent
        all_violations = getattr(agent, "violations", [])

        # Filter for ORPHAN violations
        orphans = []
        for v in all_violations:
            v_type = None
            file_path = None

            if hasattr(v, "violation_type"):
                v_type = v.violation_type.name if hasattr(v.violation_type, "name") else str(v.violation_type)
                file_path = getattr(v, "file_path", None)
            elif isinstance(v, dict):
                v_type = v.get("type", "")
                file_path = v.get("file")

            if v_type == "ORPHAN" and file_path:
                orphans.append({"type": v_type, "file": Path(file_path)})

        Logger.info(f"Found {len(orphans)} ORPHAN violations")

        if not orphans:
            Logger.info("[OK] No orphans found to test.")
            return 0

        # Select random subset
        subset = random.sample(orphans, min(len(orphans), sample_size))

        Logger.info("")
        Logger.info(f"[SCAN] Testing Gemini Reasoning on {len(subset)} files...")
        Logger.info("=" * 60)

        # Initialize Cognitive Agent with LLM enabled
        cognitive = CognitiveDispositionAgent(
            project_root=project_root,
            llm_enabled=True,
            api_key=api_key,
        )

        results = []
        for i, violation in enumerate(subset, 1):
            file_path = violation["file"]
            Logger.info("")
            Logger.info(f"[{i}/{len(subset)}] Analyzing: {file_path.name}")
            Logger.info(f"    Path: {file_path}")

            decision = cognitive.analyze_violation(file_path, "ORPHAN")

            Logger.info(f"    Decision: {decision.action}")
            Logger.info(f"    Target: {decision.target_path or 'N/A'}")
            Logger.info(f"    Reason: {decision.reason}")
            Logger.info(f"    Confidence: {decision.confidence * 100:.1f}%")

            results.append({
                "file": file_path.name,
                "action": decision.action,
                "target": decision.target_path,
                "confidence": decision.confidence,
            })

        # Summary
        Logger.info("")
        Logger.info("=" * 60)
        Logger.info("SUMMARY")
        Logger.info("=" * 60)

        action_counts = {}
        for r in results:
            action_counts[r["action"]] = action_counts.get(r["action"], 0) + 1

        for action, count in sorted(action_counts.items()):
            Logger.info(f"  {action}: {count}")

        avg_confidence = sum(r["confidence"] for r in results) / len(results) if results else 0
        Logger.info(f"  Average Confidence: {avg_confidence * 100:.1f}%")

        Logger.info("")
        Logger.info("[OK] Cognitive subset test completed.")
        return 0

    except ImportError as e:
        Logger.error(f"[ERROR] Import Error: {e}")
        return 2
    except Exception as e:
        Logger.error(f"[ERROR] Execution Error: {e}")
        import traceback
        traceback.print_exc()
        return 2


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Gemini LLM reasoning on a subset of violations",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=5,
        help="Number of files to test (default: 5)",
    )

    args = parser.parse_args()
    return run_subset_test(sample_size=args.sample)


if __name__ == "__main__":
    sys.exit(main())
