#!/usr/bin/env python3
"""
Identify and flatten verb_groups with only one file to reduce single-child count
"""

import yaml
from pathlib import Path
from collections import defaultdict

def find_flattenable_verb_groups(tree, domains, layers, phases, intents, axes, verb_groups):
    """Find verb_groups that contain only one file (excluding __init__.py)"""
    
    flattenable_candidates = []
    
    def traverse_tree(node, path):
        if not isinstance(node, dict):
            return
        
        # Skip __init__.py files
        if '__init__.py' in node:
            node_copy = {k: v for k, v in node.items() if k != '__init__.py'}
            if len(node_copy) == 1:
                node = node_copy
            elif len(node_copy) == 0:
                return
        
        # Check if we're at verb_group level (path has domain/layer/phase/intent/axis/verb_group)
        if len(path) >= 6:
            domain, layer, phase, intent, axis, verb_group = path[:6]
            
            if (domain in domains and layer in layers and phase in phases and 
                intent in intents and axis in axes and verb_group in verb_groups):
                
                # Count files in this verb_group (excluding __init__.py)
                files = [k for k, v in node.items() if not isinstance(v, dict) and k != '__init__.py']
                subdirs = [k for k, v in node.items() if isinstance(v, dict) and k != '__init__.py']
                
                # If this verb_group has exactly one file and no subdirectories, it's flattenable
                if len(files) == 1 and len(subdirs) == 0:
                    flattenable_candidates.append({
                        'path': path,
                        'verb_group': verb_group,
                        'single_file': files[0],
                        'parent_axis': axis,
                        'full_path': '/'.join(path)
                    })
        
        # Continue traversing
        for child_name, child_content in node.items():
            if isinstance(child_content, dict) and child_name != '__init__.py':
                traverse_tree(child_content, path + [child_name])
    
    # Start traversal from each domain
    for domain_name, domain_content in tree.items():
        if domain_name in domains:
            traverse_tree(domain_content, [domain_name])
    
    return flattenable_candidates

def apply_flattening(tree, flattenable_candidates):
    """Apply flattening by moving single files from verb_group to parent axis level"""
    
    flattened_tree = yaml.safe_load(yaml.safe_dump(tree))  # Deep copy
    
    for candidate in flattenable_candidates:
        path = candidate['path']
        verb_group = candidate['verb_group']
        single_file = candidate['single_file']
        
        # Navigate to the parent axis
        current = flattened_tree
        for segment in path[:-1]:  # Go to parent axis
            current = current[segment]
        
        # Get the file content from verb_group
        verb_group_content = current[verb_group]
        file_content = verb_group_content[single_file]
        
        # Move the file to parent axis with new name
        new_filename = f"{verb_group}_{single_file}"
        current[new_filename] = file_content
        
        # Remove the verb_group directory
        del current[verb_group]
        
        print(f"Flattened: {'/'.join(path)} -> {new_filename}")
    
    return flattened_tree

def main():
    yaml_path = Path('unified_structure_subatomic.yaml')
    
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found")
        return
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    # Split the file - tree structure before line 3080, meta after
    lines = content.split('\n')
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
    intents = meta_data.get('intents', [])
    axes = meta_data.get('axes', [])
    verb_groups = meta_data.get('verb_groups', [])
    
    print(f"Finding flattenable verb_groups...")
    
    # Extract tree structure
    tree = {k: v for k, v in tree_data.items() if k != 'meta'}
    
    # Find flattenable candidates
    flattenable_candidates = find_flattenable_verb_groups(
        tree, domains, layers, phases, intents, axes, verb_groups
    )
    
    print(f"\n=== FLATTENABLE VERB_GROUPS ===")
    print(f"Found {len(flattenable_candidates)} verb_groups with exactly one file")
    
    for candidate in flattenable_candidates[:10]:  # Show first 10
        print(f"  {candidate['full_path']} -> {candidate['single_file']}")
    if len(flattenable_candidates) > 10:
        print(f"  ... and {len(flattenable_candidates) - 10} more")
    
    if len(flattenable_candidates) > 0:
        print(f"\nApplying flattening...")
        flattened_tree = apply_flattening(tree, flattenable_candidates)
        
        # Save the flattened structure
        with open('unified_structure_subatomic.yaml', 'w') as f:
            # Write tree structure
            yaml.safe_dump(flattened_tree, f, default_flow_style=False, sort_keys=False)
            f.write('\n')
            # Write meta section
            f.write('# unified_structure_subatomic_meta.yaml\n')
            yaml.safe_dump(meta_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Flattened structure saved. Reduced single-child count by {len(flattenable_candidates)}")
        
        # Verify the reduction
        print(f"\nRunning verification analysis...")
        from analyze_single_child import analyze_single_child_chains
        
        single_child_chains, trivial_candidates, semantic_single_children = analyze_single_child_chains(
            flattened_tree, domains, layers, phases, intents, axes, verb_groups
        )
        
        print(f"New single-child count: {len(single_child_chains)}")
        print(f"Reduction achieved: {498 - len(single_child_chains)} nodes")
        
    else:
        print("No flattenable verb_groups found")

if __name__ == "__main__":
    main()
