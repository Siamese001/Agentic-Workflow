#!/usr/bin/env python3
"""
Duplicate File Cleanup Script - Agentic-Workflow Project

Detects and removes runaway refactoring artifacts:
- Files with _2, _3, _4, _5, etc. suffixes
- Files with _part_2, _part_3, etc. suffixes
- Multiple versioned files (e.g., config_models.py, config_models_2.py, config_models_3.py)

Modes:
1. SCAN - Analyze and report duplicates (safe, read-only)
2. CONSOLIDATE - Interactive mode to review and merge content
3. DELETE - Remove duplicates (requires confirmation)

Docker-safe: All operations use Linux paths internally.
import logging

logger = logging.getLogger(__name__)

"""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


@dataclass
class DuplicateFile:
    """Represents a duplicate file found during scan."""
    original_path: str
    duplicate_path: str
    original_size: int
    duplicate_size: int
    original_hash: str
    duplicate_hash: str
    identical_content: bool
    suffix_type: str  # '_2', '_3', '_part_2', etc.

    def to_dict(self) -> dict:
        """Docstring."""
        return asdict(self)

@dataclass
class ScanReport:
    """Scan results summary."""
    total_duplicates: int
    identical_duplicates: int
    different_duplicates: int
    total_wasted_bytes: int
    duplicates_by_suffix: Dict[str, int]
    duplicates_by_directory: Dict[str, int]
    duplicate_groups: List[Dict]

    def to_dict(self) -> dict:
        """Docstring."""
        return asdict(self)

