"""
Comprehensive Agent Audit - Scans ALL agents to map detection capabilities
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from pathlib import Path
import ast
import re

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
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

# Keywords that indicate what violations an agent should detect
DETECTION_KEYWORDS = {
    'duplicate': ['duplicate', 'dedup', 'copy', 'clone', 'identical', 'same content'],
    'syntax': ['syntax', 'parse error', 'ast.parse', 'SyntaxError', 'compile'],
    'naming': ['naming', 'snake_case', 'camelcase', 'pascal', 'file name', 'rename'],
    'gravity': ['gravity', 'upward import', 'layer violation', 'import from lower'],
    'location': ['location', 'territory', 'wrong folder', 'misplaced', 'placement'],
    'ssot': ['ssot', 'single source', 'hard-coded path', 'blueprint'],
    'hygiene': ['hygiene', 'dead code', 'orphan', 'unused', 'rot'],
    'structure': ['structure', 'hierarchy', 'depth', 'fission', 'too large'],
    'import': ['circular import', 'import cycle', 'forbidden import'],
    'coverage': ['coverage', 'test', 'zombie', 'untested'],
}

def analyze_agents():
    agents_analysis = []
    
    # Scan all agent files in agentic_core
    for py_file in Path(AGENTIC_CORE_DIR).rglob('*.py'):
        path_str = str(py_file)
        if '__pycache__' in path_str:
            continue
        
        name = py_file.name
        if 'Agent' not in name and 'Validator' not in name and 'Detector' not in name and 'Enforcer' not in name:
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            size = len(content)
            
            # Skip empty files
            if size < 50:
                agents_analysis.append({
                    'path': path_str,
                    'name': name,
                    'size': size,
                    'status': 'EMPTY',
                    'detects': []
                })
                continue
            
            content_lower = content.lower()
            
            # What does this agent detect?
            detects = []
            for category, keywords in DETECTION_KEYWORDS.items():
                if any(kw in content_lower for kw in keywords):
                    detects.append(category)
            
            # Check if it has key methods
            has_validate = 'def validate' in content_lower or 'def detect' in content_lower or 'def scan' in content_lower
            has_heal = 'def heal' in content_lower or 'def fix' in content_lower or 'def repair' in content_lower
            
            agents_analysis.append({
                'path': path_str,
                'name': name,
                'size': size,
                'status': 'ACTIVE' if has_validate else 'PASSIVE',
                'detects': detects,
                'has_heal': has_heal
            })
        except Exception as e:
            pass
    
    return agents_analysis

def print_analysis(agents_analysis):
    print('=== AGENTS BY DETECTION CAPABILITY ===')
    print()
    
    for category in DETECTION_KEYWORDS.keys():
        agents_for_cat = [a for a in agents_analysis if category in a.get('detects', [])]
        print(f'\n### {category.upper()} DETECTION ({len(agents_for_cat)} agents)')
        for a in sorted(agents_for_cat, key=lambda x: x['name'])[:10]:
            status = a['status']
            heal = 'HEALS' if a.get('has_heal') else 'DETECT-ONLY'
            print(f"  [{status}] [{heal}] {a['name']} ({a['size']} bytes)")
            print(f"           {a['path']}")
        if len(agents_for_cat) > 10:
            print(f'  ... and {len(agents_for_cat) - 10} more')
    
    print()
    print('=== EMPTY AGENTS (SHOULD BE IMPLEMENTED) ===')
    empty = [a for a in agents_analysis if a['status'] == 'EMPTY']
    for a in empty:
        print(f"  {a['path']}")

if __name__ == '__main__':
    agents = analyze_agents()
    print_analysis(agents)
    print(f'\nTotal agents analyzed: {len(agents)}')