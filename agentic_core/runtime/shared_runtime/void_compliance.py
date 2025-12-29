#!/usr/bin/env python3
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

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    CANON_KEY_TO_FOLDER_MAP,
    CANON_SIGNALS,
    CORE_SUBFOLDER_MAP,
    FORBIDDEN_PATTERNS,
    FORBIDDEN_ROOT_FOLDERS,
    ROOT_PROTECTED_FILES,
    SOVEREIGN_EXCLUDED_FOLDERS,
    TESTS_ROOT_FILE_WHITELIST,
    AUTONOMOUS_AGENT_WHITELIST,
    ROOT_WHITELIST,
    SOVEREIGN_REGISTRY,
    UPSTREAM_SOVEREIGN_ROOTS,
    DOWNSTREAM_ROOTS,
    GRAVITY_SURGERY_ENABLED,
    PYTHON_STDLIB_MODULES,  # [SSOT] Standard library modules for import validation
    CANON_KEY_EXCEPTIONS,
)

logger = logging.getLogger(__name__)

# [ULTRA-HARDENING] All structural facts are derived exclusively from SSOT
CANONICAL_HIERARCHY = {root: cfg["subfolders"] for root, cfg in SOVEREIGN_REGISTRY.items()}
CANONICAL_DEPTH_MAP = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
# [PURGE] All hardcoded sets deleted - now derived from blueprint
FORBIDDEN_FILE_PATTERNS = FORBIDDEN_PATTERNS
HIGH_SIGNAL_KEYWORDS = CANON_SIGNALS

# [DESIGN UNIFICATION] Derive all allowed stages from the SSOT
ALLOWED_CORE_STAGES = set()
for stages in CORE_SUBFOLDER_MAP.values():
    ALLOWED_CORE_STAGES.update(stages)
ALLOWED_CORE_STAGES.update(CORE_SUBFOLDER_MAP.keys())

KEY_TO_FOLDER_MAP = CANON_KEY_TO_FOLDER_MAP

# ==============================================================================
# FILE NAMING CONVENTIONS (Key 49 Hardening)
# ==============================================================================

def validate_file_naming(file_path: Path, project_root: Path) -> Tuple[bool, str]:
    """
    Enforces descriptive snake_case naming for L-layer signals.
    [KEY 49 HARDENING] Strict enforcement with correct root/nested separation.
    """
    file_name = file_path.name
    if not file_name.endswith(".py"):
        return True, ""

    stem = file_path.stem
    lower_stem = stem.lower()
    
    # 1. Snake Case Enforcement (No Caps or Dashes) - Applies to ALL Python files
    if re.search(r"[A-Z]", stem) or "-" in stem:
        return False, f"NAMING VIOLATION: '{file_name}' must be snake_case (lowercase only)."

    try:
        rel_path = file_path.relative_to(project_root)
        is_root_file = len(rel_path.parts) == 1
    except ValueError:
        return False, "File outside project root."

    # 2. Special Handling for Root-Level Files (Key 0 Protected)
    if is_root_file:
        protected = ROOT_PROTECTED_FILES # [GAP 16]
        if file_name in protected:
            return True, "Protected root file (Key 0 exempt)"

        # Sovereign markers are required for any root-level python logic
        sovereign_markers = {"validator", "compliance", "healer", "enforcer", "governor"}
        if not any(m in lower_stem for m in sovereign_markers):
            return False, f"SOVEREIGN VIOLATION: Root file '{file_name}' missing marker {sovereign_markers}."
        return True, ""

    # 3. Nested Files: Forbidden Generic/Versioned Patterns
    for pattern in FORBIDDEN_FILE_PATTERNS:
        if re.match(pattern, file_name):
            return False, f"NAMING VIOLATION: Generic/Versioned name '{file_name}' is forbidden."

    # 4. Nested Files: High-Signal Keyword Requirement
    if not any(kw in lower_stem for kw in HIGH_SIGNAL_KEYWORDS):
        return False, f"SIGNAL VIOLATION: '{file_name}' lacks high-signal canon keyword."

    return True, "Compliant"


# ==============================================================================
# CANONICAL FOLDER STRUCTURE: The Single Source of Truth
# ==============================================================================