class DuplicateFileScanner:
    """Scans project for duplicate files with version suffixes."""

    # Patterns to detect duplicate file suffixes
    DUPLICATE_PATTERNS = [
        r'_(\d+)\.',           # _2.py, _3.py, _4.py, etc.
        r'_part_(\d+)\.',      # _part_2.py, _part_3.py, etc.
        r'_v(\d+)_(\d+)\.',    # _v11_2.py, _v11_3.py (legacy versioning)
    ]

    # Directories to exclude from scan
    EXCLUDE_DIRS = {
        '__pycache__',
        '.git',
        'node_modules',
        '.venv',
        'venv',
        '.pytest_cache',
        '.mypy_cache',
        'dist',
        'build',
        'eggs',
        '*.egg-info',
        'archives',
        'data',
    }

    def __init__(self, root_path: str):
        """Initialize scanner with project root path."""
        self.root_path = Path(root_path).resolve()
        self.duplicates: List[DuplicateFile] = []
        self.duplicate_groups: Dict[str, List[str]] = defaultdict(list)

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scan."""
        parts = path.parts
        return any(exclude in parts for exclude in self.EXCLUDE_DIRS)

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"ERROR: {e}"

    def _extract_base_name(self, file_path: Path) -> Optional[Tuple[str, str]]:
        """
        Extract base filename and suffix type from a duplicate file.

        Returns:
            (base_name, suffix_type) or None if not a duplicate
        """
        filename = file_path.name

        for pattern in self.DUPLICATE_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                # Extract base name by removing the suffix
                base_name = re.sub(pattern, '.', filename)
                suffix_type = match.group(0).rstrip('.')
                return (base_name, suffix_type)

        return None

    def _find_original_file(self, duplicate_path: Path, base_name: str) -> Optional[Path]:
        """Find the original file (without suffix) for a duplicate."""
        original_path = duplicate_path.parent / base_name

        if original_path.exists() and original_path.is_file():
            return original_path

        return None

    def scan(self) -> ScanReport:
        """
        Scan project for duplicate files.

        Returns:
            ScanReport with detailed findings
        """
        logger.info(f"🔍 Scanning {self.root_path} for duplicate files...")

        # Walk through all files
        for file_path in self.root_path.rglob('*'):
            if not file_path.is_file() or self._should_exclude(file_path):
                continue

            # Check if this is a duplicate file
            result = self._extract_base_name(file_path)
            if not result:
                continue

            base_name, suffix_type = result

            # Find the original file
            original_path = self._find_original_file(file_path, base_name)

            if original_path:
                # Compare files
                original_hash = self._get_file_hash(original_path)
                duplicate_hash = self._get_file_hash(file_path)

                duplicate = DuplicateFile(
                    original_path=str(original_path.relative_to(self.root_path)),
                    duplicate_path=str(file_path.relative_to(self.root_path)),
                    original_size=original_path.stat().st_size,
                    duplicate_size=file_path.stat().st_size,
                    original_hash=original_hash,
                    duplicate_hash=duplicate_hash,
                    identical_content=(original_hash == duplicate_hash),
                    suffix_type=suffix_type,
                )

                self.duplicates.append(duplicate)

                # Group duplicates by base file
                group_key = str(original_path.relative_to(self.root_path))
                self.duplicate_groups[group_key].append(str(file_path.relative_to(self.root_path)))
            else:
                # Orphan duplicate (no original found) - still track it
                duplicate_hash = self._get_file_hash(file_path)

                duplicate = DuplicateFile(
                    original_path="ORPHAN",
                    duplicate_path=str(file_path.relative_to(self.root_path)),
                    original_size=0,
                    duplicate_size=file_path.stat().st_size,
                    original_hash="N/A",
                    duplicate_hash=duplicate_hash,
                    identical_content=False,
                    suffix_type=suffix_type,
                )

                self.duplicates.append(duplicate)
                self.duplicate_groups["ORPHANS"].append(str(file_path.relative_to(self.root_path)))

        return self._generate_report()

    def _generate_report(self) -> ScanReport:
        """Generate detailed scan report."""
        identical = sum(1 for d in self.duplicates if d.identical_content)
        different = len(self.duplicates) - identical

        total_wasted = sum(d.duplicate_size for d in self.duplicates if d.identical_content)

        # Count by suffix type
        by_suffix = defaultdict(int)
        for d in self.duplicates:
            by_suffix[d.suffix_type] += 1

        # Count by directory
        by_directory = defaultdict(int)
        for d in self.duplicates:
            dir_path = str(Path(d.duplicate_path).parent)
            by_directory[dir_path] += 1

        # Format duplicate groups
        groups = []
        for original, duplicates in sorted(self.duplicate_groups.items()):
            groups.append({
                'original': original,
                'duplicates': sorted(duplicates),
                'count': len(duplicates)
            })

        return ScanReport(
            total_duplicates=len(self.duplicates),
            identical_duplicates=identical,
            different_duplicates=different,
            total_wasted_bytes=total_wasted,
            duplicates_by_suffix=dict(by_suffix),
            duplicates_by_directory=dict(by_directory),
            duplicate_groups=groups,
        )

class DuplicateFileCleaner:
    """Handles cleanup operations for duplicate files."""

    def __init__(self, root_path: str, scanner: DuplicateFileScanner):
        """Initialize cleaner with scanner results."""
        self.root_path = Path(root_path).resolve()
        self.scanner = scanner
        self.deleted_files: List[str] = []
        self.backup_dir: Optional[Path] = None

    def create_backup(self) -> Path:
        """Create backup directory for deleted files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.root_path / 'archives' / f'cleanup_backup_{timestamp}'
        backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = backup_dir
        return backup_dir

    def delete_identical_duplicates(self, dry_run: bool = True) -> List[str]:
        """
        Delete duplicate files that are identical to their originals.

        Args:
            dry_run: If True, only simulate deletion

        Returns:
            List of deleted file paths
        """
        deleted = []

        for duplicate in self.scanner.duplicates:
            if not duplicate.identical_content or duplicate.original_path == "ORPHAN":
                continue

            duplicate_path = self.root_path / duplicate.duplicate_path

            if dry_run:
                logger.info(f"  [DRY RUN] Would delete: {duplicate.duplicate_path}")
                deleted.append(duplicate.duplicate_path)
            else:
                try:
                    # Backup before deletion
                    if self.backup_dir:
                        backup_path = self.backup_dir / duplicate.duplicate_path
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        import shutil
                        shutil.copy2(duplicate_path, backup_path)

                    # Delete the file
                    duplicate_path.unlink()
                    logger.info(f"  ✓ Deleted: {duplicate.duplicate_path}")
                    deleted.append(duplicate.duplicate_path)
                except Exception as e:
                    logger.info(f"  ✗ Error deleting {duplicate.duplicate_path}: {e}")

        self.deleted_files.extend(deleted)
        return deleted

    def delete_all_duplicates(self, dry_run: bool = True) -> List[str]:
        """
        Delete ALL duplicate files (including non-identical ones).

        Args:
            dry_run: If True, only simulate deletion

        Returns:
            List of deleted file paths
        """
        deleted = []

        for duplicate in self.scanner.duplicates:
            if duplicate.original_path == "ORPHAN":
                continue

            duplicate_path = self.root_path / duplicate.duplicate_path

            if dry_run:
                status = "IDENTICAL" if duplicate.identical_content else "DIFFERENT"
                logger.info(f"  [DRY RUN] Would delete ({status}): {duplicate.duplicate_path}")
                deleted.append(duplicate.duplicate_path)
            else:
                try:
                    # Backup before deletion
                    if self.backup_dir:
                        backup_path = self.backup_dir / duplicate.duplicate_path
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(duplicate_path, backup_path)

                    # Delete the file
                    duplicate_path.unlink()
                    status = "IDENTICAL" if duplicate.identical_content else "DIFFERENT"
                    logger.info(f"  ✓ Deleted ({status}): {duplicate.duplicate_path}")
                    deleted.append(duplicate.duplicate_path)
                except Exception as e:
                    logger.info(f"  ✗ Error deleting {duplicate.duplicate_path}: {e}")

        self.deleted_files.extend(deleted)
        return deleted

