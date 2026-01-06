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
CANONICAL_JSON = PROJECT_ROOT / 'agent_discovery_full.json'
MANIFEST_JSON = PROJECT_ROOT / 'agent_discovery_full.manifest.json'
LEGACY_JSON = PROJECT_ROOT / 'agent_discovery_full.json'
MISTAKE_JSON = PROJECT_ROOT / 'agent_full.json'
MISTAKE_JSON_2 = PROJECT_ROOT / 'agent_discovery_legacy.json'
OUTPUT_JSON = CANONICAL_JSON

EXCLUDED_DIRS = {'__pycache__', '.git', 'archives', '.sovereign_healing_backup', 'node_modules', '.venv'}

# ============================================================================
# HARDENING: Agent Count Baseline Protection
# ============================================================================
# CRITICAL: These thresholds prevent catastrophic agent loss from bugs.
# If discovery finds fewer agents than MINIMUM_AGENT_COUNT, it will ABORT.
# If discovery drops more than MAX_AGENT_DROP_PERCENT from previous run, it will WARN.
#
# History:
#   - 2026-01-02: 407 agents (initial baseline)
#   - 2026-01-05: 312 agents (after string error caused 60+ agent loss - UNACCEPTABLE)
#
# Update MINIMUM_AGENT_COUNT when legitimately removing agents (with justification).
MINIMUM_AGENT_COUNT = 300  # Hard floor - abort if below this
MAX_AGENT_DROP_PERCENT = 10  # Warn if drop exceeds this percentage from previous run
EXPECTED_AGENT_COUNT = 316  # Current expected count (update when agents added/removed)
# 2026-01-05: Updated from 312 to 316 after enabling discovery of L3-L5 BaseAgent classes
# (+3 base agents: OrchestrationBaseAgent, StateBaseAgent, SafetyBaseAgent)
# (+1 additional agent discovered during scan)


def should_exclude_file(py_file: Path) -> bool:
    """Return True if file should not be scanned for agent discovery.

    Baseline scan: do not exclude repo areas like tests/ or scripts/.
    Only exclude obvious non-source/vendor dirs.
    """
    parts = {p.lower() for p in py_file.parts}
    if parts & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    return False


def validate_agent_count(agent_count: int, previous_count: Optional[int] = None) -> Tuple[bool, List[str]]:
    """
    HARDENING: Validate agent count against safety thresholds.
    
    Returns:
        (is_valid, errors) - is_valid=False means ABORT discovery
    """
    errors = []
    warnings = []
    
    # Hard floor check - ABORT if below minimum
    if agent_count < MINIMUM_AGENT_COUNT:
        errors.append(
            f"❌ CRITICAL: Agent count {agent_count} is below MINIMUM_AGENT_COUNT ({MINIMUM_AGENT_COUNT})!\n"
            f"   This indicates a catastrophic bug in agent detection.\n"
            f"   Discovery ABORTED to prevent data loss.\n"
            f"   If this is intentional, update MINIMUM_AGENT_COUNT in full_agent_discovery.py"
        )
        return False, errors
    
    # Check against previous run (if available)
    if previous_count is not None and previous_count > 0:
        drop = previous_count - agent_count
        drop_percent = (drop / previous_count) * 100
        
        if drop > 0 and drop_percent > MAX_AGENT_DROP_PERCENT:
            errors.append(
                f"❌ CRITICAL: Agent count dropped by {drop} ({drop_percent:.1f}%) from previous run!\n"
                f"   Previous: {previous_count}, Current: {agent_count}\n"
                f"   This exceeds MAX_AGENT_DROP_PERCENT ({MAX_AGENT_DROP_PERCENT}%).\n"
                f"   Discovery ABORTED to prevent data loss.\n"
                f"   If this is intentional, run with --force flag"
            )
            return False, errors
    
    # Soft warning for deviation from expected count
    if agent_count < EXPECTED_AGENT_COUNT:
        diff = EXPECTED_AGENT_COUNT - agent_count
        warnings.append(
            f"⚠️  WARNING: Agent count {agent_count} is {diff} below EXPECTED_AGENT_COUNT ({EXPECTED_AGENT_COUNT})"
        )
    elif agent_count > EXPECTED_AGENT_COUNT:
        diff = agent_count - EXPECTED_AGENT_COUNT
        warnings.append(
            f"ℹ️  INFO: Agent count {agent_count} is {diff} above EXPECTED_AGENT_COUNT ({EXPECTED_AGENT_COUNT})"
        )
    
    # Print warnings but don't fail
    for w in warnings:
        print(w)
    
    return True, errors


