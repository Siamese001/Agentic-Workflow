"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ CANONICAL AST AGENT DISCOVERY - SINGLE SOURCE OF TRUTH (SSOT)                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ This is THE authoritative agent discovery scan for the entire repository.    ║
║ All other discovery scripts are DEPRECATED and should use this output.       ║
║                                                                              ║
║ Output: agent_discovery_full.json (407 agents as of 2026-01-02)              ║
║                                                                              ║
║ Features:                                                                    ║
║ - Full AST parsing of all Python files                                       ║
║ - Complete class inheritance chain resolution (MRO-aware)                    ║
║ - Method signature extraction                                                ║
║ - Decorator analysis                                                         ║
║ - Import tracking per file                                                   ║
║ - Class attribute detection                                                  ║
║ - MRO-aware healing detection                                                ║
║                                                                              ║
║ Usage: python scripts/full_agent_discovery.py                                ║
║                                                                              ║
║ Consumers:                                                                   ║
║ - canon_validator_agentic_v2_thin.py (--list-agents, --report)               ║
║ - AutonomyGuardianAgent.generate_compliance_report()                         ║
║ - NamingAgent._build_agent_stem_cache()                                      ║
║ - HierarchyAgent.detect_layer_sprawl_violations()                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import ast
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / 'agentic_core'
OUTPUT_JSON = PROJECT_ROOT / 'agent_discovery_full.json'

EXCLUDED_DIRS = {'__pycache__', '.git', 'archives', '.sovereign_healing_backup', 'node_modules', '.venv'}


def should_exclude_file(py_file: Path) -> bool:
    """Return True if file should not be scanned for agent discovery.

    Baseline scan: do not exclude repo areas like tests/ or scripts/.
    Only exclude obvious non-source/vendor dirs.
    """
    parts = {p.lower() for p in py_file.parts}
    if parts & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    return False

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
    # Core layers
    if 'L0_maintenance' in path_str or 'L0_' in path_str: return 'L0'
    if 'L1_cognition' in path_str or 'L1_' in path_str: return 'L1'
    if 'L2_execution' in path_str or 'L2_' in path_str: return 'L2'
    if 'L3_orchestration' in path_str or 'L3_' in path_str: return 'L3'
    if 'L4_state' in path_str or 'L4_' in path_str: return 'L4'
    if 'L5_safety' in path_str or 'L5_' in path_str: return 'L5'
    # agentic_core subfolders -> assign to appropriate layers
    if 'agentic_core' in path_str:
        if 'schemas' in path_str: return 'L1'  # Schemas are cognition-tier
        if 'common' in path_str: return 'L2'  # Common utilities are execution-tier
        if 'sovereign_clients' in path_str: return 'L2'  # Clients are execution-tier
        if 'observability' in path_str: return 'L3'  # Observability is orchestration-tier
        if 'utils' in path_str: return 'L2'  # Utils are execution-tier
        return 'L2'  # Default agentic_core to L2
    # Apps
    if 'apps_rg' in path_str: return 'apps_rg'
    if 'apps_lic' in path_str: return 'apps_lic'
    if 'apps_shared' in path_str: return 'apps_shared'
    if 'tests' in path_str: return 'tests'
    # Scripts and utilities
    if 'scripts' in path_str: return 'utils'
    # Data/examples
    if 'data' in path_str and 'examples' in path_str: return 'examples'
    # Production routers in data/sdks_mcps
    if 'data' in path_str and 'sdks_mcps' in path_str and 'multi_provider_router' in path_str: return 'L5'
    # Fallback for any remaining data files
    if 'data' in path_str: return 'examples'
    return 'utils'  # Changed from 'misc' to 'utils'


def extract_bases(class_node: ast.ClassDef) -> Set[str]:
    """Extract base class names from class definition."""
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
        elif isinstance(base, ast.Subscript):  # Handle Generic[T]
            if isinstance(base.value, ast.Name):
                bases.add(base.value.id)
    return bases


def extract_decorators(node: ast.ClassDef) -> List[str]:
    """Extract decorator names from class definition."""
    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(dec.id)
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                decorators.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                decorators.append(dec.func.attr)
        elif isinstance(dec, ast.Attribute):
            decorators.append(dec.attr)
    return decorators


def extract_class_attributes(node: ast.ClassDef) -> List[str]:
    """Extract class-level attribute assignments."""
    attrs = []
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    attrs.append(target.id)
        elif isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name):
                attrs.append(item.target.id)
    return attrs


def extract_imports(tree: ast.AST) -> Tuple[List[str], List[str]]:
    """Extract all imports from a module."""
    imports = []
    from_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                from_imports.append(f"{module}.{alias.name}")
    return imports, from_imports


