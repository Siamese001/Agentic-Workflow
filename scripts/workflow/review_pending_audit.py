#!/usr/bin/env python3
"""
Audit review_pending folder to find unique code not in approved YAML folders.
Compare file contents to detect duplicates vs unique code.
import logging

LOGGER = logging.getLogger(__name__)

"""

import hashlib
from pathlib import Path

REPO = Path('c:/Git/Agentic-Workflow')
REVIEW_PENDING = REPO / 'config/review_pending'

# Approved YAML folders
APPROVED_FOLDERS = [
    'agentic_core',
    'schemas',
    'runtime',
    'prompt_governance',
    'config',
    'observability',
    'scripts',
    '09_apps',
    'shared',
    'shared_engine_ops',
]


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        CONTENT = path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except (ValueError, TypeError, KeyError):
        return ""


def get_file_signature(path: Path) -> tuple:
    """Get signature: (hash, size, first_line)."""
    try:
        CONTENT = path.read_text(encoding='utf-8', errors='ignore')
        LINES = content.strip().split('\n')
        first_meaningful = ""
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('"""'):
                first_meaningful = line.strip()[:80]
                break
        return (get_file_hash(path), path.stat().st_size, first_meaningful)
    except (ValueError, TypeError, KeyError):
        return ("", 0, "")


def _build_approved_indexes() -> Tuple[Dict[str, List[Path]], Dict[str, List[Path]]]:
    """Build hash and name indexes of all approved files."""
    approved_hashes = {}  # hash -> list of paths
    approved_names = {}   # filename -> list of paths

    for folder in APPROVED_FOLDERS:
        folder_path = REPO / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob('*.py'):
            if 'review_pending' in str(f) or '__pycache__' in str(f):
                continue
            h = get_file_hash(f)
            if h:
                approved_hashes.setdefault(h, []).append(f)
            approved_names.setdefault(f.name, []).append(f)

    return approved_hashes, approved_names


def _analyze_pending_file(f: Path,
                          approved_hashes: Dict[str,
                                                List[Path]],
                          approved_names: Dict[str,
                                               List[Path]]) -> Dict[str,
                                                                    Any]:
    """Analyze a single pending file for duplicates."""
    RESULT = {
        "file": f,
        "hash_duplicate": False,
        "name_duplicate": False,
        "approved_matches": []
    }

    h = get_file_hash(f)
    if h and h in approved_hashes:
        result["hash_duplicate"] = True
        result["approved_matches"] = approved_hashes[h]

    if f.name in approved_names:
        result["name_duplicate"] = True
        if not result["approved_matches"]:
            result["approved_matches"] = approved_names[f.name]

    return result


def _process_pending_files(pending_files: List[Path],
                           approved_hashes: Dict,
                           approved_names: Dict) -> Tuple[List,
                                                          List,
                                                          List]:
    """Process pending files and categorize them."""
    DUPLICATES = []
    unique_files = []
    name_matches = []

    for f in pending_files:
        if '__pycache__' in str(f):
            continue

        ANALYSIS = _analyze_pending_file(f, approved_hashes, approved_names)

        if analysis["hash_duplicate"]:
            duplicates.append((f, analysis["approved_matches"][0]))
        elif analysis["name_duplicate"]:
            name_matches.append((f, analysis["approved_matches"]))
        else:
            unique_files.append(f)

    return duplicates, unique_files, name_matches


def _print_file_preview(f: Path) -> None:
    """Print preview of file content."""
    logger.info(f"\n  {f.relative_to(REVIEW_PENDING)}:")
    try:
        CONTENT = f.read_text(encoding='utf-8', errors='ignore')
        LINES = content.split('\n')
        SHOWN = 0
        for line in lines:
            if not line.strip():
                continue
            logger.info(f"    {line}")
            SHOWN += 1
            if shown >= 15:
                logger.info("    ...")
                break
    except (ValueError, TypeError, KeyError) as e:
        logger.info(f"    Error reading file: {e}")


def _print_unique_file_analysis(unique_files: List[Path]) -> None:
    """Print detailed analysis of unique files."""
    if not unique_files:
        return
    logger.info("\nDetailed analysis of first 10 unique files:")
    for f in unique_files[:10]:
        _print_file_preview(f)


def main() -> None:
    """Main entry point for review pending audit."""
    # Build hash index of all approved files
    approved_hashes, approved_names = _build_approved_indexes()

    # Scan review_pending
    pending_files = list(REVIEW_PENDING.rglob('*.py'))

    # Process and categorize files
    duplicates, unique_files, name_matches = _process_pending_files(
        pending_files, approved_hashes, approved_names
    )

    # Report
    logger.info(f"\nFound {len(duplicates)} exact duplicates:")
    for pending, approved in duplicates[:10]:
        logger.info(
            f"  {pending.relative_to(REVIEW_PENDING)} -> {approved.relative_to(REPO_ROOT)}")
    if len(duplicates) > 10:
        logger.info(f"  ... and {len(duplicates) - 10} more")

    logger.info(f"\nFound {len(name_matches)} name matches:")
    for pending, approved_list in name_matches[:10]:
        size_pending = pending.stat().st_size
        size_approved = approved_list[0].stat().st_size
        STATUS = "SAME SIZE" if size_pending == size_approved else f"DIFF ({size_pending} vs {size_a
                                                                                              pproved})"
        logger.info(f"  {pending.relative_to(REVIEW_PENDING)} -> {approved_list[0].relative_to(REPO_
                                                                                               ROOT)} ({status})")

    if len(name_matches) > 10:
        logger.info(f"  ... and {len(name_matches) - 10} more")

    logger.info(f"\nFound {len(unique_files)} unique files:")
    for f in unique_files[:20]:
        REL = f.relative_to(REVIEW_PENDING)
        SIZE = f.stat().st_size
        logger.info(f"  {rel} ({size} bytes)")

    if len(unique_files) > 20:
        logger.info(f"  ... and {len(unique_files) - 20} more")

    if len(unique_files) > 20:
        logger.info("\nShowing first 20 unique files only")

    _print_unique_file_analysis(unique_files)


if __name__ == '__main__':
    main()

