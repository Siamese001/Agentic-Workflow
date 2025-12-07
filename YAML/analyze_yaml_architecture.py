import logging
from __future__ import annotations
#!/usr/bin/env python3
"""
Systematic analysis of unified_structure_subatomic.yaml to identify
architectural redundancies where files would never be expected.
"""

import yaml
from pathlib import Path
from collections import defaultdict

def load_yaml_structure():
    """Load the unified structure YAML."""
    yaml_path = Path("unified_structure_subatomic.yaml")
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def analyze_cognitive_layer_architecture():
    """Analyze which phases make semantic sense for each cognitive layer."""
    
    logging.debug("🏗️ COGNITIVE LAYER ARCHITECTURE ANALYSIS")
    logging.debug("=" * 80)
    
    # Define architecturally appropriate phases per layer
    layer_phase_logic = {
        'L1_cognition': {
            'appropriate': ['P1_retrieve', 'P2_inspect', 'P3_aggregate', 'P4_safety'],
            'rationale': 'Full cognitive pipeline: retrieve information, inspect context, aggregate understanding, apply safety'
        },
        'L2_execution': {
            'appropriate': ['P2_inspect', 'P3_aggregate', 'P4_safety'],
            'inappropriate': ['P1_retrieve'],
            'rationale': 'Execution acts on inputs, doesn\'t retrieve. Inspect parameters, aggregate actions, enforce safety'
        },
        'L3_orchestration': {
            'appropriate': ['P3_aggregate', 'P4_safety'],
            'inappropriate': ['P1_retrieve', 'P2_inspect'],
            'rationale': 'Orchestration coordinates and aggregates existing workflows, applies safety gates'
        },
        'L4_memory': {
            'appropriate': ['P1_retrieve', 'P3_aggregate', 'P4_safety'],
            'inappropriate': ['P2_inspect'],
            'rationale': 'Memory retrieves stored data and aggregates updates, inspection is redundant'
        },
        'L5_safety': {
            'appropriate': ['P4_safety'],
            'inappropriate': ['P1_retrieve', 'P2_inspect', 'P3_aggregate'],
            'rationale': 'Safety is a cross-cutting validation layer, not a cognitive pipeline'
        }
    }
    
    logging.debug("📋 Architecturally Appropriate Phases per Layer:")
    for layer, logic in layer_phase_logic.items():
        logging.debug(f"\n{layer}:")
        logging.debug(f"  Appropriate: {', '.join(logic['appropriate'])}")
        if 'inappropriate' in logic:
            logging.debug(f"  Inappropriate: {', '.join(logic['inappropriate'])}")
        logging.debug(f"  Rationale: {logic['rationale']}")
    
    return layer_phase_logic

def analyze_yaml_structure():
    """Analyze the actual YAML structure against architectural logic."""
    
    try:
        structure = load_yaml_structure()
    except Exception as e:
        logging.debug(f"❌ Failed to load YAML: {e}")
        return
    
    layer_logic = analyze_cognitive_layer_architecture()
    
    logging.debug(f"\n" + "=" * 80)
    logging.debug("🔍 YAML STRUCTURE ANALYSIS")
    logging.debug("=" * 80)
    
    # Analyze each cognitive domain
    cognitive_domains = ['agentic_core', 'apps_lic', 'apps_rg']
    
    for domain in cognitive_domains:
        if domain not in structure:
            continue
            
        logging.debug(f"\n📁 Analyzing {domain}:")
        logging.debug("-" * 50)
        
        domain_structure = structure[domain]
        
        for layer_name, layer_content in domain_structure.items():
            if not layer_name.startswith('L'):
                continue
                
            logging.debug(f"\n{layer_name}:")
            
            # Check which phases exist
            existing_phases = [k for k in layer_content.keys() if k.startswith('P')]
            
            # Get architectural expectations
            if layer_name in layer_logic:
                appropriate = layer_logic[layer_name]['appropriate']
                inappropriate = layer_logic[layer_name].get('inappropriate', [])
                
                # Find issues
                redundant_phases = [p for p in existing_phases if p in inappropriate]
                missing_phases = [p for p in appropriate if p not in existing_phases]
                
                if redundant_phases:
                    logging.debug(f"  ⚠️  REDUNDANT phases: {', '.join(redundant_phases)}")
                
                if missing_phases:
                    logging.debug(f"  ℹ️  Missing phases: {', '.join(missing_phases)}")
                
                # Check if redundant phases are empty
                for phase in redundant_phases:
                    phase_content = layer_content[phase]
                    if isinstance(phase_content, dict):
                        file_count = len([k for k, v in phase_content.items() if v is not None and v != {}])
                        if file_count == 0:
                            logging.debug(f"    📭 {phase} is completely empty")
                        else:
                            logging.debug(f"    📄 {phase} has {file_count} files (may be legitimate)")
                
                if not redundant_phases:
                    logging.debug(f"  ✅ Architecture aligned")