def extract_method_signatures(node: ast.ClassDef) -> List[Dict[str, Any]]:
    """Extract method signatures with parameters."""
    methods = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = []
            for arg in item.args.args:
                params.append(arg.arg)
            methods.append({
                'name': item.name,
                'async': isinstance(item, ast.AsyncFunctionDef),
                'params': params,
                'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in item.decorator_list[:3]]
            })
    return methods


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


def is_agent_class(class_node: ast.ClassDef, bases: Set[str], rel_path: Optional[Path] = None) -> bool:
    """Determine if a class is an agent - precise detection (240 core target)."""
    name = class_node.name
    
    # Skip known non-agent patterns
    skip_patterns = ('Test', 'Mock', 'Stub', 'Fake', 'Dummy')
    if name.startswith(skip_patterns) and 'Agent' not in name:
        return False

    # Strong negative signals (AST-friendly): not agents.
    # NOTE: Some real agents are implemented as @dataclass (e.g., red-teaming agents).
    # Treat dataclass/attrs as disqualifying only when there is no strong positive agent signal.
    decorators = extract_decorators(class_node)
    agent_bases = {
        'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
        'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
        'ExecutionCanonBaseAgent',
        'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
        'BaseAgent',
    }
    has_strong_positive_signal = (
        name.endswith('Agent')
        or bool(bases & agent_bases)
        or ('HealerMixin' in bases)
    )
    if any(d in {'dataclass', 'attrs', 'attr.s'} for d in decorators) and not has_strong_positive_signal:
        return False
    if name.endswith('Mixin'):
        return False
    if name.endswith('Protocol') or name.startswith('I') and name[1:2].isupper():
        return False
    if name.endswith('Error') or name.endswith('Exception'):
        return False

    non_agent_bases = {
        'Protocol', 'ABC',
        'BaseModel', 'TypedDict',
        'Enum',
        'Exception', 'BaseException',
        'TestCase',
    }
    if bases & non_agent_bases:
        return False

    # Even if a class is named like an agent, do not count test harness classes.
    path_str = str(rel_path).replace('\\', '/').lower() if rel_path else ''
    if path_str.startswith('tests/') or '/tests/' in path_str:
        method_names = extract_methods(class_node)
        if name.startswith('Test'):
            return False
        if any(m.startswith('test_') for m in method_names):
            return False
    
    # Pattern 1: Ends with Agent (primary pattern)
    if name.endswith('Agent'):
        return True
    
    # Pattern 2: Agent-like suffixes (core agent roles only)
    agent_suffixes = (
        'Executor', 'Validator', 'Enforcer', 'Guardian', 'Sentinel',
        'Inspector', 'Architect', 'Healer', 'Oracle',
        'Curator', 'Router', 'Orchestrator', 'Conductor',
        'Guard', 'Detector', 'Hunter', 'Fixer', 'Reconciler',
        'Mapper', 'Classifier', 'Auditor', 'Monitor', 'Witness',
    )
    # Suffix-only detection is too permissive; require anchored evidence.
    
    # Pattern 3: Contains 'Agent' anywhere in name is too permissive;
    # only accept if the class is actually in a canonical agent inheritance chain.
    
    # Pattern 4: Inherits from canonical agent bases
    if bases & agent_bases:
        return True

    # Secondary acceptance: role suffix, but only when anchored by canonical agent inheritance.
    if name.endswith(agent_suffixes) and (bases & agent_bases):
        return True
    
    # Sovereign patterns can be agents, but only when they end with Agent.
    if name.startswith('Sovereign') and name.endswith('Agent'):
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
        if should_exclude_file(py_file):
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
            if not is_agent_class(node, bases, rel_path=rel_path):
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
                'top_dir': rel_path.parts[0] if len(rel_path.parts) >= 1 else '',
                'sub_dir': '/'.join(rel_path.parts[:2]) if len(rel_path.parts) >= 2 else (rel_path.parts[0] if len(rel_path.parts) >= 1 else ''),
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
    top_dirs = defaultdict(int)
    sub_dirs = defaultdict(int)
    healing_count = 0
    testing_count = 0
    for a in agents:
        layers[a['layer']] += 1
        top_dirs[a.get('top_dir', '')] += 1
        sub_dirs[a.get('sub_dir', '')] += 1
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

    print(f"\nBy top-level folder (baseline location):")
    for k, v in sorted(top_dirs.items(), key=lambda kv: kv[1], reverse=True):
        label = k or '(root)'
        print(f"  {label}: {v}")

    print(f"\nTop 15 subfolders (top_dir/second_dir):")
    for k, v in sorted(sub_dirs.items(), key=lambda kv: kv[1], reverse=True)[:15]:
        label = k or '(root)'
        print(f"  {label}: {v}")
    
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
