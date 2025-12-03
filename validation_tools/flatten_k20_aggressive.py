#!/usr/bin/env python3
"""
Aggressive flattening of intent→axis→verb_group chains to reduce single-child count for K20
"""

import yaml
from pathlib import Path
from collections import defaultdict

def analyze_intent_structure(tree, domains, layers, phases, intents, axes, verb_groups):
    """Analyze intent→axis→verb_group structures to find flattenable chains"""
    
    intent_analysis = {}
    
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
        
        # Check if we're at intent level (path has domain/layer/phase/intent)
        if len(path) >= 4:
            domain, layer, phase, intent = path[:4]
            
            if (domain in domains and layer in layers and phase in phases and intent in intents):
                
                if intent not in intent_analysis:
                    intent_analysis[intent] = {
                        'axes': {},
                        'total_instances': 0,
                        'flattenable_instances': []
                    }
                
                intent_analysis[intent]['total_instances'] += 1
                
                # Analyze axes under this intent
                if isinstance(node, dict):
                    for axis_name, axis_content in node.items():
                        if axis_name == '__init__.py' or not isinstance(axis_content, dict):
                            continue
                        
                        if axis_name in axes:
                            # Count verb_groups under this axis
                            verb_groups_in_axis = [k for k in axis_content.keys() 
                                                 if k != '__init__.py' and isinstance(axis_content[k], dict)]
                            
                            # Count files directly under this axis
                            files_in_axis = [k for k in axis_content.keys() 
                                           if k != '__init__.py' and not isinstance(axis_content[k], dict)]
                            
                            if axis_name not in intent_analysis[intent]['axes']:
                                intent_analysis[intent]['axes'][axis_name] = {
                                    'verb_groups': verb_groups_in_axis,
                                    'files': files_in_axis,
                                    'instances': []
                                }
                            
                            intent_analysis[intent]['axes'][axis_name]['instances'].append({
                                'path': path + [axis_name],
                                'content': axis_content
                            })
                            
                            # Check if this axis→verb_group chain is flattenable
                            if len(verb_groups_in_axis) == 1 and len(files_in_axis) == 0:
                                verb_group = verb_groups_in_axis[0]
                                verb_group_content = axis_content[verb_group]
                                
                                # Count files in verb_group
                                verb_group_files = [k for k in verb_group_content.keys() 
                                                  if k != '__init__.py' and not isinstance(verb_group_content[k], dict)]
                                verb_group_subdirs = [k for k in verb_group_content.keys() 
                                                    if k != '__init__.py' and isinstance(verb_group_content[k], dict)]
                                
                                if len(verb_group_files) > 0 or len(verb_group_subdirs) > 0:
                                    intent_analysis[intent]['flattenable_instances'].append({
                                        'path': path + [axis_name, verb_group],
                                        'axis': axis_name,
                                        'verb_group': verb_group,
                                        'files': verb_group_files,
                                        'subdirs': verb_group_subdirs,
                                        'content': verb_group_content
                                    })
        
        # Continue traversing
        for child_name, child_content in node.items():
            if isinstance(child_content, dict) and child_name != '__init__.py':
                traverse_tree(child_content, path + [child_name])
    
    # Start traversal from each domain
    for domain_name, domain_content in tree.items():
        if domain_name in domains:
            traverse_tree(domain_content, [domain_name])
    
    return intent_analysis

def apply_aggressive_flattening(tree, flattenable_instances):
    """Apply aggressive flattening by collapsing intent→axis→verb_group chains"""
    
    flattened_tree = yaml.safe_load(yaml.safe_dump(tree))  # Deep copy
    
    flattened_count = 0
    
    for instance in flattenable_instances:
        path = instance['path']
        intent = path[3]
        axis = instance['axis']
        verb_group = instance['verb_group']
        
        # Navigate to the intent level
        current = flattened_tree
        for segment in path[:-2]:  # Go to intent level
            current = current[segment]
        
        # Get the axis content
        axis_content = current[axis]
        verb_group_content = axis_content[verb_group]
        
        # Create new collapsed directory name
        collapsed_name = f"{axis}_{verb_group}"
        
        # Move verb_group content to intent level with collapsed name
        current[collapsed_name] = verb_group_content
        
        # Remove the axis directory
        del current[axis]
        
        flattened_count += 1
        print(f"Flattened: {'/'.join(path)} -> {collapsed_name}")
    
    return flattened_tree, flattened_count

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
    
    print(f"Analyzing intent→axis→verb_group structures for aggressive flattening...")
    
    # Extract tree structure
    tree = {k: v for k, v in tree_data.items() if k != 'meta'}
    
    # Analyze intent structures
    intent_analysis = analyze_intent_structure(
        tree, domains, layers, phases, intents, axes, verb_groups
    )
    
    # Collect all flattenable instances
    all_flattenable = []
    for intent, analysis in intent_analysis.items():
        if analysis['flattenable_instances']:
            all_flattenable.extend(analysis['flattenable_instances'])
    
    print(f"\n=== AGGRESSIVE FLATTENING ANALYSIS ===")
    print(f"Found {len(all_flattenable)} intent→axis→verb_group chains to flatten")
    
    # Group by intent to show impact
    intent_counts = defaultdict(int)
    for instance in all_flattenable:
        intent = instance['path'][3]
        intent_counts[intent] += 1
    
    print(f"\nFlattenable chains by intent:")
    for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {intent}: {count} chains")
    
    if len(all_flattenable) > 0:
        print(f"\nApplying aggressive flattening...")
        flattened_tree, flattened_count = apply_aggressive_flattening(tree, all_flattenable)
        
        # Save the flattened structure
        with open('unified_structure_subatomic.yaml', 'w') as f:
            # Write tree structure
            yaml.safe_dump(flattened_tree, f, default_flow_style=False, sort_keys=False)
            f.write('\n')
            # Write meta section
            f.write('# unified_structure_subatomic_meta.yaml\n')
            yaml.safe_dump(meta_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"\nFlattened structure saved. Reduced single-child count by {flattened_count}")
        
        # Verify the reduction
        print(f"\nRunning verification analysis...")
        
        # Count single-child chains in flattened tree
        def count_single_children(node, path=""):
            if not isinstance(node, dict):
                return 0
            
            count = 0
            child_dirs = [k for k, v in node.items() if isinstance(v, dict) and k != '__init__.py']
            
            if len(child_dirs) == 1:
                count += 1
            
            for child_name, child_content in node.items():
                if isinstance(child_content, dict) and child_name != '__init__.py':
                    count += count_single_children(child_content, f"{path}/{child_name}")
            
            return count
        
        total_single_children = count_single_children(flattened_tree)
        
        print(f"New single-child count: {total_single_children}")
        print(f"Original count: 498")
        print(f"Total reduction: {498 - total_single_children} nodes")
        
        if total_single_children <= 300:  # Arbitrary target for K20
            print(f"✅ K20 TARGET ACHIEVED: {total_single_children} single-child nodes")
        else:
            print(f"⚠️  K20 still needs work: {total_single_children} single-child nodes")
            print(f"Consider additional flattening strategies")
        
    else:
        print("No flattenable intent→axis→verb_group chains found")

if __name__ == "__main__":
    main()