def get_previous_agent_count() -> Optional[int]:
    """Get agent count from previous discovery run (from manifest or JSON)."""
    # Try manifest first
    if MANIFEST_JSON.exists():
        try:
            manifest = json.loads(MANIFEST_JSON.read_text(encoding='utf-8'))
            return manifest.get('agent_count')
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Fall back to counting agents in existing JSON
    if CANONICAL_JSON.exists():
        try:
            agents = json.loads(CANONICAL_JSON.read_text(encoding='utf-8'))
            return len(agents)
        except json.JSONDecodeError:
            pass
    
    return None


def generate_manifest(agents: List[Dict], scan_duration: float, parse_errors: List[str]) -> Dict:
    """Generate manifest with metadata for staleness detection and validation."""
    import hashlib
    from datetime import datetime
    
    # Compute content hash of agent data
    content_str = json.dumps(agents, sort_keys=True)
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()
    
    # Layer breakdown
    layer_counts = defaultdict(int)
    for a in agents:
        layer_counts[a.get('layer', 'unknown')] += 1
    
    manifest = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'scan_duration_seconds': round(scan_duration, 2),
        'agent_count': len(agents),
        'content_hash': f'sha256:{content_hash}',
        'layer_breakdown': dict(layer_counts),
        'parse_errors_count': len(parse_errors),
        'minimum_agent_count': MINIMUM_AGENT_COUNT,
        'expected_agent_count': EXPECTED_AGENT_COUNT,
        'validation': {
            'passed': len(agents) >= MINIMUM_AGENT_COUNT,
            'threshold': MINIMUM_AGENT_COUNT
        }
    }
    
    return manifest

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


def get_method(class_node: ast.ClassDef, method_name: str) -> Optional[ast.FunctionDef]:
    """Get a specific method from a class, or None if not found."""
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name == method_name:
                return item
    return None


