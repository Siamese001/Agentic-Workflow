#!/usr/bin/env python3
"""
L6 Runtime: Void Compliance Enforcer
Ensures files only exist in ALLOWED_ROOT_FOLDERS and enforces key-to-folder mapping.
"""
from typing import Any, Optional, Protocol, Dict, List


import logging
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

# ==============================================================================
# FILE NAMING CONVENTIONS (Key 49 Hardening)
# ==============================================================================

FORBIDDEN_FILE_PATTERNS = {
    r"^utils\.py$", r"^helper\.py$", r"^temp\.py$", r"^script\.py$",
    r"^main\.py$", r"^test\.py$", r".*_v\d+\.py$", r".*_final\.py$",
    r".*_new\.py$", r".*_old\.py$", r"^.+_\d+\.py$"
}

# Approved high-signal tokens for L-layer alignment
HIGH_SIGNAL_KEYWORDS = {
    "strategy", "reasoning", "planner", "node", "extraction", "synthesis",
    "orchestration", "fission", "hop", "router", "memory", "historian",
    "state", "cache", "safety", "guardrail", "filter", "engine",
    "compliance", "auditor", "validator", "healer", "prompt", "persona",
    "schema", "blueprint", "agent", "handler", "manager", "impl", "types",
    "action", "cognition", "context", "observer", "scheduler"
}

def validate_file_naming(file_path: Path, project_root: Path) -> Tuple[bool, str]:
    """
    Enforces descriptive snake_case naming for L-layer signals.
    """
    file_name = file_path.name
    if not file_name.endswith(".py"):
        return True, ""

    stem = file_path.stem
    lower_stem = stem.lower()
    
    # 1. Snake Case Enforcement (No Caps or Dashes)
    if re.search(r"[A-Z]", stem) or "-" in stem:
        return False, f"NAMING VIOLATION: '{file_name}' must be snake_case (lowercase only)."

    # 2. Forbidden Generic/Versioned Patterns
    for pattern in FORBIDDEN_FILE_PATTERNS:
        if re.match(pattern, file_name):
            return False, f"NAMING VIOLATION: Generic/Versioned name '{file_name}' is forbidden."

    # 3. Path-Aware Sovereign Marker check
    try:
        rel_path = file_path.relative_to(project_root)
        is_root_file = len(rel_path.parts) == 1
    except ValueError:
        return False, "File outside project root."

    if is_root_file:
        protected = {"canon_validator_agentic_v2.py", "pyproject.toml", "README.md", "langgraph.json", ".env", "windsurfrules.md", ".gitignore"}
        if file_name in protected:
            return True, ""
        # Sovereign markers are required for any root-level python logic
        sovereign_markers = {"validator", "compliance", "healer", "enforcer", "governor"}
        if not any(m in lower_stem for m in sovereign_markers):
            return False, f"SOVEREIGN VIOLATION: Root file '{file_name}' missing marker {sovereign_markers}."
        return True, ""

    # 4. High-Signal Signal Requirement
    if not any(kw in lower_stem for kw in HIGH_SIGNAL_KEYWORDS):
        return False, f"SIGNAL VIOLATION: '{file_name}' lacks high-signal canon keyword."

    return True, "Compliant"


# ==============================================================================
# CANONICAL FOLDER STRUCTURE: The Single Source of Truth
# ==============================================================================

