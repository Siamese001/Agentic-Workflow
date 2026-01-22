#!/usr/bin/env python3
"""
archive_legacy_orchestrators.py - Phase 1 Orchestrator Liquidation

Archives legacy orchestrator files that have been replaced by:
- CoreOrchestrationAgent (L3)
- AppWorkflowOrchestratorAgent (L3)

Based on WORKER_AGENT_CONSOLIDATION_REPORT_V2.md Phase 1 consolidation.

Usage:
    python scripts/archive_legacy_orchestrators.py --dry-run
    python scripts/archive_legacy_orchestrators.py
"""

import argparse
import shutil
import sys

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "archives" / "legacy_orchestrators"

# Legacy orchestrators to archive - these were consolidated into CoreOrchestrationAgent
LEGACY_L3_ORCHESTRATORS: list[str] = [
    # Merged into CoreOrchestrationAgent
    "CachedOrchestratorAgent.py",
    "SelfRecoveringOrchestratorAgent.py",
    "IntelligentOrchestratorAgent.py",
    "HardenedWorkflowOrchestratorAgent.py",
    "ConsolidatedOrchestratorAgent.py",
    # Other legacy orchestrators
    "OrchestratorAgentAndScopeManagerAgent.py",
    "ScriptsPlanningOrchestratorAgent.py",
    "PilotOrchestratorAgent.py",
    "WorkflowOrchestratorAgent.py",
    "ResumeOrchestratorAgent.py",
    "UnifiedOrchestratorAgent.py",  # Top-level duplicate
]

# Apps layer orchestrators merged into AppWorkflowOrchestratorAgent
LEGACY_APPS_ORCHESTRATORS: list[str] = [
    "LicWorkflowOrchestratorAgent.py",
    "OutreachPhase5OrchestratorAgent.py",
    "Phase4OrchestratorAgent.py",
    "Phase6OrchestratorAgent.py",
    "Phase7OrchestratorAgent.py",
    "HOPOrchestratorAgent.py",
    "LicHealingOrchestratorAgent.py",
    "RgHealingOrchestratorAgent.py",
    "RgResumeOrchestratorAgent.py",
]


def find_orchestrator(filename: str) -> Path | None:
    """Find an orchestrator file in the codebase."""
    # Search in L3 orchestration
    for path in (PROJECT_ROOT / "agentic_core" / "L3_orchestration").rglob(filename):
        if "__pycache__" not in str(path) and "unified" not in str(path).lower():
            return path

    # Search in apps_lic
    for path in (PROJECT_ROOT / "apps_lic").rglob(filename):
        if "__pycache__" not in str(path):
            return path

    # Search in apps_rg
    for path in (PROJECT_ROOT / "apps_rg").rglob(filename):
        if "__pycache__" not in str(path):
            return path

    return None


def archive_file(source: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Archive a single file."""
    target = ARCHIVE_DIR / source.name

    if target.exists():
        return False, "Already archived"

    if dry_run:
        return True, f"Would archive to {target.relative_to(PROJECT_ROOT)}"

    try:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return True, f"Archived to {target.relative_to(PROJECT_ROOT)}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Archive legacy orchestrators")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 1 Orchestrator Liquidation - Legacy Archive")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    archived = 0
    skipped = 0
    not_found = 0

    all_orchestrators = LEGACY_L3_ORCHESTRATORS + LEGACY_APPS_ORCHESTRATORS

    print("\n--- L3 Orchestrators ---")
    for filename in LEGACY_L3_ORCHESTRATORS:
        source = find_orchestrator(filename)

        if source is None:
            print(f"  ⊘ NOT FOUND: {filename}")
            not_found += 1
            continue

        success, message = archive_file(source, args.dry_run)

        if success:
            icon = "○" if args.dry_run else "✓"
            print(f"  {icon} {filename}")
            archived += 1
        else:
            if "Already archived" in message:
                print(f"  ⊘ SKIP: {filename} ({message})")
                skipped += 1
            else:
                print(f"  ✗ ERROR: {filename} - {message}")

    print("\n--- Apps Orchestrators ---")
    for filename in LEGACY_APPS_ORCHESTRATORS:
        source = find_orchestrator(filename)

        if source is None:
            print(f"  ⊘ NOT FOUND: {filename}")
            not_found += 1
            continue

        success, message = archive_file(source, args.dry_run)

        if success:
            icon = "○" if args.dry_run else "✓"
            print(f"  {icon} {filename}")
            archived += 1
        else:
            if "Already archived" in message:
                print(f"  ⊘ SKIP: {filename} ({message})")
                skipped += 1
            else:
                print(f"  ✗ ERROR: {filename} - {message}")

    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Archived:  {archived}")
    print(f"  Skipped:   {skipped}")
    print(f"  Not Found: {not_found}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n✓ ORCHESTRATOR LIQUIDATION COMPLETE")

    return 0


if __name__ == "__main__":
    sys.exit(main())
