"""
Report Migration Script - SSOT Enforcement Phase 2

Migrates misplaced reports to the canonical SSOT location (docs/reports/).
Supports git-aware moves with history preservation and rollback capability.

Usage:
    python ops_scripts/maintenance/migrate_reports_to_ssot.py [options]

Options:
    --dry-run       Show what would be migrated without making changes
    --pilot N       Migrate only the first N reports (for testing)
    --force         Skip confirmation prompts
    --rollback      Rollback the last migration using the manifest
    --manifest PATH Path to migration manifest (default: auto-generated)
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
from agentic_core.utils.report_location_validator_types_util import SSOT_REPORTS_DIR, ReportLocationValidator

@dataclass
class MigrationEntry:
    """Record of a single file migration."""
    source: str
    destination: str
    timestamp: str
    status: str = 'pending'
    error: str | None = None
    git_tracked: bool = False

@dataclass
class MigrationManifest:
    """Complete record of a migration operation."""
    id: str = field(default_factory=lambda: datetime.now().strftime('%Y%m%d_%H%M%S'))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_files: int = 0
    migrated_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    entries: list[MigrationEntry] = field(default_factory=list)
    rollback_available: bool = True

class ReportMigrator:
    """
    Handles migration of reports to SSOT location.

    Supports:
    - Git-aware moves (preserves history)
    - Dry-run mode
    - Pilot migrations (limited count)
    - Rollback capability
    - Reference updates
    """

    def __init__(self, project_root: Path | None=None, dry_run: bool=False, pilot_count: int | None=None):
        self.project_root = project_root or PROJECT_ROOT
        self.dry_run = dry_run
        self.pilot_count = pilot_count
        self.validator = ReportLocationValidator(self.project_root)
        self.manifest: MigrationManifest | None = None
        self.manifest_dir = self.project_root / 'docs' / REPORTS_DIR / '.migration'

    def is_git_tracked(self, file_path: Path) -> bool:
        """Check if a file is tracked by git."""
        try:
            result = subprocess.run(['git', 'ls-files', '--error-unmatch', str(file_path)], cwd=self.project_root, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            raise
            return False

    def git_move(self, source: Path, destination: Path) -> bool:
        """Move a file using git mv to preserve history."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(['git', 'mv', str(source), str(destination)], cwd=self.project_root, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            raise
            return False

    def regular_move(self, source: Path, destination: Path) -> bool:
        """Move a file using regular file operations."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            return True
        except Exception:
            raise
            return False

    def backup_file(self, file_path: Path) -> Path | None:
        """Create a backup of a file before migration."""
        backup_dir = self.project_root / '.sovereign_healing_backup' / REPORTS_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            rel_path = file_path.relative_to(self.project_root)
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            raise
            return None

    def get_destination_path(self, source: Path) -> Path:
        """Calculate the destination path for a report file."""
        return self.project_root / SSOT_REPORTS_DIR / source.name

    def migrate_file(self, source: Path) -> MigrationEntry:
        """Migrate a single file to SSOT location."""
        destination = self.get_destination_path(source)
        timestamp = datetime.now().isoformat()
        try:
            rel_source = source.relative_to(self.project_root)
            rel_dest = destination.relative_to(self.project_root)
        except ValueError:
            rel_source = source
            rel_dest = destination
        entry = MigrationEntry(source=str(rel_source), destination=str(rel_dest), timestamp=timestamp, git_tracked=self.is_git_tracked(source))
        if self.dry_run:
            entry.status = 'dry_run'
            return entry
        if destination.exists():
            entry.status = 'skipped'
            entry.error = 'Destination file already exists'
            return entry
        backup = self.backup_file(source)
        if not backup:
            entry.status = 'failed'
            entry.error = 'Failed to create backup'
            return entry
        if entry.git_tracked:
            success = self.git_move(source, destination)
        else:
            success = self.regular_move(source, destination)
        if success:
            entry.status = 'migrated'
        else:
            entry.status = 'failed'
            entry.error = 'Move operation failed'
        return entry

    def run_migration(self) -> MigrationManifest:
        """Execute the migration process."""
        self.manifest = MigrationManifest()
        misplaced = self.validator.get_misplaced_reports()
        if self.pilot_count:
            misplaced = misplaced[:self.pilot_count]
        self.manifest.total_files = len(misplaced)
        print(f"\n{'=' * 60}")
        print('SSOT Report Migration')
        print(f"{'=' * 60}")
        print(f"Mode: {('DRY-RUN' if self.dry_run else 'LIVE')}")
        print(f'Files to migrate: {len(misplaced)}')
        print(f'Destination: {SSOT_REPORTS_DIR}/')
        print(f"{'=' * 60}\n")
        for result in misplaced:
            source = self.project_root / result.current_location
            entry = self.migrate_file(source)
            self.manifest.entries.append(entry)
            status_icon = {'migrated': '✅', 'dry_run': '🔍', 'skipped': '⏭️', 'failed': '❌'}.get(entry.status, '❓')
            print(f'{status_icon} {entry.source}')
            if entry.status == 'migrated':
                print(f'   → {entry.destination}')
                self.manifest.migrated_files += 1
            elif entry.status == 'failed':
                print(f'   ❌ {entry.error}')
                self.manifest.failed_files += 1
            elif entry.status == 'skipped':
                print(f'   ⏭️ {entry.error}')
                self.manifest.skipped_files += 1
        if not self.dry_run:
            self.save_manifest()
        print(f"\n{'=' * 60}")
        print('Migration Summary')
        print(f"{'=' * 60}")
        print(f'Total files:    {self.manifest.total_files}')
        print(f'Migrated:       {self.manifest.migrated_files}')
        print(f'Skipped:        {self.manifest.skipped_files}')
        print(f'Failed:         {self.manifest.failed_files}')
        if not self.dry_run:
            print(f'Manifest:       {self.get_manifest_path()}')
        print(f"{'=' * 60}\n")
        return self.manifest

    def get_manifest_path(self) -> Path:
        """Get the path for the migration manifest."""
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_id = self.manifest.id if self.manifest else 'unknown'
        return self.manifest_dir / f'migration_{manifest_id}.json'

    def save_manifest(self) -> Path:
        """Save the migration manifest to disk."""
        if not self.manifest:
            raise ValueError('No manifest to save')
        manifest_path = self.get_manifest_path()
        manifest_data = {'id': self.manifest.id, 'timestamp': self.manifest.timestamp, 'total_files': self.manifest.total_files, 'migrated_files': self.manifest.migrated_files, 'failed_files': self.manifest.failed_files, 'skipped_files': self.manifest.skipped_files, 'rollback_available': self.manifest.rollback_available, 'entries': [asdict(e) for e in self.manifest.entries]}
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)
        return manifest_path

    def load_manifest(self, manifest_path: Path) -> MigrationManifest:
        """Load a migration manifest from disk."""
        with open(manifest_path, encoding='utf-8') as f:
            data = json.load(f)
        manifest = MigrationManifest(id=data['id'], timestamp=data['timestamp'], total_files=data['total_files'], migrated_files=data['migrated_files'], failed_files=data['failed_files'], skipped_files=data['skipped_files'], rollback_available=data.get('rollback_available', True))
        for entry_data in data['entries']:
            manifest.entries.append(MigrationEntry(source=entry_data['source'], destination=entry_data['destination'], timestamp=entry_data['timestamp'], status=entry_data['status'], error=entry_data.get('error'), git_tracked=entry_data.get('git_tracked', False)))
        return manifest

    def rollback(self, manifest_path: Path | None=None) -> bool:
        """Rollback a migration using the manifest."""
        if manifest_path is None:
            if not self.manifest_dir.exists():
                print('❌ No migration manifests found')
                return False
            manifests = sorted(self.manifest_dir.glob('migration_*.json'))
            if not manifests:
                print('❌ No migration manifests found')
                return False
            manifest_path = manifests[-1]
        print(f'\n🔄 Rolling back migration from: {manifest_path.name}')
        manifest = self.load_manifest(manifest_path)
        if not manifest.rollback_available:
            print('❌ Rollback not available for this migration')
            return False
        rollback_count = 0
        for entry in manifest.entries:
            if entry.status != 'migrated':
                continue
            source = self.project_root / entry.destination
            destination = self.project_root / entry.source
            if not source.exists():
                print(f'⏭️ Skipping (not found): {entry.destination}')
                continue
            try:
                if entry.git_tracked:
                    success = self.git_move(source, destination)
                else:
                    success = self.regular_move(source, destination)
                if success:
                    print(f'✅ Restored: {entry.source}')
                    rollback_count += 1
                else:
                    print(f'❌ Failed to restore: {entry.source}')
            except Exception as e:
                raise
                print(f'❌ Error restoring {entry.source}: {e}')
        print(f'\n✅ Rollback complete: {rollback_count} files restored')
        manifest.rollback_available = False
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump({'id': manifest.id, 'timestamp': manifest.timestamp, 'total_files': manifest.total_files, 'migrated_files': manifest.migrated_files, 'failed_files': manifest.failed_files, 'skipped_files': manifest.skipped_files, 'rollback_available': False, 'rolled_back_at': datetime.now().isoformat(), 'entries': [asdict(e) for e in manifest.entries]}, f, indent=2)
        return True

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate reports to SSOT location (docs/reports/)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without making changes')
    parser.add_argument('--pilot', type=int, metavar='N', help='Migrate only the first N reports (for testing)')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--rollback', action='store_true', help='Rollback the last migration')
    parser.add_argument('--manifest', type=Path, help='Path to migration manifest for rollback')
    args = parser.parse_args()
    migrator = ReportMigrator(dry_run=args.dry_run, pilot_count=args.pilot)
    if args.rollback:
        success = migrator.rollback(args.manifest)
        return 0 if success else 1
    if not args.dry_run and (not args.force):
        misplaced = migrator.validator.get_misplaced_reports()
        count = args.pilot if args.pilot else len(misplaced)
        print(f'\n⚠️  About to migrate {count} report(s) to {SSOT_REPORTS_DIR}/')
        response = input('Continue? [y/N]: ').strip().lower()
        if response != 'y':
            print('Migration cancelled.')
            return 0
    manifest = migrator.run_migration()
    if manifest.failed_files > 0:
        return 1
    return 0
if __name__ == '__main__':
    sys.exit(main())