# [KEY 40 HARDENING] Full Prescriptive 3-Level Hierarchy
CANONICAL_HIERARCHY: Dict[str, Dict[str, List[str]]] = {
    "agentic_core": {
        "L1_cognition": ["strategy", "reasoning"],
        "L2_thought_nodes": ["extraction", "synthesis"],
        "L3_orchestration": ["fission", "hop_logic"],
        "L4_state": ["memory", "historian"],
        "L5_safety": ["engines", "filters"]
    },
    "apps_shared": {
        "utils": ["formatting", "validation"],
        "infrastructure": ["database", "vector"]
    },
    "apps_lic": {
        "agents": ["compliance", "auditor"],
        "compliance": ["legal", "verification"]
    },
    "config": {
        "environment": ["local", "production"],
        "agents": ["prompts", "hyperparams"]
    },
    "observability": {
        "logs": ["missions", "agents"],
        "metrics": ["performance", "structure"]
    },
    "scripts": {
        "operations": ["maintenance", "integrity"],
        "migrations": ["structural", "data_shifts"]
    }
}

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
    
    # L2: Thought Nodes (Execution/Atomic logic)
    if "node" in content_preview.lower() or "execute" in content_preview:
        return "agentic_core/L2_thought_nodes"
    
    # L3: Orchestration (Routing/Fission)
    if any(x in content_preview for x in ["router", "orchestrator", "fission", "hop"]):
        return "agentic_core/L3_orchestration"
        
    # L4: State (Memory/Databases)
    if any(x in content_preview for x in ["pinecone", "redis", "storage", "cache"]):
        return "agentic_core/L4_state"

    return "agentic_core/L1_cognition" # Default safe-haven for generic logic

