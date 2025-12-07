"""
02_schemas/YAML/analyze_all_yaml_redundancies.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 88defb0d37d1604173461cf1175a3e92e550e24b3fce8b62d7e2a9cd5ae0432d
"""
#!/usr/bin/env python3
"""
02_schemas/YAML/analyze_all_yaml_redundancies.py
Comprehensive analysis of all 10 folders in unified_structure_subatomic.yaml.

Identifies architectural redundancies where files would never be expected
based on folder type and cognitive layer semantics.

Auto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)

def load_yaml_structure():
    """Load the unified structure YAML."""
    yaml_path = Path("unified_structure_subatomic.yaml")
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def analyze_all_folders():
    """Analyze all 10 folders for architectural redundancies."""
    
    logging.debug("🏗️ COMPREHENSIVE ANALYSIS OF ALL 10 FOLDERS")
    logging.debug("=" * 80)
    
    structure = load_yaml_structure()
    
    # Define the 10 canonical folders
    all_folders = [
        '01_agentic_core',
        '02_schemas', 
        '03_runtime',
        '04_prompt_governance',
        '05_config',
        '06_data',
        '07_observability', 
        '08_scripts',
        '09_apps',
        '10_tests'
    ]
    
    # Map YAML keys to folder names
    yaml_to_folder = {
        'agentic_core': '01_agentic_core',
        'schemas': '02_schemas',
        'runtime': '03_runtime', 
        'prompt_governance': '04_prompt_governance',
        'config': '05_config',
        'data': '06_data',
        'observability': '07_observability',
        'scripts': '08_scripts',
        'shared_engine_ops': '09_apps (shared ops)',
        'apps_lic': '09_apps (LIC)',
        'apps_rg': '09_apps (RG)',
        'tests': '10_tests'
    }
    
    # Define architectural rules for each folder type
    folder_rules = {
        'cognitive_engine': {
            'allowed_layers': ['L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_memory', 'L5_safety'],
            'allowed_phases': ['P1_retrieve', 'P2_inspect', 'P3_aggregate', 'P4_safety'],
            'forbidden_patterns': []
        },
        'operational_support': {
            'allowed_layers': [],
            'allowed_phases': [],
            'forbidden_patterns': ['L1_', 'L2_', 'L3_', 'L4_', 'L5_', 'P1_', 'P2_', 'P3_', 'P4_'],
            'rationale': 'Operational folders should not have cognitive layer/phase structures'
        },
        'library_support': {
            'allowed_layers': [],
            'allowed_phases': [],
            'forbidden_patterns': ['L1_', 'L2_', 'L3_', 'L4_', 'L5_', 'P1_', 'P2_', 'P3_', 'P4_'],
            'rationale': 'Library folders should not have cognitive layer/phase structures'
        },
        'test_taxonomy': {
            'allowed_layers': [],
            'allowed_phases': [],
            'forbidden_patterns': [],
            'rationale': 'Test folders have their own taxonomy structure'
        }
    }
    
    # Get domain modes from YAML
    domain_modes = structure.get('domain_modes', {})
    
    logging.debug("📋 Folder Classification & Rules:")
    for yaml_key, folder_name in yaml_to_folder.items():
        if yaml_key in domain_modes:
            mode = domain_modes[yaml_key]
            logging.debug(f"\n{folder_name}:")
            logging.debug(f"  YAML key: {yaml_key}")
            logging.debug(f"  Mode: {mode}")
            if mode in folder_rules:
                rules = folder_rules[mode]
                logging.debug(f"  Allowed layers: {rules['allowed_layers']}")
                logging.debug(f"  Allowed phases: {rules['allowed_phases']}")
                logging.debug(f"  Forbidden patterns: {rules['forbidden_patterns']}")
                if 'rationale' in rules:
                    logging.debug(f"  Rationale: {rules['rationale']}")
    
    return structure, yaml_to_folder, folder_rules, domain_modes

def find_redundancies_across_all_folders():
    """Find redundancies across all 10 folders."""
    
    structure, yaml_to_folder, folder_rules, domain_modes = analyze_all_folders()
    
    logging.debug(f"\n" + "=" * 80)
    logging.debug("🔍 REDUNDANCY ANALYSIS ACROSS ALL FOLDERS")
    logging.debug("=" * 80)
    
    redundancies = []
    
    # Check each folder for rule violations
    for yaml_key, folder_name in yaml_to_folder.items():
        if yaml_key not in structure:
            continue
            
        mode = domain_modes.get(yaml_key, 'unknown')
        folder_content = structure[yaml_key]
        
        logging.debug(f"\n📁 Analyzing {folder_name} ({yaml_key}, mode: {mode}):")
        logging.debug("-" * 60)
        
        if mode in folder_rules:
            rules = folder_rules[mode]
            
            # Check for forbidden patterns
            for pattern in rules['forbidden_patterns']:
                if pattern in ['L1_', 'L2_', 'L3_', 'L4_', 'L5_']:
                    # Check for cognitive layers in non-cognitive folders
                    cognitive_layers = [k for k in folder_content.keys() if k.startswith('L')]
                    if cognitive_layers:
                        redundancies.append({
                            'severity': 'HIGH',
                            'folder': folder_name,
                            'yaml_key': yaml_key,
                            'issue': f'Cognitive layers {cognitive_layers} in {mode} folder',
                            'location': f"{folder_name}/{'/'.join(cognitive_layers)}",
                            'recommendation': f'Remove cognitive layers from {mode} folder'
                        })
                        logging.debug(f"  ❌ FOUND: Cognitive layers {cognitive_layers}")
                
                elif pattern in ['P1_', 'P2_', 'P3_', 'P4_']:
                    # Check for cognitive phases in non-cognitive folders
                    cognitive_phases = []
                    for layer_key, layer_content in folder_content.items():
                        if isinstance(layer_content, dict):
                            phases = [k for k in layer_content.keys() if k.startswith('P')]
                            if phases:
                                cognitive_phases.extend([f"{layer_key}/{phase}" for phase in phases])
                    
                    if cognitive_phases:
                        redundancies.append({
                            'severity': 'HIGH', 
                            'folder': folder_name,
                            'yaml_key': yaml_key,
                            'issue': f'Cognitive phases in {mode} folder',
                            'location': f"{folder_name}/{'/'.join(cognitive_phases[:3])}...",
                            'recommendation': f'Remove cognitive phases from {mode} folder'
                        })
                        logging.debug(f"  ❌ FOUND: Cognitive phases in {len(cognitive_phases)} locations")
            
            # For cognitive engines, check phase appropriateness
            if mode == 'cognitive_engine':
                for layer_key, layer_content in folder_content.items():
                    if layer_key.startswith('L'):
                        phases = [k for k in layer_content.keys() if k.startswith('P')]
                        
                        # Apply cognitive layer logic
                        if layer_key == 'L2_execution' and 'P1_retrieve' in phases:
                            redundancies.append({
                                'severity': 'HIGH',
                                'folder': folder_name,
                                'yaml_key': yaml_key,
                                'issue': f'P1_retrieve in execution layer',
                                'location': f"{folder_name}/{layer_key}/P1_retrieve",
                                'recommendation': 'Remove P1_retrieve from execution layers'
                            })
                            logging.debug(f"  ❌ FOUND: P1_retrieve in {layer_key}")
                        
                        elif layer_key == 'L3_orchestration':
                            redundant_phases = [p for p in ['P1_retrieve', 'P2_inspect'] if p in phases]
                            if redundant_phases:
                                redundancies.append({
                                    'severity': 'MEDIUM',
                                    'folder': folder_name,
                                    'yaml_key': yaml_key,
                                    'issue': f'{redundant_phases} in orchestration layer',
                                    'location': f"{folder_name}/{layer_key}/{'/'.join(redundant_phases)}",
                                    'recommendation': 'Consider removing P1-P2 from orchestration'
                                })
                                logging.debug(f"  ⚠️  FOUND: {redundant_phases} in {layer_key}")
                        
                        elif layer_key == 'L4_memory' and 'P2_inspect' in phases:
                            redundancies.append({
                                'severity': 'LOW',
                                'folder': folder_name,
                                'yaml_key': yaml_key,
                                'issue': 'P2_inspect in memory layer',
                                'location': f"{folder_name}/{layer_key}/P2_inspect",
                                'recommendation': 'Consider removing P2_inspect from memory layers'
                            })
                            logging.debug(f"  ℹ️  FOUND: P2_inspect in {layer_key}")
                        
                        elif layer_key == 'L5_safety':
                            redundant_phases = [p for p in ['P1_retrieve', 'P2_inspect', 'P3_aggregate'] if p in phases]
                            if redundant_phases:
                                redundancies.append({
                                    'severity': 'HIGH',
                                    'folder': folder_name,
                                    'yaml_key': yaml_key,
                                    'issue': f'{redundant_phases} in safety layer',
                                    'location': f"{folder_name}/{layer_key}/{'/'.join(redundant_phases)}",
                                    'recommendation': 'Remove P1-P3 from safety layers'
                                })
                                logging.debug(f"  ❌ FOUND: {redundant_phases} in {layer_key}")
            
            if not any(r['folder'] == folder_name for r in redundancies[-10:]):  # Check last 10 for this folder
                logging.debug(f"  ✅ No architectural violations found")
    
    return redundancies

def summarize_all_redundancies(redundancies):
    """Summarize all redundancies found across the 10 folders."""
    
    logging.debug(f"\n" + "=" * 80)
    logging.debug("🚨 COMPREHENSIVE REDUNDANCY SUMMARY")
    logging.debug("=" * 80)
    
    # Group by severity
    by_severity = defaultdict(list)
    by_folder = defaultdict(list)
    
    for redundancy in redundancies:
        by_severity[redundancy['severity']].append(redundancy)
        by_folder[redundancy['folder']].append(redundancy)
    
    logging.debug(f"\n📊 Overall Statistics:")
    logging.debug(f"  Total redundancies: {len(redundancies)}")
    logging.debug(f"  High severity: {len(by_severity['HIGH'])}")
    logging.debug(f"  Medium severity: {len(by_severity['MEDIUM'])}")
    logging.debug(f"  Low severity: {len(by_severity['LOW'])}")
    
    logging.debug(f"\n📁 Redundancies by Folder:")
    for folder_name, folder_issues in sorted(by_folder.items()):
        logging.debug(f"\n{folder_name}:")
        for issue in folder_issues:
            logging.debug(f"  [{issue['severity']}] {issue['issue']}")
            logging.debug(f"    Location: {issue['location']}")
            logging.debug(f"    Recommendation: {issue['recommendation']}")
    
    logging.debug(f"\n🎯 Priority Fix Order:")
    logging.debug(f"1. HIGH SEVERITY ({len(by_severity['HIGH'])} issues):")
    for issue in by_severity['HIGH']:
        logging.debug(f"   • {issue['folder']}: {issue['issue']}")
    
    logging.debug(f"\n2. MEDIUM SEVERITY ({len(by_severity['MEDIUM'])} issues):")
    for issue in by_severity['MEDIUM']:
        logging.debug(f"   • {issue['folder']}: {issue['issue']}")
    
    logging.debug(f"\n3. LOW SEVERITY ({len(by_severity['LOW'])} issues):")
    for issue in by_severity['LOW']:
        logging.debug(f"   • {issue['folder']}: {issue['issue']}")
    
    return redundancies

if __name__ == "__main__":
    redundancies = find_redundancies_across_all_folders()
    summarize_all_redundancies(redundancies)
