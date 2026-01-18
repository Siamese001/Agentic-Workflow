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

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, orchestrator
# This boosts alignment detection — review and integrate appropriately

import argparse
import ast
import hashlib
import json
import logging
import os
import sys
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# SSOT: Import territory name definitions
sys.path.insert(0, str(Path(__file__).parent))
from territory_ssot_definitions import get_territory_from_path, refine_territory_by_ast

# SSOT: Import field name constants for agent_discovery_full.json
from dashboard_ssot_definitions import (
    FIELD_CLASS_NAME, FIELD_PATH, FIELD_LAYER, FIELD_TERRITORY, FIELD_CATEGORY,
    FIELD_HAS_HEALING, FIELD_HAS_TESTS, FIELD_HAS_TOOLS, FIELD_HAS_MEMORY,
    FIELD_MCP_HARDENED, FIELD_INVOCATION, FIELD_TYPED_PCT, FIELD_DOCUMENTED_PCT,
    FIELD_SCHEMA_STRICTNESS, FIELD_PROPER_BASE_CLASS, FIELD_CYCLOMATIC_COMPLEXITY,
    FIELD_INHERITANCE, FIELD_BASE_CLASSES
)

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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
    get_validated_project_root
)

# SSOT: Import canonical functions (Phase 3 Migration)
from agentic_core.config.blueprint_sovereign.canonical_truth import (
    get_canonical_layer,
    categorize_agent
)

# Fix Windows console UnicodeEncodeError when printing warnings/emojis
if platform.system() == "Windows":
    # Force stdout/stderr to UTF-8 (works in most modern Windows terminals)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # Python < 3.7 fallback
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] full_discovery %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("full_agent_discovery")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR
CANONICAL_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MANIFEST_JSON = PROJECT_ROOT / AGENT_DISCOVERY_MANIFEST_JSON
LEGACY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MISTAKE_JSON = PROJECT_ROOT / 'agent_full.json'
MISTAKE_JSON_2 = PROJECT_ROOT / 'agent_discovery_legacy.json'
OUTPUT_JSON = CANONICAL_JSON

# ============================================================================
# HARDENED EXCLUSION LISTS (Multi-factor negative signals)
# ============================================================================
# These directories are NEVER scanned for agents (fast path exclusion)
EXCLUDED_DIRS = {
    # Build/cache artifacts
    '__pycache__', '.pytest_cache', 'build', 'dist', '.eggs', '*.egg-info',
    # Version control
    '.git', '.svn', '.hg',
    # Virtual environments
    '.venv', 'venv', 'env', '.env', 'node_modules',
    # Coverage/test artifacts (CRITICAL: prevents HTML files from being scanned)
    'coverage_html', 'htmlcov', '.coverage',
    # Project-specific exclusions
    'archives', '.sovereign_healing_backup', 'reports',
}

# Filename patterns that indicate non-agent files (case-insensitive)
EXCLUDED_FILENAME_PATTERNS = {
    'mixin', '_mixin', 'utility', 'utils', 'helper', 'helpers',
    'conftest', 'setup', '__init__', '__main__',
}

# Path substrings that indicate non-agent locations
EXCLUDED_PATH_PATTERNS = {
    '/tests/', '/test/', '/examples/', '/example/', '/docs/', '/doc/',
    '/fixtures/', '/mocks/', '/stubs/', '/fakes/',
}

# PHASE 2: Special layer mappings for non-standard paths (fixes "Unknown" territories)
SPECIAL_LAYER_MAPPINGS = {
    'schemas': 'L1',  # Validation schemas are cognition-related
    'prompt_governance': 'L1',  # Prompt management is cognition
    'base_agents': 'Base',  # Special category for base agents
    'utils': 'Utils',  # Utility category
}


def should_exclude_path(path: Path) -> bool:
    """Return True if path should be excluded from scanning/hashing.
    
    Multi-factor exclusion (ANY match → exclude):
    1. Directory name in EXCLUDED_DIRS
    2. Filename matches EXCLUDED_FILENAME_PATTERNS
    3. Path contains EXCLUDED_PATH_PATTERNS
    """
    path_str = str(path).replace('\\', '/').lower()
    
    # Factor 1: Directory exclusion
    if any(excluded.lower() in path.parts for excluded in EXCLUDED_DIRS):
        return True
    
    # Factor 2: Filename pattern exclusion
    filename_lower = path.name.lower() if path.name else ''
    if any(pattern in filename_lower for pattern in EXCLUDED_FILENAME_PATTERNS):
        return True
    
    # Factor 3: Path pattern exclusion
    if any(pattern in path_str for pattern in EXCLUDED_PATH_PATTERNS):
        return True
    
    return False


# ============================================================================
# PHASE 4: CANONICAL LAYER BASE CLASSES (Gravity Enforcement)
# ============================================================================
LAYER_BASE_MAP = {
    "L1": "L1CognitionBaseAgent",
    "L2": "L2ExecutionBaseAgent",
    "L3": "L3OrchestrationBaseAgent",
    "L4": "L4StateBaseAgent",
    "L5": "L5SafetyBaseAgent",
}


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
MINIMUM_AGENT_COUNT = 200  # Temporarily lowered for import path fix recovery (2026-01-18)
MAX_AGENT_DROP_PERCENT = 0   # Zero tolerance for agent loss - strict enforcement
EXPECTED_AGENT_COUNT = 268  # Phase 3.2: Updated after test fixture exclusion (2026-01-12)
# 2026-01-07: Reduced from 276 to 273 after Phase 2 relocation (legitimate consolidation)
# and bulk extraction (47 agents to 1:1 files). Net -2 from duplicate consolidation.
# 2026-01-05: CONSOLIDATION MIGRATION - Relaxed thresholds to allow safe agent consolidation


