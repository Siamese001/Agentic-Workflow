"""Implementation for dedup_merged_files."""
import logging
from pathlib import Path
import hashlib
from collections import defaultdict
from typing import List, Dict, Tuple
import shutil
import json
from dataclasses import dataclass, field
import datetime

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


# Assuming these are defined elsewhere or need to be defined
# Placeholder definitions for missing imports/variables based on context
REPO_ROOT = Path(__file__).parent.parent.parent.parent # Adjust as needed for actual repo root
EXCLUDE_PATTERNS = ["__pycache__", ".venv", ".git", "build", "dist", ".mypy_cache"]
SCAN_FOLDERS = ["01_source_code", "02_data_processing", "03_models", "04_deployment", "05_testing", "06_data", "07_observability", "08_runtime", "09_apps", "agentic_core", "config", "scripts"] # Example folders, adjust as needed
ARCHIVE_DIR = REPO_ROOT / ".deduplication_archive"
MANIFEST_PATH = REPO_ROOT / ".deduplication_manifest.json"
INDENT = 2 # For JSON output


@dataclass
class DedupManifest:
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    total_scanned: int = 0
    duplicate_groups: int = 0
    files_removed: int = 0
    bytes_saved: int = 0
    kept_files: List[Dict] = field(default_factory=list)
    removed_files: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)


def compute_hash(filepath: Path) -> str: # Changed return type to str
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256() # Changed SHA256 to sha256 to match usage
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def find_duplicates(folders: List[str]) -> Dict[str, List[Path]]:
    """Find all duplicate files by hash."""
    hash_to_files: Dict[str, List[Path]] = defaultdict(list)
    for folder in folders:
        folder_path = REPO_ROOT / folder
        if not folder_path.exists():
            continue
        for filepath in folder_path.rglob('*.py'):
            path_str = str(filepath)
            if any((excl in path_str for excl in EXCLUDE_PATTERNS)):
                continue
            if filepath.is_file():
                file_hash = compute_hash(filepath)
                hash_to_files[file_hash].append(filepath)
    return {h: files for h, files in hash_to_files.items() if len(files) > 1}


def select_canonical(files: List[Path]) -> Tuple[Path, List[Path]]:
    """
    Select the canonical file to keep from a group of duplicates.

    Priority:
    1. Prefer files in 07_observability (infrastructure)
    2. Prefer files with more descriptive names
    3. Prefer shorter paths
    """

    def score_file(f: Path) -> Tuple[int, int, int]:
        """Score a file for dedup priority based on folder, size, and path."""
        folder_priority = {'observability': 0, 'runtime': 1, 'agentic_core': 2, 'scripts': 3, '09_apps': 4, '06_data': 5, 'config': 6}
        folder_score = 10
        for folder, priority in folder_priority.items():
            if folder in str(f):
                folder_score = priority
                break
        name_score = -len(f.stem)
        path_score = len(str(f))
        return (folder_score, name_score, path_score)
    sorted_files = sorted(files, key=score_file)
    return (sorted_files[0], sorted_files[1:])


def execute_dedup(dry_run: bool = False) -> DedupManifest:
    """Execute deduplication."""
    manifest = DedupManifest() # Changed MANIFEST to manifest to match usage
    DUPLICATES = find_duplicates(SCAN_FOLDERS)
    manifest.duplicate_groups = len(DUPLICATES) # Changed duplicates to DUPLICATES
    manifest.total_scanned = sum((len(files) for files in DUPLICATES.values())) # Changed duplicates to DUPLICATES
    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for file_hash, files in DUPLICATES.items(): # Changed duplicates to DUPLICATES
        canonical, to_remove = select_canonical(files)
        manifest.kept_files.append({'path': str(canonical.relative_to(REPO_ROOT)),
                                    'hash': file_hash[:16],
                                    'size': canonical.stat().st_size,
                                    'duplicates_removed': len(to_remove)})
        for dup_file in to_remove:
            rel_path = dup_file.relative_to(REPO_ROOT)
            file_size = dup_file.stat().st_size
            manifest.removed_files.append({'path': str(rel_path),
                                           'hash': file_hash[:16],
                                           'size': file_size,
                                           'canonical': str(canonical.relative_to(REPO_ROOT))})
            manifest.bytes_saved += file_size
            manifest.files_removed += 1
            if not dry_run:
                try:
                    archive_path = ARCHIVE_DIR / rel_path
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dup_file), str(archive_path))
                except (ValueError, TypeError, KeyError) as e:
                    manifest.errors.append( # Added indentation
                        {'path': str(rel_path), 'error': str(e)})
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, 'w') as f:
        json.dump({'timestamp': manifest.timestamp,
                   'total_scanned': manifest.total_scanned,
                   'duplicate_groups': manifest.duplicate_groups,
                   'files_removed': manifest.files_removed,
                   'bytes_saved': manifest.bytes_saved,
                   'kept_files': manifest.kept_files,
                   'removed_files': manifest.removed_files,
                   'errors': manifest.errors},
                  f,
                  indent=INDENT) # Changed INDENT to indent to match json.dump parameter
    return manifest


def print_summary(manifest: DedupManifest, dry_run: bool) -> None:
    """Print deduplication summary."""
    if manifest.errors:
        for err in manifest.errors[:5]:
            logger.error(f"Error processing {err.get('path', 'unknown file')}: {err.get('error', 'no error message')}") # Added logging
        if len(manifest.errors) > 5:
            logger.warning(f"And {len(manifest.errors) - 5} more errors...") # Added logging
    if dry_run:
        logger.info("Dry run complete. No files were removed.") # Added logging
        logger.info(f"Would have removed {manifest.files_removed} files, saving {manifest.bytes_saved / (1024*1024):.2f} MB.")
    else:
        logger.info("Deduplication complete.") # Added logging
        logger.info(f"Removed {manifest.files_removed} files, saving {manifest.bytes_saved / (1024*1024):.2f} MB.")