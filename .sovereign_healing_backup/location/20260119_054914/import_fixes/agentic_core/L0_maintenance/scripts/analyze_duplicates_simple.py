"""
Simple Duplicate Analysis Script
Generates detailed table showing duplicate files with same filenames.
"""
import sys
from pathlib import Path
from collections import defaultdict
import hashlib

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return "ERROR"


def scan_for_duplicates():
    """Scan project for duplicate files."""
    file_hashes = defaultdict(list)  # hash -> [paths]
    
    # Extensions to scan
    extensions = {'.py', '.html', '.json', '.yaml', '.md', '.txt'}
    
    # Directories to exclude
    exclude_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'archive'}
    
    print("Scanning for duplicate files...")
    
    for file_path in project_root.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        
        # Check extension
        if file_path.suffix not in extensions:
            continue
        
        # Compute hash
        file_hash = compute_file_hash(file_path)
        if file_hash != "ERROR":
            file_hashes[file_hash].append(file_path)
    
    # Filter to only duplicates
    duplicates = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}
    
    return duplicates


def analyze_by_filename(duplicates):
    """Group duplicates by filename."""
    by_filename = defaultdict(list)
    
    for file_hash, paths in duplicates.items():
        for path in paths:
            filename = path.name
            by_filename[filename].append({
                'path': path,
                'hash': file_hash,
                'size': path.stat().st_size if path.exists() else 0
            })
    
    # Filter to only files with multiple copies
    return {name: files for name, files in by_filename.items() if len(files) > 1}


def classify_location(path_str: str) -> tuple:
    """Classify file location as canonical or stale."""
    if 'config/blueprint_sovereign' in path_str:
        return 'STALE', 'Blueprint folder (deprecated)'
    elif 'config/validators' in path_str:
        return 'STALE', 'Old validators location'
    elif 'observability/dashboard' in path_str:
        return 'STALE', 'Old dashboard location'
    elif 'L5_safety/validators' in path_str:
        return 'CANONICAL', 'L5 validators (current)'
    elif 'L2_execution/ToolRegistry' in path_str:
        return 'CANONICAL', 'L2 execution (current)'
    elif 'tests/unit/L5_safety' in path_str:
        return 'STALE', 'Nested test location'
    elif TESTS_UNIT_DIR in path_str and path_str.count('\\') == 2:
        return 'CANONICAL', 'Root test location'
    else:
        return 'REVIEW', 'Needs manual review'


def main():
    print("=" * 120)
    print("DETAILED DUPLICATE FILE ANALYSIS")
    print("=" * 120)
    print()
    
    # Scan for duplicates
    duplicates = scan_for_duplicates()
    print(f"Found {len(duplicates)} duplicate file sets")
    print()
    
    # Analyze by filename
    by_filename = analyze_by_filename(duplicates)
    print(f"Found {len(by_filename)} unique filenames with duplicates")
    print()
    
    # Generate detailed table
    print("=" * 120)
    print("DUPLICATE FILES - DETAILED BREAKDOWN")
    print("=" * 120)
    print()
    
    # Sort by filename
    sorted_files = sorted(by_filename.items(), key=lambda x: x[0])
    
    for idx, (filename, file_info) in enumerate(sorted_files, 1):
        # Check if all hashes are the same (identical files)
        hashes = set(f['hash'] for f in file_info)
        identical = len(hashes) == 1
        
        print(f"[{idx}] {filename}")
        print(f"    Copies: {len(file_info)}")
        print(f"    Size: {file_info[0]['size']:,} bytes")
        print(f"    Status: {'IDENTICAL CONTENT' if identical else 'DIFFERENT CONTENT - REQUIRES REVIEW'}")
        print()
        
        # Show each location
        for f in file_info:
            rel_path = str(f['path'].relative_to(project_root))
            status, reason = classify_location(rel_path)
            
            status_marker = {
                'CANONICAL': '[KEEP]',
                'STALE': '[DELETE]',
                'REVIEW': '[REVIEW]'
            }[status]
            
            print(f"    {status_marker:10} {rel_path}")
            print(f"               Reason: {reason}")
            print(f"               Hash: {f['hash'][:12]}...")
        
        print()
        
        # Recommendation
        if identical:
            canonical_count = sum(1 for f in file_info if classify_location(str(f['path'].relative_to(project_root)))[0] == 'CANONICAL')
            stale_count = sum(1 for f in file_info if classify_location(str(f['path'].relative_to(project_root)))[0] == 'STALE')
            
            print(f"    RECOMMENDATION: Safe to delete {stale_count} stale copies (keep {canonical_count} canonical)")
        else:
            print(f"    RECOMMENDATION: Files have DIFFERENT content!")
            print(f"                    1. Use CodeDeduplicationAgent to analyze functional differences")
            print(f"                    2. Use FilenameUniquenessGuardianAgent to suggest unique names")
            print(f"                    3. Manually review and decide: rename or delete")
        
        print()
        print("-" * 120)
        print()
    
    # Summary
    print()
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print()
    
    identical_count = sum(1 for _, files in by_filename.items() if len(set(f['hash'] for f in files)) == 1)
    different_count = len(by_filename) - identical_count
    
    total_files = sum(len(files) for files in by_filename.values())
    canonical_files = sum(1 for _, files in by_filename.items() for f in files 
                         if classify_location(str(f['path'].relative_to(project_root)))[0] == 'CANONICAL')
    stale_files = sum(1 for _, files in by_filename.items() for f in files 
                     if classify_location(str(f['path'].relative_to(project_root)))[0] == 'STALE')
    review_files = total_files - canonical_files - stale_files
    
    print(f"Total duplicate filename groups: {len(by_filename)}")
    print(f"  - Identical content (safe to delete): {identical_count}")
    print(f"  - Different content (needs review): {different_count}")
    print()
    print(f"Total files: {total_files}")
    print(f"  - Canonical (keep): {canonical_files}")
    print(f"  - Stale (delete): {stale_files}")
    print(f"  - Review needed: {review_files}")
    print()
    
    print("=" * 120)
    print("NEXT STEPS")
    print("=" * 120)
    print()
    print("For files with IDENTICAL content:")
    print("  Run: python scripts/delete_duplicates.py --execute")
    print()
    print("For files with DIFFERENT content:")
    print("  1. Review each file manually")
    print("  2. Use CodeDeduplicationAgent to analyze functional differences")
    print("  3. Use FilenameUniquenessGuardianAgent to rename if needed")
    print()


if __name__ == "__main__":
    main()
