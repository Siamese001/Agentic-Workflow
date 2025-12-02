#!/usr/bin/env python3

import re

def fix_remaining_general_nodes():
    """Fix the 8 remaining general nodes in manage_*_costs sections"""
    
    print("=== FIXING REMAINING 8 GENERAL NODES ===")
    
    # Read the file as text
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The 8 general nodes are in these exact locations:
    # config/L5_safety/P4_safety/check_rules/manage_config_costs/general:
    # data/L5_safety/P4_safety/check_rules/manage_data_costs/general:
    # etc.
    
    # Pattern to match and fix the general nodes
    patterns_to_fix = [
        'manage_config_costs:\n          general:\n            update_memory:',
        'manage_data_costs:\n          general:\n            update_memory:',
        'manage_observability_costs:\n          general:\n            update_memory:',
        'manage_prompt_costs:\n          general:\n            update_memory:',
        'manage_runtime_costs:\n          general:\n            update_memory:',
        'manage_schema_costs:\n          general:\n            update_memory:',
        'manage_scripts_costs:\n          general:\n            update_memory:',
        'manage_tests_costs:\n          general:\n            update_memory:',
    ]
    
    for pattern in patterns_to_fix:
        if pattern in content:
            # Replace general: with update_memory: (promote the child)
            replacement = pattern.replace('general:\n            update_memory:', 'update_memory:')
            content = content.replace(pattern, replacement)
            print(f"  Fixed: {pattern.split(':')[0]}")
    
    # Write back
    with open('unified_structure_subatomic.yaml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed 8 remaining general nodes")

if __name__ == '__main__':
    fix_remaining_general_nodes()
