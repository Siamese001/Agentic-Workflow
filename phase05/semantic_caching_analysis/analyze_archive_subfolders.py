#!/usr/bin/env python3
"""
Analyze archive subfolder distribution for 01_agentic_core operations.
Shows what % of matches came from each archive subfolder.
"""

import json
from pathlib import Path
from collections import Counter

def analyze_archive_subfolders():
    """Parse migration plan to extract archive_name distribution."""
    
    # Load migration plan
    plan_path = Path("02_schemas/01_agentic_core_migration_and_rewrite_plan.json")
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    operations = plan.get('operations', [])
    print(f"Total operations: {len(operations)}")
    
    # Count operations by archive_name
    archive_counts = Counter()
    for op in operations:
        archive_name = op.get('archive_name', 'Unknown')
        archive_counts[archive_name] += 1
    
    # Create distribution table
    print("\n" + "="*80)
    print("ARCHIVE SUBFOLDER DISTRIBUTION ANALYSIS FOR 01_agentic_core")
    print("="*80)
    
    print(f"\nDistribution by Archive Subfolder:")
    print("-" * 70)
    print(f"{'Archive Subfolder':<35} {'Operations':<12} {'Percentage':<12} {'Archive Type':<15}")
    print("-" * 70)
    
    total_ops = len(operations)
    
    # Sort by count (highest first)
    for archive_name, count in archive_counts.most_common():
        percentage = (count / total_ops) * 100
        
        # Determine archive type based on folder location
        if archive_name in ["Agentic-Workflow-10_7_main", "Agentic-Workflow-10_8_core", 
                           "Agentic-Workflow-10_9", "Agentic-Workflow-10_11",
                           "v10.2", "v10.4", "v10.5", "v10.6", "v10.7",
                           "v10_0", "v10_1", "v2", "v5.6", "v6.0", "v6.2",
                           "v6.4", "v7.0", "v7.5", "v8.0", "v9.0", "v9.7", "v9.8", "v9.9",
                           "Resumable", "Monolith", "Monolithic", "Microservices Model"]:
            archive_type = "Resume Engine"
        elif archive_name in ["Agentic LIC", "Agentic-LIC", "Monolithic", "Old LIC", "deprecated in v13"]:
            archive_type = "Reachout Engine"
        else:
            archive_type = "Unknown"
        
        print(f"{archive_name:<35} {count:<12} {percentage:<12.1f}% {archive_type:<15}")
    
    print("-" * 70)
    print(f"{'TOTAL':<35} {total_ops:<12} {100.0:<12.1f}%")
    
    # Summary by archive type
    print(f"\nSummary by Archive Type:")
    print("-" * 40)
    
    resume_total = sum(count for archive, count in archive_counts.items() 
                      if archive in ["Agentic-Workflow-10_7_main", "Agentic-Workflow-10_8_core", 
                                   "Agentic-Workflow-10_9", "Agentic-Workflow-10_11",
                                   "v10.2", "v10.4", "v10.5", "v10.6", "v10.7",
                                   "v10_0", "v10_1", "v2", "v5.6", "v6.0", "v6.2",
                                   "v6.4", "v7.0", "v7.5", "v8.0", "v9.0", "v9.7", "v9.8", "v9.9",
                                   "Resumable", "Monolith", "Monolithic", "Microservices Model"])
    
    reachout_total = sum(count for archive, count in archive_counts.items() 
                        if archive in ["Agentic LIC", "Agentic-LIC", "Monolithic", "Old LIC", "deprecated in v13"])
    
    print(f"Resume Engine Archive: {resume_total} operations ({resume_total/total_ops*100:.1f}%)")
    print(f"Reachout Engine Archive: {reachout_total} operations ({reachout_total/total_ops*100:.1f}%)")
    
    print(f"\nKey Insights:")
    print("-" * 40)
    print(f"• Operations came from {len(archive_counts)} different archive subfolders")
    print(f"• Most used subfolder: {archive_counts.most_common(1)[0][0]}")
    print(f"• Archive concentration: {'High' if len(archive_counts) <= 3 else 'Medium' if len(archive_counts) <= 6 else 'Low'}")

if __name__ == "__main__":
    analyze_archive_subfolders()