# [KEY 40] LLM GUIDANCE: Content Heuristics for File Placement
GUIDANCE_EXAMPLES: Dict[str, str] = {
    "agentic_core/L1_cognition/strategy": "Generic reasoning loops, high-level mission goal planning, and task decomposition.",
    "agentic_core/L3_orchestration/fission": "Logic that splits large files into smaller modules or manages atomic code shifts.",
    "agentic_core/L4_state/memory": "Interfaces for persistent vector storage (Pinecone) used for long-term meta-learning.",
    "apps_shared/utils/validation": "Shared Pydantic models or regex patterns used across multiple app domains.",
    "apps_rg/agents/rankers": "Scoring logic specifically for resume-to-JD matching (Domain-specific).",
    "config/agents/prompts": "System instructions and persona definitions used to initialize LLM sessions.",
    "scripts/operations/integrity": "Utilities that check for structural drift or 'Span of Two' violations."
}

def get_placement_guidance(content_preview: str) -> str:
    """
    [SSOT] High-Signal Heuristics for Key 40/49 Enforcement.
    Guides the HealerAgent to the correct L-layer.
    """
    # L1: Cognition & Strategy
    if any(x in content_preview for x in ["planner", "strategy", "reasoning", "mission"]):
        return "agentic_core/L1_cognition"
    
    # L1: Thought Nodes (Execution/Atomic logic) - now under L1_cognition/thought_engine
    if "node" in content_preview.lower() or "execute" in content_preview:
        return "agentic_core/L1_cognition/thought_engine"
    
    # L3: Orchestration (Routing/Fission)
    if any(x in content_preview for x in ["router", "orchestrator", "fission", "hop"]):
        return "agentic_core/L3_orchestration"
        
    # L4: State (Memory/Databases)
    if any(x in content_preview for x in ["pinecone", "redis", "storage", "cache"]):
        return "agentic_core/L4_state"

    return "agentic_core/L1_cognition" # Default safe-haven for generic logic

def check_span_of_two_violation(folder_path: Path) -> Tuple[bool, str]:
    """
    [NAMING RULE HARDENING] Enforces Minimum Span of 2.
    A violation occurs ONLY if a folder contains exactly one meaningful child AND that child is a directory (a redundant tunnel).
    Folders containing only one file are valid 'leaves'.
    """
    if not folder_path.is_dir():
        return True, ""

    meaningful_children = [
        x for x in folder_path.iterdir()
        if x.name not in {".git", "__pycache__", ".pytest_cache", ".ruff_cache"}
        and not x.name.startswith(".")
    ]

    if len(meaningful_children) == 1 and meaningful_children[0].is_dir():
        return False, f"SPAN-OF-TWO VIOLATION: Redundant tunnel '{folder_path.name}' -> flatten" # [GAP 4/13]

    return True, ""


# ==============================================================================
# KEY-TO-FOLDER MAPPING: Canon Key Enforcement
# ==============================================================================

KEY_TO_FOLDER_MAP = CANON_KEY_TO_FOLDER_MAP


# ==============================================================================
# IMPORT CONVENTIONS ENFORCEMENT (Key 40/42 Hardening – Full Version)
# ==============================================================================

# [SSOT] Standard library modules — derived from structure_blueprint.py
STDLIB_MODULES = PYTHON_STDLIB_MODULES