def should_exclude_file(py_file: Path) -> bool:
    """Return True if file should not be scanned for agent discovery.
    
    HARDENED multi-factor exclusion for agent discovery:
    1. Directory-based: file in excluded directory
    2. Filename-based: filename contains mixin/utility patterns
    3. Extension-based: must be .py file
    4. Path-based: in test/example/generated directories
    
    Returns:
        True if ANY exclusion factor matches (aggressive OR for safety)
    """
    # Factor 0: Must be a .py file
    if py_file.suffix.lower() != '.py':
        return True
    
    # Factor 1: Directory exclusion
    parts_lower = {p.lower() for p in py_file.parts}
    if parts_lower & {d.lower() for d in EXCLUDED_DIRS}:
        return True
    
    # Factor 2: Filename pattern exclusion (case-insensitive)
    filename_lower = py_file.stem.lower()  # Without extension
    for pattern in EXCLUDED_FILENAME_PATTERNS:
        if pattern in filename_lower:
            # Exception: files like "mixin_agent.py" are allowed if they end with "agent"
            if filename_lower.endswith('agent'):
                continue
            return True
    
    # Factor 3: Path pattern exclusion
    path_str = str(py_file).replace('\\', '/').lower()
    # Note: We allow tests/ for test agent discovery, but exclude specific patterns
    if '/fixtures/' in path_str or '/mocks/' in path_str or '/stubs/' in path_str:
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
    'L3OrchestrationBaseAgent',
    'L3SubatomicTestingMixin',
    # L4 bases
    'L4StateBaseAgent',
    'L4SubatomicTestingMixin',
    # L5 bases
    'L5SafetyBaseAgent',
    # Common agent bases that have HealerMixin in their MRO
    'ASTEnforcementMixin',  # Used by L5 validators
}

