#!/usr/bin/env python3
"""
Audit review_pending folder to find unique code not in approved YAML folders.
Compare file contents to detect duplicates vs unique code.
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
        content = path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except (ValueError, TypeError, KeyError):
        return ""


def get_file_signature(path: Path) -> tuple:
    """Get signature: (hash, size, first_line)."""
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        lines = content.strip().split('\n')
        first_meaningful = ""
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('"""'):
                first_meaningful = line.strip()[:80]
                break
        return (get_file_hash(path), path.stat().st_size, first_meaningful)
    except (ValueError, TypeError, KeyError):
        return ("", 0, "")


def main():
    # Build hash index of all approved files
    print("Building index of approved files...")
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

    print(f"  Indexed {len(approved_hashes)} unique file hashes")
    print(f"  Indexed {len(approved_names)} unique filenames")

    # Scan review_pending
    print(f"\nScanning {REVIEW_PENDING}...")

    pending_files = list(REVIEW_PENDING.rglob('*.py'))
    print(f"  Found {len(pending_files)} Python files")

    duplicates = []
    unique_files = []
    name_matches = []

    for f in pending_files:
        if '__pycache__' in str(f):
            continue

        h = get_file_hash(f)

        if h in approved_hashes:
            duplicates.append((f, approved_hashes[h][0]))
        elif f.name in approved_names:
            name_matches.append((f, approved_names[f.name]))
        else:
            unique_files.append(f)

    # Report
    print("\n" + "=" * 80)
    print("AUDIT RESULTS")
    print("=" * 80)

    print(f"\nEXACT DUPLICATES (can be deleted): {len(duplicates)}")
    for pending, approved in duplicates[:10]:
        print(f"  {pending.name} == {approved.relative_to(REPO)}")
    if len(duplicates) > 10:
        print(f"  ... and {len(duplicates) - 10} more")

    print(f"\nNAME MATCHES (need content review): {len(name_matches)}")
    for pending, approved_list in name_matches[:10]:
        size_pending = pending.stat().st_size
        size_approved = approved_list[0].stat().st_size
        status = "SAME SIZE" if size_pending == size_approved else f"DIFF ({size_pending} vs {size_approved})"
        print(f"  {pending.name}: {status}")
    if len(name_matches) > 10:
        print(f"  ... and {len(name_matches) - 10} more")

    print(f"\nUNIQUE FILES (not in approved folders): {len(unique_files)}")
    for f in unique_files[:20]:
        rel = f.relative_to(REVIEW_PENDING)
        size = f.stat().st_size
        print(f"  {rel} ({size} bytes)")
    if len(unique_files) > 20:
        print(f"  ... and {len(unique_files) - 20} more")

    # Detailed unique file analysis
    if unique_files:
        print("\n" + "-" * 80)
        print("UNIQUE FILE DETAILS (first 10):")
        print("-" * 80)
        for f in unique_files[:10]:
            print(f"\n>>> {f.relative_to(REVIEW_PENDING)}")
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                # Show first 15 non-empty lines
                shown = 0
                for line in lines:
                    if line.strip():
                        print(f"    {line[:100]}")
                        shown += 1
                        if shown >= 15:
                            break
            except (ValueError, TypeError, KeyError) as e:
                print(f"    ERROR: {e}")

    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print(f"  - DELETE {len(duplicates)} exact duplicates")
    print(f"  - REVIEW {len(name_matches)} name matches for content merge")
    print(f"  - EVALUATE {len(unique_files)} unique files for inclusion or archival")
    print("  - MOVE entire folder to 06_data/deprecated/review_pending_archive")


if __name__ == '__main__':
    main()
