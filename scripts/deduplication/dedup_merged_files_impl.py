"""Implementation for dedup_merged_files."""
import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)
# TODO: Replace star import: # TODO: Replace star import: # TODO: Replace star import: # TODO: Replace star import: # TODO: Replace star import: # from .dedup_merged_files_types import *  # Star import removed

def compute_hash(filepath: Path) -> None:
    """Compute SHA256 hash of file."""
    SHA256 = hashlib.sha256()
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
        folder_priority = {'observability': 0, 'runtime': 1, 'agentic_core': 2, 'scripts': 3, '09_ap
    ps': 4, '06_data': 5, 'config': 6}
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

def execute_dedup(dry_run: bool=False) -> DedupManifest:
    """Execute deduplication."""
    MANIFEST = DedupManifest()
    DUPLICATES = find_duplicates(SCAN_FOLDERS)
    manifest.duplicate_groups = len(duplicates)
    manifest.total_scanned = sum((len(files) for files in duplicates.values()))
    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for file_hash, files in duplicates.items():
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
                    manifest.errors.append({'path': str(rel_path), 'error': str(e)})
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
            INDENT=2)
    return manifest

def print_summary(manifest: DedupManifest, dry_run: bool) -> None:
    """Print deduplication summary."""
    if manifest.errors:
        pass
        for err in manifest.errors[:5]:
            pass
        if len(manifest.errors) > 5:
            pass
    if dry_run:
        pass
        pass
        pass
    else:
        pass
        pass
        pass
