#!/usr/bin/env python3
"""
Simple validation of apps/ folder structure against L5 agentic architecture.
Bypasses YAML parsing issues by using hardcoded expected structure.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

# Expected structure based on YAML lines 434-714
EXPECTED_LAYERS = [
    'budget-manager-layer',
    'executor-microagent-layer', 
    'observer-microagent-layer',
    'planner-microagent-layer',
    'retriever-microagent-layer',
    'router-microagent-layer',
    'safety-guard-layer',
    'shared'
]

# Phase groups expected for each layer (varies by layer)
EXPECTED_PHASE_GROUPS = {
    'budget-manager-layer': ['act-phase-group', 'aggregate-phase-group', 'expand-phase-group', 'inspect-phase-group', 'rank-phase-group', 'retry-phase-group'],
    'executor-microagent-layer': ['act-phase-group', 'aggregate-phase-group', 'expand-phase-group', 'inspect-phase-group', 'rank-phase-group', 'refine-phase-group', 'retry-phase-group', 'validate-phase-group'],
    'observer-microagent-layer': ['act-phase-group', 'expand-phase-group', 'inspect-phase-group', 'rank-phase-group', 'refine-phase-group', 'retry-phase-group', 'validate-phase-group'],
    'planner-microagent-layer': ['act-phase-group', 'aggregate-phase-group', 'expand-phase-group', 'inspect-phase-group', 'rank-phase-group', 'refine-phase-group', 'retry-phase-group', 'validate-phase-group'],
    'retriever-microagent-layer': ['act-phase-group', 'aggregate-phase-group', 'expand-phase-group', 'inspect-phase-group', 'refine-phase-group', 'retry-phase-group', 'validate-phase-group'],
    'router-microagent-layer': ['act-phase-group', 'aggregate-phase-group', 'expand-phase-group', 'inspect-phase-group', 'rank-phase-group', 'refine-phase-group', 'retry-phase-group', 'validate-phase-group'],
    'safety-guard-layer': ['aggregate-phase-group', 'expand-phase-group', 'inspect-phase-group', 'rank-phase-group', 'refine-phase-group', 'retry-phase-group', 'validate-phase-group'],
    'shared': ['LEVEL_1']
}

# Standard ops hierarchy for most layers
STANDARD_OPS_HIERARCHY = [
    'general-operations-ops',
    'utility-functions-ops', 
    'helper-methods-ops'
]

# Valid LEVEL suffixes
VALID_LEVEL_SUFFIXES = ['_LEVEL_3', '_LEVEL_4', '_LEVEL_5']

def get_actual_apps_structure(apps_path: str) -> Dict:
    """Get the actual apps/ directory structure."""
    root = Path(apps_path)
    structure: Dict[str, Dict] = {}
    
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
            
            # Walk the full hierarchy for non-shared layers
            if layer_name != 'shared':
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
                                structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name] = []
                                
                                # List files
                                for file_path in helper_dir.iterdir():
                                    if file_path.is_file():
                                        structure[layer_name][phase_name][ops_name][general_name][utility_name][helper_name].append(file_path.name)
            else:
                # Handle shared/LEVEL_1/ special structure
                for level_dir in phase_dir.iterdir():
                    if not level_dir.is_dir():
                        continue
                        
                    level_name = level_dir.name
                    structure[layer_name][phase_name][level_name] = {}
                    
                    # Continue walking the hierarchy for shared structure
                    for sublayer_dir in level_dir.iterdir():
                        if not sublayer_dir.is_dir():
                            continue
                            
                        sublayer_name = sublayer_dir.name
                        structure[layer_name][phase_name][level_name][sublayer_name] = {}
                        
                        for subphase_dir in sublayer_dir.iterdir():
                            if not subphase_dir.is_dir():
                                continue
                                
                            subphase_name = subphase_dir.name
                            structure[layer_name][phase_name][level_name][sublayer_name][subphase_name] = {}
                            
                            for subops_dir in subphase_dir.iterdir():
                                if not subops_dir.is_dir():
                                    continue
                                    
                                subops_name = subops_dir.name
                                structure[layer_name][phase_name][level_name][sublayer_name][subphase_name][subops_name] = {}
                                
                                for general_dir in subops_dir.iterdir():
                                    if not general_dir.is_dir():
                                        continue
                                        
                                    general_name = general_dir.name
                                    structure[layer_name][phase_name][level_name][sublayer_name][subphase_name][subops_name][general_name] = []
                                    
                                    # List files at this level
                                    for file_path in general_dir.iterdir():
                                        if file_path.is_file():
                                            structure[layer_name][phase_name][level_name][sublayer_name][subphase_name][subops_name][general_name].append(file_path.name)
    
    return structure

def validate_layer_structure(layer_name: str, actual_structure: Dict) -> Tuple[List[str], List[str], List[str]]:
    """Validate a single layer's structure."""
    missing = []
    extra = []
    valid = []
    
    expected_phases = EXPECTED_PHASE_GROUPS.get(layer_name, [])
    actual_phases = list(actual_structure.keys())
    
    # Check missing phases
    for phase in expected_phases:
        if phase not in actual_phases:
            missing.append(f"{layer_name}/{phase}")
        else:
            valid.append(f"{layer_name}/{phase}")
    
    # Check extra phases
    for phase in actual_phases:
        if phase not in expected_phases:
            extra.append(f"{layer_name}/{phase}")
    
    return missing, extra, valid

