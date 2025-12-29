"""
L6 Runtime: Void Compliance Enforcer
Ensures files only exist in ALLOWED_ROOT_FOLDERS and enforces key-to-folder mapping.
"""
import ast
import fnmatch
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple
from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_KEY_TO_FOLDER_MAP, CANON_SIGNALS, CORE_SUBFOLDER_MAP, FORBIDDEN_PATTERNS, FORBIDDEN_ROOT_FOLDERS, ROOT_PROTECTED_FILES, SOVEREIGN_EXCLUDED_FOLDERS, TESTS_ROOT_FILE_WHITELIST, AUTONOMOUS_AGENT_WHITELIST, ROOT_WHITELIST, SOVEREIGN_REGISTRY, UPSTREAM_SOVEREIGN_ROOTS, DOWNSTREAM_ROOTS, GRAVITY_SURGERY_ENABLED, PYTHON_STDLIB_MODULES, CANON_KEY_EXCEPTIONS
logger: Any = logging.getLogger(__name__)
canonical_hierarchy: Any = {root: cfg['subfolders'] for root, cfg in SOVEREIGN_REGISTRY.items()}
canonical_depth_map: Any = {root: cfg['depth'] for root, cfg in SOVEREIGN_REGISTRY.items()}
allowed_root_folders: Any = set(ROOT_WHITELIST)
forbidden_file_patterns: Any = FORBIDDEN_PATTERNS
high_signal_keywords: Any = CANON_SIGNALS
allowed_core_stages: Any = set()
for stages in CORE_SUBFOLDER_MAP.values():
    allowed_core_stages.update(stages)
allowed_core_stages.update(CORE_SUBFOLDER_MAP.keys())
key_to_folder_map: Any = CANON_KEY_TO_FOLDER_MAP

# Uppercase aliases for backward compatibility
ALLOWED_ROOT_FOLDERS = allowed_root_folders
ALLOWED_CORE_STAGES = allowed_core_stages
CANONICAL_HIERARCHY = canonical_hierarchy
CANONICAL_DEPTH_MAP = canonical_depth_map

def validate_file_naming(file_path: Path, project_root: Path) -> Tuple[bool, str]:
    """
    Enforces descriptive snake_case naming for L-layer signals.
    [KEY 49 HARDENING] Strict enforcement with correct root/nested separation.
    """
    file_name: Any = file_path.name
    if not file_name.endswith('.py'):
        return (True, '')
    stem: Any = file_path.stem
    lower_stem: Any = stem.lower()
    if re.search('[A-Z]', stem) or '-' in stem:
        return (False, f"NAMING VIOLATION: '{file_name}' must be snake_case (lowercase only).")
    try:
        rel_path: Any = file_path.relative_to(project_root)
        is_root_file: Any = len(rel_path.parts) == 1
    except ValueError:
        return (False, 'File outside project root.')
    if is_root_file:
        protected: Any = ROOT_PROTECTED_FILES
        if file_name in protected:
            return (True, 'Protected root file (Key 0 exempt)')
        sovereign_markers: Any = {'validator', 'compliance', 'healer', 'enforcer', 'governor'}
        if not any((m in lower_stem for m in sovereign_markers)):
            return (False, f"SOVEREIGN VIOLATION: Root file '{file_name}' missing marker {sovereign_markers}.")
        return (True, '')
    for pattern in FORBIDDEN_FILE_PATTERNS:
        if re.match(pattern, file_name):
            return (False, f"NAMING VIOLATION: Generic/Versioned name '{file_name}' is forbidden.")
    if not any((kw in lower_stem for kw in HIGH_SIGNAL_KEYWORDS)):
        return (False, f"SIGNAL VIOLATION: '{file_name}' lacks high-signal canon keyword.")
    return (True, 'Compliant')
