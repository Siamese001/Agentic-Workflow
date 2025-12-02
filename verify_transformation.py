#!/usr/bin/env python3

import yaml
import os

def analyze_yaml_file(filepath, name):
    """Analyze a YAML file for transformation indicators"""
    print(f"\n=== ANALYZING {name.upper()} ===")
    print(f"File: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ File does not exist: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None
    
    # Count key indicators
    def count_patterns(data, patterns):
        counts = {pattern: 0 for pattern in patterns}
        
        def traverse(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    for pattern in patterns:
                        if pattern in key.lower():
                            counts[pattern] += 1
                    traverse(value, f"{path}/{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, f"{path}[{i}]")
        
        traverse(data)
        return counts
    
    # Check for transformation indicators
    legacy_patterns = ["plan-layer", "exec-layer", "orc-layer", "mem-layer", "safe-layer", 
                      "plan-phase", "act-phase", "safety-phase", "general", "-phase", "-layer"]
    canonical_patterns = ["l1_", "l2_", "l3_", "l4_", "l5_", "p1_", "p2_", "p3_", "p4_"]
    
    legacy_counts = count_patterns(data, legacy_patterns)
    canonical_counts = count_patterns(data, canonical_patterns)
    
    # Count total nodes and files
    def count_elements(data):
        total_nodes = 0
        py_files = 0
        init_files = 0
        
        def traverse(obj):
            nonlocal total_nodes, py_files, init_files
            if isinstance(obj, dict):
                total_nodes += len(obj)
                for key, value in obj.items():
                    if key.endswith('.py'):
                        py_files += 1
                        if key == '__init__.py':
                            init_files += 1
                    traverse(value)
            elif isinstance(obj, list):
                total_nodes += len(obj)
                for item in obj:
                    traverse(item)
        
        traverse(data)
        return total_nodes, py_files, init_files
    
    total_nodes, py_files, init_files = count_elements(data)
    
    print(f"✅ File loaded successfully")
    print(f"📊 Total nodes: {total_nodes}")
    print(f"📄 Python files: {py_files}")
    print(f"📄 __init__.py files: {init_files}")
    
    print(f"\n🔍 LEGACY PATTERNS (should be 0):")
    for pattern, count in legacy_counts.items():
        status = "❌" if count > 0 else "✅"
        print(f"  {status} {pattern}: {count}")
    
    print(f"\n🎯 CANONICAL PATTERNS (should be >0):")
    for pattern, count in canonical_counts.items():
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {pattern}: {count}")
    
    # Check root structure
    print(f"\n🏗️  ROOT STRUCTURE:")
    if 'agentic-directory' in data:
        print(f"  ❌ Has 'agentic-directory' wrapper")
        domains = list(data['agentic-directory'].keys())
    else:
        print(f"  ✅ No 'agentic-directory' wrapper")
        domains = list(data.keys())
    
    print(f"  📁 Domains: {domains}")
    
    # Sample a few paths
    print(f"\n🔎 SAMPLE PATHS:")
    def sample_paths(data, current_path="", samples=None, max_samples=5):
        if samples is None:
            samples = []
        
        if len(samples) >= max_samples:
            return samples
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{current_path}/{key}" if current_path else key
                if key.endswith('.py'):
                    samples.append(new_path)
                    if len(samples) >= max_samples:
                        break
                else:
                    samples = sample_paths(value, new_path, samples, max_samples)
                    if len(samples) >= max_samples:
                        break
        
        return samples
    
    sample_paths_list = sample_paths(data)
    for i, path in enumerate(sample_paths_list, 1):
        print(f"  {i}. {path}")
    
    return {
        'total_nodes': total_nodes,
        'py_files': py_files,
        'init_files': init_files,
        'legacy_counts': legacy_counts,
        'canonical_counts': canonical_counts,
        'domains': domains,
        'has_wrapper': 'agentic-directory' in data
    }

def compare_files():
    """Compare original backup with transformed file"""
    print("=" * 80)
    print("YAML TRANSFORMATION VERIFICATION REPORT")
    print("=" * 80)
    
    # Analyze backup (original)
    backup_analysis = analyze_yaml_file('unified_structure_subatomic_backup.yaml', 'BACKUP (Original)')
    
    # Analyze current file
    current_analysis = analyze_yaml_file('unified_structure_subatomic.yaml', 'CURRENT (Transformed)')
    
    if backup_analysis and current_analysis:
        print(f"\n" + "=" * 80)
        print("COMPARISON SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 FILE COUNTS:")
        print(f"  Original:  {backup_analysis['py_files']} Python files")
        print(f"  Transformed: {current_analysis['py_files']} Python files")
        print(f"  Difference: {backup_analysis['py_files'] - current_analysis['py_files']} files")
        
        print(f"\n🔄 TRANSFORMATION SUCCESS INDICATORS:")
        
        # Check legacy patterns removed
        legacy_removed = True
        for pattern in ["plan-layer", "exec-layer", "general"]:
            if current_analysis['legacy_counts'][pattern] > 0:
                legacy_removed = False
                break
        print(f"  {'✅' if legacy_removed else '❌'} Legacy patterns removed")
        
        # Check canonical patterns added
        canonical_added = sum(current_analysis['canonical_counts'].values()) > 0
        print(f"  {'✅' if canonical_added else '❌'} Canonical patterns added")
        
        # Check wrapper removed
        wrapper_removed = not current_analysis['has_wrapper']
        print(f"  {'✅' if wrapper_removed else '❌'} agentic-directory wrapper removed")
        
        # Overall success
        overall_success = legacy_removed and canonical_added and wrapper_removed
        print(f"\n🎯 OVERALL TRANSFORMATION: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        
        if not overall_success:
            print(f"\n⚠️  TRANSFORMATION ISSUES IDENTIFIED:")
            if not legacy_removed:
                print(f"  - Legacy patterns still present")
            if not canonical_added:
                print(f"  - Canonical patterns missing")
            if not wrapper_removed:
                print(f"  - agentic-directory wrapper still present")

if __name__ == '__main__':
    compare_files()
