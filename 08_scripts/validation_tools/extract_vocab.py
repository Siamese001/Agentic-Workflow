#!/usr/bin/env python3
"""
Extract all actual intents, axes, and verb_groups from unified_structure_subatomic.yaml
"""

import yaml
from pathlib import Path

def extract_vocab_from_tree(tree, domains, layers, phases):
    """Extract all unique intents, axes, and verb_groups from the tree structure"""
    
    intents = set()
    axes = set()
    verb_groups = set()
    
    for domain_name, domain_content in tree.items():
        if domain_name not in domains:
            continue
            
        for layer_name, layer_content in domain_content.items():
            if layer_name not in layers:
                continue
                
            for phase_name, phase_content in layer_content.items():
                if phase_name not in phases:
                    continue
                    
                # Skip __init__.py files (they're leaves, not structural nodes)
                if isinstance(phase_content, dict):
                    for intent_name, intent_content in phase_content.items():
                        # Skip __init__.py files
                        if intent_name == '__init__.py' or not isinstance(intent_content, dict):
                            continue
                            
                        intents.add(intent_name)
                        
                        for axis_name, axis_content in intent_content.items():
                            # Skip __init__.py files
                            if axis_name == '__init__.py' or not isinstance(axis_content, dict):
                                continue
                                
                            axes.add(axis_name)
                            
                            for verb_group_name, verb_group_content in axis_content.items():
                                # Skip __init__.py files
                                if verb_group_name == '__init__.py' or not isinstance(verb_group_content, dict):
                                    continue
                                    
                                verb_groups.add(verb_group_name)
    
    return sorted(intents), sorted(axes), sorted(verb_groups)

def main():
    yaml_path = Path('unified_structure_subatomic.yaml')
    
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found")
        return
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    # Split the file - tree structure before line 3080, meta after
    lines = content.split('\n')
    tree_lines = [line for line in lines if not line.startswith('# unified_structure_subatomic_meta.yaml') and line.strip() != '']
    meta_start = None
    for i, line in enumerate(lines):
        if line.startswith('# unified_structure_subatomic_meta.yaml'):
            meta_start = i + 1
            break
    
    if meta_start is None:
        print("Error: Could not find meta section")
        return
    
    # Parse tree structure (everything before meta comment)
    tree_content = '\n'.join(lines[:meta_start-1])
    tree_data = yaml.safe_load(tree_content)
    
    # Parse meta section (everything after meta comment)
    meta_content = '\n'.join(lines[meta_start:])
    meta_data = yaml.safe_load(meta_content)
    
    # Extract meta sections
    domains = list(meta_data.get('domains', {}).keys())
    layers = list(meta_data.get('layers', {}).keys())
    phases = list(meta_data.get('phases', {}).keys())
    
    print(f"Found {len(domains)} domains: {domains}")
    print(f"Found {len(layers)} layers: {layers}")
    print(f"Found {len(phases)} phases: {phases}")
    
    # Extract tree structure (exclude meta section)
    tree = {k: v for k, v in tree_data.items() if k != 'meta'}
    
    # Extract vocabulary
    intents, axes, verb_groups = extract_vocab_from_tree(tree, domains, layers, phases)
    
    print(f"Found {len(intents)} unique intents:")
    for intent in intents:
        print(f"  - {intent}")
    
    print(f"\nFound {len(axes)} unique axes:")
    for axis in axes:
        print(f"  - {axis}")
    
    print(f"\nFound {len(verb_groups)} unique verb_groups:")
    for verb_group in verb_groups:
        print(f"  - {verb_group}")
    
    # Compare with current meta
    current_intents = meta_data.get('intents', [])
    current_axes = meta_data.get('axes', [])
    current_verb_groups = meta_data.get('verb_groups', []) if 'verb_groups' in meta_data else []
    
    print(f"\n=== MISSING FROM META ===")
    missing_intents = set(intents) - set(current_intents)
    if missing_intents:
        print(f"Missing intents ({len(missing_intents)}):")
        for intent in sorted(missing_intents):
            print(f"  - {intent}")
    else:
        print("No missing intents")
    
    missing_axes = set(axes) - set(current_axes)
    if missing_axes:
        print(f"Missing axes ({len(missing_axes)}):")
        for axis in sorted(missing_axes):
            print(f"  - {axis}")
    else:
        print("No missing axes")
    
    missing_verb_groups = set(verb_groups) - set(current_verb_groups)
    if missing_verb_groups:
        print(f"Missing verb_groups ({len(missing_verb_groups)}):")
        for verb_group in sorted(missing_verb_groups):
            print(f"  - {verb_group}")
    else:
        print("No missing verb_groups")
    
    # Generate updated meta sections
    updated_intents = {intent: {"description": f"Intent: {intent}"} for intent in intents}
    updated_axes = {axis: {"description": f"Axis: {axis}"} for axis in axes}
    updated_verb_groups = {verb_group: {"description": f"Verb group: {verb_group}"} for verb_group in verb_groups}
    
    print(f"\n=== UPDATED META SECTIONS ===")
    print("intents:")
    for intent, desc in updated_intents.items():
        print(f"  {intent}: {desc}")
    
    print("\naxes:")
    for axis, desc in updated_axes.items():
        print(f"  {axis}: {desc}")
    
    print("\nverb_groups:")
    for verb_group, desc in updated_verb_groups.items():
        print(f"  {verb_group}: {desc}")

if __name__ == "__main__":
    main()
