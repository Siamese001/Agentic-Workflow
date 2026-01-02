"""
Full Agent Discovery - Canonical Single Source of Truth
Regenerates agent_discovery_full.json with safe parsing and complete detection.
"""
import ast
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / 'agentic_core'
OUTPUT_JSON = PROJECT_ROOT / 'agent_discovery_full.json'

EXCLUDED_DIRS = {'__pycache__', '.git', 'archives', '.sovereign_healing_backup', 'node_modules', '.venv'}

# Healing-capable bases (for detection) - expanded for full MRO coverage
HEALING_BASES = {
    # Core mixin
    'HealerMixin',
    # L1 bases
    'CanonBaseAgent',
    'CognitionCanonBaseAgent',
    # L2 bases (inherit from HealerMixin)
    'SubAtomicAgent',
    'ExecutionCanonBaseAgent',
    'SubatomicTestingMixin',  # Often co-inherited with HealerMixin
    # L3 bases
    'OrchestrationBaseAgent',
    'L3SubatomicTestingMixin',
    # L4 bases
    'StateBaseAgent',
    'L4SubatomicTestingMixin',
    # L5 bases
    'SafetyBaseAgent',
    # Common agent bases that have HealerMixin in their MRO
    'ASTEnforcementMixin',  # Used by L5 validators
}

SELF_TESTING_BASES = {
    'SubAtomicAgent',
    'SubatomicTestingMixin',
    'OrchestrationBaseAgent',
    'L3SubatomicTestingMixin',
    'StateBaseAgent',
    'L4SubatomicTestingMixin',
    'CanonBaseAgent',
}

DELEGATION_BASES = {
    'MaintenanceBaseAgent',
    'L0DelegationTestingMixin',
    'L0DelegationMixin',
}


def safe_parse(code: str, file_path: Path) -> Optional[ast.AST]:
    """Parse code with error tolerance."""
    try:
        return ast.parse(code)
    except SyntaxError as e:
        print(f"  [SYNTAX] Skipped {file_path.name}: {e}")
        return None


def infer_layer(file_path: Path) -> str:
    """Infer canonical layer from file path."""
    path_str = str(file_path)
    if 'L0_maintenance' in path_str or 'L0_' in path_str: return 'L0'
    if 'L1_cognition' in path_str or 'L1_' in path_str: return 'L1'
    if 'L2_execution' in path_str or 'L2_' in path_str: return 'L2'
    if 'L3_orchestration' in path_str or 'L3_' in path_str: return 'L3'
    if 'L4_state' in path_str or 'L4_' in path_str: return 'L4'
    if 'L5_safety' in path_str or 'L5_' in path_str: return 'L5'
    if 'observability' in path_str: return 'L3'  # Observability is L3-tier
    if 'utils' in path_str: return 'L2'  # Utils are L2-tier
    if 'apps_rg' in path_str: return 'apps_rg'
    if 'apps_lic' in path_str: return 'apps_lic'
    if 'apps_shared' in path_str: return 'apps_shared'
    if 'tests' in path_str: return 'tests'
    return 'misc'


def extract_bases(class_node: ast.ClassDef) -> Set[str]:
    """Extract base class names from class definition."""
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
    return bases


# Build inheritance map for MRO-like traversal
CLASS_INHERITANCE_MAP: Dict[str, Set[str]] = {}

