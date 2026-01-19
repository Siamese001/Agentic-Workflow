"""
DEPRECATED: Use scripts/full_agent_discovery.py instead.

This scanner is deprecated - full_agent_discovery.py is the canonical Single Source of Truth
for agent discovery with MRO-aware healing detection and ULTRA zero-loss detection.

PHASE 1: Exhaustive PascalCase Agent Discovery Audit
AST-based structural fingerprinting for deduplication, dead code, and layer analysis.
"""
import warnings
warnings.warn(
    "agent_discovery_audit.py is DEPRECATED. Use full_agent_discovery.py instead.",
    DeprecationWarning,
    stacklevel=2
)
import ast
import hashlib
import os
from tqdm import tqdm
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any
import copy

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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

EXCLUDED_DIRS = {'__pycache__', '.git', 'archives', 'data', '.sovereign_healing_backup'}
ORCHESTRATOR_FILES = {'compliance_orchestrator.py', 'canon_validator_agentic_v2.py'}


def infer_layer(file_path: Path) -> str:
    """Infer canonical layer from file path."""
    path_str = str(file_path)
    if 'L0_maintenance' in path_str: return 'L0'
    if 'L1_cognition' in path_str: return 'L1'
    if 'L2_execution' in path_str: return 'L2'
    if 'L3_orchestration' in path_str: return 'L3'
    if 'L4_state' in path_str: return 'L4'
    if 'L5_safety' in path_str: return 'L5'
    if 'observability' in path_str: return 'observability'
    if 'utils' in path_str: return 'utils'
    if 'config' in path_str: return 'config'
    if 'prompt_governance' in path_str: return 'prompt'
    return 'other'


def count_loc(source: str) -> int:
    """Count non-comment, non-blank lines."""
    lines = source.splitlines()
    count = 0
    in_docstring = False
    for line in lines:
        stripped = line.strip()
        # Handle docstrings
        if '"""' in stripped or "'''" in stripped:
            quote = '"""' if '"""' in stripped else "'''"
            occurrences = stripped.count(quote)
            if occurrences >= 2:
                continue  # Single line docstring
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if not stripped or stripped.startswith('#'):
            continue
        count += 1
    return count


def extract_methods(class_node: ast.ClassDef) -> Dict[str, bool]:
    """Extract key methods from class definition."""
    methods = {
        '__init__': False,
        'heal_violation': False,
        'execute': False,
        'run': False,
        'monitor': False,
        'validate': False
    }
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name in methods:
                methods[item.name] = True
    return methods


class ASTNormalizer(ast.NodeTransformer):
    """Normalize AST for structural fingerprinting."""
    
    def __init__(self):
        super().__init__()
        self.arg_counter = 0
        self.var_counter = 0

    def visit_Constant(self, node):
        # Replace long strings with placeholder
        if isinstance(node.value, str) and len(node.value) > 20:
            node.value = '<STR>'
        return node
    
    def visit_arg(self, node: ast.arg) -> ast.arg:
        """Canonicalize parameter names"""
        self.arg_counter += 1
        return ast.arg(arg=f"param{self.arg_counter}", annotation=None)

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Canonicalize local variable names (preserve dunders)"""
        if node.id.startswith('__') and node.id.endswith('__'):
            return node
        self.var_counter += 1
        return ast.Name(id=f"var{self.var_counter}", ctx=node.ctx)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Strip class docstring, sort methods, process body"""
        # Remove class-level docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]

        # Sort methods alphabetically for canonical order
        methods = []
        non_methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item)
            else:
                non_methods.append(item)
        methods.sort(key=lambda m: m.name)
        node.body = methods + non_methods

        return self.generic_visit(node)


def generate_fingerprint(class_node: ast.ClassDef) -> str:
    """Generate structural fingerprint for a class."""
    try:
        node_copy = copy.deepcopy(class_node)
        normalizer = ASTNormalizer()
        normalized = normalizer.visit(node_copy)
        ast.fix_missing_locations(normalized)
        dump = ast.dump(normalized, include_attributes=False)
        return hashlib.sha256(dump.encode()).hexdigest()[:16]
    except Exception as e:
        return f'ERROR:{str(e)[:20]}'


def is_real_usage(node: ast.AST, agent_name: str) -> bool:
    """AST-based check if node represents real usage (not discovery)"""
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == agent_name:
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == agent_name:
            return True
    elif isinstance(node, ast.Compare):
        # isinstance(x, XxxAgent)
        if (isinstance(node.left, ast.Call) and
            isinstance(node.left.func, ast.Name) and node.left.func.id == 'isinstance' and
            len(node.left.args) == 2 and
            isinstance(node.comparators[0], ast.Name) and node.comparators[0].id == agent_name):
            return True
    # Type hints: def func(x: XxxAgent) or variable: XxxAgent = ...
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.annotation, ast.Name) and node.annotation.id == agent_name:
            return True
    elif isinstance(node, ast.arg) and isinstance(node.annotation, ast.Name) and node.annotation.id == agent_name:
        return True
    # Attribute access on instance: agent.do_something()
    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id.lower() == agent_name.lower():
        return True
    return False

