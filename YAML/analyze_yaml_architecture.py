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
    
    print("🏗️ COGNITIVE LAYER ARCHITECTURE ANALYSIS")
    print("=" * 80)
    
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
    
    print("📋 Architecturally Appropriate Phases per Layer:")
    for layer, logic in layer_phase_logic.items():
        print(f"\n{layer}:")
        print(f"  Appropriate: {', '.join(logic['appropriate'])}")
        if 'inappropriate' in logic:
            print(f"  Inappropriate: {', '.join(logic['inappropriate'])}")
        print(f"  Rationale: {logic['rationale']}")
    
    return layer_phase_logic

def analyze_yaml_structure():
    """Analyze the actual YAML structure against architectural logic."""
    
    try:
        structure = load_yaml_structure()
    except Exception as e:
        print(f"❌ Failed to load YAML: {e}")
        return
    
    layer_logic = analyze_cognitive_layer_architecture()
    
    print(f"\n" + "=" * 80)
    print("🔍 YAML STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Analyze each cognitive domain
    cognitive_domains = ['agentic_core', 'apps_lic', 'apps_rg']
    
    for domain in cognitive_domains:
        if domain not in structure:
            continue
            
        print(f"\n📁 Analyzing {domain}:")
        print("-" * 50)
        
        domain_structure = structure[domain]
        
        for layer_name, layer_content in domain_structure.items():
            if not layer_name.startswith('L'):
                continue
                
            print(f"\n{layer_name}:")
            
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
                    print(f"  ⚠️  REDUNDANT phases: {', '.join(redundant_phases)}")
                
                if missing_phases:
                    print(f"  ℹ️  Missing phases: {', '.join(missing_phases)}")
                
                # Check if redundant phases are empty
                for phase in redundant_phases:
                    phase_content = layer_content[phase]
                    if isinstance(phase_content, dict):
                        file_count = len([k for k, v in phase_content.items() if v is not None and v != {}])
                        if file_count == 0:
                            print(f"    📭 {phase} is completely empty")
                        else:
                            print(f"    📄 {phase} has {file_count} files (may be legitimate)")
                
                if not redundant_phases:
                    print(f"  ✅ Architecture aligned")

def find_all_architectural_issues():
    """Find all architectural issues across the entire structure."""
    
    print(f"\n" + "=" * 80)
    print("🚨 COMPREHENSIVE ARCHITECTURAL ISSUES")
    print("=" * 80)
    
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
        print(f"\n{i}. [{issue['severity']}] {issue['issue']}")
        print(f"   Location: {issue['location']}")
        print(f"   Recommendation: {issue['recommendation']}")
    
    print(f"\n📊 Summary: {len(issues)} architectural issues found")
    print(f"   High severity: {sum(1 for i in issues if i['severity'] == 'HIGH')}")
    print(f"   Medium severity: {sum(1 for i in issues if i['severity'] == 'MEDIUM')}")
    print(f"   Low severity: {sum(1 for i in issues if i['severity'] == 'LOW')}")

def generate_recommendations():
    """Generate specific recommendations for fixing the architecture."""
    
    print(f"\n" + "=" * 80)
    print("🔧 ARCHITECTURAL FIX RECOMMENDATIONS")
    print("=" * 80)
    
    print(f"\n1. IMMEDIATE FIXES (High Priority):")
    print(f"   • Remove P1_retrieve, P2_inspect, P3_aggregate from all L5_safety layers")
    print(f"   • Remove P1_retrieve from all L2_execution layers")
    print(f"   • This eliminates ~60 empty directories across all domains")
    
    print(f"\n2. CONSIDERED FIXES (Medium Priority):")
    print(f"   • Evaluate if L3_orchestration needs P1-P2 phases")
    print(f"   • Consider consolidating orchestration to P3_aggregate + P4_safety")
    
    print(f"\n3. OPTIONAL FIXES (Low Priority):")
    print(f"   • Review L4_memory/P2_inspect usage")
    print(f"   • Memory typically retrieves and updates, inspection may be redundant")
    
    print(f"\n4. VALIDATION APPROACH:")
    print(f"   • Check semantic cache for operations targeting these directories")
    print(f"   • If zero operations, safe to remove")
    print(f"   • If some operations exist, evaluate if they're architecturally appropriate")

if __name__ == "__main__":
    analyze_cognitive_layer_architecture()
    analyze_yaml_structure()
    find_all_architectural_issues()
    generate_recommendations()