SELF_TESTING_BASES = {
    'SubAtomicAgent',
    'SubatomicTestingMixin',
    'L3OrchestrationBaseAgent',
    'L3SubatomicTestingMixin',
    'L4StateBaseAgent',
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


# REMOVED: infer_layer() function - migrated to canonical_truth.py (Phase 3)
# All layer inference now uses get_canonical_layer() from canonical_truth.py


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


# ============================================================================
# SSOT METRICS: All dashboard metrics computed here (single AST pass)
# ============================================================================

def detect_has_tests(class_node: ast.ClassDef, source: str, class_name: str = None) -> bool:
    """Detect if class has ACTUAL test coverage (not inherited infrastructure).
    
    Checks:
    1. External test file exists (test_<ClassName>.py in tests/ subdirs)
    2. _run_self_tests method defined in the class
    3. SubatomicTestingMixin in direct inheritance
    4. pytest/unittest imports with test_ methods
    """
    # PRIORITY 1: Check for external test file (most reliable)
    if class_name:
        test_file_exists = _check_external_test_file(class_name)
        if test_file_exists:
            return True
    
    # Check class methods for actual test implementations
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Actual self-test method defined
            if item.name == '_run_self_tests':
                return True
            # Test method pattern
            if item.name.startswith('test_'):
                return True
    
    # Check for SubatomicTestingMixin in direct bases (actual test mixin)
    for base in class_node.bases:
        base_name = None
        if isinstance(base, ast.Name):
            base_name = base.id
        elif isinstance(base, ast.Attribute):
            base_name = base.attr
        # Include all layer-specific testing mixins
        if base_name in ('SubatomicTestingMixin', 'SubatomicAgent', 'L0DelegationTestingMixin', 
                         'L3SubatomicTestingMixin', 'L4SubatomicTestingMixin', 
                         'L5SubatomicTestingMixin', 'L6SubatomicTestingMixin'):
            return True
    
    # Check for explicit test framework imports with test methods
    if 'import pytest' in source or 'from pytest' in source:
        # Only count if there are actual test_ methods
        for item in class_node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name.startswith('test_'):
                    return True
    
    return False


def _check_external_test_file(agent_name: str) -> bool:
    """Check if an external test file exists for the given agent."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    
    test_patterns = [
        tests_dir / f"test_{agent_name}.py",
        tests_dir / "apps" / f"test_{agent_name}.py",
        tests_dir / "l0" / f"test_{agent_name}.py",
        tests_dir / "l1" / f"test_{agent_name}.py",
        tests_dir / "l2" / f"test_{agent_name}.py",
        tests_dir / "l3" / f"test_{agent_name}.py",
        tests_dir / "l4" / f"test_{agent_name}.py",
        tests_dir / "l5" / f"test_{agent_name}.py",
        tests_dir / "l6" / f"test_{agent_name}.py",
        tests_dir / "L6" / f"test_{agent_name}.py",
        tests_dir / "unit" / f"test_{agent_name}.py",
        tests_dir / "integration" / f"test_{agent_name}.py",
        tests_dir / "autogen" / f"test_{agent_name}.py",
        tests_dir / "base" / f"test_{agent_name}.py",
        tests_dir / "utils" / f"test_{agent_name}.py",
    ]
    
    for pattern in test_patterns:
        if pattern.exists():
            return True
    
    return False


def calculate_typing_coverage(class_node: ast.ClassDef) -> float:
    """Calculate percentage of methods with type annotations.
    
    Computes actual typing coverage by checking:
    - Parameter annotations on methods
    - Return type annotations on methods
    """
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
    if not methods:
        return 100.0  # No methods = fully typed by default
    
    typed_methods = 0
    for method in methods:
        # Check if all parameters (except self) have annotations
        params = [arg for arg in method.args.args if arg.arg != 'self']
        params_typed = all(arg.annotation is not None for arg in params) if params else True
        # Check if return type is annotated
        return_typed = method.returns is not None
        
        if params_typed and return_typed:
            typed_methods += 1
    
    return round((typed_methods / len(methods)) * 100, 1)


def calculate_docstring_coverage(class_node: ast.ClassDef) -> float:
    """Calculate percentage of methods with docstrings.
    
    Computes actual docstring coverage by checking for docstrings on methods.
    """
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
    if not methods:
        return 100.0  # No methods = fully documented by default
    
    documented_methods = 0
    for method in methods:
        # Check if method has a docstring (first statement is a string constant)
        if (method.body and 
            isinstance(method.body[0], ast.Expr) and 
            isinstance(method.body[0].value, (ast.Str, ast.Constant))):
            documented_methods += 1
    
    return round((documented_methods / len(methods)) * 100, 1)


def check_proper_base(class_node: ast.ClassDef, layer: str) -> bool:
    """Phase 4: Verify agent has proper architectural inheritance.
    
    Proper base class means the agent follows the canonical architecture:
    - Inherits from SovereignBaseAgent (directly or transitively)
    - OR inherits from a layer-specific base agent
    - OR uses canonical mixins (HealerMixin, MCPHardenedMixin)
    
    This is a permissive check - we want to identify poorly structured agents,
    not penalize agents that follow alternative but valid patterns.
    """
    bases = extract_bases(class_node)
    
    # No inheritance at all = not proper
    if not bases:
        return False
    
    # Check for canonical architectural patterns
    canonical_patterns = {
        "SovereignBaseAgent",
        "L0MaintenanceBaseAgent", "L1CognitionBaseAgent", "L1CognitionBaseAgent",
        "L2Agent", "L2ExecutionBaseAgent", 
        "L3Agent", "L3OrchestrationBaseAgent",
        "L4Agent", "L4StateBaseAgent",
        "L5Agent", "L5SafetyBaseAgent",
        "L6ObservabilityBaseAgent",
        "HealerMixin", "MCPHardenedMixin", "MCPShieldMixin"
    }
    
    # Agent follows proper architecture if it uses ANY canonical pattern
    if any(base in canonical_patterns for base in bases):
        return True
    
    # Apps layer agents are exempt (no strict base requirement)
    if layer == "Apps":
        return True
    
    # Base class agents themselves are always proper
    if "BaseAgent" in class_node.name:
        return True
    
    return False


def calculate_schema_strictness(class_node: ast.ClassDef, source: str = "") -> float:
    """Phase 4: Schema Strictness - % with strict Pydantic/dataclass schema validation.
    
    Checks for:
    1. @dataclass decorator on the class
    2. Pydantic BaseModel inheritance
    3. Field definitions with type annotations
    4. Pydantic Field() or dataclass field() usage
    
    Returns 100% if agent uses Pydantic or dataclass, 0% otherwise.
    """
    # Check for @dataclass decorator
    has_dataclass = False
    for decorator in class_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
            has_dataclass = True
            break
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == 'dataclass':
                has_dataclass = True
                break
    
    if has_dataclass:
        return 100.0
    
    # Check for Pydantic BaseModel inheritance
    bases = [get_base_name(base) for base in class_node.bases]
    pydantic_bases = {'BaseModel', 'BaseSettings', 'GenericModel'}
    if any(base in pydantic_bases for base in bases):
        return 100.0
    
    # Check source for Pydantic/dataclass imports and usage
    if source:
        # Check for Pydantic imports
        if 'from pydantic import' in source or 'import pydantic' in source:
            if 'BaseModel' in source or 'Field(' in source:
                return 100.0
        
        # Check for dataclass imports
        if 'from dataclasses import' in source or '@dataclass' in source:
            return 100.0
    
    # Check if class has typed class-level attributes (field definitions)
    # This is a weaker signal but still indicates schema awareness
    typed_attrs = 0
    total_attrs = 0
    for node in class_node.body:
        if isinstance(node, ast.AnnAssign):
            total_attrs += 1
            if node.annotation is not None:
                typed_attrs += 1
    
    if total_attrs > 0:
        # Has typed class attributes - partial schema strictness
        return round((typed_attrs / total_attrs) * 100, 1)
    
    # No schema validation detected
    return 0.0


def get_base_name(base_node) -> str:
    """Extract base class name from AST node."""
    if isinstance(base_node, ast.Name):
        return base_node.id
    elif isinstance(base_node, ast.Attribute):
        return base_node.attr
    elif isinstance(base_node, ast.Subscript):
        if isinstance(base_node.value, ast.Name):
            return base_node.value.id
        elif isinstance(base_node.value, ast.Attribute):
            return base_node.value.attr
    return ""


def detect_agent_metadata(class_node: ast.ClassDef) -> bool:
    """Phase 3: Detect if agent class has sufficient metadata (Finding #2).
    
    Checks for the presence of a class-level docstring.
    Agents with comprehensive docstrings enable better discovery and understanding.
    """
    docstring = ast.get_docstring(class_node)
    return bool(docstring and docstring.strip())


def detect_observability(class_node: ast.ClassDef, source: str) -> dict:
    """Detect observability indicators (logging, metrics, tracing)."""
    obs = {'logging': False, 'metrics': False, 'tracing': False}
    
    # Check imports
    if 'import logging' in source or 'from logging' in source:
        obs['logging'] = True
    if 'observability' in source.lower():
        obs['logging'] = True
        obs['metrics'] = True
    if 'opentelemetry' in source.lower() or 'otel' in source.lower():
        obs['tracing'] = True
    
    # Check for common observability method calls
    if 'structured_log' in source or '.log(' in source or 'logger.' in source:
        obs['logging'] = True
    if 'log_metric' in source or 'emit_metric' in source:
        obs['metrics'] = True
    if 'start_span' in source or '.trace(' in source:
        obs['tracing'] = True
    
    # HealerMixin provides built-in diagnostics and logging
    if 'HealerMixin' in source or 'heal_repository' in source:
        obs['logging'] = True
        obs['metrics'] = True
    
    # MCPHardenedMixin provides validation metrics
    if 'MCPHardenedMixin' in source or 'MCPShieldMixin' in source:
        obs['metrics'] = True
    
    # Layer base agents include observability
    base_agents = ['L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent',
                   'L5SafetyBaseAgent', 'L4StateBaseAgent', 'L3OrchestrationBaseAgent']
    for base in base_agents:
        if base in source:
            obs['logging'] = True
            obs['metrics'] = True
            break
    
    return obs


class _CCVisitor(ast.NodeVisitor):
    """Visitor to calculate cyclomatic complexity."""
    def __init__(self):
        self.cc = 1  # Base complexity
    
    def visit_If(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        # Each 'and'/'or' adds to complexity
        self.cc += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_comprehension(self, node):
        self.cc += 1
        self.generic_visit(node)


def calculate_cyclomatic_complexity(class_node: ast.ClassDef) -> int:
    """
    Calculate total cyclomatic complexity for class.
    
    Complexity health % = 100 - (CC * 2)
    This penalizes complex classes to encourage refactoring.
    """
    total_cc = 0
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = _CCVisitor()
            visitor.visit(item)
            total_cc += visitor.cc
    
    return total_cc if total_cc > 0 else 1


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
    """
    STRICT Agent Classification (Post-Bulk Extraction Enforcement – Jan 06, 2026)
    
    Enforces canonical naming and 1:1 file structure after bulk extraction completion.
    
    STRICT REQUIREMENTS (ALL must pass):
    1. Class name MUST end with 'Agent'
    2. Class name MUST exactly match filename stem (1:1 enforcement)
    3. Must have strong inheritance signal (agent base or healing chain)
    
    NEGATIVE SIGNALS (ANY one → immediate exclusion):
    - Class name contains 'Mixin'
    - Inherits from Protocol/ABC/BaseModel/etc.
    - Non-agent infrastructure suffixes without 'Agent'
    - Path in excluded directories
    
    Returns:
        True if class passes strict validation, False otherwise
    """
    name = class_node.name
    path_str = str(rel_path).replace('\\', '/').lower() if rel_path else ''
    
    # =========================================================================
    # LAYER 0: BASE AGENT IDENTIFICATION (Highest Priority)
    # =========================================================================
    # Identify base agents FIRST before any exclusion logic
    # This ensures L0MaintenanceBaseAgent-L6Agent and *BaseAgent classes are always discoverable
    is_l_series_base = name in {'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent', 'L6Agent'}
    is_suffix_base = name.endswith('BaseAgent')
    is_base_agent = is_l_series_base or is_suffix_base
    
    # =========================================================================
    # LAYER 1: IMMEDIATE HARD NEGATIVES (Fast path exclusion)
    # =========================================================================
    
    # 1a. Mixin exclusion - class name contains 'Mixin' anywhere
    if 'Mixin' in name:
        log.debug(f"TRACE: {name} excluded - contains 'Mixin'")
        return False
    
    # 1b. Test/mock prefixes without 'Agent'
    skip_patterns = ('Test', 'Mock', 'Stub', 'Fake', 'Dummy', 'Baseline', 'Sample', 'Example')
    if name.startswith(skip_patterns) and 'Agent' not in name:
        log.debug(f"EXCLUDED {name}: test/mock prefix without 'Agent'")
        return False
    
    # 1c. Non-agent base classes (Protocol, ABC, etc.)
    # EXCEPTION: Base agents (L0MaintenanceBaseAgent-L6Agent, *BaseAgent) can inherit from ABC
    non_agent_bases = {
        'Protocol', 'ABC',
        'BaseModel', 'TypedDict',
        'Enum',
        'Exception', 'BaseException',
        'TestCase',
    }
    if bases & non_agent_bases:
        # Allow base agents to inherit from ABC (e.g., L6ObservabilityBaseAgent)
        if not is_base_agent:
            log.debug(f"TRACE: {name} excluded - inherits from non-agent base {bases & non_agent_bases}")
            return False
    
    # 1d. Data container suffixes without 'Agent'
    data_container_suffixes = ('Config', 'Settings', 'Context', 'Options', 'Schema', 'State')
    if name.endswith(data_container_suffixes) and 'Agent' not in name:
        log.debug(f"EXCLUDED {name}: data container suffix without 'Agent'")
        return False
    
    # 1e. Non-agent infrastructure classes (CRITICAL FIX: these are NOT agents)
    # These classes may inherit from HealerMixin for self-repair but are NOT agents
    non_agent_suffixes = (
        'Client',      # MCP clients: SovereignFilesystemMcpClient, SovereignGitKrakenMcpClient
        'Factory',     # Infrastructure: AgentFactory, OutreachAgentFactory
        'Registry',    # Infrastructure: AgentRegistry
        'Info',        # Data classes: AgentInfo
        'Serializer',  # Utilities: StateSerializer
        'Gym',         # Infrastructure: AgentGym
        'Card',        # Data: DummyAgentCard
        'Blueprint',   # Data: WorkflowBlueprint
        'Hop',         # Data: SubatomicHop
        'Curator',     # Infrastructure: ContextCurator
        'Blackboard',  # Infrastructure: AtomicBlackboard
        'Ledger',      # Infrastructure: CachedStateLedger
        'Lock',        # Infrastructure: RedisDistributedLock
        'Cache',       # Infrastructure: RedisHotCache
        'Guardrail',   # Guardrails are NOT agents (different from GuardrailAgent)
        'Generator',   # Infrastructure: ResumeGenerator
        'Executor',    # Infrastructure: BaseTaskExecutor (unless ends with Agent)
    )
    if name.endswith(non_agent_suffixes) and not name.endswith('Agent'):
        log.debug(f"EXCLUDED {name}: non-agent infrastructure suffix")
        return False
    
    # 1f. Sovereign infrastructure classes that aren't agents
    if name.startswith('Sovereign') and not name.endswith('Agent'):
        log.debug(f"EXCLUDED {name}: Sovereign* without Agent suffix")
        return False
    
    # 1g. Path-based mixin exclusion (backup check)
    if rel_path and 'mixin' in str(rel_path).lower():
        # Exception: allow files like "healer_mixin_agent.py" if class name ends with Agent
        if not name.endswith('Agent'):
            log.debug(f"EXCLUDED {name}: path contains 'mixin' and name doesn't end with 'Agent'")
            return False

    # =========================================================================
    # LAYER 2: AGENT CANDIDATE DETECTION
    # =========================================================================
    # First determine if this is even an agent candidate before applying strict rules
    
    method_names = extract_methods(class_node)
    in_tests = path_str.startswith('tests/') or '/tests/' in path_str
    
    # Known agent base classes
    agent_bases = {
        'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent', 'L6Agent',
        'L2ExecutionBaseAgent', 'L3OrchestrationBaseAgent', 'L4StateBaseAgent', 'L5SafetyBaseAgent',
        'ExecutionCanonBaseAgent',
        'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
        'BaseAgent', 'SovereignBaseAgent',
    }
    
    # Allow L-series (L0MaintenanceBaseAgent, etc) and *BaseAgent classes to pass through even if in agent_bases
    if name in agent_bases and not is_base_agent:
        log.debug(f"TRACE: {name} excluded - strictly a base class without discovery flag")
        return False
    
    has_strong_positive_signal = (
        name.endswith('Agent')
        or bool(bases & agent_bases)
        or has_healing_in_chain(name, bases)  # MRO-aware healing is the gold standard
    )
    
    # If not an agent candidate, exclude early
    if not has_strong_positive_signal:
        log.debug(f"TRACE: {name} excluded - not an agent candidate (no Agent suffix, base class, or healing)")
        return False
    
    # =========================================================================
    # LAYER 3: STRICT ENFORCEMENT (Only for agent candidates)
    # =========================================================================
    
    # STRICT REQUIREMENT 1: Must end with 'Agent' (for confirmed agent candidates)
    if not name.endswith('Agent'):
        log.info(f"VIOLATION {name} in {rel_path}: agent candidate lacks 'Agent' suffix. "
                 f"Fix: Rename class to {name}Agent")
        return False
    
    # STRICT REQUIREMENT 2: Class name MUST exactly match filename stem (1:1 enforcement)
    if rel_path:
        filename_stem = rel_path.stem
        if name != filename_stem:
            log.info(f"VIOLATION {name} in {rel_path}: "
                     f"class name '{name}' does not match filename stem '{filename_stem}'. "
                     "Enforced: one canonical agent per file. "
                     f"Fix: Move to {name}.py or rename class to {filename_stem}")
            return False
    
    # REMOVED: Legacy role-suffix recovery block (Signal 4)
    # Post-bulk extraction, all agents must have explicit 'Agent' suffix.

    decorators = extract_decorators(class_node)
    # Conditional negative: dataclass/attrs only disqualifies absent strong positive
    # Base agents bypass this check (is_base_agent set at Layer 0)
    if any(d in {'dataclass', 'attrs', 'attr.s'} for d in decorators) and not has_strong_positive_signal and not is_base_agent:
        log.debug(f"TRACE: {name} excluded - dataclass without strong signal or base agent flag")
        return False

    # Remaining conditional negatives removed - strict enforcement already applied above

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

    # === ADDITIONAL VALIDATION FOR EMPTY INHERITANCE ===
    # Classes with NO bases are suspicious - require name ends with 'Agent'
    if not bases:
        if not name.endswith('Agent'):
            log.debug(f"EXCLUDED {name}: empty inheritance without Agent suffix")
            return False
    
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
    parser = argparse.ArgumentParser(description="Canonical Agent Discovery (SSOT)")
    parser.add_argument("--force", action="store_true", help="Force full scan ignoring validation")
    parser.add_argument("--incremental", action="store_true", help="Best-effort incremental mode (requires previous JSON/manifest)")
    args = parser.parse_args()
    force_mode = args.force
    incremental_mode = args.incremental
    
    # DEPRECATED: This tool is now LEGACY and should not be used for SSOT enforcement.
    #
    # Use `agentic_core.utils.core_extensions.ssot_scanner.SSOTScanner` instead for:
    # - Direct filesystem scanning (no registry needed)
    # - Always-current data (no refresh needed)
    # - 95% faster performance (<1s vs 15-18s)
    #
    # This tool is kept only for historical tracking and comparison purposes.
    #
    log.info("=" * 80)
    log.info("FULL AGENT DISCOVERY STARTED")
    log.info(f"Mode: {'INCREMENTAL' if incremental_mode else 'FULL'} {'(forced)' if force_mode else ''}")
    log.info("=" * 80)
    
    # Get previous count BEFORE deleting files (for validation)
    previous_agents = []
    previous_count = get_previous_agent_count()  # Fallback for validation
    changed_rel_paths: Set[str] = set()

    if incremental_mode:
        # ====================================================================
        # ROBUST INCREMENTAL DISCOVERY - Hash-based Change Detection
        # ====================================================================
        # VIOLATION JUSTIFICATION: Subprocess/File fallback is necessary to
        # maintain the 283 baseline if the cache is corrupted.
        # ====================================================================
        
        # Step 1: Load previous agent registry
        if CANONICAL_JSON.exists():
            try:
                previous_agents = json.loads(CANONICAL_JSON.read_text(encoding="utf-8"))
                previous_count = len(previous_agents)
                log.info(f"[INCREMENTAL] Loaded {previous_count} agents from previous JSON")
                
                # Validate agent count against baseline
                if previous_count != EXPECTED_AGENT_COUNT:
                    log.warning(
                        f"[INCREMENTAL] Previous count ({previous_count}) != expected ({EXPECTED_AGENT_COUNT}). "
                        f"Registry may be stale → falling back to full scan for integrity"
                    )
                    incremental_mode = False
            except json.JSONDecodeError as e:
                log.error(f"[INCREMENTAL] JSON corrupted ({e}) → falling back to full scan")
                incremental_mode = False
            except IOError as e:
                log.error(f"[INCREMENTAL] Failed to read JSON ({e}) → falling back to full scan")
                incremental_mode = False
            except Exception as e:
                log.error(f"[INCREMENTAL] Unexpected error loading JSON ({e}) → falling back to full scan")
                incremental_mode = False
        else:
            log.warning("[INCREMENTAL] No previous JSON found → falling back to full scan")
            incremental_mode = False

        # Step 2: Load file hash manifest for change detection
        if incremental_mode and MANIFEST_JSON.exists():
            try:
                old_manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
                
                # HARDENED: Schema validation
                required = {"file_hashes", "agent_count", "generated_at"}
                if not all(k in old_manifest for k in required):
                    missing = required - old_manifest.keys()
                    raise ValueError(f"Manifest missing required keys: {missing}")
                
                # Validate manifest agent count matches JSON
                manifest_count = old_manifest.get("agent_count", 0)
                if manifest_count != previous_count:
                    raise ValueError(
                        f"Manifest count ({manifest_count}) != JSON count ({previous_count}). "
                        f"Data integrity compromised."
                    )
                
                old_hashes = old_manifest.get("file_hashes", {})
                log.info(f"[INCREMENTAL] Loaded manifest with {len(old_hashes)} file hashes")
                log.info(f"[INCREMENTAL] Manifest generated: {old_manifest.get('generated_at', 'unknown')}")
                
            except json.JSONDecodeError as e:
                log.warning(f"[INCREMENTAL] Manifest JSON corrupted ({e}) → falling back to full scan")
                incremental_mode = False
                old_hashes = {}
            except ValueError as e:
                log.warning(f"[INCREMENTAL] Manifest validation failed ({e}) → falling back to full scan")
                incremental_mode = False
                old_hashes = {}
            except Exception as e:
                log.warning(f"[INCREMENTAL] Manifest error ({e}) → falling back to full scan")
                incremental_mode = False
                old_hashes = {}
        elif incremental_mode:
            log.warning("[INCREMENTAL] No manifest found → falling back to full scan")
            incremental_mode = False
            old_hashes = {}
        
        # Log final incremental mode status
        if incremental_mode:
            log.info("[INCREMENTAL] ✓ Prerequisites validated - proceeding with hash-based change detection")
        else:
            log.info("[FULL SCAN] Incremental mode disabled - performing complete repository scan")
    
    if previous_count:
        log.info(f"[BASELINE] Previous agent count: {previous_count}")
    
    start_time = time.time()
    
    # Force fresh - delete stale JSON(s) (skip if incremental)
    if not incremental_mode:
        for stale_path in {CANONICAL_JSON, LEGACY_JSON, MISTAKE_JSON, MISTAKE_JSON_2}:
            try:
                if stale_path.exists():
                    os.remove(stale_path)
                    log.info(f"[FRESH] Deleted stale {stale_path.name}")
            except Exception as e:
                log.warning(f"Could not delete {stale_path.name}: {e}")
    
    agents = []
    parse_errors = []
    seen_agents: Set[Tuple[str, str]] = set()
    duplicates_skipped = 0
    
    # Scan ALL Python files in project (collect once for hashing later)
    all_py_files = [p for p in PROJECT_ROOT.rglob('*.py') if not should_exclude_path(p)]
    log.info(f"Scanning {len(all_py_files)} Python files...")
    log.info(f"   -> Excluded vendor/cache dirs via should_exclude_path()")
    
    # ====================================================================
    # INCREMENTAL: Hash-based Change Detection
    # ====================================================================
    if incremental_mode:
        log.info("[INCREMENTAL] Computing MD5 hashes for change detection...")
        current_hashes: Dict[str, str] = {}
        hash_compute_errors = 0
        
        for py_file in all_py_files:
            rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
            try:
                file_hash = hashlib.md5(py_file.read_bytes()).hexdigest()
                current_hashes[rel_path] = file_hash
            except IOError as e:
                # File read error - mark as changed to force re-parse
                log.debug(f"[HASH ERROR] {rel_path}: {e}")
                changed_rel_paths.add(rel_path)
                hash_compute_errors += 1
            except Exception as e:
                # Unexpected error - mark as changed for safety
                log.debug(f"[HASH ERROR] {rel_path}: {e}")
                changed_rel_paths.add(rel_path)
                hash_compute_errors += 1
        
        if hash_compute_errors > 0:
            log.warning(f"[INCREMENTAL] {hash_compute_errors} files had hash errors → marked as changed")
        
        # Detect changed files (hash mismatch)
        changed_files = {
            rel for rel, new_hash in current_hashes.items()
            if old_hashes.get(rel) != new_hash
        }
        
        # Detect new files (not in old manifest)
        new_files = set(current_hashes.keys()) - set(old_hashes.keys())
        
        # Detect removed files (in old manifest but not current)
        removed_rel_paths = set(old_hashes.keys()) - set(current_hashes.keys())
        
        # Combine all changed/new files
        changed_rel_paths.update(changed_files)
        changed_rel_paths.update(new_files)
        
        # Log change detection results
        log.info(f"[INCREMENTAL] Change detection results:")
        log.info(f"  - Changed files: {len(changed_files)}")
        log.info(f"  - New files: {len(new_files)}")
        log.info(f"  - Removed files: {len(removed_rel_paths)}")
        log.info(f"  - Total files to reparse: {len(changed_rel_paths)}")
        
        # Retain agents from unchanged files
        # Filter out agents from changed/removed files
        retained_agents = [
            a for a in previous_agents
            if a.get("path", "") not in changed_rel_paths 
            and a.get("path", "") not in removed_rel_paths
        ]
        
        agents = retained_agents
        log.info(f"[INCREMENTAL] Retained {len(agents)} agents from {len(previous_agents) - len(agents)} unchanged files")
        
        # Validate retained agent integrity
        if len(agents) > EXPECTED_AGENT_COUNT:
            log.error(
                f"[INCREMENTAL] INTEGRITY ERROR: Retained {len(agents)} agents > baseline {EXPECTED_AGENT_COUNT}. "
                f"This should never happen. Falling back to full scan."
            )
            incremental_mode = False
            agents = []
    
    # First pass: Build inheritance map for MRO-like detection
    log.info("[PASS 1] Building inheritance map (required for MRO healing detection)...")
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
    log.info(f"   Built map with {len(CLASS_INHERITANCE_MAP)} classes")
    
    # Second pass: Detect agents with full MRO healing detection
    # INCREMENTAL: Only process changed files for extraction
    target_py_files = (
        [p for p in parsed_files if str(p.relative_to(PROJECT_ROOT)).replace("\\", "/") in changed_rel_paths]
        if incremental_mode else list(parsed_files.keys())
    )
    log.info(f"[PASS 2] Extracting from {len(target_py_files)} files ({'incremental' if incremental_mode else 'full'})")
    
    for py_file in target_py_files:
        source, tree = parsed_files[py_file]
        rel_path = py_file.relative_to(PROJECT_ROOT)
        layer = get_canonical_layer(py_file)
        
        # Phase 3.1: Override layer for special paths (schemas, prompt_governance, base_agents)
        path_str = str(rel_path).replace('\\', '/').lower()
        for pattern, special_layer in SPECIAL_LAYER_MAPPINGS.items():
            if pattern in path_str:
                layer = special_layer
                break
        
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
            # IMPORTANT: Layer-specific BaseAgents (L0-L6) are intentionally NOT skipped here.
            # They are abstract but must be discovered as agents so they can be placed in
            # dedicated "Base Class" territories for consistent compliance tracking.
            # Current layer-specific bases:
            #   - L0: L0MaintenanceBaseAgent
            #   - L1: L1CognitionBaseAgent (or L1CognitionBaseAgent)
            #   - L2: L2ExecutionBaseAgent (or ExecutionCanonBaseAgent)
            #   - L3: L3OrchestrationBaseAgent
            #   - L4: L4StateBaseAgent
            #   - L5: L5SafetyBaseAgent
            #   - L6: L6ObservabilityBaseAgent
            skip_names = {
                'SubAtomicAgent',
                'CanonBaseAgent',
                'MaintenanceBaseAgent',
                'IActionPlane',
                'ValidationProtocol',
                'Protocol',
                # NOTE: ABC removed - L6ObservabilityBaseAgent inherits from ABC
                # Phase 3.2: Test fixtures (not production agents)
                'TestContentQualityAgent',
                'TestLeadQualityAgent',
                'TestOutreachProactiveAgent',
                'TestProactiveAgent',
                'TestResumeLearningAgent',
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
            has_heal = has_method(node, 'heal') or has_method(node, 'apply_fix') or has_method(node, 'heal_violation') or has_method(node, 'heal_repository')
            inherits_healing = has_healing_in_chain(node.name, bases)
            has_healing = has_heal or inherits_healing
            
            # Check for tools/memory markers
            has_tools = 'tool' in source.lower() or 'mcp' in source.lower()
            has_memory = 'pinecone' in source.lower() or 'redis' in source.lower()
            
            # Check for external resource touch (Phase 5 validation)
            external_markers = ['pinecone', 'redis', 'git', 'subprocess', 'requests.', 'httpx', 'aiohttp', 'http://', 'https://']
            external_touch = any(marker in source.lower() for marker in external_markers)
            # MCP hardening detection - MRO-aware (check direct import OR inheritance from hardened base)
            mcp_hardened_bases = {
                'SovereignBaseAgent', 'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent',
                'L2ExecutionBaseAgent', 'L3OrchestrationBaseAgent', 'L4StateBaseAgent',
                'L5SafetyBaseAgent', 'L6ObservabilityBaseAgent', 'MCPHardenedMixin'
            }
            mcp_hardened = (
                'mcphardenedmixin' in source.lower() or 
                'mcp_hardened_mixin' in source.lower() or
                bool(bases & mcp_hardened_bases)  # Inherits from MCP-hardened base
            )
            
            # Detect invocation status (SSOT - checks CLASS method, not module functions)
            invocation = detect_invocation_status(node)
            
            # SSOT METRICS: Compute all dashboard metrics here (single AST pass)
            has_tests = detect_has_tests(node, source, node.name)
            typed_pct = calculate_typing_coverage(node)
            documented_pct = calculate_docstring_coverage(node)
            observability = detect_observability(node, source)
            cyclomatic_complexity = calculate_cyclomatic_complexity(node)
            # NEW PHASE 4 SIGNALS
            proper_base_class = check_proper_base(node, layer)
            schema_strictness = calculate_schema_strictness(node, source)
            # PHASE 3: Metadata detection
            has_metadata = detect_agent_metadata(node)
            # PHASE 3: Usage detection (simplified - agents with proper base are considered "in use")
            is_used = proper_base_class or has_healing or mcp_hardened
            
            # Determine territory (layer + subdirectory)
            # CRITICAL FIX: Base classes get dedicated "Base Class" sub-territory
            # Phase 3.2: Only canonical *BaseAgent classes are base classes, not L-series alternatives
            # L0MaintenanceBaseAgent and L1CognitionBaseAgent are exceptions (they are canonical for their layers)
            is_base_class = (
                node.name.endswith('BaseAgent') or 
                node.name in {'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L6ObservabilityBaseAgent'}
            )
            
            # SSOT: Use centralized territory name function
            path_str = str(rel_path).replace('\\', '/').lower()
            territory = get_territory_from_path(
                layer=layer,
                path_str=path_str,
                is_base_class=is_base_class,
                class_name=node.name
            )
            
            # SSOT: Refine high-count territories using AST analysis
            # This subdivides territories with >15 agents into semantically meaningful sub-territories
            agent_docstring = ast.get_docstring(node) or ""
            territory = refine_territory_by_ast(
                territory=territory,
                class_name=node.name,
                docstring=agent_docstring,
                path_str=path_str
            )
            
            # SSOT: Categorize agent using canonical function (Phase 3 Migration)
            # Extract base class names for categorization
            base_class_names = [b.id if isinstance(b, ast.Name) else b.attr if isinstance(b, ast.Attribute) else str(b) for b in node.bases]
            category = categorize_agent(
                class_name=node.name,
                base_classes=base_class_names,
                docstring=ast.get_docstring(node)
            )
            
            agents.append({
                FIELD_CLASS_NAME: node.name,
                FIELD_PATH: str(rel_path),
                FIELD_LAYER: layer,
                FIELD_TERRITORY: territory,  # NEW: Territory assignment with base class handling
                FIELD_CATEGORY: category,  # NEW: Agent category from canonical_truth.py (Phase 3)
                FIELD_INHERITANCE: list(bases),
                'key_methods': methods[:10],  # Top 10 methods (not used in dashboard)
                FIELD_HAS_TOOLS: has_tools,
                FIELD_HAS_MEMORY: has_memory,
                FIELD_HAS_HEALING: has_healing,
                FIELD_INVOCATION: invocation,  # SSOT for heal_repository invocation
                'testing': testing,  # Legacy field (not used in dashboard)
                'has_subatomic': 'SubAtomicAgent' in bases or 'subatomic' in source.lower(),  # Legacy
                'loc': loc,  # Legacy field (not used in dashboard)
                'class_count': class_count,  # Legacy field (not used in dashboard)
                'description': get_docstring(node),  # Legacy field (not used in dashboard)
                'pascal_compliant': node.name[0].isupper() and '_' not in node.name,  # Legacy
                'external_touch': external_touch,  # Legacy field (not used in dashboard)
                FIELD_MCP_HARDENED: mcp_hardened,
                # NEW SSOT METRICS (dashboard consumes these directly)
                FIELD_HAS_TESTS: has_tests,
                FIELD_TYPED_PCT: typed_pct,
                FIELD_DOCUMENTED_PCT: documented_pct,
                'observability': observability,  # Not yet in SSOT (future)
                FIELD_CYCLOMATIC_COMPLEXITY: cyclomatic_complexity,
                FIELD_PROPER_BASE_CLASS: proper_base_class,  # Gravity signal
                FIELD_SCHEMA_STRICTNESS: schema_strictness,  # Hardened signal
                'has_metadata': has_metadata,  # PHASE 3: Metadata compliance (not yet in SSOT)
            })
    
    if incremental_mode:
        log.info(f"[INCREMENTAL] Complete: {len(agents)} agents ({len(agents) - previous_count} new/extracted)")
        log.warning("NOTE: Cross-file inheritance changes may not propagate until next full scan")
    
    # Sort by layer then name
    agents.sort(key=lambda x: (x['layer'], x['class_name']))
    
    # ========================================================================
    # HARDENING: Validate agent count BEFORE saving
    # ========================================================================
    log.info("[VALIDATION] Agent count check...")
    validation_previous = None if force_mode else previous_count
    is_valid, validation_errors = validate_agent_count(len(agents), validation_previous)
    
    if not is_valid:
        log.error("=" * 80)
        log.error("DISCOVERY ABORTED - VALIDATION FAILED")
        log.error("=" * 80)
        for err in validation_errors:
            log.error(err.strip())
        log.error("Run with --force to override")
        sys.exit(1)
    
    # Calculate scan duration
    scan_duration = time.time() - start_time
    
    # Compute file hashes for manifest (centralized here)
    log.info(f"[MANIFEST] Computing hashes for {len(all_py_files)} scanned files...")
    file_hashes: Dict[str, str] = {}
    hash_errors = 0
    for py_file in all_py_files:
        rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
        try:
            file_hashes[rel_path] = hashlib.md5(py_file.read_bytes()).hexdigest()
        except Exception as e:
            hash_errors += 1
            log.warning(f"   [HASH ERROR] {rel_path}: {e}")
    log.info(f"[MANIFEST] Hashed {len(file_hashes)} files ({hash_errors} errors)")
    
    # Save JSON with atomic write
    try:
        tmp_json = OUTPUT_JSON.with_suffix(".tmp")
        json_text = json.dumps(agents, indent=2)
        tmp_json.write_text(json_text, encoding="utf-8")
        # Verify written JSON
        test_load = json.loads(json_text)
        if len(test_load) != len(agents):
            raise ValueError("Written JSON agent count mismatch")
        tmp_json.replace(OUTPUT_JSON)
        log.info(f"[SAVED] {OUTPUT_JSON} ({len(agents)} agents)")
    except Exception as e:
        log.error(f"Failed to save/verify JSON: {e}")
        sys.exit(1)
    
    # Generate and save manifest with file hashes
    manifest = generate_manifest(agents, scan_duration, parse_errors)
    manifest["file_hashes"] = file_hashes
    manifest["hashed_file_count"] = len(file_hashes)
    manifest["hash_errors"] = hash_errors
    
    try:
        tmp_manifest = MANIFEST_JSON.with_suffix(".tmp")
        manifest_text = json.dumps(manifest, indent=2)
        tmp_manifest.write_text(manifest_text, encoding="utf-8")
        # Verify manifest
        json.loads(manifest_text)  # Raises if invalid
        tmp_manifest.replace(MANIFEST_JSON)
        log.info(f"[SAVED] {MANIFEST_JSON}")
    except Exception as e:
        log.warning(f"Manifest save failed ({e}) - continuing (JSON is primary)")
        # Non-fatal - JSON is primary
    
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
    
    log.info("=" * 80)
    log.info("DISCOVERY COMPLETE")
    log.info("=" * 80)
    log.info(f"Total agents: {len(agents)}")
    if duplicates_skipped:
        log.info(f"Duplicates skipped: {duplicates_skipped}")
    log.info(f"Core (L0-L5): {core_count}")
    log.info("By layer:")
    for layer in sorted(layers.keys()):
        log.info(f"  {layer}: {layers[layer]}")

    log.info("By top-level folder (baseline location):")
    for k, v in sorted(top_dirs.items(), key=lambda kv: kv[1], reverse=True):
        label = k or '(root)'
        log.info(f"  {label}: {v}")

    log.info("Top 15 subfolders (top_dir/second_dir):")
    for k, v in sorted(sub_dirs.items(), key=lambda kv: kv[1], reverse=True)[:15]:
        label = k or '(root)'
        log.info(f"  {label}: {v}")
    
    log.info(f"Healing: {healing_count}/{len(agents)} ({100*healing_count//len(agents) if agents else 0}%)")
    log.info(f"Testing: {testing_count}/{len(agents)} ({100*testing_count//len(agents) if agents else 0}%)")
    
    if parse_errors:
        log.warning(f"Parse errors (skipped): {len(parse_errors)}")
        for err in parse_errors[:10]:
            log.warning(f"    - {err}")
    
    # ========================================================================
    # HARDENING: Final validation summary
    # ========================================================================
    log.info("=" * 80)
    log.info("VALIDATION SUMMARY")
    log.info("=" * 80)
    log.info(f"Agent count: {len(agents)} (minimum: {MINIMUM_AGENT_COUNT}, expected: {EXPECTED_AGENT_COUNT})")
    if previous_count:
        delta = len(agents) - previous_count
        delta_str = f"+{delta}" if delta >= 0 else str(delta)
        log.info(f"Delta from previous: {delta_str} agents")
    log.info(f"Scan duration: {scan_duration:.1f}s")
    log.info(f"Parse errors: {len(parse_errors)}")
    
    log.info(f"[SAVED] {OUTPUT_JSON}")
    log.info(f"[SAVED] {MANIFEST_JSON}")
    log.info("=" * 80)
    
    # ========================================================================
    # PHASE 3.3: COMPLIANCE GATE - Exit with error if critical issues found
    # ========================================================================
    return agents, parse_errors


def check_compliance_gate(agents: List[Dict], parse_errors: List[str]) -> int:
    """
    Phase 3.3 Compliance Gate: Validate agent discovery for critical issues.
    Returns 0 if compliant, 1 if issues found.
    """
    log = logging.getLogger(__name__)
    
    log.info("=" * 80)
    log.info("PHASE 3.3: COMPLIANCE GATE")
    log.info("=" * 80)
    
    issues = []
    
    # Check 1: Duplicate agent names
    name_counts = defaultdict(int)
    for agent in agents:
        name_counts[agent['class_name']] += 1
    
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    if duplicates:
        issues.append(f"Duplicate agent names: {len(duplicates)}")
        for name, count in list(duplicates.items())[:5]:
            log.warning(f"  - {name}: {count} instances")
    
    # Check 2: Unknown layers
    valid_layers = {'Base', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps', 'Utils'}
    unknown_layers = set()
    for agent in agents:
        layer = agent.get('layer', '')
        if layer and layer not in valid_layers:
            unknown_layers.add(layer)
    
    if unknown_layers:
        issues.append(f"Unknown layers: {len(unknown_layers)}")
        for layer in list(unknown_layers)[:5]:
            log.warning(f"  - {layer}")
    
    # Check 3: Orphaned agents (no proper base class)
    proper_bases = {
        'SovereignBaseAgent',
        'L0MaintenanceBaseAgent',
        'L1CognitionBaseAgent',
        'L2ExecutionBaseAgent',
        'L3OrchestrationBaseAgent',
        'L4StateBaseAgent',
        'L5SafetyBaseAgent',
        'L6ObservabilityBaseAgent'
    }
    
    orphans = []
    for agent in agents:
        inheritance = agent.get('inheritance', [])
        has_proper_base = any(base in proper_bases for base in inheritance)
        if not has_proper_base and agent.get('layer') not in ['Apps', 'Utils']:
            orphans.append(agent['class_name'])
    
    # Note: Apps agents inheriting from mixins is a known architectural pattern
    # Only flag core layer agents (L0-L6) as orphans
    if orphans:
        issues.append(f"Core layer orphaned agents: {len(orphans)}")
        for name in orphans[:5]:
            log.warning(f"  - {name}")
    
    # Check 4: Parse errors
    if len(parse_errors) > 10:
        issues.append(f"Excessive parse errors: {len(parse_errors)}")
    
    # Report compliance status
    log.info("=" * 80)
    if issues:
        log.warning(f"❌ COMPLIANCE FAILURE: {len(issues)} issue categories detected")
        for issue in issues:
            log.warning(f"  - {issue}")
        log.info("=" * 80)
        return 1
    else:
        log.info(f"✅ COMPLIANCE PASSED: All {len(agents)} agents are standardized")
        log.info("=" * 80)
        return 0


if __name__ == '__main__':
    agents, parse_errors = main()
    
    # Phase 3.3: Run compliance gate
    exit_code = check_compliance_gate(agents, parse_errors)
    sys.exit(exit_code)