def check_span_of_two_violation(folder_path: Path) -> Tuple[bool, str]:
    """
    [KEY 49 HARDENING] Enforces Minimum Span of 2.
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
        return False, f"SPAN VIOLATION (Key 49): '{folder_path.name}' is a redundant tunnel to '{meaningful_children[0].name}'. Flatten."

    return True, ""

ALLOWED_ROOT_FOLDERS = {
    # [L1: THE BRAIN]
    # NOTE: Root-level files (e.g., canon_validator_*.py, pyproject.toml, README.md) 
    #       are allowed separately via validate_file_location() logic for Key 0.
    "agentic_core",
    
    # [L1: THE LAW]
    "prompt_governance",
    
    # [L1: THE CONTRACTS]
    "schemas",
    
    # [L1: INFRA & DOMAINS]
    "apps_shared",
    "apps_rg",
    "apps_lic",
    
    # [L1: QA, TELEMETRY & OPERATIONS]
    "tests",
    "config",
    "observability",
    "scripts",  # Elevated to Sovereign Root - operational utilities
    
    # [VOID ZONES] (Exist but strictly ignored by validation)
    "data", 
    "archives",
}

FORBIDDEN_ROOT_FOLDERS = {
    "data",      # Static assets (out of scope)
    "archives",  # Deprecated code (out of scope)
    "cache",     # Temporary files
    ".git",      # Version control
    ".venv",     # Virtual environments
    "venv",
    "venv_stable",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    # Numbered folders from Light Canon migration (NOT APPROVED)
    "01_runtime_logic",
    "02_runtime_cache",
    "03_scripts_logic",
    "04_scripts_cache",
    "05_runtime_security",
    "06_runtime_runtime",
    "07_runtime_pipeline",
    "08_shared_security",
    "09_shared_runtime",
    "10_shared_pipeline",
    "11_shared_logic",
    "12_shared_cache",
    "13_scripts_security",
    "14_scripts_runtime",
    "15_scripts_pipeline",
}


# ==============================================================================
# KEY-TO-FOLDER MAPPING: Canon Key Enforcement
# ==============================================================================

KEY_TO_FOLDER_MAP: Dict[int, List[str]] = {
    # --- GLOBAL CONFIG [Key 0] ---
    0:  ["."], 

    # --- PROMPT GOVERNANCE [L1: THE LAW] ---
    # [L2: IDENTITY] Keys 11-20
    11: ["prompt_governance/personas/architectural"], # Surgeon
    12: ["prompt_governance/personas/operational"],   # Janitor
    
    # [L2: DIRECTIVES] Keys 21-25
    21: ["prompt_governance/logic/instructional"],
    24: ["prompt_governance/logic/negative"],

    # [L2: GUARDRAILS] Keys 26-30
    26: ["prompt_governance/security/defensive"],
    28: ["prompt_governance/security/injections"],

    # --- SCHEMAS [L1: THE CONTRACTS] ---
    # [L2: MISSION] Keys 31-35
    31: ["schemas/canon/blueprints"], # Fission
    33: ["schemas/canon/reports"],    # Audit
    
    # [L2: COMMUNICATION] Keys 36-39
    36: ["schemas/api/internal"],
    38: ["schemas/api/external"],

    # --- AGENTIC CORE [L1: THE BRAIN] ---
    # Keys 40-42 and 51 cover the Expanded Hierarchy
    40: ["agentic_core/L1_cognition"],       # Basic Logic/Strategy
    41: ["agentic_core/L2_thought_nodes"],   # Refined Thought Processing
    42: ["agentic_core/L3_orchestration"],   # Hop Management & Flow
    51: ["agentic_core/L4_state"],           # Persistent State & Historian

    # --- INFRA & DOMAINS [L1: INFRA] ---
    43: ["apps_shared", "apps_rg", "apps_lic"],       # Core Logic
    44: ["apps_rg/agents", "apps_lic/agents"],        # App Specialists
    45: ["apps_shared/utils"],                        # Shared Utils

    # --- QA & TELEMETRY ---
    47: ["tests"],
    48: ["observability/logs"],
    49: ["observability/metrics"],
    50: ["scripts"]  # [Key 50: Operational Tools]
}


# ==============================================================================
# IMPORT CONVENTIONS ENFORCEMENT (Key 40/42 Hardening – Full Version)
# ==============================================================================

STDLIB_MODULES = {
    "os", "sys", "pathlib", "logging", "asyncio", "typing", "dataclasses",
    "collections", "json", "re", "datetime", "functools", "itertools",
    "abc", "enum", "contextlib", "threading", "time", "random", "math",
    "urllib", "http", "socket", "subprocess", "shutil"
}

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
        
        # Special Case: Root-level files are explicitly allowed (Key 0: Global Config, Orchestrator, Law)
        # Protected root-level files that must remain at project root
        protected_root_files = {
            "canon_validator_agentic_v2.py", "pyproject.toml", "README.md",
            "langgraph.json", ".env", "windsurfrules.md", ".gitignore"
        }
        if len(rel_path.parts) == 1 and file_path.name in protected_root_files:
            return True, "Root-level file allowed (Key 0 compliance: global config/orchestrator)"

        # Nested files: Must belong to an approved root folder
        root_folder = rel_path.parts[0]
        
        # HARDENING: Sovereign Depth Law (L6 Enforcement)
        # Depth 1: agentic_core/file.py (ORPHAN - FORBIDDEN)
        # Depth 2: agentic_core/L1_cognition/file.py (VALID)
        # Depth 3: agentic_core/L1_cognition/sub/file.py (VALID)
        depth = len(rel_path.parts) - 1 # Subtract 1 for the file itself
        
        if root_folder == "tests":
            # Tests must be exactly depth 2 (tests/unit/file.py)
            if depth != 2:
                return False, f"DEPTH VIOLATION: tests/ requires exactly depth 2 subfolders, found depth {depth} at '{rel_path}'."
        else:
            # Sovereign Roots: min 2, max 4
            if depth < 2:
                return False, f"ORPHAN VIOLATION: '{file_path.name}' is sitting in the root of '{root_folder}'. Move to an L-layer."
            if depth > 4:
                return False, f"DEPTH VIOLATION: Path '{rel_path}' is too deep ({depth} levels). Max allowed is 4 levels of nesting."
        
        # [L6 HARDENING] Silent Ignore for standard environment/git noise
        if root_folder in {".venv", "venv", ".git", "__pycache__", "node_modules"}:
            return True, f"System folder ignored: {root_folder}"
        
        if root_folder in ALLOWED_ROOT_FOLDERS:
            return True, f"File in allowed root folder: {root_folder}"
        
        # Check if in forbidden folder
        if root_folder in FORBIDDEN_ROOT_FOLDERS:
            return False, f"VOID VIOLATION: File in forbidden folder '{root_folder}' (out of scope)"
        
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


def get_applicable_keys_for_file(file_path: Path, project_root: Path) -> Set[int]:
    """
    Determine which canon keys should apply to a given file based on its location.
    
    Args:
        file_path: Absolute path to file
        project_root: Project root directory
        
    Returns:
        Set of applicable key numbers
    """
    try:
        rel_path = file_path.relative_to(project_root)
        rel_path_str = str(rel_path).replace("\\", "/")
        
        applicable_keys = set()
        
        for key_num, folders in KEY_TO_FOLDER_MAP.items():
            for folder_pattern in folders:
                if rel_path_str.startswith(folder_pattern):
                    applicable_keys.add(key_num)
                    break
        
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
    Generate summary of files per allowed folder.
    
    Args:
        project_root: Project root directory
        
    Returns:
        Dictionary mapping folder names to file counts
    """
    summary = {folder: 0 for folder in ALLOWED_ROOT_FOLDERS}
    
    for folder in ALLOWED_ROOT_FOLDERS:
        folder_path = project_root / folder
        if folder_path.exists() and folder_path.is_dir():
            py_files = list(folder_path.rglob("*.py"))
            summary[folder] = len(py_files)
    
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
    IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache"}

    for root_folder in ALLOWED_ROOT_FOLDERS:
        root_path = project_root / root_folder
        if not root_path.exists():
            continue

        for dirpath, _, _ in os.walk(root_path):
            current_dir = Path(dirpath)
            if current_dir.name in IGNORE_DIRS or current_dir.name.startswith("."):
                continue

            valid, msg = check_span_of_two_violation(current_dir)
            if not valid:
                violations.append((current_dir, msg))

    return violations

