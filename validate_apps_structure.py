#!/usr/bin/env python3
"""
Systematic validation of apps/ folder structure against L5 agentic architecture YAML specification.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Tuple

def load_yaml_structure(yaml_path: str) -> Dict:
    """Load the YAML structure and extract apps specification."""
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return data.get('Agentic_Workflow', {}).get('apps', {})

def get_actual_structure(apps_path: str) -> Dict:
    """Walk the actual apps/ directory and build structure."""
    root = Path(apps_path)
    structure = {}
    
    if not root.exists():
        return structure
    
    for layer_dir in root.iterdir():
        if not layer_dir.is_dir():
            continue
            
        layer_name = layer_dir.name
        structure[layer_name] = {}
        
        for phase_dir in layer_dir.iterdir():
            if not phase_dir.is_dir():
                continue
                
            phase_name = phase_dir.name
            structure[layer_name][phase_name] = {}
            
            for ops_dir in phase_dir.iterdir():
                if not ops_dir.is_dir():
                    continue
                    
                ops_name = ops_dir.name
                structure[layer_name][phase_name][ops_name] = {}
                
                for general_dir in ops_dir.iterdir():
                    if not general_dir.is_dir():
                        continue
                        
                    general_name = general_dir.name
                    structure[layer_name][phase_name][ops_name][general_name] = {}
                    
                    for utility_dir in general_dir.iterdir():
                        if not utility_dir.is_dir():
                            continue
                            
                        utility_name = utility_dir.name
                        structure[layer_name][phase_name][ops_name][general_name][utility_name] = {}
                        
                        for helper_dir in utility_dir.iterdir():
                            if not helper_dir.is_dir():
                                continue
                                
                            helper_name = helper_dir.name
                            structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name] = {}
                            
                            # List files in this deepest directory
                            for file_path in helper_dir.iterdir():
                                if file_path.is_file():
                                    structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name][file_path.name] = None
    
    return structure

def extract_yaml_apps_structure(yaml_apps: Dict) -> Dict:
    """Extract the expected apps structure from YAML."""
    structure = {}
    
    for layer_name, layer_content in yaml_apps.items():
        if layer_name == 'shared':
            # Handle shared/LEVEL_1/ structure separately
            structure[layer_name] = extract_shared_structure(layer_content)
            continue
            
        structure[layer_name] = {}
        
        for phase_name, phase_content in layer_content.items():
            structure[layer_name][phase_name] = {}
            
            for ops_name, ops_content in phase_content.items():
                structure[layer_name][phase_name][ops_name] = {}
                
                for general_name, general_content in ops_content.items():
                    structure[layer_name][phase_name][ops_name][general_name] = {}
                    
                    for utility_name, utility_content in general_content.items():
                        structure[layer_name][phase_name][ops_name][general_name][utility_name] = {}
                        
                        for helper_name, helper_content in utility_content.items():
                            structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name] = {}
                            
                            # Files are listed as key: null in YAML
                            for file_name in helper_content.keys():
                                structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name][file_name] = None
    
    return structure

def extract_shared_structure(shared_yaml: Dict) -> Dict:
    """Extract shared/LEVEL_1/ structure."""
    structure = {}
    
    for level_name, level_content in shared_yaml.items():
        structure[level_name] = {}
        
        for layer_name, layer_content in level_content.items():
            structure[level_name][layer_name] = {}
            
            for phase_name, phase_content in layer_content.items():
                structure[level_name][layer_name][phase_name] = {}
                
                for ops_name, ops_content in phase_content.items():
                    structure[level_name][layer_name][phase_name][ops_name] = {}
                    
                    for general_name, general_content in ops_content.items():
                        structure[level_name][layer_name][phase_name][ops_name][general_name] = {}
                        
                        for utility_name, utility_content in general_content.items():
                            structure[level_name][layer_name][phase_name][ops_name][general_name][utility_name] = {}
                            
                            for file_name in utility_content.keys():
                                structure[level_name][layer_name][phase_name][ops_name][general_name][utility_name][file_name] = None
    
    return structure

def compare_structures(expected: Dict, actual: Dict) -> Tuple[List[str], List[str], List[str]]:
    """Compare expected vs actual structures and return missing, extra, and matched items."""
    missing = []
    extra = []
    matched = []
    
    def compare_recursive(exp_path: str, act_path: str, exp_dict: Dict, act_dict: Dict):
        if isinstance(exp_dict, dict) and isinstance(act_dict, dict):
            # Check for missing keys
            for key in exp_dict.keys():
                if key not in act_dict:
                    missing.append(f"{exp_path}/{key}")
                else:
                    compare_recursive(f"{exp_path}/{key}", f"{act_path}/{key}", 
                                    exp_dict[key], act_dict[key])
            
            # Check for extra keys
            for key in act_dict.keys():
                if key not in exp_dict:
                    extra.append(f"{act_path}/{key}")
                else:
                    if exp_dict.get(key) is not None and act_dict.get(key) is not None:
                        compare_recursive(f"{exp_path}/{key}", f"{act_path}/{key}", 
                                        exp_dict[key], act_dict[key])
        else:
            matched.append(exp_path)
    
    compare_recursive("apps", "apps", expected, actual)
    
    return missing, extra, matched

def validate_level_suffixes(files: List[str]) -> Tuple[List[str], List[str]]:
    """Validate LEVEL suffixes on files."""
    valid_suffixes = ['_LEVEL_3', '_LEVEL_4', '_LEVEL_5']
    invalid_files = []
    valid_files = []
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        if any(file_name.endswith(suffix) for suffix in valid_suffixes):
            valid_files.append(file_path)
        elif file_name.endswith('.json') or file_name.endswith('.yaml') or file_name.endswith('.py'):
            invalid_files.append(file_path)
    
    return valid_files, invalid_files

def main():
    """Main validation function."""
    yaml_path = "repo_root_tree.yaml"
    apps_path = "apps"
    
    print("🔍 VALIDATING APPS/ FOLDER STRUCTURE AGAINST L5 YAML SPECIFICATION")
    print("=" * 60)
    
    # Load YAML specification
    print("📋 Loading YAML specification...")
    yaml_apps = load_yaml_structure(yaml_path)
    expected_structure = extract_yaml_apps_structure(yaml_apps)
    
    # Get actual structure
    print("📁 Analyzing actual apps/ structure...")
    actual_structure = get_actual_structure(apps_path)
    
    # Compare structures
    print("🔍 Comparing expected vs actual structure...")
    missing, extra, matched = compare_structures(expected_structure, actual_structure)
    
    # Print results
    print("\n📊 VALIDATION RESULTS:")
    print(f"✅ Matched items: {len(matched)}")
    print(f"❌ Missing items: {len(missing)}")
    print(f"⚠️  Extra items: {len(extra)}")
    
    # Detailed analysis
    if missing:
        print(f"\n❌ MISSING ITEMS ({len(missing)}):")
        for item in sorted(missing)[:20]:  # Show first 20
            print(f"   - {item}")
        if len(missing) > 20:
            print(f"   ... and {len(missing) - 20} more")
    
    if extra:
        print(f"\n⚠️  EXTRA ITEMS ({len(extra)}):")
        for item in sorted(extra)[:20]:  # Show first 20
            print(f"   - {item}")
        if len(extra) > 20:
            print(f"   ... and {len(extra) - 20} more")
    
    # Validate LEVEL suffixes
    all_files = []
    def collect_files(structure, path=""):
        if isinstance(structure, dict):
            for key, value in structure.items():
                collect_files(value, f"{path}/{key}" if path else key)
        else:
            all_files.append(path)
    
    collect_files(actual_structure)
    valid_files, invalid_files = validate_level_suffixes(all_files)
    
    print("\n🏷️  LEVEL SUFFIX VALIDATION:")
    print(f"✅ Valid LEVEL suffixes: {len(valid_files)}")
    print(f"❌ Invalid/missing suffixes: {len(invalid_files)}")
    
    if invalid_files:
        print(f"\n❌ FILES WITH INVALID LEVEL SUFFIXES ({len(invalid_files)}):")
        for file_path in sorted(invalid_files)[:10]:
            print(f"   - {file_path}")
        if len(invalid_files) > 10:
            print(f"   ... and {len(invalid_files) - 10} more")
    
    # Overall compliance score
    total_expected = len(missing) + len(matched)
    compliance_rate = (len(matched) / total_expected * 100) if total_expected > 0 else 0
    
    print(f"\n📈 OVERALL COMPLIANCE: {compliance_rate:.1f}%")
    
    if compliance_rate >= 95:
        print("🎉 EXCELLENT: apps/ folder strongly follows L5 YAML specification")
    elif compliance_rate >= 85:
        print("✅ GOOD: apps/ folder mostly follows L5 YAML specification")
    elif compliance_rate >= 70:
        print("⚠️  FAIR: apps/ folder partially follows L5 YAML specification")
    else:
        print("❌ POOR: apps/ folder does not follow L5 YAML specification")
    
    return compliance_rate >= 85

if __name__ == "__main__":
    is_compliant = main()
    exit(0 if is_compliant else 1)
