from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "generate_hooks_util")
_emit_applies_guardrail("p0", "generate_hooks_util", "p0_governance")
_emit_reads_policy_state("p0", "generate_hooks_util", "policy_binding")
_emit_snapshots_state("p0", "generate_hooks_util", "state_snapshot")
emit_replay_key("p0", "generate_hooks_util")
emit_determinism_digest("p0", "generate_hooks_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

#!/usr/bin/env python3
"""
Pre-commit Hook Generator - SSOT Synchronization
Dynamically generates .pre-commit-config.yaml patterns from structure_blueprint.py
to eliminate hardcoded folder lists and prevent drift.

Usage:
    python scripts/maintenance/generate_hooks_util.py
    python scripts/maintenance/generate_hooks_util.py --dry-run
"""
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

# Add project root to path
project_root = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.config.structure_blueprint import DEPTH_RULES, PROJECT_ROOT_WHITELIST


def sync_pre_commit(dry_run: bool = False):
    """
    Synchronize .pre-commit-config.yaml with SSOT from structure_blueprint.py

    Args:
        dry_run: If True, only print changes without modifying files
    """
    # [SSOT] Dynamically derive sovereign roots
    sovereign_roots = sorted(PROJECT_ROOT_WHITELIST)

    # Add system folders that should be included in patterns
    system_folders = ["data", ARCHIVES_DIR]
    all_roots = sovereign_roots + system_folders

    # Build regex patterns
    roots_pattern = "|".join(sovereign_roots)
    all_roots_pattern = "|".join(all_roots)

    exclude_pattern = f"^({all_roots_pattern})/"
    files_pattern = f"^({roots_pattern})/.*\\.py$"

    print("[*] Syncing Pre-commit Config with SSOT...")
    print(f"   [SSOT] Sovereign Roots: {', '.join(sovereign_roots)}")
    print(f"   [PATTERN] Exclude: {exclude_pattern}")
    print(f"   [PATTERN] Files: {files_pattern}")

    # Locate the pre-commit config
    config_path = project_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts" / ".pre-commit-config.yaml"

    if not config_path.exists():
        print(f"   [!] Config not found at: {config_path}")
        print("   [!] Checking alternate location...")
        config_path = project_root / ".pre-commit-config.yaml"

        if not config_path.exists():
            print("   [X] No .pre-commit-config.yaml found!")
            return False

    print(f"   [OK] Found config at: {config_path}")

    # Read current config
    with open(config_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern replacements - target the hardcoded folder lists
    replacements = [
        # Exclude patterns (with data/archives)
        (
            r"exclude: \^[(]agentic_core\|apps_lic\|apps_rg\|apps_shared\|schemas\|prompt_governance\|observability\|config\|data\|archives[)]/",
            f"exclude: ^({all_roots_pattern})/",
        ),
        # Files patterns (sovereign only)
        (
            r"files: \^[(]agentic_core\|apps_lic\|apps_rg\|apps_shared\|schemas\|prompt_governance\|observability\|config[)]/\.\*\\\.py\$",
            f"files: ^({roots_pattern})/.*\\.py$",
        ),
    ]

    changes_made = 0
    for pattern, replacement in replacements:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f"   [✓] Updated {len(matches)} pattern(s)")

    if changes_made == 0:
        print("   [OK] No changes needed - config already synchronized")
        return True

    if dry_run:
        print(f"\n   [DRY-RUN] Would update {changes_made} pattern(s)")
        print("\n--- DIFF ---")
        print("Original patterns found, would be replaced with SSOT-derived patterns")
        return True

    # Write updated config
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"   [✓] Updated {changes_made} pattern(s) in {config_path.name}")
    print("   [SUCCESS] Pre-commit config synchronized with SSOT")

    return True


def generate_sovereign_list():
    """Generate a formatted list of sovereign roots for documentation"""
    sovereign_roots = sorted(PROJECT_ROOT_WHITELIST)
    print("\n[SSOT] Current Sovereign Registry (PROJECT_ROOT_WHITELIST):")
    for i, root in enumerate(sovereign_roots, 1):
        depth = DEPTH_RULES.get(root, "N/A")
        print(f"  {i:2d}. {root:<25} (Depth: {depth})")
    print(f"\nTotal: {len(sovereign_roots)} sovereign roots")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync pre-commit config with SSOT")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--list", action="store_true", help="List current sovereign roots")

    args = parser.parse_args()

    if args.list:
        generate_sovereign_list()
    else:
        success = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