GUIDANCE_EXAMPLES: Dict[str, str] = {'agentic_core/L1_cognition/strategy': 'Generic reasoning loops, high-level mission goal planning, and task decomposition.', 'agentic_core/L3_orchestration/fission': 'Logic that splits large files into smaller modules or manages atomic code shifts.', 'agentic_core/L4_state/memory': 'Interfaces for persistent vector storage (Pinecone) used for long-term meta-learning.', 'apps_shared/utils/validation': 'Shared Pydantic models or regex patterns used across multiple app domains.', 'apps_rg/agents/rankers': 'Scoring logic specifically for resume-to-JD matching (Domain-specific).', 'config/agents/prompts': 'System instructions and persona definitions used to initialize LLM sessions.', 'scripts/operations/integrity': "Utilities that check for structural drift or 'Span of Two' violations."}

def get_placement_guidance(content_preview: str) -> str:
    """
    [SSOT] High-Signal Heuristics for Key 40/49 Enforcement.
    Guides the HealerAgent to the correct L-layer.
    """
    if any((x in content_preview for x in ['planner', 'strategy', 'reasoning', 'mission'])):
        return 'agentic_core/L1_cognition'
    if 'node' in content_preview.lower() or 'execute' in content_preview:
        return 'agentic_core/L1_cognition/thought_engine'
    if any((x in content_preview for x in ['router', 'orchestrator', 'fission', 'hop'])):
        return 'agentic_core/L3_orchestration'
    if any((x in content_preview for x in ['pinecone', 'redis', 'storage', 'cache'])):
        return 'agentic_core/L4_state'
    return 'agentic_core/L1_cognition'

def check_span_of_two_violation(folder_path: Path) -> Tuple[bool, str]:
    """
    [NAMING RULE HARDENING] Enforces Minimum Span of 2.
    A violation occurs ONLY if a folder contains exactly one meaningful child AND that child is a directory (a redundant tunnel).
    Folders containing only one file are valid 'leaves'.
    """
    if not folder_path.is_dir():
        return (True, '')
    meaningful_children: Any = [x for x in folder_path.iterdir() if x.name not in {'.git', '__pycache__', '.pytest_cache', '.ruff_cache'} and (not x.name.startswith('.'))]
    if len(meaningful_children) == 1 and meaningful_children[0].is_dir():
        return (False, f"SPAN-OF-TWO VIOLATION: Redundant tunnel '{folder_path.name}' -> flatten")
    return (True, '')
key_to_folder_map: Any = CANON_KEY_TO_FOLDER_MAP
stdlib_modules: Any = PYTHON_STDLIB_MODULES

