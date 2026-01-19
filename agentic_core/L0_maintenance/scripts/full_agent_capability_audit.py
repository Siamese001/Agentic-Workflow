"""
Full Agent Capability Audit - Maps ALL agents to violation types they should catch
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from pathlib import Path
import re

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from archives.location_violations.sovereign_index import SovereignIndex

def analyze_all_agents():
    """Analyze all agents and their detection capabilities."""
    
    agents_with_methods = []
    
    for py_file in Path(AGENTIC_CORE_DIR).rglob('*.py'):
        path_str = str(py_file)
        if '__pycache__' in path_str:
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            size = len(content)
            
            if size < 100:
                continue
                
            # Find all method definitions
            methods = []
            for line in content.split('\n'):
                if line.strip().startswith('def '):
                    method_name = line.strip().split('(')[0].replace('def ', '')
                    if any(kw in method_name.lower() for kw in ['validate', 'detect', 'scan', 'check', 'audit', 'find', 'verify']):
                        methods.append(method_name)
            
            if methods:
                agents_with_methods.append({
                    'path': path_str,
                    'name': py_file.name,
                    'methods': methods,
                    'size': size
                })
        except:
            pass
    
    # Sort by number of detection methods
    agents_with_methods.sort(key=lambda x: len(x['methods']), reverse=True)
    
    print('=== TOP AGENTS WITH DETECTION/VALIDATION METHODS ===')
    print()
    for a in agents_with_methods[:50]:
        name = a['name']
        method_count = len(a['methods'])
        size = a['size']
        path = a['path']
        methods_str = ', '.join(a['methods'][:5])
        
        print(f"{name} ({method_count} methods, {size} bytes)")
        print(f"  Path: {path}")
        print(f"  Methods: {methods_str}")
        if len(a['methods']) > 5:
            print(f"           ... and {len(a['methods']) - 5} more")
        print()
    
    return agents_with_methods

def find_violation_specific_agents():
    """Find agents specifically designed to catch each violation type."""
    
    violation_map = {
        'DUPLICATE_FILES': {
            'keywords': ['duplicate', 'dedup', 'identical content', 'same file', 'clone'],
            'agents': []
        },
        'SYNTAX_ERRORS': {
            'keywords': ['syntax', 'parse', 'ast.parse', 'SyntaxError'],
            'agents': []
        },
        'NAMING_VIOLATIONS': {
            'keywords': ['naming', 'snake_case', 'camelcase', 'pascal', 'file name convention'],
            'agents': []
        },
        'GRAVITY_VIOLATIONS': {
            'keywords': ['gravity', 'upward import', 'layer violation', 'import leak'],
            'agents': []
        },
        'LOCATION_VIOLATIONS': {
            'keywords': ['location', 'territory', 'wrong folder', 'misplaced file'],
            'agents': []
        },
        'SSOT_VIOLATIONS': {
            'keywords': ['ssot', 'single source', 'hard-coded path', 'blueprint'],
            'agents': []
        },
        'HYGIENE_VIOLATIONS': {
            'keywords': ['hygiene', 'dead code', 'orphan', 'unused', 'rot'],
            'agents': []
        },
        'EMPTY_FILES': {
            'keywords': ['empty', 'stub', 'not implemented'],
            'agents': []
        }
    }
    
    for py_file in Path(AGENTIC_CORE_DIR).rglob('*.py'):
        path_str = str(py_file)
        if '__pycache__' in path_str:
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore').lower()
            name = py_file.name
            
            for vtype, data in violation_map.items():
                if any(kw in content for kw in data['keywords']):
                    # Check if it has detection methods
                    if any(m in content for m in ['def validate', 'def detect', 'def scan', 'def check', 'def find', 'def audit']):
                        data['agents'].append({
                            'name': name,
                            'path': path_str
                        })
        except:
            pass
    
    print('\n=== AGENTS BY VIOLATION TYPE THEY SHOULD CATCH ===\n')
    for vtype, data in violation_map.items():
        agents = data['agents']
        print(f"\n### {vtype} ({len(agents)} agents)")
        for a in sorted(agents, key=lambda x: x['name'])[:15]:
            print(f"  {a['name']}")
            print(f"    {a['path']}")
        if len(agents) > 15:
            print(f"  ... and {len(agents) - 15} more")
    
    return violation_map

if __name__ == '__main__':
    print("=" * 60)
    print("COMPREHENSIVE AGENT CAPABILITY AUDIT")
    print("=" * 60)
    
    agents = analyze_all_agents()
    print(f"\nTotal agents with detection methods: {len(agents)}")
    
    violation_map = find_violation_specific_agents()
