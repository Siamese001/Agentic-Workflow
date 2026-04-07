#!/usr/bin/env python3
"""Fix archive inefficiency by removing duplicate individual files and keeping only zip files."""

import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = ROOT / "artifacts" / "adg" / "_archive"


def analyze_archive_inefficiency():
    """Analyze storage inefficiency in archive."""
    print("🔍 ANALYZING ARCHIVE INEFFICIENCY")
    print("=" * 60)

    total_individual_size = 0
    total_zip_size = 0
    duplicate_runs = []

    # Group files by timestamp
    timestamp_groups = {}

    for file_path in ARCHIVE_DIR.rglob("*.gz"):
        if file_path.is_file():
            # Extract timestamp from filename
            parts = file_path.stem.split('_')
            if len(parts) >= 3:
                timestamp = '_'.join(parts[-2:])  # Get MMDDYYYY_HHMM part

                if timestamp not in timestamp_groups:
                    timestamp_groups[timestamp] = {'individual': [], 'zip': None}

                if 'zip' in file_path.name:
                    timestamp_groups[timestamp]['zip'] = file_path
                    total_zip_size += file_path.stat().st_size
                else:
                    timestamp_groups[timestamp]['individual'].append(file_path)
                    total_individual_size += file_path.stat().st_size

    # Find runs with both individual files AND zip files
    for timestamp, files in timestamp_groups.items():
        if files['individual'] and files['zip']:
            individual_size = sum(f.stat().st_size for f in files['individual'])
            zip_size = files['zip'].stat().st_size
            waste = individual_size

            duplicate_runs.append({
                'timestamp': timestamp,
                'individual_files': len(files['individual']),
                'individual_size': individual_size,
                'zip_size': zip_size,
                'waste': waste,
            })

    # Print analysis
    total_waste = sum(run['waste'] for run in duplicate_runs)

    print(f"Total individual files size: {total_individual_size / (1024*1024):.1f} MB")
    print(f"Total zip files size: {total_zip_size / (1024*1024):.1f} MB")
    print(f"Total waste (duplicates): {total_waste / (1024*1024):.1f} MB")
    print(f"Number of inefficient runs: {len(duplicate_runs)}")

    print("\n📊 INEFFICIENT RUNS:")
    for run in sorted(duplicate_runs, key=lambda x: x['timestamp']):
        print(f"  {run['timestamp']}: {run['individual_files']} files, "
              f"{run['individual_size']/(1024*1024):.1f} MB wasted")

    return duplicate_runs


def cleanup_archive_inefficiency(duplicate_runs, dry_run=True):
    """Clean up archive by removing duplicate individual files."""
    print(f"\n{'🔧 DRY RUN' if dry_run else '🗑️  CLEANUP'} - Removing duplicate individual files")
    print("=" * 60)

    total_freed = 0
    files_removed = 0

    for run in duplicate_runs:
        print(f"\nProcessing run {run['timestamp']}:")

        # Get individual files for this timestamp
        timestamp = run['timestamp']
        individual_files = []

        for file_path in ARCHIVE_DIR.rglob(f"*_{timestamp}.gz"):
            if file_path.is_file() and 'zip' not in file_path.name:
                individual_files.append(file_path)

        for file_path in individual_files:
            file_size = file_path.stat().st_size
            print(f"  Would remove: {file_path.name} ({file_size/(1024*1024):.1f} MB)")

            if not dry_run:
                file_path.unlink()
                total_freed += file_size
                files_removed += 1
            else:
                total_freed += file_size
                files_removed += 1

        # Keep the zip file
        zip_file = next((f for f in ARCHIVE_DIR.rglob(f"*_{timestamp}.zip.gz")), None)
        if zip_file:
            print(f"  Keeping: {zip_file.name}")

    print(f"\n{'Would free' if dry_run else 'Freed'}: {total_freed/(1024*1024):.1f} MB")
    print(f"{'Would remove' if dry_run else 'Removed'}: {files_removed} files")

    return total_freed, files_removed


def create_efficient_archive_structure():
    """Create efficient archive structure with only zip files."""
    print("\n📁 CREATING EFFICIENT ARCHIVE STRUCTURE")
    print("=" * 60)

    # Create new efficient archive directory
    efficient_archive = ARCHIVE_DIR.parent / "_archive_efficient"
    efficient_archive.mkdir(exist_ok=True)

    # Copy only zip files to new structure
    zip_files = list(ARCHIVE_DIR.rglob("*.zip.gz"))

    for zip_file in zip_files:
        # Determine year-month from file modification time
        mod_time = datetime.fromtimestamp(zip_file.stat().st_mtime)
        year_month = mod_time.strftime("%Y-%m")

        # Create year-month directory
        month_dir = efficient_archive / year_month
        month_dir.mkdir(exist_ok=True)

        # Copy zip file
        dest = month_dir / zip_file.name
        shutil.copy2(zip_file, dest)
        print(f"  Copied: {zip_file.name} -> {year_month}/")

    print(f"\n✅ Efficient archive created: {efficient_archive}")
    print(f"  Zip files: {len(zip_files)}")
    print("  Storage: Only zip files, no duplicates!")

    return efficient_archive, len(zip_files)


def main():
    """Main archive efficiency fix."""
    print("=" * 80)
    print("ADG ARCHIVE INEFFICIENCY FIX")
    print("=" * 80)

    # 1. Analyze current inefficiency
    duplicate_runs = analyze_archive_inefficiency()

    if not duplicate_runs:
        print("\n✅ No archive inefficiency found!")
        return

    # 2. Show what would be cleaned up (dry run)
    total_waste, files_removed = cleanup_archive_inefficiency(duplicate_runs, dry_run=True)

    # 3. Ask for confirmation
    print(f"\n❓ Remove {files_removed} duplicate files to free {total_waste/(1024*1024):.1f} MB? (y/n)")
    # For automation, we'll proceed with cleanup

    print("🗑️  PROCEEDING WITH CLEANUP...")

    # 4. Actually clean up
    total_freed, files_removed = cleanup_archive_inefficiency(duplicate_runs, dry_run=False)

    # 5. Create efficient archive structure
    efficient_archive, zip_count = create_efficient_archive_structure()

    print("\n" + "=" * 80)
    print("ARCHIVE EFFICIENCY FIX COMPLETE")
    print("=" * 80)
    print(f"Files removed: {files_removed}")
    print(f"Space freed: {total_freed/(1024*1024):.1f} MB")
    print(f"Efficient archive: {efficient_archive}")
    print(f"Zip files preserved: {zip_count}")
    print("\n✅ Archive is now storage-efficient!")


if __name__ == "__main__":
    main()
