import argparse
import os
from pathlib import Path

from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent

# The exact list of 13 files identified in the Agent Overlap Analysis Report
TARGETS = [
    # 1. The 11 Unified Agents (from guardrails)
    "agentic_core/L5_safety/enforcement/CodeDetectorAgent.py",
    "agentic_core/L5_safety/enforcement/CodeEnforcerAgent.py",
    "agentic_core/L5_safety/enforcement/CodeHealerAgent.py",
    "agentic_core/L5_safety/enforcement/CodeValidatorAgent.py",
    "agentic_core/L5_safety/enforcement/ResourceManagerAgent.py",
    "agentic_core/L5_safety/enforcement/SafetyDetectorAgent.py",
    "agentic_core/L5_safety/enforcement/SafetyExecutorAgent.py",
    "agentic_core/L5_safety/enforcement/SecurityManagerAgent.py",
    "agentic_core/L5_safety/enforcement/StructureEnforcerAgent.py",
    "agentic_core/L5_safety/enforcement/StructureHealerAgent.py",
    "agentic_core/L5_safety/enforcement/StructureValidatorAgent.py",
    # 2. The Duplicate Model router (from tool_registry)
    "agentic_core/L2_execution/reasoning/ModelRouterAgent.py",
    # 3. The Duplicate Hygiene Agent (from apps_shared)
    "apps_shared/base_agents/HygieneGuardianAgent.py",
]


def main():
    parser = argparse.ArgumentParser(description="Archive identified duplicate files via ArchivalGatekeeper.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be archived without moving files"
    )
    args = parser.parse_args()
    dry_run = args.dry_run

    print("[*] Starting Archive Operation via ArchivalGatekeeper")
    if dry_run:
        print("[*] DRY RUN — no files will be moved")

    # Enable batch mode so ArchivalGatekeeper does not prompt interactively
    if not dry_run:
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"

    gk = ArchivalGatekeeper.get_instance()
    moved_count = 0
    missing_count = 0

    for rel_path in TARGETS:
        source_path = PROJECT_ROOT / rel_path

        if not source_path.exists():
            print(f"[-] Skipped (Not Found): {rel_path}")
            missing_count += 1
            continue

        if dry_run:
            print(f"[DRY RUN] Would archive: {rel_path}")
            moved_count += 1
        else:
            result = gk.safe_archive(
                source_path,
                requester_agent="archive_duplicates",
                reason="Identified duplicate — Agent Overlap Analysis Report",
            )
            if result.success:
                print(f"[+] Archived: {rel_path}")
                moved_count += 1
            else:
                print(f"[!] Failed to archive {rel_path}: {result.error}")

    print("-" * 50)
    print("SUMMARY:")
    print(f"  {'Would move' if dry_run else 'Moved'}:   {moved_count}")
    print(f"  Missing: {missing_count}")
    print("-" * 50)

    if moved_count > 0:
        print("✅ Archive operation completed successfully." if not dry_run else "✅ Dry run complete.")
    else:
        print("⚠️  No files were moved.")


if __name__ == "__main__":
    main()
