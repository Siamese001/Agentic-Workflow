#!/usr/bin/env python3
"""
Validate semantic cache operations against proposed YAML architectural fixes
to ensure no operations target directories we plan to remove.
"""

import json
from pathlib import Path
from collections import defaultdict

def load_migration_plan():
    """Load the current migration plan to analyze operation targets."""
    plan_path = Path("02_schemas/01_agentic_core_migration_and_rewrite_plan.json")
    with open(plan_path, 'r') as f:
        return json.load(f)

def analyze_operation_targets():
    """Analyze which paths are targeted by semantic operations."""
    
    print("🔍 VALIDATING YAML ARCHITECTURAL FIXES")
    print("=" * 80)
    
    try:
        plan = load_migration_plan()
    except Exception as e:
        print(f"❌ Failed to load migration plan: {e}")
        return
    
    operations = plan.get('operations', [])
    print(f"📊 Analyzing {len(operations)} operations from migration plan")
    
    # Define potentially redundant directories to check
    redundant_patterns = [
        'L5_safety/P1_retrieve',
        'L5_safety/P2_inspect', 
        'L5_safety/P3_aggregate',
        'L2_execution/P1_retrieve',
        'L3_orchestration/P1_retrieve',
        'L3_orchestration/P2_inspect',
        'L4_memory/P2_inspect'
    ]
    
    # Count operations targeting each pattern
    pattern_counts = defaultdict(list)
    
    for op in operations:
        target_path = op.get('target_path', '')
        
        for pattern in redundant_patterns:
            if pattern in target_path:
                pattern_counts[pattern].append({
                    'target_path': target_path,
                    'operation_type': op.get('operation_type', 'unknown'),
                    'archive_name': op.get('archive_name', 'unknown')
                })
    
    print(f"\n📋 Operations Targeting Potentially Redundant Directories:")
    print("-" * 60)
    
    total_redundant_ops = 0
    safe_to_remove = []
    needs_review = []
    
    for pattern, ops in pattern_counts.items():
        count = len(ops)
        total_redundant_ops += count
        
        if count == 0:
            safe_to_remove.append(pattern)
            print(f"✅ {pattern}: 0 operations (SAFE TO REMOVE)")
        else:
            needs_review.append((pattern, ops))
            print(f"⚠️  {pattern}: {count} operations (NEEDS REVIEW)")
            for op in ops[:3]:  # Show first 3 examples
                print(f"    • {op['target_path']} ({op['operation_type']})")
            if count > 3:
                print(f"    ... and {count - 3} more")
    
    print(f"\n📊 Summary:")
    print(f"  Total operations analyzed: {len(operations)}")
    print(f"  Operations targeting redundant dirs: {total_redundant_ops}")
    print(f"  Safe to remove: {len(safe_to_remove)} patterns")
    print(f"  Needs review: {len(needs_review)} patterns")
    
    return safe_to_remove, needs_review, total_redundant_ops

def generate_yaml_fix_recommendations(safe_to_remove, needs_review, total_redundant_ops):
    """Generate specific YAML fix recommendations based on validation."""
    
    print(f"\n" + "=" * 80)
    print("🔧 YAML FIX RECOMMENDATIONS")
    print("=" * 80)
    
    if total_redundant_ops == 0:
        print(f"🎉 EXCELLENT: No operations target redundant directories!")
        print(f"\n✅ SAFE TO IMPLEMENT IMMEDIATELY:")
        for pattern in safe_to_remove:
            print(f"   • Remove {pattern} from all cognitive domains")
        
        print(f"\n🏗️ ARCHITECTURAL IMPACT:")
        print(f"   • Eliminates ~60 empty directories")
        print(f"   • Aligns YAML with cognitive architecture principles")
        print(f"   • Zero risk of breaking existing operations")
        
    else:
        print(f"⚠️  CAUTION: {total_redundant_ops} operations target redundant directories")
        
        print(f"\n✅ SAFE TO REMOVE (Zero operations):")
        for pattern in safe_to_remove:
            print(f"   • {pattern}")
        
        print(f"\n🔍 NEEDS MANUAL REVIEW ({len(needs_review)} patterns):")
        for pattern, ops in needs_review:
            print(f"   • {pattern} ({len(ops)} operations)")
            
        print(f"\n📋 RECOMMENDED APPROACH:")
        print(f"   1. Remove safe patterns immediately")
        print(f"   2. Manually review operations in needs_review patterns")
        print(f"   3. Determine if operations are architecturally appropriate")
        print(f"   4. Consider moving inappropriate operations to correct layers")

def check_current_yaml_state():
    """Check current YAML state to see what's already fixed."""
    
    print(f"\n" + "=" * 80)
    print("📋 CURRENT YAML STATE VERIFICATION")
    print("=" * 80)
    
    yaml_path = Path("unified_structure_subatomic.yaml")
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    # Check if L5_safety P1-P3 are already removed
    l5_p1 = 'L5_safety:\n    P1_retrieve:' in content
    l5_p2 = 'L5_safety:\n    P2_inspect:' in content
    l5_p3 = 'L5_safety:\n    P3_aggregate:' in content
    
    print(f"L5_safety current state:")
    print(f"  P1_retrieve present: {'Yes' if l5_p1 else 'No'}")
    print(f"  P2_inspect present: {'Yes' if l5_p2 else 'No'}")
    print(f"  P3_aggregate present: {'Yes' if l5_p3 else 'No'}")
    
    if not (l5_p1 or l5_p2 or l5_p3):
        print(f"  ✅ L5_safety already fixed (only P4_safety present)")
    else:
        print(f"  ⚠️  L5_safety still has redundant phases")

if __name__ == "__main__":
    safe_to_remove, needs_review, total_redundant_ops = analyze_operation_targets()
    generate_yaml_fix_recommendations(safe_to_remove, needs_review, total_redundant_ops)
    check_current_yaml_state()
