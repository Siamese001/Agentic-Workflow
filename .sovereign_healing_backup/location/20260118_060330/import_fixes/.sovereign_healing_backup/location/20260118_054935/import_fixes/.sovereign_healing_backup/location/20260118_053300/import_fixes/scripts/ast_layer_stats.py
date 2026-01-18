#!/usr/bin/env python3
"""AST-based layer statistics scanner for agents."""
import ast
import os
from pathlib import Path
from collections import defaultdict

from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
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

PROJECT_ROOT = Path(__file__).parent.parent

# Mixins to detect
HEALER_MIXINS = {'HealerMixin', 'Healer'}
MCP_MIXINS = {'MCPHardenedMixin', 'MCPHardened', 'HardenedMixin'}

def get_layer(path: Path) -> str:
    """Extract layer from path."""
    rel = str(path.relative_to(PROJECT_ROOT))
    parts = rel.replace('\\', '/').split('/')
    
    # Check root folder first
    if parts[0] == APPS_LIC_DIR: return APPS_LIC_DIR
    if parts[0] == APPS_RG_DIR: return APPS_RG_DIR
    if parts[0] == APPS_SHARED_DIR: return APPS_SHARED_DIR
    
    # Check agentic_core subfolders
    if parts[0] == AGENTIC_CORE_DIR and len(parts) > 1:
        for part in parts[1:]:
            if part.startswith('L0'): return 'L0'
            if part.startswith('L1'): return 'L1'
            if part.startswith('L2'): return 'L2'
            if part.startswith('L3'): return 'L3'
            if part.startswith('L4'): return 'L4'
            if part.startswith('L5'): return 'L5'
        # Other agentic_core folders
        subfolder = parts[1]
        if subfolder in ['config', 'utils', 'observability', 'schemas', 'runtime', 'prompt_governance']:
            return subfolder
    
    return 'other'

def find_test_file(agent_path: Path, agent_class: str) -> bool:
    """Check if a test file exists for this agent."""
    tests_dir = PROJECT_ROOT / TESTS_DIR
    if not tests_dir.exists():
        return False
    
    # Check for test_<filename>.py or test_<classname>.py
    agent_name = agent_path.stem
    class_snake = ''.join(['_' + c.lower() if c.isupper() else c for c in agent_class]).lstrip('_')
    
    patterns = [
        f"test_{agent_name}.py",
        f"test_{class_snake}.py",
        f"test_{agent_name.lower()}.py",
    ]
    
    for test_file in tests_dir.rglob("test_*.py"):
        if test_file.name in patterns:
            return True
        # Also check if the test file imports this agent
        try:
            content = test_file.read_text(encoding='utf-8', errors='ignore')
            if agent_class in content:
                return True
        except:
            pass
    
    return False

# Name suffixes that indicate an agent (not a mixin/base)
AGENT_SUFFIXES = {'Agent', 'Handler', 'Manager', 'Controller', 'Executor', 'Validator', 
                  'Orchestrator', 'Router', 'Dispatcher', 'Governor', 'Enforcer', 
                  'Analyzer', 'Mapper', 'Loader', 'Provider', 'Engine', 'Plane',
                  'Shield', 'Guard', 'Sentinel', 'Monitor', 'Observer', 'Historian'}

# Base classes that indicate inheritance from agent architecture
AGENT_BASE_CLASSES = {'BaseAgent', 'AutonomousAgent', 'HealerMixin', 'MCPHardenedMixin',
                      'ExecutionCanonBaseAgent', 'CanonBaseAgent'}

# Exclude pure base/mixin classes
EXCLUDE_PATTERNS = {'Mixin', 'Base', 'Abstract', 'Protocol', 'Interface', 'Meta'}

def analyze_file(path: Path) -> list:
    """Analyze a Python file for agent classes."""
    agents = []
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(content)
    except:
        return agents
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Skip pure base/mixin classes
            if any(p in node.name for p in EXCLUDE_PATTERNS):
                continue
            
            # Check if it's an agent by name suffixes
            name_match = any(node.name.endswith(s) for s in AGENT_SUFFIXES)
            
            # Check base classes
            bases = set()
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.add(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.add(base.attr)
            
            base_match = bool(bases & AGENT_BASE_CLASSES)
            
            is_agent = name_match or base_match
            if not is_agent:
                continue
            
            # Get all base class names
            bases = set()
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.add(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.add(base.attr)
            
            # Check for healing mixin
            has_healing = bool(bases & HEALER_MIXINS)
            
            # Check for MCP mixin
            has_mcp = bool(bases & MCP_MIXINS)
            
            # Also check method names and decorators for healing/MCP patterns
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if 'heal' in item.name.lower():
                        has_healing = True
                    if 'mcp' in item.name.lower() or 'hardened' in item.name.lower():
                        has_mcp = True
            
            # Check imports at file level for mixin usage
            for n in ast.walk(tree):
                if isinstance(n, ast.ImportFrom):
                    if n.module and 'healer' in n.module.lower():
                        for alias in n.names:
                            if alias.name in HEALER_MIXINS:
                                has_healing = True
                    if n.module and 'mcp' in n.module.lower():
                        for alias in n.names:
                            if alias.name in MCP_MIXINS:
                                has_mcp = True
            
            # Check for testing
            has_testing = find_test_file(path, node.name)
            
            agents.append({
                'class': node.name,
                'path': path,
                'layer': get_layer(path),
                'has_healing': has_healing,
                'has_mcp': has_mcp,
                'has_testing': has_testing,
                'bases': list(bases),
            })
    
    return agents

def main():
    stats = defaultdict(lambda: {'count': 0, 'healing': 0, 'mcp': 0, 'testing': 0})
    
    # Directories to scan
    scan_dirs = [
        PROJECT_ROOT / AGENTIC_CORE_DIR,
        PROJECT_ROOT / APPS_LIC_DIR,
        PROJECT_ROOT / APPS_RG_DIR,
        PROJECT_ROOT / APPS_SHARED_DIR,
    ]
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            for agent in analyze_file(py_file):
                layer = agent['layer']
                stats[layer]['count'] += 1
                if agent['has_healing']:
                    stats[layer]['healing'] += 1
                if agent['has_mcp']:
                    stats[layer]['mcp'] += 1
                if agent['has_testing']:
                    stats[layer]['testing'] += 1
    
    # Define row order
    all_layers = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'config', 'utils', 'observability', 'schemas', 'runtime', 'prompt_governance', APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'other']
    
    print("| Layer | Agents | Testing% | Healing% | MCP% |")
    print("|-------|--------|----------|----------|------|")
    
    total_count = 0
    total_healing = 0
    total_mcp = 0
    total_testing = 0
    
    for layer in all_layers:
        s = stats[layer]
        count = s['count']
        if count == 0:
            continue  # Skip empty layers
        
        total_count += count
        total_healing += s['healing']
        total_mcp += s['mcp']
        total_testing += s['testing']
        
        testing_pct = s['testing'] * 100 // count
        healing_pct = s['healing'] * 100 // count
        mcp_pct = s['mcp'] * 100 // count
        
        print(f"| {layer} | {count} | {testing_pct}% | {healing_pct}% | {mcp_pct}% |")
    
    # Total row
    print("|-------|--------|----------|----------|------|")
    if total_count > 0:
        print(f"| **TOTAL** | {total_count} | {total_testing*100//total_count}% | {total_healing*100//total_count}% | {total_mcp*100//total_count}% |")

if __name__ == '__main__':
    main()