def validate_file_level_suffixes(all_files: List[str]) -> Tuple[List[str], List[str]]:
    """Validate LEVEL suffixes on files."""
    valid_files = []
    invalid_files = []
    
    for file_path in all_files:
        file_name = os.path.basename(file_path)
        
        # Skip non-code files that shouldn't have LEVEL suffixes
        if file_name.endswith('.json') or file_name.endswith('.yaml'):
            valid_files.append(file_path)
            continue
            
        # Check for valid LEVEL suffix
        has_valid_suffix = any(file_name.endswith(suffix) for suffix in VALID_LEVEL_SUFFIXES)
        
        if has_valid_suffix:
            valid_files.append(file_path)
        else:
            invalid_files.append(file_path)
    
    return valid_files, invalid_files

def collect_all_files(structure: Dict, path: str = "") -> List[str]:
    """Recursively collect all file paths."""
    files = []
    
    if isinstance(structure, dict):
        for key, value in structure.items():
            new_path = f"{path}/{key}" if path else key
            files.extend(collect_all_files(value, new_path))
    elif isinstance(structure, list):
        for item in structure:
            files.append(f"{path}/{item}")
    
    return files

def main():
    """Main validation function."""
    apps_path = "apps"
    
    print("🔍 SIMPLE APPS/ FOLDER STRUCTURE VALIDATION")
    print("=" * 60)
    
    # Get actual structure
    print("📁 Analyzing apps/ structure...")
    actual_structure = get_actual_apps_structure(apps_path)
    
    # Validate layers
    print("🏗️  Validating layer structure...")
    all_missing = []
    all_extra = []
    all_valid = []
    
    actual_layers = list(actual_structure.keys())
    
    # Check missing layers
    for layer in EXPECTED_LAYERS:
        if layer not in actual_layers:
            all_missing.append(f"apps/{layer}")
        else:
            missing, extra, valid = validate_layer_structure(layer, actual_structure[layer])
            all_missing.extend(missing)
            all_extra.extend(extra)
            all_valid.extend(valid)
    
    # Check extra layers
    for layer in actual_layers:
        if layer not in EXPECTED_LAYERS:
            all_extra.append(f"apps/{layer}")
    
    # Collect all files for LEVEL suffix validation
    print("🏷️  Validating LEVEL suffixes...")
    all_files = collect_all_files(actual_structure)
    valid_files, invalid_files = validate_file_level_suffixes(all_files)
    
    # Print results
    print("\n📊 VALIDATION RESULTS:")
    print(f"✅ Valid structure items: {len(all_valid)}")
    print(f"❌ Missing structure items: {len(all_missing)}")
    print(f"⚠️  Extra structure items: {len(all_extra)}")
    print(f"✅ Valid LEVEL suffixes: {len(valid_files)}")
    print(f"❌ Invalid LEVEL suffixes: {len(invalid_files)}")
    
    # Detailed missing items
    if all_missing:
        print(f"\n❌ MISSING ITEMS ({len(all_missing)}):")
        for item in sorted(all_missing)[:10]:
            print(f"   - {item}")
        if len(all_missing) > 10:
            print(f"   ... and {len(all_missing) - 10} more")
    
    # Detailed extra items
    if all_extra:
        print(f"\n⚠️  EXTRA ITEMS ({len(all_extra)}):")
        for item in sorted(all_extra)[:10]:
            print(f"   - {item}")
        if len(all_extra) > 10:
            print(f"   ... and {len(all_extra) - 10} more")
    
    # Invalid LEVEL suffixes
    if invalid_files:
        print(f"\n❌ INVALID LEVEL SUFFIXES ({len(invalid_files)}):")
        for file_path in sorted(invalid_files)[:10]:
            print(f"   - {file_path}")
        if len(invalid_files) > 10:
            print(f"   ... and {len(invalid_files) - 10} more")
    
    # Calculate compliance
    total_expected = len(all_valid) + len(all_missing)
    structure_compliance = (len(all_valid) / total_expected * 100) if total_expected > 0 else 0
    
    total_files = len(valid_files) + len(invalid_files)
    suffix_compliance = (len(valid_files) / total_files * 100) if total_files > 0 else 0
    
    overall_compliance = (structure_compliance + suffix_compliance) / 2
    
    print("\n📈 COMPLIANCE BREAKDOWN:")
    print(f"   Structure compliance: {structure_compliance:.1f}%")
    print(f"   LEVEL suffix compliance: {suffix_compliance:.1f}%")
    print(f"   Overall compliance: {overall_compliance:.1f}%")
    
    # Final assessment
    if overall_compliance >= 95:
        print("\n🎉 EXCELLENT: apps/ folder strongly follows L5 YAML specification")
        return True
    elif overall_compliance >= 85:
        print("\n✅ GOOD: apps/ folder mostly follows L5 YAML specification")
        return True
    elif overall_compliance >= 70:
        print("\n⚠️  FAIR: apps/ folder partially follows L5 YAML specification")
        return False
    else:
        print("\n❌ POOR: apps/ folder does not follow L5 YAML specification")
        return False

if __name__ == "__main__":
    is_compliant = main()
    exit(0 if is_compliant else 1)