def validate_import_conventions(file_path: Path, project_root: Path) -> List[str]:
    """
    Enforces L6 import conventions + expanded circular import detection.
    """
    violations: Any = []
    try:
        rel_path: Any = file_path.relative_to(project_root)
        own_root: Any = rel_path.parts[0] if rel_path.parts else None
    except ValueError:
        return violations
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        tree: Any = ast.parse(content, filename=str(file_path))
    except Exception as e:
        violations.append(f'PARSE ERROR: Cannot analyze imports in {file_path.name}: {e}')
        return violations
    import_nodes: Any = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    import_nodes.sort(key=lambda n: n.lineno if hasattr(n, 'lineno') else 0)
    for node in import_nodes:
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                violations.append(f'RELATIVE IMPORT FORBIDDEN (Line {node.lineno}): Use absolute paths.')
            if any((a.name == '*' for a in node.names)):
                violations.append(f"STAR IMPORT FORBIDDEN (Line {node.lineno}): 'import *' detected.")
    categories: Any = {'stdlib': [], 'thirdparty': [], 'local': []}
    project_roots: Any = ALLOWED_ROOT_FOLDERS | {'void_compliance', 'canon_validator_agentic_v2'}
    imported_roots: Any = set()
    for node in import_nodes:
        module_name: Any = None
        if isinstance(node, ast.Import):
            module_name: Any = node.names[0].name.split('.')[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_name: Any = node.module.split('.')[0]
        if module_name:
            imported_roots.add(module_name)
            if module_name in stdlib_modules:
                categories['stdlib'].append(node.lineno)
            elif module_name in project_roots:
                categories['local'].append(node.lineno)
            else:
                categories['thirdparty'].append(node.lineno)
    prev_cat: Any = None
    for cat in ['stdlib', 'thirdparty', 'local']:
        if categories[cat] and prev_cat and categories[prev_cat]:
            if min(categories[cat]) < max(categories[prev_cat]):
                violations.append(f'IMPORT ORDER VIOLATION: {cat.capitalize()} appears before {prev_cat}.')
        if categories[cat]:
            prev_cat: Any = cat
    if own_root and own_root in imported_roots:
        violations.append(f"DIRECT CIRCULAR RISK: File imports own root '{own_root}'.")
    return violations

def validate_file_location(file_path: Path, project_root: Path) -> Tuple[bool, str]:
    """
    Validate that a file exists in an allowed root folder.
    
    Args:
        file_path: Absolute path to file
        project_root: Project root directory
        
    Returns:
        Tuple of (is_valid, reason)
    """
    try:
        rel_path: Any = file_path.relative_to(project_root)
        parts: Any = rel_path.parts
        depth: Any = len(parts) - 1
        root_folder: Any = parts[0]
        if file_path.name == '__init__.py' or depth == 1:
            return (True, 'Sovereign Structural Component')
        if root_folder == 'agentic_core':
            agentic_core_exact_depth: Any = SOVEREIGN_REGISTRY['agentic_core']['depth']
            if depth != agentic_core_exact_depth:
                reason: Any = 'SHALLOW' if depth < agentic_core_exact_depth else 'DEEP'
                return (False, f"{reason} VIOLATION: '{rel_path}' depth {depth} != {agentic_core_exact_depth}")
        if root_folder.startswith('apps_'):
            apps_depth: Any = SOVEREIGN_REGISTRY.get(root_folder, {}).get('depth', 2)
            if depth != apps_depth:
                reason: Any = 'SHALLOW' if depth < apps_depth else 'DEEP'
                return (False, f"{reason} VIOLATION (apps_*): '{rel_path}' depth {depth} != {apps_depth}")
        if root_folder == 'tests':
            tests_depth: Any = SOVEREIGN_REGISTRY.get('tests', {}).get('depth', 2)
            if depth != tests_depth:
                reason: Any = 'SHALLOW' if depth < tests_depth else 'DEEP'
                return (False, f"{reason} VIOLATION (tests): '{rel_path}' depth {depth} != {tests_depth}")
        if root_folder == 'agentic_core':
            stage: Any = parts[2]
            if stage not in allowed_core_stages and (not (stage.startswith('P') or stage.startswith('S') or stage.startswith('L'))):
                return (False, f"UNAUTHORIZED STAGE: '{stage}' is not a recognized Sovereign territory.")
        return (True, f'{root_folder} depth verified')
        if root_folder in ALLOWED_ROOT_FOLDERS:
            return (True, f'File in allowed root folder: {root_folder}')
        if root_folder in FORBIDDEN_ROOT_FOLDERS:
            return (False, f"VOID VIOLATION: Forbidden root folder '{root_folder}' (legacy)")
        from agentic_core.config.blueprint_sovereign.structure_blueprint import FORBIDDEN_FOLDER_PATTERN
        for part in parts:
            if part in FORBIDDEN_ROOT_FOLDERS:
                return (False, f"VOID VIOLATION: Forbidden folder '{part}' at any depth.")
            if FORBIDDEN_FOLDER_PATTERN.match(part):
                return (False, f"VOID VIOLATION: Numbered folder pattern '{part}' forbidden at any depth.")
        if root_folder and root_folder[0:2].isdigit() and (root_folder[2:3] == '_'):
            return (False, f"VOID VIOLATION: Numbered folder '{root_folder}' not approved (use approved folders only)")
        validator_markers: Any = {'validator', 'compliance', 'canon'}
        if root_folder.startswith('apps_') and any((m in file_path.name.lower() for m in validator_markers)):
            return (False, f"GRAVITY ERROR: Sovereign compliance logic ('{file_path.name}') leaked into downstream '{root_folder}'.")
        is_name_valid, name_reason = validate_file_naming(file_path, project_root)
        if not is_name_valid:
            return (False, name_reason)
        return (True, 'Path and Name compliant.')
    except ValueError:
        return (False, f'VOID VIOLATION: File outside project root')

def get_applicable_keys_for_file(file_path: Path, project_root: Path, include_behavioral: bool=True) -> Set[int]:
    """
    Determine which canon keys should apply to a given file based on its location.
    [NORMALIZED] Handles both Territorial (0-12) and Behavioral (13-19) wildcards.

    Args:
        file_path: Absolute path to file
        project_root: Project root directory
        include_behavioral: Whether to include global behavioral keys (13-19)
        
    Returns:
        Set of applicable key numbers
    """
    try:
        rel_path: Any = file_path.relative_to(project_root)
        rel_path_str: Any = str(rel_path).replace('\\', '/')
        applicable_keys: Any = set()
        for key_num, folders in KEY_TO_FOLDER_MAP.items():
            for folder_pattern in folders:
                if folder_pattern == '*' or rel_path_str.startswith(folder_pattern):
                    applicable_keys.add(key_num)
                    break
        if not include_behavioral:
            applicable_keys: Any = {k for k in applicable_keys if k <= 12}
        return applicable_keys
    except ValueError:
        return set()

def enforce_void_compliance(files: List[Path], project_root: Path) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    """
    Filter files to only those in allowed folders.
    
    Args:
        files: List of file paths to validate
        project_root: Project root directory
        
    Returns:
        Tuple of (valid_files, violations)
    """
    valid_files: Any = []
    violations: Any = []
    for file_path in files:
        is_valid, reason = validate_file_location(file_path, project_root)
        if is_valid:
            valid_files.append(file_path)
        else:
            violations.append((file_path, reason))
            logger.warning(f'   [VOID] {file_path.name}: {reason}')
    return (valid_files, violations)

def get_folder_scope_summary(project_root: Path) -> Dict[str, int]:
    """
    Returns count of .py files per top-level folder for territory verification.
    """
    if not project_root.is_dir():
        logger.warning(f'[SCOPE] Project root {project_root} is not a directory — returning empty summary')
        return {}
    summary: Any = {}
    SCOPE_SKIP_FOLDERS: Any = SOVEREIGN_EXCLUDED_FOLDERS | {'tests'}
    for folder_path in project_root.iterdir():
        if not folder_path.is_dir():
            continue
        if folder_path.name in SCOPE_SKIP_FOLDERS:
            continue
        py_files: Any = list(folder_path.rglob('*.py'))
        summary[folder_path.name] = len(py_files)
    return summary

def generate_ascii_tree(start_path: Path, max_depth: int=3) -> str:
    """[VISUALIZER] Returns the physical directory structure as an ASCII tree string."""
    tree: Any = []
    start_path: Any = start_path.resolve()
    tree.append(f'{start_path.name}/')

    def _add(path, prefix, depth):
        if depth > max_depth:
            return
        items = sorted([x for x in path.iterdir() if x.name not in {'.git', '__pycache__'}])
        for i, item in enumerate(items):
            connector = '└── ' if i == len(items) - 1 else '├── '
            tree.append(f'{prefix}{connector}{item.name}')
            if item.is_dir():
                _add(item, prefix + ('    ' if i == len(items) - 1 else '│   '), depth + 1)
    _add(start_path, '', 1)
    return '\n'.join(tree)

def check_span_of_two_violations(project_root: Path) -> List[Tuple[Path, str]]:
    """
    Scans Sovereign Roots for Span of Two violations.
    Replaces the buggy total_children == 1 check to allow single-file leaves.
    """
    violations: Any = []
    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path: Any = project_root / root_folder
        if not root_path.exists():
            continue
        for dirpath, dirs, _ in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS and (not d.startswith('.'))]
            current_dir: Any = Path(dirpath)
            if current_dir.name in SOVEREIGN_EXCLUDED_FOLDERS or current_dir.name.startswith('.') or '.git' in current_dir.parts:
                continue
            valid, msg = check_span_of_two_violation(current_dir)
            if not valid:
                violations.append((current_dir, msg))
    return violations

