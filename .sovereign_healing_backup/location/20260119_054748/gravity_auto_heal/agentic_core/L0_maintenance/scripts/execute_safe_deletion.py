"""
Execute safe deletion of verified identical duplicates.
This script bypasses the interactive prompt for automated execution.
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apps_shared.utils.DuplicateCodeDetectorAgent import DuplicateCodeDetectorAgent


async def main():
    """Execute deletion of verified identical duplicates."""
    print("=" * 120)
    print("SAFE DELETION - Verified Identical Duplicates Only")
    print("=" * 120)
    print()
    print("This script will delete files that are byte-for-byte identical (same SHA-256 hash)")
    print("Intentional variants with different content will NOT be deleted")
    print()
    
    # Initialize agent
    agent = DuplicateCodeDetectorAgent(project_root=project_root)
    
    # Scan for duplicates
    print("[1/3] Scanning for duplicates...")
    results = await agent.execute(scan_whole_files=True)
    recommendations = results["deletion_recommendations"]
    
    print(f"   Found {len(recommendations)} duplicate sets")
    print()
    
    if not recommendations:
        print("No duplicates to delete!")
        return
    
    # Show what will be deleted
    print("[2/3] Files to be deleted:")
    print()
    total_to_delete = 0
    for rec in recommendations[:10]:  # Show first 10
        print(f"   Keeping: {rec['keep']}")
        print(f"   Deleting: {len(rec['delete'])} copies")
        for del_path in rec['delete'][:3]:  # Show first 3 of each set
            print(f"     - {del_path}")
        if len(rec['delete']) > 3:
            print(f"     ... and {len(rec['delete']) - 3} more")
        print()
        total_to_delete += len(rec['delete'])
    
    if len(recommendations) > 10:
        print(f"   ... and {len(recommendations) - 10} more duplicate sets")
        for rec in recommendations[10:]:
            total_to_delete += len(rec['delete'])
    
    print(f"   Total files to delete: {total_to_delete}")
    print()
    
    # Execute deletion
    print("[3/3] Executing deletion...")
    delete_result = agent.delete_duplicates(recommendations, dry_run=False)
    
    print()
    print("=" * 120)
    print("DELETION RESULTS")
    print("=" * 120)
    print(f"✓ Files deleted: {delete_result['deleted_count']}")
    print(f"✓ Errors: {len(delete_result['errors'])}")
    print()
    
    if delete_result['errors']:
        print("Errors encountered:")
        for error in delete_result['errors']:
            print(f"  ✗ {error['path']}: {error['error']}")
        print()
    
    print("✓ Deletion complete!")
    print(f"  Successfully deleted {delete_result['deleted_count']} duplicate files")
    print(f"  Kept {len(recommendations)} canonical copies")
    print()


if __name__ == "__main__":
    asyncio.run(main())
