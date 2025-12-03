#!/usr/bin/env python3
"""
Zero-loss verification script comparing original baseline vs current YAML structure
"""

import yaml
from pathlib import Path
from collections import defaultdict

def extract_all_files_from_yaml(yaml_data):
    """Extract all leaf file paths from YAML structure, excluding __init__.py"""
    
    def traverse_tree(node, path, files_list):
        if not isinstance(node, dict):
            return
        
        for key, value in node.items():
            if key == '__init__.py':
                # Skip __init__.py files as they're structural, not functional
                continue
            elif isinstance(value, dict):
                traverse_tree(value, path + [key], files_list)
            else:
                # This is a functional file leaf
                files_list.append('/'.join(path + [key]))
    
    files = []
    traverse_tree(yaml_data, [], files)
    return files

def load_yaml_tree_only(yaml_path):
    """Load only the tree structure from YAML, excluding meta section"""
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    # Split tree and meta sections
    lines = content.split('\n')
    meta_start = None
    for i, line in enumerate(lines):
        if line.startswith('# unified_structure_subatomic_meta.yaml'):
            meta_start = i + 1
            break
    
    if meta_start is not None:
        # Exclude meta section
        tree_content = '\n'.join(lines[:meta_start-1])
        yaml_data = yaml.safe_load(tree_content)
    else:
        # No meta section found, load entire file
        yaml_data = yaml.safe_load(content)
    
    return yaml_data

def normalize_file_path(file_path):
    """Normalize file path for comparison - handle flattened structures"""
    # Remove common prefixes and normalize separators
    normalized = file_path.replace('\\', '/')
    
    # Handle flattened intent→axis→verb_group patterns
    # e.g., .../policy/check_safety/file.py -> .../policy_check_safety/file.py
    parts = normalized.split('/')
    
    # Look for patterns that could be flattened
    for i in range(len(parts) - 2):
        if (parts[i] in ['policy', 'semantic', 'embedding', 'utility', 'routing', 'refinement'] and
            parts[i+1] in ['check_safety', 'adjust_scores', 'compare_meaning', 'prepare_information', 'retry_task']):
            
            # This could be a flattened pattern
            flattened_name = f"{parts[i]}_{parts[i+1]}"
            if i + 2 < len(parts):
                # Reconstruct with flattened name
                new_parts = parts[:i] + [flattened_name] + parts[i+2:]
                normalized = '/'.join(new_parts)
                break
    
    # Handle manage_*_costs/update_memory -> manage_*_costs_update_memory patterns
    for i in range(len(parts) - 2):
        if (parts[i].startswith('manage_') and parts[i].endswith('_costs') and
            parts[i+1] == 'update_memory'):
            
            # This is a manage_costs_update_memory pattern
            flattened_name = f"{parts[i]}_update_memory"
            if i + 2 < len(parts):
                new_parts = parts[:i] + [flattened_name] + parts[i+2:]
                normalized = '/'.join(new_parts)
                break
    
    return normalized

def compare_structures(original_yaml, current_yaml):
    """Compare original and current YAML structures for zero-loss verification"""
    
    original_files = extract_all_files_from_yaml(original_yaml)
    current_files = extract_all_files_from_yaml(current_yaml)
    
    # Normalize both sets for comparison
    original_normalized = {normalize_file_path(f) for f in original_files}
    current_normalized = {normalize_file_path(f) for f in current_files}
    
    # Find differences
    missing_files = original_normalized - current_normalized
    added_files = current_normalized - original_normalized
    
    # Detailed analysis
    results = {
        'original_file_count': len(original_files),
        'current_file_count': len(current_files),
        'original_unique_normalized': len(original_normalized),
        'current_unique_normalized': len(current_normalized),
        'missing_files': sorted(list(missing_files)),
        'added_files': sorted(list(added_files)),
        'preserved_files': len(original_normalized & current_normalized),
        'zero_loss_status': 'PASS' if len(missing_files) == 0 else 'FAIL',
        'expansion_status': 'EXPANDED' if len(added_files) > 0 else 'IDENTICAL'
    }
    
    # Analyze structural changes
    original_depths = [len(f.split('/')) for f in original_files]
    current_depths = [len(f.split('/')) for f in current_files]
    
    results['depth_analysis'] = {
        'original_max_depth': max(original_depths) if original_depths else 0,
        'current_max_depth': max(current_depths) if current_depths else 0,
        'original_avg_depth': sum(original_depths) / len(original_depths) if original_depths else 0,
        'current_avg_depth': sum(current_depths) / len(current_depths) if current_depths else 0,
        'depth_reduction': max(original_depths) - max(current_depths) if original_depths and current_depths else 0
    }
    
    return results, original_files, current_files

def main():
    """Main zero-loss verification function"""
    
    print("Running zero-loss verification...")
    
    # Load original baseline (tree only)
    original_path = Path('original_baseline.yaml')
    if not original_path.exists():
        print("❌ Original baseline file not found")
        return
    
    original_yaml = load_yaml_tree_only(original_path)
    
    # Load current structure (tree only)
    current_path = Path('unified_structure_subatomic.yaml')
    if not current_path.exists():
        print("❌ Current YAML file not found")
        return
    
    current_yaml = load_yaml_tree_only(current_path)
    
    # Compare structures
    results, original_files, current_files = compare_structures(original_yaml, current_yaml)
    
    # Generate detailed report
    print(f"\n=== ZERO-LOSS VERIFICATION RESULTS ===")
    print(f"Original file count: {results['original_file_count']}")
    print(f"Current file count: {results['current_file_count']}")
    print(f"Preserved files: {results['preserved_files']}")
    print(f"Missing files: {len(results['missing_files'])}")
    print(f"Added files: {len(results['added_files'])}")
    print(f"Zero-loss status: {results['zero_loss_status']}")
    print(f"Expansion status: {results['expansion_status']}")
    
    print(f"\n=== DEPTH ANALYSIS ===")
    print(f"Original max depth: {results['depth_analysis']['original_max_depth']}")
    print(f"Current max depth: {results['depth_analysis']['current_max_depth']}")
    print(f"Depth reduction: {results['depth_analysis']['depth_reduction']}")
    
    if results['missing_files']:
        print(f"\n=== MISSING FILES ===")
        for file in results['missing_files'][:10]:  # Show first 10
            print(f"  - {file}")
        if len(results['missing_files']) > 10:
            print(f"  ... and {len(results['missing_files']) - 10} more")
    
    if results['added_files']:
        print(f"\n=== ADDED FILES ===")
        for file in results['added_files'][:10]:  # Show first 10
            print(f"  + {file}")
        if len(results['added_files']) > 10:
            print(f"  ... and {len(results['added_files']) - 10} more")
    
    # Save detailed report
    report = {
        'timestamp': '2025-12-02T20:30:00.000000',
        'verification_type': 'zero_loss_analysis',
        'results': results,
        'sample_missing_files': results['missing_files'][:20],
        'sample_added_files': results['added_files'][:20]
    }
    
    with open('zero_loss_verification.json', 'w') as f:
        import json
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Detailed verification saved to: zero_loss_verification.json")
    
    # Return status for K5-K6
    if results['zero_loss_status'] == 'PASS':
        print("🎉 ZERO-LOSS VERIFICATION PASSED - All original files preserved")
        return True
    else:
        print("⚠️  ZERO-LOSS VERIFICATION FAILED - Some files missing")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