def validate_import_conventions(file_path: Path, project_root: Path) -> List[str]:
    """
    Enforces L6 import conventions + expanded circular import detection.
    """
    violations = []
    try:
        rel_path = file_path.relative_to(project_root)
        own_root = rel_path.parts[0] if rel_path.parts else None
    except ValueError:
        return violations

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except Exception as e:
        violations.append(f"PARSE ERROR: Cannot analyze imports in {file_path.name}: {e}")
        return violations

    import_nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    import_nodes.sort(key=lambda n: n.lineno if hasattr(n, 'lineno') else 0)

    # 1. No relative/star imports
    for node in import_nodes:
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                violations.append(f"RELATIVE IMPORT FORBIDDEN (Line {node.lineno}): Use absolute paths.")
            if any(a.name == "*" for a in node.names):
                violations.append(f"STAR IMPORT FORBIDDEN (Line {node.lineno}): 'import *' detected.")

    # 2. Ordering Check (stdlib → third-party → local)
    categories = {"stdlib": [], "thirdparty": [], "local": []}
    project_roots = ALLOWED_ROOT_FOLDERS | {"void_compliance", "canon_validator_agentic_v2"}
    imported_roots = set()

    for node in import_nodes:
        module_name = None
        if isinstance(node, ast.Import):
            module_name = node.names[0].name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_name = node.module.split(".")[0]

        if module_name:
            imported_roots.add(module_name)
            if module_name in STDLIB_MODULES:
                categories["stdlib"].append(node.lineno)
            elif module_name in project_roots:
                categories["local"].append(node.lineno)
            else:
                categories["thirdparty"].append(node.lineno)

    prev_cat = None
    for cat in ["stdlib", "thirdparty", "local"]:
        if categories[cat] and prev_cat and categories[prev_cat]:
            if min(categories[cat]) < max(categories[prev_cat]):
                violations.append(f"IMPORT ORDER VIOLATION: {cat.capitalize()} appears before {prev_cat}.")
        if categories[cat]: prev_cat = cat

    # 3. Expanded Circular Risk
    if own_root and own_root in imported_roots:
        violations.append(f"DIRECT CIRCULAR RISK: File imports own root '{own_root}'.")

    return violations


# ==============================================================================
# ENFORCEMENT FUNCTIONS
# ==============================================================================

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
        # Get relative path from project root
        rel_path = file_path.relative_to(project_root)
        parts = rel_path.parts
        # Depth = folder levels only (exclude filename)
        # e.g., agentic_core/config/blueprint_sovereign/file.py -> depth 3
        depth = len(parts) - 1
        root_folder = parts[0]
        
        # Rule 0: Exempt the root structure
        if file_path.name == "__init__.py" or depth == 1:
            return True, "Sovereign Structural Component"
        
        # [ETERNAL DEPTH 4] Universal enforcement for all L-layers
        if root_folder == "agentic_core":
            agentic_core_exact_depth = SOVEREIGN_REGISTRY["agentic_core"]["depth"]  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
            if depth != agentic_core_exact_depth:
                reason = "SHALLOW" if depth < agentic_core_exact_depth else "DEEP"
                return False, f"{reason} VIOLATION: '{rel_path}' depth {depth} != {agentic_core_exact_depth}"

        # [SSOT] All apps_* folders — depth from SOVEREIGN_REGISTRY
        if root_folder.startswith("apps_"):
            apps_depth = SOVEREIGN_REGISTRY.get(root_folder, {}).get("depth", 2)
            if depth != apps_depth:
                reason = "SHALLOW" if depth < apps_depth else "DEEP"
                return False, f"{reason} VIOLATION (apps_*): '{rel_path}' depth {depth} != {apps_depth}"

        # [SSOT] tests/ folder lockdown — depth from SOVEREIGN_REGISTRY
        if root_folder == "tests":
            tests_depth = SOVEREIGN_REGISTRY.get("tests", {}).get("depth", 2)
            if depth != tests_depth:
                reason = "SHALLOW" if depth < tests_depth else "DEEP"
                return False, f"{reason} VIOLATION (tests): '{rel_path}' depth {depth} != {tests_depth}"
            
        # Rule 1a: Core Stage Enforcement (Identity/Inference/Meta or P/S/L)
        if root_folder == "agentic_core":
            stage = parts[2]
            # Check against authorized list AND standard P/S/L naming convention
            if stage not in ALLOWED_CORE_STAGES and not (stage.startswith('P') or stage.startswith('S') or stage.startswith('L')):
                return False, f"UNAUTHORIZED STAGE: '{stage}' is not a recognized Sovereign territory."
        
        return True, f"{root_folder} depth verified"
        
        if root_folder in ALLOWED_ROOT_FOLDERS:
            return True, f"File in allowed root folder: {root_folder}"
        
        # Check if in forbidden folder (static legacy list)
        if root_folder in FORBIDDEN_ROOT_FOLDERS:
            return False, f"VOID VIOLATION: Forbidden root folder '{root_folder}' (legacy)"

        # [GAP FIX] Check for numbered folder pattern at any depth
        from agentic_core.config.blueprint_sovereign.structure_blueprint import FORBIDDEN_FOLDER_PATTERN
        for part in parts:
            # Check static forbidden list
            if part in FORBIDDEN_ROOT_FOLDERS:
                return False, f"VOID VIOLATION: Forbidden folder '{part}' at any depth."
            # Check numbered pattern (e.g., "08_*")
            if FORBIDDEN_FOLDER_PATTERN.match(part):
                return False, f"VOID VIOLATION: Numbered folder pattern '{part}' forbidden at any depth."
        
        # Check for numbered prefix pattern (NOT APPROVED)
        if root_folder and root_folder[0:2].isdigit() and root_folder[2:3] == "_":
            return False, f"VOID VIOLATION: Numbered folder '{root_folder}' not approved (use approved folders only)"
        
        # SOVEREIGN PROTECTION: Key 0 (General) must remain at Project Root
        validator_markers = {"validator", "compliance", "canon"}
        if root_folder.startswith("apps_") and any(m in file_path.name.lower() for m in validator_markers):
            return False, f"GRAVITY ERROR: Sovereign compliance logic ('{file_path.name}') leaked into downstream '{root_folder}'."
        
        # [L6 HARDENING] Strict Naming Enforcement
        is_name_valid, name_reason = validate_file_naming(file_path, project_root)
        if not is_name_valid:
            return False, name_reason

        return True, "Path and Name compliant."
        
    except ValueError:
        # File is outside project root
        return False, f"VOID VIOLATION: File outside project root"


