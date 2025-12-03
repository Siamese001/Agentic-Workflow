#!/usr/bin/env python3
"""
Analyze single-child directory chains to identify trivial wrappers vs semantically meaningful nodes
"""

import yaml
from pathlib import Path
from collections import defaultdict

def analyze_single_child_chains(tree, domains, layers, phases, intents, axes, verb_groups):
    """Analyze single-child directory chains and categorize them"""
    
    semantic_levels = set(layers) | set(phases) | set(intents) | set(axes) | set(verb_groups)
    
    single_child_chains = []
    trivial_candidates = []
    semantic_single_children = []
    
    def traverse_tree(node, path, level=0):
        if not isinstance(node, dict):
            return
        
        # Skip __init__.py files
        if '__init__.py' in node:
            node_copy = {k: v for k, v in node.items() if k != '__init__.py'}
            if len(node_copy) == 1:
                node = node_copy
            elif len(node_copy) == 0:
                return
        
        # Check if this node has exactly one child directory
        child_dirs = [k for k, v in node.items() if isinstance(v, dict) and k != '__init__.py']
        
        if len(child_dirs) == 1:
            single_child = child_dirs[0]
            full_path = path + [single_child]
            
            chain_info = {
                'path': full_path,
                'parent_path': path,
                'single_child': single_child,
                'is_semantic': single_child in semantic_levels,
                'level': level,
                'has_files': any(not isinstance(v, dict) for v in node[single_child].values()),
                'grandchildren': list(node[single_child].keys()) if isinstance(node[single_child], dict) else []
            }
            
            single_child_chains.append(chain_info)
            
            if chain_info['is_semantic']:
                semantic_single_children.append(chain_info)
            else:
                # Check if this is truly trivial - just passes through to files or semantic nodes
                grandchildren = [k for k, v in node[single_child].items() if isinstance(v, dict) and k != '__init__.py']
                if len(grandchildren) <= 1:  # Either has files or one more directory
                    trivial_candidates.append(chain_info)
            
            # Continue traversing
            traverse_tree(node[single_child], full_path, level + 1)
        else:
            # Continue traversing all children
            for child_name, child_content in node.items():
                if isinstance(child_content, dict) and child_name != '__init__.py':
                    traverse_tree(child_content, path + [child_name], level + 1)
    
    # Start traversal from each domain
    for domain_name, domain_content in tree.items():
        if domain_name in domains:
            traverse_tree(domain_content, [domain_name])
    
    return single_child_chains, trivial_candidates, semantic_single_children

def generate_flattening_plan(trivial_candidates):
    """Generate a plan for flattening trivial single-child chains"""
    
    flattening_plan = []
    
    for chain in trivial_candidates:
        path = chain['path']
        if len(path) >= 2:  # Need at least parent -> child -> grandchild
            parent_path = path[:-1]
            single_child = path[-1]
            
            flattening_plan.append({
                'remove_path': path,
                'move_to': parent_path,
                'reason': f"Trivial wrapper '{single_child}' that doesn't add semantic value"
            })
    
    return flattening_plan

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
    
    print(f"Analyzing single-child chains...")
    print(f"Semantic levels: {len(layers)} layers + {len(phases)} phases + {len(intents)} intents + {len(axes)} axes + {len(verb_groups)} verb_groups = {len(set(layers) | set(phases) | set(intents) | set(axes) | set(verb_groups))}")
    
    # Extract tree structure
    tree = {k: v for k, v in tree_data.items() if k != 'meta'}
    
    # Analyze single-child chains
    single_child_chains, trivial_candidates, semantic_single_children = analyze_single_child_chains(
        tree, domains, layers, phases, intents, axes, verb_groups
    )
    
    print(f"\n=== SINGLE-CHILD CHAIN ANALYSIS ===")
    print(f"Total single-child directory nodes: {len(single_child_chains)}")
    print(f"Semantic single-children (intent/axis/verb_group): {len(semantic_single_children)}")
    print(f"Trivial wrapper candidates: {len(trivial_candidates)}")
    print(f"Potential reduction: {len(trivial_candidates)} nodes")
    
    print(f"\n=== SEMANTIC SINGLE-CHILDREN (TO KEEP) ===")
    for chain in semantic_single_children[:10]:  # Show first 10
        print(f"  {'/'.join(chain['path'])} - semantic level: {chain['single_child']}")
    if len(semantic_single_children) > 10:
        print(f"  ... and {len(semantic_single_children) - 10} more")
    
    print(f"\n=== TRIVIAL WRAPPER CANDIDATES (TO FLATTEN) ===")
    for chain in trivial_candidates[:15]:  # Show first 15
        print(f"  {'/'.join(chain['path'])} - grandchildren: {chain['grandchildren']}")
    if len(trivial_candidates) > 15:
        print(f"  ... and {len(trivial_candidates) - 15} more")
    
    # Generate flattening plan
    flattening_plan = generate_flattening_plan(trivial_candidates)
    
    print(f"\n=== FLATTENING PLAN ===")
    print(f"Would flatten {len(flattening_plan)} trivial single-child chains")
    
    # Group by depth to show impact
    depth_counts = defaultdict(int)
    for chain in trivial_candidates:
        depth_counts[chain['level']] += 1
    
    print(f"\nTrivial chains by depth:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} chains")
    
    # Save detailed analysis
    with open('single_child_analysis.txt', 'w') as f:
        f.write("=== SINGLE-CHILD CHAIN ANALYSIS ===\n\n")
        f.write(f"Total single-child directory nodes: {len(single_child_chains)}\n")
        f.write(f"Semantic single-children: {len(semantic_single_children)}\n")
        f.write(f"Trivial wrapper candidates: {len(trivial_candidates)}\n\n")
        
        f.write("=== SEMANTIC SINGLE-CHILDREN (TO KEEP) ===\n")
        for chain in semantic_single_children:
            f.write(f"  {'/'.join(chain['path'])} - semantic level: {chain['single_child']}\n")
        
        f.write("\n=== TRIVIAL WRAPPER CANDIDATES (TO FLATTEN) ===\n")
        for chain in trivial_candidates:
            f.write(f"  {'/'.join(chain['path'])} - grandchildren: {chain['grandchildren']}\n")
        
        f.write("\n=== FLATTENING PLAN ===\n")
        for plan in flattening_plan:
            f.write(f"  Remove {'/'.join(plan['remove_path'])}, move to {'/'.join(plan['move_to'])} - {plan['reason']}\n")
    
    print(f"\nDetailed analysis saved to: single_child_analysis.txt")

if __name__ == "__main__":
    main()
