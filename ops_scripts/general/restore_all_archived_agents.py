#!/usr/bin/env python3
# RELOCATED: Moved from apps_shared/reasoning/ to ops_scripts/general/ (P1-B, 2026-03-11).
"""
restore_all_archived_agents.py - Comprehensive restoration of incorrectly archived agents

Restores unique agents from:
- L4_state/ (4 agents) -> agentic_core/L4_state/memory/
- location_violations/ (12 agents) -> appropriate layer directories
- runtime/ (14 agents) -> apps_lic/engines/outreach_engine/ or apps_rg/
- void_violations/ (82 remaining unique) -> appropriate layer directories
- Reachout Engine Archive/ (4 agents) -> apps_lic/engines/outreach_engine/
- apps_rg/ (1 agent) -> apps_rg/engines/resume_engine/

Usage:
    python scripts/restore_all_archived_agents.py --dry-run
    python scripts/restore_all_archived_agents.py
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    OPS_ARCHIVES_DIR,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    ARCHIVES_DIR,
)
from tqdm import tqdm


def _resolve_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _resolve_project_root()
ARCHIVES = PROJECT_ROOT / OPS_ARCHIVES_DIR
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

# Target directories for restoration
TARGETS = {
    "L0": "L0_routing/scripts/",
    "L1": "L1_cognition/thought_engine/",
    "L2": "L2_execution/engine/",
    "L3": "L3_orchestration/engine/",
    "L4": "L4_state/memory/",
    "L5": "L5_safety/validators/",
    "L6": "L6_observability/agents/",
}


def get_current_agents() -> set:
    """Get all agent names currently in the codebase."""
    agents = set()
    for f in AGENTIC_CORE.rglob("*Agent.py"):
        agents.add(f.stem)
    for d in [APPS_LIC_DIR, APPS_RG_DIR]:
        p = PROJECT_ROOT / d
        if p.exists():
            for f in p.rglob("*Agent.py"):
                agents.add(f.stem)
    return agents


def infer_target_directory(agent_name: str, source_path: str) -> str | None:
    """Infer the target directory for an agent based on its name and source."""
    name_lower = agent_name.lower()

    # L4 State agents
    if "state" in name_lower or "checkpoint" in name_lower or "validation" in name_lower:
        return TARGETS["L4"]

    # L3 Orchestration agents
    if "orchestrat" in name_lower or "workflow" in name_lower or "dag" in name_lower:
        return TARGETS["L3"]

    # L5 Safety/Validation agents
    if any(x in name_lower for x in ["validator", "enforcer", "guard", "safety", "canon", "hygiene"]):
        return TARGETS["L5"]

    # L6 observability agents
    if any(x in name_lower for x in ["telemetry", "metrics", "tracing", "monitor", "observ"]):
        return TARGETS["L6"]

    # L2 Execution agents
    if any(x in name_lower for x in ["executor", "registry", "router", "dispatcher"]):
        return TARGETS["L2"]

    # L1 Cognition agents
    if any(x in name_lower for x in ["cognitive", "reasoning", "learning", "prompt"]):
        return TARGETS["L1"]

    # Runtime/k-agents go to apps
    if source_path.startswith("runtime/") or source_path.startswith("Reachout"):
        return None  # Handle separately for apps

    # Default to L5 for validators
    return TARGETS["L5"]


def restore_agent(source: Path, target: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Restore a single agent file."""
    if not source.exists():
        return False, "Source not found"

    if target.exists():
        return False, "Already exists"

    if dry_run:
        return True, f"Would restore to {target.relative_to(PROJECT_ROOT)}"

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return True, f"Restored to {target.relative_to(PROJECT_ROOT)}"
    except Exception as e:  # guardian: allow-silent-swallow
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Restore all incorrectly archived agents")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 80)
    print("COMPREHENSIVE ARCHIVE RESTORATION")
    print("=" * 80)

    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    current = get_current_agents()
    print(f"Current agents: {len(current)}")

    # Load manifest
    manifest_path = PROJECT_ROOT / OPS_ARCHIVES_DIR / "restoration_manifest.json"
    if not manifest_path.exists():
        print("Run scan_archives_for_restoration.py first!")
        return 1

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    restored = 0
    skipped = 0
    errors = 0

    # Process each folder
    folders_to_process = [
        "L4_state",
        "location_violations",
        "runtime",
        "void_violations",
        "Reachout Engine Archive",
        APPS_RG_DIR,
    ]

    for folder in tqdm(folders_to_process, desc="Processing", unit="item"):
        if folder not in manifest["by_folder"]:
            continue

        data = manifest["by_folder"][folder]
        if data["count"] == 0:
            continue

        print(f"\n## {folder}/ ({data['count']} agents)")

        for agent in tqdm(data["agents"], desc="Processing", unit="item"):
            name = agent["name"]
            source_path = agent["path"]
            source = ARCHIVES / source_path

            # Skip if already in codebase
            if name in current:
                print(f"  ⊘ SKIP: {name} (already exists)")
                skipped += 1
                continue

            # Determine target
            if folder == "L4_state":
                target_dir = AGENTIC_CORE / TARGETS["L4"]
            elif folder in ["runtime", "Reachout Engine Archive"]:
                # k-agents go to apps_lic outreach engine
                target_dir = PROJECT_ROOT / APPS_LIC_DIR / "engines" / "outreach_engine"
            elif folder == APPS_RG_DIR:
                target_dir = PROJECT_ROOT / APPS_RG_DIR / "engines" / "resume_engine"
            elif folder == "location_violations":
                # Infer from agent name
                inferred = infer_target_directory(name, source_path)
                if inferred:
                    target_dir = AGENTIC_CORE / inferred
                else:
                    target_dir = AGENTIC_CORE / TARGETS["L5"]
            elif folder == "void_violations":
                inferred = infer_target_directory(name, source_path)
                if inferred:
                    target_dir = AGENTIC_CORE / inferred
                else:
                    target_dir = AGENTIC_CORE / TARGETS["L5"]
            else:
                target_dir = AGENTIC_CORE / TARGETS["L5"]

            target = target_dir / f"{name}.py"

            success, message = restore_agent(source, target, args.dry_run)

            if success:
                icon = "○" if args.dry_run else "✓"
                print(f"  {icon} {name}")
                restored += 1
                current.add(name)  # Track restored agents
            else:
                if "Already exists" in message:
                    print(f"  ⊘ SKIP: {name} ({message})")
                    skipped += 1
                else:
                    print(f"  ✗ ERROR: {name} - {message}")
                    errors += 1

    print(f"\n{'=' * 80}")
    print("Summary:")
    print(f"  Restored: {restored}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n✓ RESTORATION COMPLETE")
        print(f"\nNew total: {len(current)} agents")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