def get_applicable_keys_for_file(file_path: Path, project_root: Path, include_behavioral: bool = True) -> Set[int]:
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
        rel_path = file_path.relative_to(project_root)
        rel_path_str = str(rel_path).replace("\\", "/")
        
        applicable_keys = set()
        
        for key_num, folders in KEY_TO_FOLDER_MAP.items():
            for folder_pattern in folders:
                # [KEY 20 FIX] Handle territorial prefix OR behavioral wildcard
                if folder_pattern == "*" or rel_path_str.startswith(folder_pattern):
                    applicable_keys.add(key_num)
                    break
        
        if not include_behavioral:
            applicable_keys = {k for k in applicable_keys if k <= 12}

        return applicable_keys
        
    except ValueError:
        return set()


def enforce_void_compliance(
    files: List[Path], 
    project_root: Path
) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    """
    Filter files to only those in allowed folders.
    
    Args:
        files: List of file paths to validate
        project_root: Project root directory
        
    Returns:
        Tuple of (valid_files, violations)
    """
    valid_files = []
    violations = []
    
    for file_path in files:
        is_valid, reason = validate_file_location(file_path, project_root)
        
        if is_valid:
            valid_files.append(file_path)
        else:
            violations.append((file_path, reason))
            logger.warning(f"   [VOID] {file_path.name}: {reason}")
    
    return valid_files, violations


def get_folder_scope_summary(project_root: Path) -> Dict[str, int]:
    """
    Returns count of .py files per top-level folder for territory verification.
    """
    # [DEFENSIVE HARDENING] Early guard against malformed root
    if not project_root.is_dir():
        logger.warning(f"[SCOPE] Project root {project_root} is not a directory — returning empty summary")
        return {}

    summary = {}

    # [SSOT REFACTOR] Use global exclusion set
    # 'tests' is intentionally NOT in global ignore (it's a root), but we skip it for summary counts
    SCOPE_SKIP_FOLDERS = SOVEREIGN_EXCLUDED_FOLDERS | {'tests'}
    
    for folder_path in project_root.iterdir():
        if not folder_path.is_dir():
            continue
        
        if folder_path.name in SCOPE_SKIP_FOLDERS:
            # [PROTECTED] Skipping folder logic handled by caller or implicit here
            continue
            
        # [RESOURCE SAFETY] Limit recursion or just rely on the .git skip above
        # Since we explicitly skipped .git/protected, rglob is safe on code folders
        py_files = list(folder_path.rglob("*.py"))
        summary[folder_path.name] = len(py_files)
    
    return summary


