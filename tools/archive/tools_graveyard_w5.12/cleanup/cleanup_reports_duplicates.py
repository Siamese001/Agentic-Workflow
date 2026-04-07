#!/usr/bin/env python3
"""Clean up duplicate precision pass reports - keep only latest version."""

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "artifacts" / "adg" / "reports"


def analyze_report_duplicates():
    """Analyze duplicate precision pass reports."""
    print("🔍 ANALYZING REPORT DUPLICATES")
    print("=" * 60)

    # Group reports by type (base name without timestamp)
    report_groups = {}

    for file_path in REPORTS_DIR.glob("*.json"):
        if file_path.is_file():
            # Extract base name and timestamp
            # Pattern: report_type_YYYYMMDD_HHMM.json
            parts = file_path.stem.split('_')
            if len(parts) >= 3:
                # Extract timestamp (last 2 parts)
                timestamp = '_'.join(parts[-2:])
                base_name = '_'.join(parts[:-2])

                if base_name not in report_groups:
                    report_groups[base_name] = []

                report_groups[base_name].append({
                    'path': file_path,
                    'timestamp': timestamp,
                    'datetime': datetime.strptime(timestamp, "%Y%m%d_%H%M"),
                    'size': file_path.stat().st_size,
                })

    # Find duplicates
    duplicate_groups = {}
    total_waste = 0

    for base_name, reports in report_groups.items():
        if len(reports) > 1:
            # Sort by timestamp (newest first)
            reports.sort(key=lambda x: x['datetime'], reverse=True)

            # Calculate waste (all except newest)
            waste_size = sum(r['size'] for r in reports[1:])
            total_waste += waste_size

            duplicate_groups[base_name] = {
                'reports': reports,
                'waste': waste_size,
                'keep': reports[0],  # Keep the newest
                'remove': reports[1:],  # Remove older ones
            }

    print(f"Found {len(duplicate_groups) } report types with duplicates")
    print(f"Total waste: {total_waste / 1024:.1f} KB")

    # Show details
    for base_name, group in duplicate_groups.items():
        print(f"\n📄 {base_name}:")
        print(f"  Keep: {group['keep']['path'].name} ({group['keep']['timestamp']})")
        for old_report in group['remove']:
            print(f"  Remove: {old_report['path'].name} ({old_report['timestamp']})")

    return duplicate_groups


def cleanup_report_duplicates(duplicate_groups, dry_run=True):
    """Clean up duplicate reports."""
    print(f"\n{'🔧 DRY RUN' if dry_run else '🗑️  CLEANUP'} - Removing duplicate reports")
    print("=" * 60)

    total_freed = 0
    files_removed = 0

    for base_name, group in duplicate_groups.items():
        print(f"\nCleaning {base_name}:")

        for old_report in group['remove']:
            file_size = old_report['size']
            print(f"  Would remove: {old_report['path'].name} ({file_size} bytes)")

            if not dry_run:
                old_report['path'].unlink()
                total_freed += file_size
                files_removed += 1
            else:
                total_freed += file_size
                files_removed += 1

        print(f"  Keeping: {group['keep']['path'].name}")

    print(f"\n{'Would free' if dry_run else 'Freed'}: {total_freed} bytes ({total_freed/1024:.1f} KB)")
    print(f"{'Would remove' if dry_run else 'Removed'}: {files_removed} files")

    return total_freed, files_removed


def main():
    """Main cleanup process."""
    print("=" * 80)
    print("REPORTS DUPLICATE CLEANUP")
    print("=" * 80)

    # 1. Analyze duplicates
    duplicate_groups = analyze_report_duplicates()

    if not duplicate_groups:
        print("\n✅ No duplicate reports found!")
        return

    # 2. Show what would be cleaned up (dry run)
    total_waste, files_removed = cleanup_report_duplicates(duplicate_groups, dry_run=True)

    # 3. Actually clean up
    print("\n🗑️  PROCEEDING WITH CLEANUP...")
    total_freed, files_removed = cleanup_report_duplicates(duplicate_groups, dry_run=False)

    # 4. Verify cleanup
    print("\n🔍 VERIFYING CLEANUP")
    remaining_files = list(REPORTS_DIR.glob("*.json"))
    print(f"Remaining report files: {len(remaining_files)}")

    # Check for remaining duplicates
    report_names = [f.stem for f in remaining_files]
    base_names = set(['_'.join(name.split('_')[:-2]) for name in report_names if len(name.split('_')) >= 3])

    duplicates_remain = any(
        report_names.count(base) > 1
        for base in base_names
    )

    print(f"Duplicates remain: {'❌ YES' if duplicates_remain else '✅ NO'}")

    print("\n" + "=" * 80)
    print("REPORTS CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Files removed: {files_removed}")
    print(f"Space freed: {total_freed} bytes ({total_freed/1024:.1f} KB)")
    print(f"Reports folder optimized: {'✅ YES' if not duplicates_remain else '❌ NO'}")


if __name__ == "__main__":
    main()
