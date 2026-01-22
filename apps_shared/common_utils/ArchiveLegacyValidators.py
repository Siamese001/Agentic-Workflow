#!/usr/bin/env python3
"""
archive_legacy_validators.py - Phase 2 Validator Liquidation

Archives 17 legacy validator files that have been replaced by:
- UnifiedCodeValidatorAgent (L5)
- UnifiedStructureValidatorAgent (L5)
- AppContentValidatorAgent (Apps)

Usage:
    python scripts/archive_legacy_validators.py --dry-run
    python scripts/archive_legacy_validators.py
"""


import argparse
import shutil
import sys

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "archives" / "legacy_validators"

# Legacy validators to archive with their current locations
LEGACY_VALIDATORS: dict[str, str] = {
    # L5 Code Validators -> UnifiedCodeValidatorAgent
    "SyntaxValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "CanonAstValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "CanonValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "AsyncBlockingValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "PrintStatementValidatorAgent.py": "agentic_core/L5_safety/validators/",
    # L5 Structure Validators -> UnifiedStructureValidatorAgent
    "GravityValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "HygieneValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "UnifiedHygieneValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "AgentRegistryValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "CognitiveContractValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "ContextAwareValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "ExternalHttpValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "HealValidatorAgent.py": "agentic_core/L5_safety/validators/",
    "InputValidatorAgent.py": "agentic_core/L5_safety/validators/",
    # App Content Validators -> AppContentValidatorAgent
    "ContactValidatorAgent.py": "apps_lic/domain/validators/",
    "ContentCleanlinessValidatorAgent.py": "apps_lic/domain/validators/",
    "MessageDiversityValidatorAgent.py": "apps_lic/domain/validators/",
}


def find_validator(filename: str, expected_dir: str) -> Path | None:
    """Find a validator file, checking expected location first then searching."""
    # Check expected location
    expected_path = PROJECT_ROOT / expected_dir / filename
    if expected_path.exists():
        return expected_path

    # Search in agentic_core
    for path in (PROJECT_ROOT / "agentic_core").rglob(filename):
        if "archive" not in str(path).lower() and "unified" not in str(path).lower():
            return path

    # Search in apps_lic
    for path in (PROJECT_ROOT / "apps_lic").rglob(filename):
        if "archive" not in str(path).lower():
            return path

    # Search in apps_rg
    for path in (PROJECT_ROOT / "apps_rg").rglob(filename):
        if "archive" not in str(path).lower():
            return path

    return None


def archive_validator(source: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Archive a single validator file."""
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
    parser = argparse.ArgumentParser(description="Archive legacy validators")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 2 Validator Liquidation - Legacy Archive")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE]\n")

    archived = 0
    skipped = 0
    not_found = 0

    for filename, expected_dir in sorted(LEGACY_VALIDATORS.items()):
        source = find_validator(filename, expected_dir)

        if source is None:
            print(f"  ⊘ NOT FOUND: {filename}")
            not_found += 1
            continue

        success, message = archive_validator(source, args.dry_run)

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
        print("\n✓ LIQUIDATION COMPLETE")

    return 0


if __name__ == "__main__":
    sys.exit(main())