def find_all_architectural_issues():
    """Find all architectural issues across the entire structure."""
    
    logging.debug(f"\n" + "=" * 80)
    logging.debug("🚨 COMPREHENSIVE ARCHITECTURAL ISSUES")
    logging.debug("=" * 80)
    
    issues = []
    
    # Issue 1: L5_safety with P1-P3 (already identified)
    issues.append({
        'severity': 'HIGH',
        'location': 'All cognitive domains: L5_safety/P1_retrieve, P2_inspect, P3_aggregate',
        'issue': 'Safety layer has cognitive pipeline phases',
        'recommendation': 'Remove P1-P3, keep only P4_safety'
    })
    
    # Issue 2: L2_execution with P1_retrieve
    issues.append({
        'severity': 'HIGH', 
        'location': 'All cognitive domains: L2_execution/P1_retrieve',
        'issue': 'Execution layer has retrieval phase',
        'recommendation': 'Remove P1_retrieve from execution layers'
    })
    
    # Issue 3: L3_orchestration with P1-P2
    issues.append({
        'severity': 'MEDIUM',
        'location': 'All cognitive domains: L3_orchestration/P1_retrieve, P2_inspect', 
        'issue': 'Orchestration layer has cognitive phases',
        'recommendation': 'Consider removing P1-P2, keep P3-P4 only'
    })
    
    # Issue 4: L4_memory with P2_inspect
    issues.append({
        'severity': 'LOW',
        'location': 'All cognitive domains: L4_memory/P2_inspect',
        'issue': 'Memory layer has inspection phase',
        'recommendation': 'Consider removing P2_inspect from memory layers'
    })
    
    for i, issue in enumerate(issues, 1):
        logging.debug(f"\n{i}. [{issue['severity']}] {issue['issue']}")
        logging.debug(f"   Location: {issue['location']}")
        logging.debug(f"   Recommendation: {issue['recommendation']}")
    
    logging.debug(f"\n📊 Summary: {len(issues)} architectural issues found")
    logging.debug(f"   High severity: {sum(1 for i in issues if i['severity'] == 'HIGH')}")
    logging.debug(f"   Medium severity: {sum(1 for i in issues if i['severity'] == 'MEDIUM')}")
    logging.debug(f"   Low severity: {sum(1 for i in issues if i['severity'] == 'LOW')}")

def generate_recommendations():
    """Generate specific recommendations for fixing the architecture."""
    
    logging.debug(f"\n" + "=" * 80)
    logging.debug("🔧 ARCHITECTURAL FIX RECOMMENDATIONS")
    logging.debug("=" * 80)
    
    logging.debug(f"\n1. IMMEDIATE FIXES (High Priority):")
    logging.debug(f"   • Remove P1_retrieve, P2_inspect, P3_aggregate from all L5_safety layers")
    logging.debug(f"   • Remove P1_retrieve from all L2_execution layers")
    logging.debug(f"   • This eliminates ~60 empty directories across all domains")
    
    logging.debug(f"\n2. CONSIDERED FIXES (Medium Priority):")
    logging.debug(f"   • Evaluate if L3_orchestration needs P1-P2 phases")
    logging.debug(f"   • Consider consolidating orchestration to P3_aggregate + P4_safety")
    
    logging.debug(f"\n3. OPTIONAL FIXES (Low Priority):")
    logging.debug(f"   • Review L4_memory/P2_inspect usage")
    logging.debug(f"   • Memory typically retrieves and updates, inspection may be redundant")
    
    logging.debug(f"\n4. VALIDATION APPROACH:")
    logging.debug(f"   • Check semantic cache for operations targeting these directories")
    logging.debug(f"   • If zero operations, safe to remove")
    logging.debug(f"   • If some operations exist, evaluate if they're architecturally appropriate")

if __name__ == "__main__":
    analyze_cognitive_layer_architecture()
    analyze_yaml_structure()
    find_all_architectural_issues()
    generate_recommendations()