def validate_canonical_hierarchy(project_root: Path) -> List[Tuple[Path, str]]:
    """
    [L6 HARDENING] Validates physical folders against the CANONICAL_HIERARCHY SSOT.
    Flags:
    - Unapproved L1 or L2 folders (drift prevention)
    - Files placed too shallow (under Root or L1) — enforces min depth 3 (Key 41)
    """
    violations: Any = []
    for root_key, layers in CANONICAL_HIERARCHY.items():
        root_path: Any = project_root / root_key
        if not root_path.exists():
            continue
        root_files: Any = [p.name for p in root_path.iterdir() if p.is_file() and p.suffix == '.py' and (p.name != '__init__.py') and (not (root_key == 'tests' and p.name in TESTS_ROOT_FILE_WHITELIST))]
        if root_files:
            violations.append((root_path, f"DEPTH VIOLATION (Key 41): Files directly under Root '{root_key}' (depth 1). Found: {root_files}"))
        expected_l1: Any = set(layers) if isinstance(layers, list) else set(layers.keys())
        actual_l1: Any = {p.name for p in root_path.iterdir() if p.is_dir() and (not p.name.startswith('.')) and (p.name not in SOVEREIGN_EXCLUDED_FOLDERS)}
        unexpected_l1: Any = actual_l1 - expected_l1
        for bad in unexpected_l1:
            violations.append((root_path / bad, f"HIERARCHY DRIFT: Unapproved L1 folder '{bad}'. Allowed: {expected_l1}"))
        if root_key == 'agentic_core' and isinstance(layers, list):
            for l1_name in layers:
                l1_path: Any = root_path / l1_name
                if not l1_path.exists():
                    continue
                expected_l2: Any = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
                actual_l2_dirs: Any = {p.name for p in l1_path.iterdir() if p.is_dir() and (not p.name.startswith('.')) and (p.name not in SOVEREIGN_EXCLUDED_FOLDERS)}
                actual_l2_files: Any = [p.name for p in l1_path.iterdir() if p.is_file() and p.suffix == '.py']
                actual_l2_files: Any = [f for f in actual_l2_files if f not in AUTONOMOUS_AGENT_WHITELIST]
                unexpected_l2: Any = actual_l2_dirs - expected_l2
                for bad in unexpected_l2:
                    violations.append((l1_path / bad, f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}"))
        elif isinstance(layers, dict):
            for l1_name, l2_list in layers.items():
                l1_path: Any = root_path / l1_name
                if not l1_path.exists():
                    continue
                expected_l2: Any = set(l2_list)
                actual_l2_dirs: Any = {p.name for p in l1_path.iterdir() if p.is_dir() and (not p.name.startswith('.')) and (p.name not in SOVEREIGN_EXCLUDED_FOLDERS)}
                actual_l2_files: Any = [p.name for p in l1_path.iterdir() if p.is_file() and p.suffix == '.py']
                actual_l2_files: Any = [f for f in actual_l2_files if f not in AUTONOMOUS_AGENT_WHITELIST]
                unexpected_l2: Any = actual_l2_dirs - expected_l2
                for bad in unexpected_l2:
                    violations.append((l1_path / bad, f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}"))
    return violations

def check_import_waterfall_violations(file_path: Path, project_root: Path) -> List[str]:
    """
    Enforces Gravity (Waterfall): Upstream sovereign → no imports from downstream.
    [SSOT] All rules derived from structure_blueprint.GRAVITY_CONFIG
    """
    if not GRAVITY_SURGERY_ENABLED:
        return []
    violations: Any = []
    try:
        rel_path: Any = file_path.relative_to(project_root)
        if not rel_path.parts or rel_path.parts[0] in SOVEREIGN_EXCLUDED_FOLDERS:
            return []
    except ValueError:
        return []
    upstream_sovereign_roots: Any = UPSTREAM_SOVEREIGN_ROOTS
    downstream_roots: Any = DOWNSTREAM_ROOTS
    try:
        current_root: Any = rel_path.parts[0]
    except IndexError:
        return violations
    if current_root not in upstream_sovereign_roots:
        return violations
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content: Any = f.read()
    except Exception:
        return violations
    if downstream_roots and current_root in upstream_sovereign_roots:
        downstream_regex: Any = '|'.join(map(re.escape, sorted(downstream_roots)))
        forbidden_pattern: Any = re.compile(f'^(?:import|from)\\s+({downstream_regex})(?:\\.\\w|\\s|$)', re.MULTILINE)
        matches: Any = forbidden_pattern.findall(content)
        if matches:
            unique_matches: Any = sorted(set(matches))
            violations.append(f"GRAVITY VIOLATION (SSOT Enforced): Upstream '{current_root}' imports downstream: {unique_matches}. Rationale: Prevents core contamination. Move shared logic to apps_shared or sovereign runtime/utils.")
    violations.extend(validate_import_conventions(file_path, project_root))
    return violations

def validate_sovereign_roots(project_root: Path) -> List[Tuple[Path, str]]:
    """
    Validate that all sovereign roots exist and are properly structured.
    
    Args:
        project_root: Project root directory
        
    Returns:
        List of violations as (path, reason) tuples
    """
    violations: Any = []
    for root_name in ALLOWED_ROOT_FOLDERS:
        root_path: Any = project_root / root_name
        if not root_path.exists():
            violations.append((root_path, f'Missing sovereign root: {root_name}'))
            continue
        if not root_path.is_dir():
            violations.append((root_path, f'Sovereign root is not a directory: {root_name}'))
    return violations

def is_excepted_from_key(key_id: int, file_path: Path, line_content: str='') -> bool:
    """
    [L6 HARDENING] Central SSOT check for known false-positive exceptions.
    Supports exact paths, glob patterns, and regex-based line suppression.
    
    Args:
        key_id: Canon key number to check exceptions for
        file_path: Path to the file being validated
        line_content: Optional line content for pattern matching
        
    Returns:
        True if this file/line is excepted from the key validation
    """
    exceptions: Any = CANON_KEY_EXCEPTIONS.get(key_id, {})
    if not exceptions:
        return False
    try:
        project_root: Any = Path(__file__).resolve().parents[3]
        rel_path: Any = str(file_path.relative_to(project_root)).replace('\\', '/')
    except (ValueError, IndexError):
        rel_path: Any = file_path.name
    file_exceptions: Any = exceptions.get('files', set())
    if rel_path in file_exceptions or any((fnmatch.fnmatch(rel_path, pattern) for pattern in file_exceptions)):
        return True
    if line_content:
        for pattern in exceptions.get('patterns', []):
            if re.search(pattern, line_content):
                return True
    return False

def get_ast_safe_imports(content: str) -> Set[str]:
    """
    [L5 SAFETY] Uses AST to extract functional imports only, ignoring comments/docstrings.
    
    Args:
        content: Python source code as string
        
    Returns:
        Set of imported module names
    """
    imports: Any = set()
    try:
        tree: Any = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except SyntaxError:
        regex_imports: Any = re.findall('^(?:import|from)\\s+([a-zA-Z0-9_.]+)', content, re.MULTILINE)
        imports.update(regex_imports)
    return imports
