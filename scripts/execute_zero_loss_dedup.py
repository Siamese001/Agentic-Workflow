#!/usr/bin/env python3
"""
Execute Zero-Loss Deduplication

Based on the comprehensive analysis, this script:
1. Reads the dedup analysis report
2. For each cluster, keeps the canonical file
3. Replaces non-canonical files with pointer files
4. Archives original duplicates
5. Generates verification report
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "06_data" / "dedup_analysis"
ARCHIVE_DIR = REPO_ROOT / "06_data" / "dedup_archive_comprehensive"
POINTER_DIR = REPO_ROOT / "06_data" / "dedup_pointers"

def load_latest_analysis() -> Dict:
    """Load the most recent analysis report."""
    reports = sorted(ANALYSIS_DIR.glob("dedup_analysis_*.json"), reverse=True)
    if not reports:
        raise FileNotFoundError("No analysis reports found")
    
    with open(reports[0]) as f:
        return json.load(f)


def create_pointer_file(original_path: Path, canonical_path: str, source_hash: str) -> str:
    """Create pointer file content."""
    return json.dumps({
        "pointer_type": "dedup",
        "canonical_path": canonical_path,
        "reason": "AST+semantic duplicate - zero-loss merge",
        "source_hash": source_hash,
        "original_path": str(original_path),
        "created": datetime.now().isoformat(),
    }, indent=2)


def execute_dedup(dry_run: bool = True) -> Dict:
    """Execute the deduplication."""
    report = load_latest_analysis()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "clusters_processed": 0,
        "files_archived": 0,
        "pointers_created": 0,
        "bytes_recovered": 0,
        "errors": [],
    }
    
    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        POINTER_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print(f"ZERO-LOSS DEDUPLICATION EXECUTION {'(DRY RUN)' if dry_run else ''}")
    print("=" * 70)
    print(f"\nAnalysis: {report['timestamp']}")
    print(f"Total clusters: {len(report['clusters'])}")
    print(f"Total duplicates: {report['total_duplicates']}")
    print(f"Bytes recoverable: {report['bytes_recoverable']:,}")
    
    for cluster in report['clusters']:
        cluster_id = cluster['cluster_id']
        canonical = cluster['canonical_path']
        merge_plan = cluster['merge_plan']
        non_canonical = merge_plan['non_canonical']
        
        if not non_canonical:
            continue
        
        print(f"\n[{cluster_id}] Processing {len(non_canonical)} duplicates")
        print(f"  Canonical: {canonical}")
        
        for nc_path_str in non_canonical:
            nc_path = REPO_ROOT / nc_path_str
            
            if not nc_path.exists():
                print(f"  [SKIP] {nc_path_str} (not found)")
                continue
            
            try:
                file_size = nc_path.stat().st_size
                
                if not dry_run:
                    # Archive the original
                    archive_path = ARCHIVE_DIR / nc_path_str
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(nc_path, archive_path)
                    
                    # Create pointer file
                    pointer_content = create_pointer_file(
                        nc_path,
                        canonical,
                        merge_plan.get('canonical_hash', 'unknown')
                    )
                    
                    # Replace original with pointer
                    pointer_path = nc_path.with_suffix('.py.dedup_pointer.json')
                    pointer_path.write_text(pointer_content)
                    
                    # Remove original
                    nc_path.unlink()
                    
                    results['pointers_created'] += 1
                
                results['files_archived'] += 1
                results['bytes_recovered'] += file_size
                print(f"  [{'WOULD ARCHIVE' if dry_run else 'ARCHIVED'}] {nc_path_str} ({file_size} bytes)")
                
            except Exception as e:
                results['errors'].append({
                    "path": nc_path_str,
                    "error": str(e)
                })
                print(f"  [ERROR] {nc_path_str}: {e}")
        
        results['clusters_processed'] += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Clusters processed: {results['clusters_processed']}")
    print(f"Files archived: {results['files_archived']}")
    print(f"Pointers created: {results['pointers_created']}")
    print(f"Bytes recovered: {results['bytes_recovered']:,} ({results['bytes_recovered'] / 1024 / 1024:.2f} MB)")
    print(f"Errors: {len(results['errors'])}")
    
    if dry_run:
        print("\n[DRY RUN] No files were actually modified.")
        print("Run with --execute to perform the deduplication.")
    
    return results


if __name__ == "__main__":
    import sys
    
    dry_run = "--execute" not in sys.argv
    
    results = execute_dedup(dry_run=dry_run)
    
    # Save results
    results_path = ANALYSIS_DIR / f"dedup_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")
