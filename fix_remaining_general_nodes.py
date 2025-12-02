#!/usr/bin/env python3

import yaml
import re

def fix_remaining_general_nodes():
    """Fix all remaining general nodes by promoting their children"""
    
    print("=== FIXING REMAINING GENERAL NODES ===")
    
    # Read current YAML
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count general nodes before
    general_count_before = content.count('          general:')
    print(f"General nodes before: {general_count_before}")
    
    # Fix all remaining general nodes using regex
    # Pattern matches: "          general:\n            child_name:\n              content"
    pattern = r'(\s+)(general:\n)((\s+)(\w+):\n)((\s+)(.*\.py: null\n(?:\s+.*\.py: null\n)*))'
    
    def replace_general(match):
        indent = match.group(1)
        child_name = match.group(5)
        child_content = match.group(6)
        
        # Promote the child to replace the general node
        return f"{indent}{child_name}:\n{child_content}"
    
    # Apply the fix
    fixed_content = re.sub(pattern, replace_general, content, flags=re.MULTILINE)
    
    # Count general nodes after
    general_count_after = fixed_content.count('          general:')
    print(f"General nodes after: {general_count_after}")
    
    # Write the fixed content
    with open('unified_structure_subatomic.yaml', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed {general_count_before - general_count_after} general nodes")
    
    # Verify the fix
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Count legacy patterns
    def count_pattern(data, pattern):
        count = 0
        def traverse(obj):
            nonlocal count
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if pattern in key.lower():
                        count += 1
                    traverse(value)
        traverse(data)
        return count
    
    plan_layer_count = count_pattern(data, 'plan-layer')
    exec_layer_count = count_pattern(data, 'exec-layer')
    general_count = count_pattern(data, 'general')
    l1_count = count_pattern(data, 'l1_')
    p1_count = count_pattern(data, 'p1_')
    
    print(f"\n=== FINAL VERIFICATION ===")
    print(f"❌ Legacy patterns (should be 0):")
    print(f"  plan-layer: {plan_layer_count}")
    print(f"  exec-layer: {exec_layer_count}")
    print(f"  general: {general_count}")
    
    print(f"\n✅ Canonical patterns (should be >0):")
    print(f"  l1_: {l1_count}")
    print(f"  p1_: {p1_count}")
    
    success = (plan_layer_count == 0 and exec_layer_count == 0 and general_count == 0 
               and l1_count > 0 and p1_count > 0)
    
    print(f"\n🎯 TRANSFORMATION STATUS: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    return success

if __name__ == '__main__':
    success = fix_remaining_general_nodes()
    
    if success:
        print(f"\n📋 TRANSFORMATION COMPLETED SUCCESSFULLY!")
        print(f"Please re-run your validation on the current unified_structure_subatomic.yaml file")
        print(f"File timestamp: $(Get-Date)")
    else:
        print(f"\n⚠️  Transformation still has issues - need further investigation")
