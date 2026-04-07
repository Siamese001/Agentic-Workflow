#!/usr/bin/env python3
"""Simple fix for archive inefficiency - remove individual files when zip exists."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = ROOT / "artifacts" / "adg" / "_archive"


def find_duplicate_runs():
    """Find runs that have both zip files and individual files."""
    print("🔍 FINDING DUPLICATE RUNS")
    print("=" * 60)

    # Get all zip files
    zip_files = list(ARCHIVE_DIR.rglob("*.zip.gz"))
    print(f"Found {len(zip_files)} zip files")

    duplicate_runs = []

    for zip_file in zip_files:
        # Extract timestamp from zip filename
        # Pattern: adg_run_MMDDYYYY_HHMM.zip.gz
        parts = zip_file.stem.split('_')  # Remove .gz
        if len(parts) >= 3:
            timestamp = '_'.join(parts[-2:])  # Get MMDDYYYY_HHMM part

            # Find individual files with same timestamp
            individual_files = list(ARCHIVE_DIR.rglob(f"*_{timestamp}.gz"))
            individual_files = [f for f in individual_files if 'zip' not in f.name]

            if individual_files:
                individual_size = sum(f.stat().st_size for f in individual_files)
                zip_size = zip_file.stat().st_size

                duplicate_runs.append({
                    'timestamp': timestamp,
                    'zip_file': zip_file,
                    'individual_files': individual_files,
                    'individual_count': len(individual_files),
                    'individual_size': individual_size,
                    'zip_size': zip_size,
                    'waste': individual_size,
                })

                print(f"  {timestamp}: {len(individual_files)} individual files, "
                      f"{individual_size/(1024*1024):.1f} MB waste")

    total_waste = sum(run['waste'] for run in duplicate_runs)
    print(f"\nTotal waste: {total_waste/(1024*1024):.1f} MB")
    print(f"Duplicate runs: {len(duplicate_runs)}")

    return duplicate_runs


def cleanup_duplicates(duplicate_runs):
    """Remove individual files when zip exists."""
    print("\n🗑️  CLEANING UP DUPLICATES")
    print("=" * 60)

    total_freed = 0
    files_removed = 0

    for run in duplicate_runs:
        print(f"\nProcessing {run['timestamp']}:")

        for file_path in run['individual_files']:
            file_size = file_path.stat().st_size
            print(f"  Removing: {file_path.name} ({file_size/(1024*1024):.1f} MB)")

            file_path.unlink()
            total_freed += file_size
            files_removed += 1

        print(f"  Keeping: {run['zip_file'].name}")

    print(f"\n✅ Freed: {total_freed/(1024*1024):.1f} MB")
    print(f"✅ Removed: {files_removed} files")

    return total_freed, files_removed


def verify_cleanup():
    """Verify cleanup was successful."""
    print("\n🔍 VERIFYING CLEANUP")
    print("=" * 60)

    # Check remaining files
    remaining_files = list(ARCHIVE_DIR.rglob("*.gz"))
    zip_files = [f for f in remaining_files if 'zip' in f.name]
    individual_files = [f for f in remaining_files if 'zip' not in f.name]

    print(f"Remaining zip files: {len(zip_files)}")
    print(f"Remaining individual files: {len(individual_files)}")

    if individual_files:
        print("\n⚠️  Still have individual files:")
        for f in individual_files[:10]:  # Show first 10
            print(f"  {f.name}")
        if len(individual_files) > 10:
            print(f"  ... and {len(individual_files) - 10} more")
    else:
        print("✅ No individual files remaining - all efficient!")

    return len(individual_files) == 0


def main():
    """Main cleanup process."""
    print("=" * 80)
    print("ADG ARCHIVE INEFFICIENCY FIX")
    print("=" * 80)

    # 1. Find duplicate runs
    duplicate_runs = find_duplicate_runs()

    if not duplicate_runs:
        print("\n✅ No archive inefficiency found!")
        return

    # 2. Clean up duplicates
    total_freed, files_removed = cleanup_duplicates(duplicate_runs)

    # 3. Verify cleanup
    is_clean = verify_cleanup()

    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Files removed: {files_removed}")
    print(f"Space freed: {total_freed/(1024*1024):.1f} MB")
    print(f"Archive is efficient: {'✅ YES' if is_clean else '❌ NO'}")


if __name__ == "__main__":
    main()
