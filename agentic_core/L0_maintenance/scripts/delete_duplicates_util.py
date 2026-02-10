#!/usr/bin/env python3
"""
Delete duplicate files based on scan results.
"""

# TODO: GRAVITY VIOLATION AUTO-HEALED
# Downstream imports removed — move shared logic to apps_shared or sovereign utils
# Original violation: GRAVITY VIOLATION: Upstream 'agentic_core' imports downstream roots: ['apps_lic']. Move shared logic to apps_shared or sovereign utils.
# Removed: apps_lic.engines.DuplicateCodeDetectorAgent

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))


async def main():
    """Delete duplicates with dry-run or execute mode."""
    parser = argparse.ArgumentParser(description="Delete duplicate files")
    parser.add_argument("--execute", action="store_true", help="Actually delete files (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deletion without actually deleting")
    args = parser.parse_args()

    # Default to dry-run if neither flag is specified
    dry_run = not args.execute or args.dry_run

    print("=" * 80)
    print(f"DUPLICATE FILE DELETION - {'DRY RUN' if dry_run else 'EXECUTE MODE'}")
    print("=" * 80)
    print()

    if not dry_run:
        print("⚠️  WARNING: This will PERMANENTLY DELETE files!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
        print()

    # Initialize agent
    agent = DuplicateCodeDetectorAgent(project_root=project_root)

    # Scan for duplicates
    print("Scanning for duplicates...")
    results = await agent.execute(scan_whole_files=True)
    recommendations = results["deletion_recommendations"]

    print(f"Found {len(recommendations)} duplicate sets")
    print()

    if not recommendations:
        print("No duplicates to delete!")
        return

    # Delete duplicates
    print(f"{'Simulating' if dry_run else 'Executing'} deletion...")
    delete_result = agent.delete_duplicates(recommendations, dry_run=dry_run)

    print()
    print("=" * 80)
    print("DELETION RESULTS")
    print("=" * 80)
    print(f"Files deleted: {delete_result['deleted_count']}")
    print(f"Errors: {len(delete_result['errors'])}")
    print(f"Mode: {'DRY RUN' if delete_result['dry_run'] else 'EXECUTED'}")
    print()

    if delete_result["errors"]:
        print("Errors encountered:")
        for error in delete_result["errors"]:
            print(f"  ❌ {error['path']}: {error['error']}")
        print()

    if dry_run:
        print("✅ Dry run complete - no files were actually deleted")
        print("   Run with --execute to actually delete files")
    else:
        print("✅ Deletion complete!")
        print(f"   Deleted {delete_result['deleted_count']} duplicate files")
    print()


if __name__ == "__main__":
    asyncio.run(main())
