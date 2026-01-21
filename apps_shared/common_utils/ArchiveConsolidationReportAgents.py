#!/usr/bin/env python3
"""
archive_consolidation_report_agents.py - Archive all legacy agents from WORKER_AGENT_CONSOLIDATION_REPORT.md

Archives agents marked with ⭐ CONSOLIDATE in the report:
- L1 AST Validators (5 agents) -> UnifiedASTValidatorAgent
- L4 Checkpoint/State Managers (5 agents) -> UnifiedCheckpointManagerAgent/UnifiedStateManagementAgent
- L5 Pattern Enforcers (3 agents) -> CodeStandardsEnforcerAgent

Usage:
    python scripts/archive_consolidation_report_agents.py --dry-run
    python scripts/archive_consolidation_report_agents.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "archives" / "consolidated_agents"

# Agents from WORKER_AGENT_CONSOLIDATION_REPORT.md marked with ⭐ CONSOLIDATE
LEGACY_AGENTS: dict[str, list[str]] = {
    # Priority 1: L1 AST Validators -> UnifiedASTValidatorAgent
    "L1_AST_Validators": [
        "BareExceptValidatorAgent.py",
        "EmptyExceptValidatorAgent.py",
        "EvalExecValidatorAgent.py",
        "DangerousBuiltinsValidatorAgent.py",
        "DebuggerValidatorAgent.py",
    ],
    # Priority 2: L4 Checkpoint Managers -> UnifiedCheckpointManagerAgent
    "L4_Checkpoint_Managers": [
        "CheckpointManagerAgent.py",
        "AutonomousCheckpointManagerAgent.py",
    ],
    # Priority 3: L5 Hygiene Validators (already archived in legacy_validators)
    # Skipping - already handled
    # Priority 4: L5 Pattern Enforcers -> CodeStandardsEnforcerAgent
    "L5_Pattern_Enforcers": [
        "BaseClassEnforcerAgent.py",
        "PatternEnforcerAgent.py",
        "TypeHintEnforcementAgent.py",
    ],
    # Priority 5: L4 State Management -> UnifiedStateManagementAgent
    "L4_State_Management": [
        "AutonomousStateGuardianAgent.py",
        "ManifestManagerAgent.py",
        "MemoryManagerAgent.py",
        "ValidationContextManagerAgent.py",
    ],
    # Additional from report appendix
    "L0_Test_Utilities": [
        "MockOrchestratorAgent.py",
        "ScriptToAgentClassifierAgent.py",
        "TestAgent.py",
    ],
    "L3_Exercisers": [
        "GeneralExerciserAgent.py",
        "L1CognitionExerciserAgent.py",
        "L4StateExerciserAgent.py",
        "MetaCoverageOptimizerAgent.py",
    ],
}


def find_agent(filename: str) -> Path | None:
    """Find an agent file in the codebase."""
    # Search in agentic_core
    for path in (PROJECT_ROOT / "agentic_core").rglob(filename):
        path_str = str(path).lower()
        if "__pycache__" not in path_str and "archive" not in path_str:
            return path

    # Search in apps_lic
    for path in (PROJECT_ROOT / "apps_lic").rglob(filename):
        path_str = str(path).lower()
        if "__pycache__" not in path_str and "archive" not in path_str:
            return path

    # Search in apps_rg
    for path in (PROJECT_ROOT / "apps_rg").rglob(filename):
        path_str = str(path).lower()
        if "__pycache__" not in path_str and "archive" not in path_str:
            return path

    return None


def archive_file(source: Path, category: str, dry_run: bool = False) -> tuple[bool, str]:
    """Archive a single file to category subfolder."""
    target_dir = ARCHIVE_DIR / category
    target = target_dir / source.name

    if target.exists():
        return False, "Already archived"

    if dry_run:
        return True, f"Would archive to {target.relative_to(PROJECT_ROOT)}"

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return True, f"Archived to {target.relative_to(PROJECT_ROOT)}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Archive legacy agents from consolidation report")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 70)
    print("WORKER_AGENT_CONSOLIDATION_REPORT.md - Legacy Agent Archive")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    total_archived = 0
    total_skipped = 0
    total_not_found = 0

    for category, agents in LEGACY_AGENTS.items():
        print(f"\n--- {category} ---")

        for filename in agents:
            source = find_agent(filename)

            if source is None:
                print(f"  ⊘ NOT FOUND: {filename}")
                total_not_found += 1
                continue

            success, message = archive_file(source, category, args.dry_run)

            if success:
                icon = "○" if args.dry_run else "✓"
                print(f"  {icon} {filename}")
                total_archived += 1
            else:
                if "Already archived" in message:
                    print(f"  ⊘ SKIP: {filename} ({message})")
                    total_skipped += 1
                else:
                    print(f"  ✗ ERROR: {filename} - {message}")

    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Archived:  {total_archived}")
    print(f"  Skipped:   {total_skipped}")
    print(f"  Not Found: {total_not_found}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n✓ CONSOLIDATION REPORT ARCHIVE COMPLETE")

    return 0


if __name__ == "__main__":
    sys.exit(main())