def generate_ascii_tree(start_path: Path, max_depth: int = 3) -> str:
    """[VISUALIZER] Returns the physical directory structure as an ASCII tree string."""
    tree = []
    start_path = start_path.resolve()
    tree.append(f"{start_path.name}/")

    def _add(path, prefix, depth):
        if depth > max_depth: return
        items = sorted([x for x in path.iterdir() if x.name not in {'.git', '__pycache__'}])
        for i, item in enumerate(items):
            connector = "└── " if i == len(items)-1 else "├── "
            tree.append(f"{prefix}{connector}{item.name}")
            if item.is_dir():
                _add(item, prefix + ("    " if i == len(items)-1 else "│   "), depth + 1)
    
    _add(start_path, "", 1)
    return "\n".join(tree)


def check_span_of_two_violations(project_root: Path) -> List[Tuple[Path, str]]:
    """
    Scans Sovereign Roots for Span of Two violations.
    Replaces the buggy total_children == 1 check to allow single-file leaves.
    """
    violations = []

    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path = project_root / root_folder
        if not root_path.exists():
            continue

        for dirpath, dirs, _ in os.walk(root_path):
            # [PERFORMANCE FIX] Prune ignored directories in-place to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS and not d.startswith(".")]
            
            current_dir = Path(dirpath)
            if current_dir.name in SOVEREIGN_EXCLUDED_FOLDERS or current_dir.name.startswith(".") or ".git" in current_dir.parts:
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
    violations = []

    for root_key, layers in CANONICAL_HIERARCHY.items():
        root_path = project_root / root_key
        if not root_path.exists():
            continue

        # 1. Root Level Check: No files directly in Sovereign Root (depth 1)
        # Whitelist __init__.py as it's required for Python package recognition
        # Whitelist conftest.py and test files in tests/ root (pytest requirement)
        # [SSOT] Whitelist derived from structure_blueprint
        root_files = [
            p.name for p in root_path.iterdir() 
            if p.is_file() and p.suffix == ".py" 
            and p.name != "__init__.py"
            and not (root_key == "tests" and p.name in TESTS_ROOT_FILE_WHITELIST)
        ]
        if root_files:
            violations.append((root_path, f"DEPTH VIOLATION (Key 41): Files directly under Root '{root_key}' (depth 1). Found: {root_files}"))

        # 2. Level 1 Validation (e.g., agentic_core -> L1_cognition)
        # layers is now a list of allowed L1 folders from SOVEREIGN_REGISTRY
        expected_l1 = set(layers) if isinstance(layers, list) else set(layers.keys())
        actual_l1 = {p.name for p in root_path.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in SOVEREIGN_EXCLUDED_FOLDERS}

        unexpected_l1 = actual_l1 - expected_l1
        for bad in unexpected_l1:
            violations.append((root_path / bad, f"HIERARCHY DRIFT: Unapproved L1 folder '{bad}'. Allowed: {expected_l1}"))

        # 3. Level 2 Validation + Min Depth Enforcement
        # For L2 validation, we need to check CORE_SUBFOLDER_MAP for agentic_core
        if root_key == "agentic_core" and isinstance(layers, list):
            for l1_name in layers:
                l1_path = root_path / l1_name
                if not l1_path.exists():
                    continue
                
                # Get expected L2 folders from CORE_SUBFOLDER_MAP
                expected_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
                actual_l2_dirs = {p.name for p in l1_path.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in SOVEREIGN_EXCLUDED_FOLDERS}
                actual_l2_files = [p.name for p in l1_path.iterdir() if p.is_file() and p.suffix == ".py"]
                
                # [SSOT] Filter out whitelisted autonomous agents from violations
                actual_l2_files = [f for f in actual_l2_files if f not in AUTONOMOUS_AGENT_WHITELIST]
                
                # Unexpected L2 folders
                unexpected_l2 = actual_l2_dirs - expected_l2
                for bad in unexpected_l2:
                    violations.append((l1_path / bad, f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}"))
        elif isinstance(layers, dict):
            # Legacy dict format support
            for l1_name, l2_list in layers.items():
                l1_path = root_path / l1_name
                if not l1_path.exists():
                    continue
                
                expected_l2 = set(l2_list)
                actual_l2_dirs = {p.name for p in l1_path.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in SOVEREIGN_EXCLUDED_FOLDERS}
                actual_l2_files = [p.name for p in l1_path.iterdir() if p.is_file() and p.suffix == ".py"]
                
                # [SSOT] Filter out whitelisted autonomous agents from violations
                actual_l2_files = [f for f in actual_l2_files if f not in AUTONOMOUS_AGENT_WHITELIST]
                
                # Unexpected L2 folders
                unexpected_l2 = actual_l2_dirs - expected_l2
                for bad in unexpected_l2:
                    violations.append((l1_path / bad, f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}"))

    return violations


def check_import_waterfall_violations(file_path: Path, project_root: Path) -> List[str]:
    """
    Enforces Gravity (Waterfall): Upstream sovereign → no imports from downstream.
    [SSOT] All rules derived from structure_blueprint.GRAVITY_CONFIG
    """
    if not GRAVITY_SURGERY_ENABLED:
        return []  # Sovereign override — gravity disabled

    violations = []
    # [SSOT] Use SOVEREIGN_EXCLUDED_FOLDERS instead of hardcoding

    try:
        rel_path = file_path.relative_to(project_root)
        if not rel_path.parts or rel_path.parts[0] in SOVEREIGN_EXCLUDED_FOLDERS:
            return []
    except ValueError:
        return []

    # [SSOT] Fully derived from blueprint — zero drift
    upstream_sovereign_roots = UPSTREAM_SOVEREIGN_ROOTS
    downstream_roots = DOWNSTREAM_ROOTS

    try:
        current_root = rel_path.parts[0]
    except IndexError:
        return violations

    # Gravity restriction applies only to files in upstream sovereign roots
    if current_root not in upstream_sovereign_roots:
        return violations

    # Read file content once
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return violations  # Skip unreadable files

    # [L6 GRAVITY HARDENING] Prevent upstream -> downstream contamination
    if downstream_roots and current_root in upstream_sovereign_roots:
        # Use word boundaries and multi-line matching to catch direct imports
        downstream_regex = "|".join(map(re.escape, sorted(downstream_roots)))
        forbidden_pattern = re.compile(
            rf"^(?:import|from)\s+({downstream_regex})(?:\.\w|\s|$)",
            re.MULTILINE
        )

        matches = forbidden_pattern.findall(content)
        if matches:
            unique_matches = sorted(set(matches))
            violations.append(
                f"GRAVITY VIOLATION (SSOT Enforced): Upstream '{current_root}' imports downstream: {unique_matches}. "
                "Rationale: Prevents core contamination. Move shared logic to apps_shared or sovereign runtime/utils."
            )

    # [PHASE 2] Convention Enforcement
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
    violations = []
    
    for root_name in ALLOWED_ROOT_FOLDERS:
        root_path = project_root / root_name
        
        # Check if root exists
        if not root_path.exists():
            violations.append((root_path, f"Missing sovereign root: {root_name}"))
            continue
            
        # Check if it's a directory
        if not root_path.is_dir():
            violations.append((root_path, f"Sovereign root is not a directory: {root_name}"))
    
    return violations


# ==============================================================================
# EXCEPTION HANDLING & AST UTILITIES
# ==============================================================================

def is_excepted_from_key(key_id: int, file_path: Path, line_content: str = "") -> bool:
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
    exceptions = CANON_KEY_EXCEPTIONS.get(key_id, {})
    if not exceptions:
        return False
        
    # 1. Resolve relative path for SSOT comparison
    try:
        project_root = Path(__file__).resolve().parents[3]  # Adjust based on void_compliance location
        rel_path = str(file_path.relative_to(project_root)).replace("\\", "/")
    except (ValueError, IndexError):
        rel_path = file_path.name

    # 2. Check file-level exceptions (Exact or Glob)
    file_exceptions = exceptions.get("files", set())
    if rel_path in file_exceptions or any(fnmatch.fnmatch(rel_path, pattern) for pattern in file_exceptions):
        return True

    # 3. Check line-level pattern exceptions
    if line_content:
        for pattern in exceptions.get("patterns", []):
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
    imports = set()
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except SyntaxError:
        # Fallback to regex if file is currently broken during healing
        regex_imports = re.findall(r"^(?:import|from)\s+([a-zA-Z0-9_.]+)", content, re.MULTILINE)
        imports.update(regex_imports)
    return imports