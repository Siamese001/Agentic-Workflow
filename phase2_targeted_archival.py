"""
Phase 2 Step 3: Targeted Archival
Archives only truly heretical folders: docs, shared, common, bases, knowledge

Protects legitimate L0-L5 layers and core infrastructure.
"""

import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
ARCHIVE_ROOT = PROJECT_ROOT / "archives" / "unmapped_drift" / datetime.now().strftime("%Y%m%d")

# Heretical folders to archive (not in Gospel blueprint)
HERETICAL_FOLDERS = [
    "agentic_core/docs",
    "agentic_core/shared", 
    "agentic_core/common",
    "agentic_core/bases",
    "agentic_core/knowledge",
]

def archive_folder(source_rel: str, dry_run: bool = True) -> dict:
    """Archive a single heretical folder."""
    source = PROJECT_ROOT / source_rel
    target = ARCHIVE_ROOT / source_rel
    
    result = {
        "source": str(source),
        "target": str(target),
        "success": False,
        "action": "PREVIEW" if dry_run else "ARCHIVED",
        "error": None
    }
    
    try:
        if not source.exists():
            result["error"] = "Source does not exist (already clean)"
            result["success"] = True  # Not an error if already gone
            return result
        
        if not source.is_dir():
            result["error"] = "Source is not a directory"
            return result
        
        if dry_run:
            result["success"] = True
            result["action"] = "PREVIEW"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            result["success"] = True
            result["action"] = "ARCHIVED"
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


def run_targeted_archival(dry_run: bool = True):
    """Execute targeted archival of heretical folders only."""
    print("\n" + "=" * 80)
    print(f"  PHASE 2 STEP 3: TARGETED ARCHIVAL ({'DRY-RUN' if dry_run else 'LIVE'})")
    print("=" * 80 + "\n")
    
    print(f"Archive destination: {ARCHIVE_ROOT}")
    print(f"Heretical folders to purge: {len(HERETICAL_FOLDERS)}\n")
    
    results = []
    archived_count = 0
    skipped_count = 0
    
    for i, folder_rel in enumerate(HERETICAL_FOLDERS, 1):
        print(f"[{i}/{len(HERETICAL_FOLDERS)}] {folder_rel}")
        
        result = archive_folder(folder_rel, dry_run=dry_run)
        results.append(result)
        
        if result["success"]:
            error_msg = result.get("error") or ""
            if "already clean" in error_msg:
                skipped_count += 1
                print(f"  ⏭️  SKIP: {result['error']}")
            else:
                archived_count += 1
                print(f"  ✅ {result['action']}")
        else:
            print(f"  ❌ ERROR: {result['error']}")
        print()
    
    # Summary
    print("=" * 80)
    print("  ARCHIVAL SUMMARY")
    print("=" * 80 + "\n")
    print(f"Total folders: {len(HERETICAL_FOLDERS)}")
    print(f"Archived: {archived_count}")
    print(f"Skipped (already clean): {skipped_count}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE EXECUTION'}")
    
    if dry_run:
        print("\n⚠️  This was a DRY-RUN. No folders were archived.")
        print("   Run with --execute to apply changes.")
    else:
        print(f"\n✅ Targeted archival complete!")
        print(f"   Archived folders moved to: {ARCHIVE_ROOT}")
    
    return {
        "total": len(HERETICAL_FOLDERS),
        "archived": archived_count,
        "skipped": skipped_count,
        "dry_run": dry_run,
        "results": results
    }


if __name__ == "__main__":
    import sys
    
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        dry_run = False
        print("\n⚠️  WARNING: LIVE EXECUTION MODE")
        print("   Folders will be moved to archives/")
        response = input("   Continue? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            print("   Aborted.")
            sys.exit(0)
    
    summary = run_targeted_archival(dry_run=dry_run)
    sys.exit(0 if summary["archived"] >= 0 else 1)