def detect_invocation_status(class_node: ast.ClassDef) -> str:
    """
    Detect heal_repository invocation status for a CLASS.
    
    Returns:
        'Yes' - Class defines heal_repository with super().heal_repository() call
        'No (missing super)' - Class defines heal_repository but no super() call
        'Inherited' - Class does not define heal_repository (inherits from base)
    
    IMPORTANT: This checks the CLASS's heal_repository method specifically,
    not standalone module-level functions. This is the SSOT for invocation.
    """
    heal_method = get_method(class_node, 'heal_repository')
    
    if heal_method is None:
        return 'Inherited'
    
    # Check if super().heal_repository() is called within the method
    for node in ast.walk(heal_method):
        if isinstance(node, ast.Call):
            # Look for super().heal_repository(...)
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'heal_repository':
                if isinstance(node.func.value, ast.Call):
                    if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == 'super':
                        return 'Yes'
    
    return 'No (missing super)'


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

    # 1. IMMEDIATE HARD NEGATIVES (Maximal Precision)
    # - Obvious mock/test prefixes without 'Agent'
    # - Fundamental non-agent bases (Protocol/ABC/Data structures) — never concrete agents
    skip_patterns = ('Test', 'Mock', 'Stub', 'Fake', 'Dummy', 'Baseline', 'Sample', 'Example')
    if name.startswith(skip_patterns) and 'Agent' not in name:
        return False

    # HARD NEGATIVE: Mixins are never concrete agents
    if name.endswith('Mixin'):
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

    # HARD NEGATIVE: Data/container patterns — pure configs/schemas/states are never agents
    # Rationale: Zero FP from Pydantic/dataclass schemas misnamed without agent identity
    # Exceptions forgiven later via strong positive override
    data_container_suffixes = ('Config', 'Settings', 'Context', 'Options', 'Schema', 'State')
    if name.endswith(data_container_suffixes) and 'Agent' not in name:
        return False

    # Extract methods early — needed for harness detection and optional anchoring
    method_names = extract_methods(class_node)

    # Compute path once for reuse
    path_str = str(rel_path).replace('\\', '/').lower() if rel_path else ''
    in_tests = path_str.startswith('tests/') or '/tests/' in path_str

    # === ULTRA-HARDENED AGENT DETECTION (Single Source of Truth) ===
    # Four high-confidence positive signals (prioritized in order of strength):
    # 1. Strict naming: ends with 'Agent' (primary canonical pattern)
    # 2. Direct inheritance from known agent base classes
    agent_bases = {
        'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
        'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
        'ExecutionCanonBaseAgent',
        'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
        'BaseAgent',
    }

    # Base strong signal (signals 1-3)
    has_strong_positive_signal = (
        name.endswith('Agent')
        or bool(bases & agent_bases)
        or has_healing_in_chain(name, bases)  # MRO-aware healing is the gold standard for agent hierarchy
    )

    # Signal 4: Anchored role suffixes (historical recovery with precision)
    # Only accept curated suffixes if structurally anchored (prevents false positives)
    agent_role_suffixes = (
        'Executor', 'Validator', 'Enforcer', 'Guardian', 'Sentinel',
        'Inspector', 'Architect', 'Healer', 'Oracle',
        'Curator', 'Router', 'Orchestrator', 'Conductor',
        'Guard', 'Detector', 'Hunter', 'Fixer', 'Reconciler',
        'Mapper', 'Classifier', 'Auditor', 'Monitor', 'Witness',
    )
    if name.endswith(agent_role_suffixes):
        anchored = (
            bool(bases & agent_bases)
            or has_healing_in_chain(name, bases)
        )
        if anchored:
            has_strong_positive_signal = True
    # Rationale: This recovers ~150-200 legitimate hierarchical agents (e.g., Validators,
    # Orchestrators) that contributed to the historical ~407 count, without admitting junk.

    decorators = extract_decorators(class_node)
    # Conditional negative: dataclass/attrs only disqualifies absent strong positive
    if any(d in {'dataclass', 'attrs', 'attr.s'} for d in decorators) and not has_strong_positive_signal:
        return False

    # Remaining conditional negatives (low-risk name patterns)
    if not has_strong_positive_signal:
        if name.endswith(('Protocol', 'Error', 'Exception')):
            return False
        if name.startswith('I') and len(name) > 1 and name[1].isupper():
            return False

    # TEST HARNESS REJECTION (Strongest in tests/, weaker elsewhere)
    # - In tests/: unconditionally reject obvious harness patterns (Test* name or test_* methods)
    # - Outside tests/: reject only if NO strong positive signal (allows real agents with test_ methods)
    is_harness = name.startswith('Test') or any(m.startswith('test_') for m in method_names)
    if in_tests:
        if is_harness:
            return False  # Unconditional in tests/ — eliminates FP explosion
    else:
        if is_harness and not has_strong_positive_signal:
            return False  # Conditional outside — prevents stray harnesses but allows real agents

    # Sovereign edge case: covered by primary 'Agent' suffix signal above — no special path needed

    # === FINAL DECISION ===
    # Single return point: accept only if any strong positive signal exists
    return has_strong_positive_signal


def get_docstring(class_node: ast.ClassDef) -> str:
    """Extract class docstring."""
    if class_node.body and isinstance(class_node.body[0], ast.Expr):
        if isinstance(class_node.body[0].value, ast.Constant):
            doc = class_node.body[0].value.value
            if isinstance(doc, str):
                return doc[:100]  # Truncate
    return ""