def validate_canonical_hierarchy(project_root: Path) -> List[Tuple[Path, str]]:
    """
    [L6 HARDENING] Validates physical folders against the CANONICAL_HIERARCHY SSOT.
    Flags any unapproved subfolders to prevent organic architectural drift.
    """
    violations = []

    for root_key, layers in CANONICAL_HIERARCHY.items():
        root_path = project_root / root_key
        if not root_path.exists():
            continue

        # Level 1 Validation (e.g., agentic_core -> L1_cognition)
        expected_l1 = set(layers.keys())
        actual_l1 = {p.name for p in root_path.iterdir() if p.is_dir() and not p.name.startswith(".")}

        unexpected = actual_l1 - expected_l1
        for bad in unexpected:
            violations.append((root_path / bad, f"HIERARCHY DRIFT: Unapproved L1 folder '{bad}'. Allowed: {expected_l1}"))

        # Level 2 Validation (e.g., L1_cognition -> strategy)
        for l1_name, l2_list in layers.items():
            l1_path = root_path / l1_name
            if not l1_path.exists():
                continue
            expected_l2 = set(l2_list)
            actual_l2 = {p.name for p in l1_path.iterdir() if p.is_dir() and not p.name.startswith(".")}
            
            unexpected_l2 = actual_l2 - expected_l2
            for bad in unexpected_l2:
                violations.append((l1_path / bad, f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}"))

    return violations


def check_import_waterfall_violations(file_path: Path, project_root: Path) -> List[str]:
    """
    Unified Integrity Pass: Enforces Gravity (Waterfall) + Style (Conventions).
    """
    violations = []
    SYSTEM_FOLDERS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache"}

    try:
        rel_path = file_path.relative_to(project_root)
        if not rel_path.parts or rel_path.parts[0] in SYSTEM_FOLDERS:
            return []
    except ValueError:
        return []

    # [PHASE 1] Gravity (Waterfall) Enforcement
    SOVEREIGN_RANKING = ["agentic_core", "prompt_governance", "schemas", "config", "scripts"]
    DOWNSTREAM_APPS = {"apps_rg", "apps_lic", "apps_shared"}
    current_root = rel_path.parts[0]
    
    if current_root in SOVEREIGN_RANKING:
        current_rank = SOVEREIGN_RANKING.index(current_root)
        forbidden_roots = set(SOVEREIGN_RANKING[current_rank + 1:]) | DOWNSTREAM_APPS
        
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        for forbidden in forbidden_roots:
            if f"import {forbidden}" in content or f"from {forbidden}" in content:
                violations.append(f"GRAVITY VIOLATION: '{current_root}' depends on downstream '{forbidden}'.")

    # [PHASE 2] Convention Enforcement
    violations.extend(validate_import_conventions(file_path, project_root))
        
    return violations