def build_inheritance_map(tree: ast.AST) -> None:
    """Build map of class -> bases for MRO traversal."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = extract_bases(node)
            CLASS_INHERITANCE_MAP[node.name] = bases


def has_healing_in_chain(class_name: str, bases: Set[str], visited: Set[str] = None) -> bool:
    """Check if class has healing capability through inheritance chain."""
    if visited is None:
        visited = set()
    
    # Prevent infinite recursion
    if class_name in visited:
        return False
    visited.add(class_name)
    
    # Direct check
    if class_name in HEALING_BASES:
        return True
    if bases & HEALING_BASES:
        return True
    
    # Traverse inheritance chain
    for base in bases:
        if base in HEALING_BASES:
            return True
        # Check if base's bases have healing
        if base in CLASS_INHERITANCE_MAP:
            if has_healing_in_chain(base, CLASS_INHERITANCE_MAP[base], visited):
                return True
    
    return False


def extract_methods(class_node: ast.ClassDef) -> List[str]:
    """Extract method names from class definition."""
    methods = []
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(item.name)
    return methods


def has_method(class_node: ast.ClassDef, method_name: str) -> bool:
    """Check if class has a specific method."""
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name == method_name:
                return True
    return False


def count_loc(source: str) -> int:
    """Count non-blank, non-comment lines."""
    count = 0
    in_docstring = False
    for line in source.splitlines():
        stripped = line.strip()
        if '"""' in stripped or "'''" in stripped:
            quote = '"""' if '"""' in stripped else "'''"
            if stripped.count(quote) >= 2:
                continue
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if not stripped or stripped.startswith('#'):
            continue
        count += 1
    return count


def is_agent_class(class_node: ast.ClassDef, bases: Set[str]) -> bool:
    """Determine if a class is an agent - ULTRA zero-loss detection (240 core target)."""
    name = class_node.name
    
    # Pattern 1: Ends with Agent (primary pattern)
    if name.endswith('Agent'):
        return True
    
    # Pattern 2: Agent-like suffixes (curated for accuracy)
    agent_suffixes = (
        'Executor', 'Validator', 'Enforcer', 'Guardian', 'Sentinel',
        'Inspector', 'Architect', 'Engineer', 'Healer', 'Oracle',
        'Curator', 'Router', 'Orchestrator', 'Conductor',
        'Guard', 'Detector', 'Hunter', 'Fixer', 'Reconciler',
        'Mapper', 'Classifier', 'Auditor', 'Monitor',
    )
    if name.endswith(agent_suffixes):
        return True
    
    # Pattern 3: Contains 'Agent' anywhere in name
    if 'Agent' in name:
        return True
    
    # Pattern 4: Inherits from agent bases (canonical bases only)
    agent_bases = {
        'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
        'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
        'HealerMixin', 'SubatomicTestingMixin', 'ExecutionCanonBaseAgent',
        'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
        'AutonomyMixin', 'AdaptiveExecutionMixin',
    }
    if bases & agent_bases:
        return True
    
    # Pattern 5: Specific Mixin classes that are agent-like
    if name.endswith('Mixin') and any(x in name for x in ['Testing', 'Healing', 'Delegation', 'Autonomy']):
        return True
    
    return False


def get_docstring(class_node: ast.ClassDef) -> str:
    """Extract class docstring."""
    if class_node.body and isinstance(class_node.body[0], ast.Expr):
        if isinstance(class_node.body[0].value, ast.Constant):
            doc = class_node.body[0].value.value
            if isinstance(doc, str):
                return doc[:100]  # Truncate
    return ""


