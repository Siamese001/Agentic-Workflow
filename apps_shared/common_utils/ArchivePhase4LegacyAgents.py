#!/usr/bin/env python3
"""
archive_phase4_legacy_agents.py - Phase 4 Detector/Healer/Router/Executor Hard Migration

Archives legacy agents that have been consolidated into:
- UnifiedCodeDetectorAgent
- UnifiedSafetyDetectorAgent
- UnifiedCodeHealerAgent
- UnifiedStructureHealerAgent
- UnifiedModelRouterAgent
- UnifiedSafetyExecutorAgent

Usage:
    python scripts/archive_phase4_legacy_agents.py --dry-run
    python scripts/archive_phase4_legacy_agents.py
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "archives" / "legacy_agents"

# Phase 4 legacy agents to archive
LEGACY_DETECTORS: list[str] = [
    "BiasDetectorAgent.py",
    "DeadCodeDetectorAgent.py",
    "DeadlockDetectorAgent.py",
    "DriftDetectorAgent.py",
    "HallucinationDetectorAgent.py",
    "MethodChangeDetectorAgent.py",
    "PromptInjectionDetectorAgent.py",
    "MemoryLeakDetectorAgent.py",
]

LEGACY_HEALERS: list[str] = [
    "CanonHealerAgent.py",
    "GravityHealerAgent.py",
    "HealerAgent.py",
    "HierarchyHealerAgent.py",
    "ImportHealerAgent.py",
    "NamingLawHealerAgent.py",
    "StructuralHealerAgent.py",
    "TerritoryHealerAgent.py",
    "BlueprintHierarchyHealerAgent.py",
    "BlueprintHierarchyHealerAgent_1.py",
]

LEGACY_ROUTERS: list[str] = [
    "DynamicModelRouterAgent.py",
    "McpRouterAgent.py",
    "ModelRouterAgent.py",
    "MultiProviderRouterAgent.py",
    "ReasoningRouterAgent.py",
]

LEGACY_EXECUTORS: list[str] = [
    "IntegrityGateExecutorAgent.py",
    "L5IntegrityGateExecutorAgent.py",
    "SafetyExecutorAgent.py",
    "DagExecutorAgent.py",
    "SystemCommandExecutorAgent.py",
]


def find_agent(filename: str) -> Path | None:
    """Find an agent file in the codebase."""
    for path in (PROJECT_ROOT / "agentic_core").rglob(filename):
        path_str = str(path).lower()
        if "__pycache__" not in path_str and "archive" not in path_str and "unified" not in path_str:
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
    parser = argparse.ArgumentParser(description='Archive Phase 4 legacy agents')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 4 Hard Migration - Detector/Healer/Router/Executor Archive")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    total_archived = 0
    total_skipped = 0
    total_not_found = 0

    categories = [
        ("Legacy Detectors", LEGACY_DETECTORS, "legacy_detectors"),
        ("Legacy Healers", LEGACY_HEALERS, "legacy_healers"),
        ("Legacy Routers", LEGACY_ROUTERS, "legacy_routers"),
        ("Legacy Executors", LEGACY_EXECUTORS, "legacy_executors"),
    ]

    for title, agents, category in categories:
        print(f"\n--- {title} ---")
        for filename in agents:
            source = find_agent(filename)

            if source is None:
                print(f"  - NOT FOUND: {filename}")
                total_not_found += 1
                continue

            success, message = archive_file(source, category, args.dry_run)

            if success:
                icon = "o" if args.dry_run else "+"
                print(f"  {icon} {filename}")
                total_archived += 1
            else:
                if "Already archived" in message:
                    print(f"  - SKIP: {filename} ({message})")
                    total_skipped += 1
                else:
                    print(f"  x ERROR: {filename} - {message}")

    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Archived:  {total_archived}")
    print(f"  Skipped:   {total_skipped}")
    print(f"  Not Found: {total_not_found}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n+ PHASE 4 LEGACY ARCHIVE COMPLETE")

    return 0


if __name__ == "__main__":
    sys.exit(main())
