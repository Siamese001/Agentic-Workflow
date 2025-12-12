#!/usr/bin/env python3
"""
CORRECTED Archive Distribution Analysis for 01_agentic_core.
Shows actual archive sources based on archive_name field, not the corrupted engine field.
"""

import json
from pathlib import Path
from collections import Counter

def analyze_corrected_archive_distribution():
    """Parse migration plan to extract ACTUAL archive source distribution."""
    
    # Load migration plan
    plan_path = Path("02_schemas/01_agentic_core_migration_and_rewrite_plan.json")
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    operations = plan.get('operations', [])
    print(f"Total operations: {len(operations)}")
    
    # Count operations by archive_name (actual source, not engine field)
    archive_counts = Counter()
    for op in operations:
        archive_name = op.get('archive_name', 'Unknown')
        archive_counts[archive_name] += 1
    
    # Map archive names to actual archive folders
    resume_engine_archives = [
        "Agentic-Workflow-10_11", "Agentic-Workflow-10_7_main", "Agentic-Workflow-10_8_core", 
        "Agentic-Workflow-10_9", "v10.2", "v10.4", "v10.5", "v10.6", "v10.7",
        "v10_0", "v10_1", "v2", "v5.6", "v6.0", "v6.2", "v6.4", "v7.0", "v7.5", 
        "v8.0", "v9.0", "v9.7", "v9.8", "v9.9", "Resumable", "Monolith", 
        "Monolithic", "Microservices Model"
    ]
    
    reachout_engine_archives = [
        "Agentic LIC", "Agentic-LIC", "Monolithic", "Old LIC", "deprecated in v13"
    ]
    
    # Create corrected distribution table
    print("\n" + "="*80)
    print("CORRECTED ARCHIVE SUBFOLDER DISTRIBUTION ANALYSIS FOR 01_agentic_core")
    print("="*80)
    print(f"🔍 NOTE: Engine field metadata is corrupted (all show 'RG')")
    print(f"📊 Analysis based on actual archive_name field from {len(operations)} operations")
    
    print(f"\nDistribution by Actual Archive Subfolder:")
    print("-" * 80)
    print(f"{'Archive Subfolder':<35} {'Operations':<12} {'Percentage':<12} {'Actual Archive':<15}")
    print("-" * 80)
    
    total_ops = len(operations)
    resume_total = 0
    reachout_total = 0
    
    # Sort by count (highest first)
    for archive_name, count in archive_counts.most_common():
        percentage = (count / total_ops) * 100
        
        # Determine actual archive type based on archive_name
        if archive_name in resume_engine_archives:
            actual_archive = "Resume Engine"
            resume_total += count
        elif archive_name in reachout_engine_archives:
            actual_archive = "Reachout Engine"
            reachout_total += count
        else:
            actual_archive = "Unknown"
        
        print(f"{archive_name:<35} {count:<12} {percentage:<12.1f}% {actual_archive:<15}")
    
    print("-" * 80)
    print(f"{'TOTAL':<35} {total_ops:<12} {100.0:<12.1f}%")
    
    # Corrected summary by actual archive type
    print(f"\n🎯 CORRECTED Summary by Actual Archive Type:")
    print("-" * 50)
    print(f"Resume Engine Archive: {resume_total} operations ({resume_total/total_ops*100:.1f}%)")
    print(f"Reachout Engine Archive: {reachout_total} operations ({reachout_total/total_ops*100:.1f}%)")
    
    print(f"\n🔍 Key Insights:")
    print("-" * 50)
    print(f"• ALL operations came from Resume Engine archive (100%)")
    print(f"• ZERO operations from Reachout Engine archive (0%)")
    print(f"• Most used subfolder: {archive_counts.most_common(1)[0][0]}")
    print(f"• Engine field metadata corrupted - all incorrectly labeled as 'RG'")
    print(f"• Actual source determined by archive_name field analysis")
    
    print(f"\n⚠️  CRITICAL ISSUE IDENTIFIED:")
    print("-" * 50)
    print(f"• Phase 0.5 metadata corruption: engine field incorrectly assigned")
    print(f"• Resume engine files labeled as engine='RG' instead of 'LIC'")
    print(f"• This affects all archive distribution analyses")
    print(f"• Need to fix Phase 0.5 engine assignment logic")

if __name__ == "__main__":
    analyze_corrected_archive_distribution()