def count_usages_ast(agent_name: str, agent_file: Path) -> Dict[str, Any]:
    """Sovereign AST-based usage counting (excludes orchestrator discovery)"""
    usages = {'real': 0, 'string_ref': 0, 'files': set()}

    for py_file in tqdm(list(PROJECT_ROOT.rglob('*.py')), desc=f"Scanning {agent_name}", leave=False):
        if any(ex in str(py_file) for ex in EXCLUDED_DIRS):
            continue
        if py_file == agent_file:
            continue
        if py_file.name in ORCHESTRATOR_FILES:
            continue
        if py_file.name == '__init__.py':
            continue  # re-exports don't count as usage

        try:
            source = py_file.read_text(encoding='utf-8')
            tree = ast.parse(source)
        except:
            continue

        has_real = False
        for node in ast.walk(tree):
            if is_real_usage(node, agent_name):
                has_real = True
            # String references
            if (isinstance(node, ast.Constant) and isinstance(node.value, str) and
                agent_name in node.value):
                usages['string_ref'] += 1

        if has_real:
            usages['real'] += 1
            usages['files'].add(str(py_file.relative_to(PROJECT_ROOT)))

    return {'real': usages['real'], 'string_ref': usages['string_ref'], 'files': list(usages['files'])}


def suggest_layer(agent: Dict) -> str:
    """Suggest appropriate layer based on agent characteristics."""
    name = agent['name'].lower()
    methods = agent['methods']
    
    # Safety/validators -> L5
    if 'validator' in name or 'guard' in name or 'enforcer' in name:
        return 'L5'
    if methods.get('heal_violation'):
        return 'L5'
    
    # Orchestration -> L3
    if 'orchestrator' in name or 'workflow' in name or 'mission' in name:
        return 'L3'
    
    # State/caching -> L4
    if 'redis' in name or 'pinecone' in name or 'cache' in name or 'state' in name:
        return 'L4'
    
    # Execution/tools -> L2
    if 'tool' in name or 'executor' in name or 'registry' in name:
        return 'L2'
    
    # Cognition -> L1
    if 'thought' in name or 'reflection' in name or 'research' in name:
        return 'L1'
    
    # Maintenance/bootstrap -> L0
    if 'bootstrap' in name or 'maintenance' in name or 'watchdog' in name:
        return 'L0'
    
    # Observability
    if 'telemetry' in name or 'metrics' in name or 'tracing' in name or 'reporting' in name:
        return 'observability'
    
    return agent['layer']  # Keep current