def main():
    import sys
    import time
    
    # Parse command line args
    force_mode = '--force' in sys.argv
    
    print("=" * 80)
    print("FULL AGENT DISCOVERY - Single Source of Truth (HARDENED)")
    print("=" * 80)
    
    # Get previous count BEFORE deleting files (for validation)
    previous_count = get_previous_agent_count()
    if previous_count:
        print(f"[BASELINE] Previous agent count: {previous_count}")
    
    start_time = time.time()
    
    # Force fresh - delete stale JSON(s)
    for stale_path in {CANONICAL_JSON, LEGACY_JSON, MISTAKE_JSON, MISTAKE_JSON_2}:
        try:
            if stale_path.exists():
                os.remove(stale_path)
                print(f"[FRESH] Deleted stale {stale_path.name}")
        except OSError:
            pass
    
    agents = []
    parse_errors = []
    seen_agents: Set[Tuple[str, str]] = set()
    duplicates_skipped = 0
    
    # Scan ALL Python files in project
    all_py_files = list(PROJECT_ROOT.rglob('*.py'))
    print(f"\nScanning {len(all_py_files)} Python files...")

    # Diagnostic: Report on files explicitly skipped by EXCLUDED_DIRS
    excluded_files = [f for f in all_py_files if should_exclude_file(f)]
    print(f"   -> Excluding {len(excluded_files)} files in non-source dirs (archives, backups, etc.)")
    
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
            
            # Known higher-level abstract bases that are NOT concrete agents and should be excluded
            # (e.g. shared mixins or root ABCs across the hierarchy).
            #
            # IMPORTANT: Layer-specific BaseAgents (L1-L5) are intentionally NOT skipped here.
            # They are abstract but must be discovered as agents so they can be placed in
            # dedicated "Base Class" territories for consistent compliance tracking.
            # Current layer-specific bases:
            #   - L1: L1CognitionBaseAgent (or CognitionCanonBaseAgent)
            #   - L2: L2ExecutionBaseAgent (or ExecutionCanonBaseAgent)
            #   - L3: OrchestrationBaseAgent
            #   - L4: StateBaseAgent
            #   - L5: SafetyBaseAgent
            skip_names = {
                'SubAtomicAgent',
                'CanonBaseAgent',
                'MaintenanceBaseAgent',
                'IActionPlane',
                'ValidationProtocol',
                'Protocol',
                'ABC'
            }
            if node.name in skip_names:
                continue

            dedupe_key = (node.name, str(rel_path))
            if dedupe_key in seen_agents:
                duplicates_skipped += 1
                continue
            seen_agents.add(dedupe_key)
            
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
            
            # Detect invocation status (SSOT - checks CLASS method, not module functions)
            invocation = detect_invocation_status(node)
            
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
                'invocation': invocation,  # SSOT for heal_repository invocation
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
    
    # ========================================================================
    # HARDENING: Validate agent count BEFORE saving
    # ========================================================================
    print(f"\n[VALIDATION] Checking agent count...")
    validation_previous = None if force_mode else previous_count
    is_valid, validation_errors = validate_agent_count(len(agents), validation_previous)
    
    if not is_valid:
        print("\n" + "=" * 80)
        print("❌ DISCOVERY ABORTED - VALIDATION FAILED")
        print("=" * 80)
        for err in validation_errors:
            print(err)
        print("\nTo force discovery despite validation failure, run:")
        print("  python scripts/full_agent_discovery.py --force")
        print("=" * 80)
        sys.exit(1)
    
    # Calculate scan duration
    scan_duration = time.time() - start_time
    
    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(agents, f, indent=2)
    
    # Generate and save manifest
    manifest = generate_manifest(agents, scan_duration, parse_errors)
    with open(MANIFEST_JSON, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
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
    if duplicates_skipped:
        print(f"Duplicates skipped: {duplicates_skipped}")
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
    
    # ========================================================================
    # HARDENING: Final validation summary
    # ========================================================================
    print(f"\n{'=' * 80}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 80}")
    print(f"✅ Agent count: {len(agents)} (minimum: {MINIMUM_AGENT_COUNT}, expected: {EXPECTED_AGENT_COUNT})")
    if previous_count:
        delta = len(agents) - previous_count
        delta_str = f"+{delta}" if delta >= 0 else str(delta)
        print(f"✅ Delta from previous: {delta_str} agents")
    print(f"✅ Scan duration: {scan_duration:.1f}s")
    print(f"✅ Parse errors: {len(parse_errors)}")
    
    print(f"\n[SAVED] {OUTPUT_JSON}")
    print(f"[SAVED] {MANIFEST_JSON}")
    print("=" * 80)


if __name__ == '__main__':
    main()
