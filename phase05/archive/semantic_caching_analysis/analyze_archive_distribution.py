#!/usr/bin/env python3
"""
Analyze semantic cache distribution for 01_agentic_core operations.
Shows what % of matches came from each archive subfolder.
"""

import json
import os
from pathlib import Path
from collections import Counter, defaultdict

def analyze_migration_plan():
    """Analyze the migration plan to extract archive distribution."""
    
    # Load migration plan
    plan_path = Path("02_schemas/01_agentic_core_migration_and_rewrite_plan.json")
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    operations = plan.get('operations', [])
    print(f"Total operations: {len(operations)}")
    
    # Group operations by semantic_hash to see unique matches
    hash_groups = defaultdict(list)
    for op in operations:
        hash_groups[op['semantic_hash']].append(op)
    
    print(f"\nUnique semantic hashes: {len(hash_groups)}")
    
    # Analyze each unique hash
    for i, (hash_val, ops) in enumerate(hash_groups.items()):
        print(f"\n=== Hash Group {i+1} ===")
        print(f"Hash: {hash_val}")
        print(f"Operations: {len(ops)}")
        print(f"Percentage: {len(ops)/len(operations)*100:.1f}%")
        
        # Show sample operation details
        sample_op = ops[0]
        print(f"Archive: {sample_op['archive_name']}")
        print(f"Engine: {sample_op['engine']}")
        print(f"Confidence: {sample_op['confidence']}")
        
        # Trace to semantic cache to find original file path
        trace_to_archive(hash_val)

def trace_to_archive(hash_val):
    """Trace a semantic hash back to its original archive file path."""
    
    # Search in semantic cache for this hash
    cache_root = Path("06_data/semantic_cache")
    
    # Look in both RG and LIC directories
    for engine in ["rg", "lic"]:
        pointer_dir = cache_root / "02_schemas" / "L1_archive" / "P0_5" / "ingest" / engine
        
        if pointer_dir.exists():
            pointer_file = pointer_dir / f"{hash_val}.pointer.json"
            if pointer_file.exists():
                try:
                    with open(pointer_file, 'r') as f:
                        pointer_data = json.load(f)
                    
                    # Extract original file path
                    canonical_relative = pointer_data.get('canonical_relative', '')
                    if canonical_relative:
                        # Determine which archive it came from based on the path
                        if 'resume_engine' in canonical_relative:
                            archive_type = "Resume Engine"
                        elif 'reachout_engine' in canonical_relative:
                            archive_type = "Reachout Engine"
                        else:
                            archive_type = "Unknown"
                        
                        # Extract subfolder
                        path_parts = canonical_relative.split('/')
                        if len(path_parts) >= 2:
                            subfolder = path_parts[1] if path_parts[0] in ['resume_engine', 'reachout_engine'] else path_parts[0]
                        else:
                            subfolder = "root"
                        
                        print(f"Original path: {canonical_relative}")
                        print(f"Archive type: {archive_type}")
                        print(f"Subfolder: {subfolder}")
                        
                        return {
                            'archive_type': archive_type,
                            'subfolder': subfolder,
                            'full_path': canonical_relative
                        }
                except Exception as e:
                    print(f"Error reading pointer file: {e}")
    
    print("No pointer file found for this hash")
    return None

def create_distribution_table():
    """Create a comprehensive distribution table."""
    
    print("\n" + "="*80)
    print("ARCHIVE DISTRIBUTION ANALYSIS FOR 01_agentic_core")
    print("="*80)
    
    # Load migration plan
    plan_path = Path("02_schemas/01_agentic_core_migration_and_rewrite_plan.json")
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    operations = plan.get('operations', [])
    
    # Track distribution by archive type and subfolder
    distribution = Counter()
    detailed_paths = []
    
    for op in operations:
        hash_val = op['semantic_hash']
        
        # Trace to archive
        result = trace_to_archive(hash_val)
        if result:
            key = f"{result['archive_type']} - {result['subfolder']}"
            distribution[key] += len([o for o in operations if o['semantic_hash'] == hash_val])
            detailed_paths.append({
                'hash': hash_val,
                'archive_type': result['archive_type'],
                'subfolder': result['subfolder'],
                'full_path': result['full_path'],
                'operations': len([o for o in operations if o['semantic_hash'] == hash_val])
            })
    
    # Print distribution table
    print(f"\nDistribution Table:")
    print("-" * 60)
    print(f"{'Archive Source':<30} {'Operations':<12} {'Percentage':<12}")
    print("-" * 60)
    
    total_ops = len(operations)
    for source, count in distribution.most_common():
        percentage = (count / total_ops) * 100
        print(f"{source:<30} {count:<12} {percentage:<12.1f}%")
    
    print("-" * 60)
    print(f"{'TOTAL':<30} {total_ops:<12} {100.0:<12.1f}%")
    
    # Show detailed breakdown
    print(f"\nDetailed Breakdown:")
    print("-" * 80)
    for path_info in detailed_paths:
        print(f"Hash: {path_info['hash'][:16]}...")
        print(f"  Source: {path_info['archive_type']} - {path_info['subfolder']}")
        print(f"  Path: {path_info['full_path']}")
        print(f"  Operations: {path_info['operations']}")
        print()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    create_distribution_table()