def main():
    print("=" * 80)
    print("FULL AGENT DISCOVERY - Single Source of Truth")
    print("=" * 80)
    
    # Force fresh - delete old JSON
    if OUTPUT_JSON.exists():
        os.remove(OUTPUT_JSON)
        print(f"[FRESH] Deleted stale {OUTPUT_JSON.name}")
    
    agents = []
    parse_errors = []
    
    # Scan ALL Python files in project
    all_py_files = list(PROJECT_ROOT.rglob('*.py'))
    print(f"\nScanning {len(all_py_files)} Python files...")
    
    # First pass: Build inheritance map for MRO-like detection
    print("[PASS 1] Building inheritance map...")
    parsed_files = {}  # Cache parsed ASTs
    for py_file in all_py_files:
        if any(ex in str(py_file) for ex in EXCLUDED_DIRS):
            continue
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
            tree = safe_parse(source, py_file)
            if tree:
                build_inheritance_map(tree)
                parsed_files[py_file] = (source, tree)
        except Exception:
            continue
    print(f"   Built map with {len(CLASS_INHERITANCE_MAP)} classes")
    
    # Second pass: Detect agents with full MRO healing detection
    print("[PASS 2] Detecting agents with MRO healing...")
    for py_file, (source, tree) in parsed_files.items():
        rel_path = py_file.relative_to(PROJECT_ROOT)
        layer = infer_layer(py_file)
        loc = count_loc(source)
        class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            
            bases = extract_bases(node)
            
            # Skip if not an agent class
            if not is_agent_class(node, bases):
                continue
            
            # Skip lowercase/snake_case (aliases)
            if node.name.islower():
                continue
            if '_' in node.name and not node.name[0].isupper():
                continue
            
            # Skip known base classes (not concrete agents)
            skip_names = {'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
                         'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
                         'IActionPlane', 'ValidationProtocol', 'Protocol', 'ABC'}
            if node.name in skip_names:
                continue
            
            methods = extract_methods(node)
            
            # Determine testing type
            has_self_test = has_method(node, '_run_self_tests') or bool(bases & SELF_TESTING_BASES)
            has_delegation = has_method(node, '_delegate_tests') or bool(bases & DELEGATION_BASES)
            if has_self_test:
                testing = 'Self'
            elif has_delegation:
                testing = 'Delegated'
            else:
                testing = 'None'
            
            # Determine healing (MRO-aware detection)
            has_heal = has_method(node, 'heal') or has_method(node, 'apply_fix') or has_method(node, 'heal_violation')
            inherits_healing = has_healing_in_chain(node.name, bases)
            has_healing = has_heal or inherits_healing
            
            # Check for tools/memory markers
            has_tools = 'tool' in source.lower() or 'mcp' in source.lower()
            has_memory = 'pinecone' in source.lower() or 'redis' in source.lower()
            
            # Check for external resource touch (Phase 5 validation)
            external_markers = ['pinecone', 'redis', 'git', 'subprocess', 'requests.', 'httpx', 'aiohttp', 'http://', 'https://']
            external_touch = any(marker in source.lower() for marker in external_markers)
            mcp_hardened = 'mcphardenedmixin' in source.lower() or 'mcp_hardened_mixin' in source.lower()
            
            agents.append({
                'class_name': node.name,
                'path': str(rel_path),
                'layer': layer,
                'inheritance': list(bases),
                'key_methods': methods[:10],  # Top 10 methods
                'has_tools': has_tools,
                'has_memory': has_memory,
                'has_healing': has_healing,
                'testing': testing,
                'has_subatomic': 'SubAtomicAgent' in bases or 'subatomic' in source.lower(),
                'loc': loc,
                'class_count': class_count,
                'description': get_docstring(node),
                'pascal_compliant': node.name[0].isupper() and '_' not in node.name,
                'external_touch': external_touch,
                'mcp_hardened': mcp_hardened,
            })
    
    # Sort by layer then name
    agents.sort(key=lambda x: (x['layer'], x['class_name']))
    
    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(agents, f, indent=2)
    
    # Statistics
    layers = defaultdict(int)
    healing_count = 0
    testing_count = 0
    for a in agents:
        layers[a['layer']] += 1
        if a['has_healing']:
            healing_count += 1
        if a['testing'] != 'None':
            testing_count += 1
    
    core_layers = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']
    core_count = sum(layers.get(l, 0) for l in core_layers)
    
    print(f"\n{'=' * 80}")
    print("DISCOVERY COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nTotal agents: {len(agents)}")
    print(f"Core (L0-L5): {core_count}")
    print(f"\nBy layer:")
    for layer in sorted(layers.keys()):
        print(f"  {layer}: {layers[layer]}")
    
    print(f"\nHealing: {healing_count}/{len(agents)} ({100*healing_count//len(agents) if agents else 0}%)")
    print(f"Testing: {testing_count}/{len(agents)} ({100*testing_count//len(agents) if agents else 0}%)")
    
    if parse_errors:
        print(f"\n[!] Parse errors (skipped): {len(parse_errors)}")
        for err in parse_errors[:10]:
            print(f"    - {err}")
    
    print(f"\n[SAVED] {OUTPUT_JSON}")
    print("=" * 80)


if __name__ == '__main__':
    main()