def print_report(report: ScanReport):
    """Print formatted scan report."""
    logger.info("\n" + "="*80)
    logger.info("📊 DUPLICATE FILE SCAN REPORT")
    logger.info("="*80)

    logger.info(f"\n📈 Summary:")
    logger.info(f"  Total duplicates found: {report.total_duplicates}")
    logger.info(f"  Identical to original:  {report.identical_duplicates}")
    logger.info(f"  Different from original: {report.different_duplicates}")
    logger.info(f"  Wasted space (identical): {report.total_wasted_bytes:,
        } bytes ({report.total_wasted_bytes / 1024:.2f} KB)")

    logger.info(f"\n🏷️  Duplicates by suffix type:")
    for suffix, count in sorted(report.duplicates_by_suffix.items(), key=lambda x: -x[1]):
        logger.info(f"  {suffix:15s}: {count:3d} files")

    logger.info(f"\n📁 Top directories with duplicates:")
    sorted_dirs = sorted(report.duplicates_by_directory.items(), key=lambda x: -x[1])[:10]
    for dir_path, count in sorted_dirs:
        logger.info(f"  {dir_path:60s}: {count:3d} files")

    logger.info(f"\n📦 Duplicate groups (showing first 20):")
    for group in report.duplicate_groups[:20]:
        logger.info(f"\n  Original: {group['original']}")
        for dup in group['duplicates']:
            logger.info(f"    → {dup}")

    if len(report.duplicate_groups) > 20:
        logger.info(f"\n  ... and {len(report.duplicate_groups) - 20} more groups")

    logger.info("\n" + "="*80)

def save_report(report: ScanReport, output_path: str):
    """Save report to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, indent=2)
    logger.info(f"\n💾 Report saved to: {output_path}")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Cleanup duplicate files in Agentic-Workflow project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan and report only (safe)
  python cleanup_duplicate_files.py --mode scan

  # Delete identical duplicates (dry run)
  python cleanup_duplicate_files.py --mode delete --identical-only --dry-run

  # Delete identical duplicates (REAL)
  python cleanup_duplicate_files.py --mode delete --identical-only

  # Delete ALL duplicates (dry run)
  python cleanup_duplicate_files.py --mode delete --dry-run

  # Delete ALL duplicates (REAL - DANGEROUS)
  python cleanup_duplicate_files.py --mode delete --confirm-delete-all
        """
    )

    parser.add_argument(
        '--mode',
        choices=['scan', # SQL query removed],
        default='scan',
        help='Operation mode (default: scan)'
    )

    parser.add_argument(
        '--root',
        default='/workspace',
        help='Project root path (default: /workspace for Docker)'
    )

    parser.add_argument(
        '--identical-only',
        action='store_true',
        help='Only delete files identical to their originals'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate deletion without actually deleting files'
    )

    parser.add_argument(
        '--confirm-delete-all',
        action='store_true',
        help='Confirm deletion of ALL duplicates (including non-identical)'
    )

    parser.add_argument(
        '--output',
        default='duplicate_scan_report.json',
        help='Output file for scan report (default: duplicate_scan_report.json)'
    )

    args = parser.parse_args()

    # Validate root path
    root_path = Path(args.root).resolve()
    if not root_path.exists():
        logger.info(f"❌ Error: Root path does not exist: {root_path}")
        return 1

    # Run scanner
    scanner = DuplicateFileScanner(str(root_path))
    report = scanner.scan()

    # Print report
    print_report(report)

    # Save report
    output_path = root_path / args.output
    save_report(report, str(output_path))

    # Handle deletion mode
    if args.mode == # SQL query removed:
        if report.total_duplicates == 0:
            logger.info("\n✅ No duplicates to delete!")
            return 0

        cleaner = DuplicateFileCleaner(str(root_path), scanner)

        # Create backup directory
        if not args.dry_run:
            backup_dir = cleaner.create_backup()
            logger.info(f"\n💾 Backup directory created: {backup_dir}")

        logger.info("\n🗑️  Starting deletion process...")

        if args.identical_only:
            logger.info("  Mode: Delete identical duplicates only")
            deleted = cleaner.delete_identical_duplicates(dry_run=args.dry_run)
        elif args.confirm_delete_all:
            logger.info("  Mode: Delete ALL duplicates (including non-identical)")
            if not args.dry_run:
                confirm = input("\n⚠️  WARNING: This will delete ALL duplicates. Type '# SQL remo...
                if confirm != "# SQL removed: DELETE ALL":
                    logger.info("❌ Deletion cancelled.")
                    return 1
            deleted = cleaner.delete_all_duplicates(dry_run=args.dry_run)
        else:
            logger.info("❌ Error: Must specify --identical-only or --confirm-delete-all")
            return 1

        logger.info(f"\n✅ Deletion complete: {len(deleted)} files {'would be ' if args.dry_run else
    ''}deleted")

        if not args.dry_run and cleaner.backup_dir:
            logger.info(f"💾 Backup saved to: {cleaner.backup_dir}")

    return 0

if __name__ == '__main__':
    exit(main())