def main():
    print('=' * 80)
    print('PHASE 1: EXHAUSTIVE PASCALCASE AGENT DISCOVERY')
    print('=' * 80)
    
    agents = []
    
    # Discover all Agent files
    for py_file in AGENTIC_CORE.rglob('*Agent.py'):
        if '__pycache__' in str(py_file):
            continue
        if '.sovereign_healing_backup' in str(py_file):
            continue
        
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
            tree = ast.parse(source)
        except Exception as e:
            print(f'[PARSE ERROR] {py_file.name}: {e}')
            continue
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith('Agent'):
                # Skip snake_case aliases
                if node.name.islower() or '_' in node.name:
                    if not node.name[0].isupper():
                        continue
                
                rel_path = py_file.relative_to(PROJECT_ROOT)
                module_path = str(rel_path).replace(os.sep, '.').replace('.py', '')
                layer = infer_layer(py_file)
                methods = extract_methods(node)
                loc = count_loc(source)
                fingerprint = generate_fingerprint(node)
                
                agents.append({
                    'name': node.name,
                    'module': module_path,
                    'file': str(rel_path),
                    'layer': layer,
                    'methods': methods,
                    'loc': loc,
                    'fingerprint': fingerprint,
                    'line': node.lineno,
                    'abs_path': str(py_file)
                })
    
    # Sort by layer then name
    agents.sort(key=lambda x: (x['layer'], x['name']))
    
    print(f'\nTotal Agent classes discovered: {len(agents)}')
    
    # SECTION 1: Inventory Table
    print('\n' + '=' * 80)
    print('SECTION 1: FULL INVENTORY TABLE')
    print('=' * 80)
    print(f'{"Agent Name":<40} {"Layer":<8} {"LOC":<6} {"FP":<18} {"Methods"}')
    print('-' * 100)
    
    for a in agents:
        method_flags = []
        if a['methods']['__init__']: method_flags.append('init')
        if a['methods']['heal_violation']: method_flags.append('heal')
        if a['methods']['execute']: method_flags.append('exec')
        if a['methods']['run']: method_flags.append('run')
        if a['methods']['validate']: method_flags.append('valid')
        method_str = ','.join(method_flags) if method_flags else '-'
        print(f'{a["name"]:<40} {a["layer"]:<8} {a["loc"]:<6} {a["fingerprint"]:<18} {method_str}')
    
    # SECTION 2: Deduplication Analysis
    print('\n' + '=' * 80)
    print('SECTION 2: DEDUPLICATION ANALYSIS (AST Fingerprints)')
    print('=' * 80)
    
    fingerprint_groups = defaultdict(list)
    for a in agents:
        fingerprint_groups[a['fingerprint']].append(a)
    
    duplicates = {fp: group for fp, group in fingerprint_groups.items() if len(group) > 1}
    
    if duplicates:
        print(f'\nFound {len(duplicates)} duplicate fingerprint groups:')
        for fp, group in duplicates.items():
            print(f'\n  [EXACT DUPLICATE GROUP - Fingerprint: {fp}]')
            for a in group:
                print(f'    - {a["name"]} ({a["layer"]}) -> {a["file"]}')
    else:
        print('\n[OK] No exact structural duplicates found.')
    
    # SECTION 3: Dead Code Detection
    print('\n' + '=' * 80)
    print('SECTION 3: DEAD CODE DETECTION')
    print('=' * 80)
    
    dead_agents = []
    suspect_agents = []
    live_agents = []
    
    print('\nAnalyzing usage patterns (AST-based)...')
    
    for a in agents:
        print(f"  Analyzing: {a['name']} ({a['layer']})")
        usages = count_usages_ast(a['name'], Path(a['abs_path']))
        a['usages'] = usages
        
        real_usages = usages['real']
        
        if real_usages == 0 and usages['string_ref'] == 0:
            dead_agents.append(a)
        elif real_usages == 0 and usages['string_ref'] > 0:
            suspect_agents.append(a)
        else:
            live_agents.append(a)
    
    print(f'\n  LIVE agents (real usage): {len(live_agents)}')
    print(f'  SUSPECT agents (string/import only): {len(suspect_agents)}')
    print(f'  DEAD agents (no usage): {len(dead_agents)}')
    
    if dead_agents:
        print(f'\n  [DEAD AGENTS - Zero external usage]')
        for a in dead_agents:
            print(f'    - {a["name"]} ({a["layer"]}) -> {a["file"]}')
    
    if suspect_agents:
        print(f'\n  [SUSPECT AGENTS - String references only]')
        for a in suspect_agents:
            u = a['usages']
            print(f'    - {a["name"]} ({a["layer"]}) strings={u["string_ref"]}')
    
    # SECTION 4: Layer Misplacement Analysis
    print('\n' + '=' * 80)
    print('SECTION 4: LAYER ORGANIZATION ANALYSIS')
    print('=' * 80)
    
    misplacements = []
    for a in agents:
        suggested = suggest_layer(a)
        if suggested != a['layer']:
            misplacements.append({
                'agent': a['name'],
                'current': a['layer'],
                'suggested': suggested,
                'file': a['file']
            })
    
    if misplacements:
        print(f'\nFound {len(misplacements)} potential layer misplacements:')
        print(f'\n{"Agent":<40} {"Current":<10} {"Suggested":<10}')
        print('-' * 60)
        for m in misplacements:
            print(f'{m["agent"]:<40} {m["current"]:<10} {m["suggested"]:<10}')
    else:
        print('\n[OK] All agents appear to be in appropriate layers.')
    
    # SECTION 5: Summary
    print('\n' + '=' * 80)
    print('SECTION 5: SUMMARY')
    print('=' * 80)
    
    layer_counts = defaultdict(int)
    for a in agents:
        layer_counts[a['layer']] += 1
    
    print(f'\n  Total agents discovered: {len(agents)}')
    print(f'\n  By Layer:')
    for layer in sorted(layer_counts.keys()):
        print(f'    {layer}: {layer_counts[layer]} agents')
    
    print(f'\n  Exact duplicates found: {sum(len(g)-1 for g in duplicates.values())}')
    print(f'  DEAD agents: {len(dead_agents)}')
    print(f'  SUSPECT agents: {len(suspect_agents)}')
    print(f'  Layer mismatches: {len(misplacements)}')
    
    # Save full report
    report = {
        'agents': agents,
        'duplicates': {fp: [a['name'] for a in group] for fp, group in duplicates.items()},
        'dead_agents': [a['name'] for a in dead_agents],
        'suspect_agents': [a['name'] for a in suspect_agents],
        'misplacements': misplacements,
        'summary': {
            'total': len(agents),
            'duplicates': sum(len(g)-1 for g in duplicates.values()),
            'dead': len(dead_agents),
            'suspect': len(suspect_agents),
            'misplacements': len(misplacements)
        }
    }
    
    with open(PROJECT_ROOT / 'agent_discovery_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f'\n[SAVED] Full report exported to agent_discovery_report.json')
    
    print('\n' + '=' * 80)
    print('PHASE 1 DISCOVERY COMPLETE')
    print('AST FINGERPRINTS GENERATED')
    print('DUPLICATES, DEAD CODE, AND LAYER ISSUES IDENTIFIED')
    print('READY FOR PHASE 2 IMPLEMENTATION')
    print('=' * 80)


if __name__ == '__main__':
    main()
