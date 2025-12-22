#!/usr/bin/env python3
"""
L6 Runtime: Void Compliance Enforcer
Ensures files only exist in ALLOWED_ROOT_FOLDERS and enforces key-to-folder mapping.
"""
from typing import Any, Optional, Protocol, Dict, List


import logging
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


# ==============================================================================
# CANONICAL FOLDER STRUCTURE: The Single Source of Truth
# ==============================================================================

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
    
    # [L1: QA & TELEMETRY]
    "tests",
    "config",
    "observability",
    
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
    # Keys 40-42 cover the Strategy/Action/Workflow Layers
    40: ["agentic_core"],
    41: ["agentic_core"],
    42: ["agentic_core"],

    # --- INFRA & DOMAINS [L1: INFRA] ---
    43: ["apps_shared", "apps_rg", "apps_lic"],       # Core Logic
    44: ["apps_rg/agents", "apps_lic/agents"],        # App Specialists
    45: ["apps_shared/utils"],                        # Shared Utils

    # --- QA & TELEMETRY ---
    47: ["tests"],
    48: ["observability/logs"],
    49: ["observability/metrics"]
}


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
        
        if root_folder in ALLOWED_ROOT_FOLDERS:
            return True, f"File in allowed root folder: {root_folder}"
        
        # Check if in forbidden folder
        if root_folder in FORBIDDEN_ROOT_FOLDERS:
            return False, f"VOID VIOLATION: File in forbidden folder '{root_folder}' (out of scope)"
        
        # Check for numbered prefix pattern (NOT APPROVED)
        if root_folder and root_folder[0:2].isdigit() and root_folder[2:3] == "_":
            return False, f"VOID VIOLATION: Numbered folder '{root_folder}' not approved (use approved folders only)"
        
        # SOVEREIGN PROTECTION: Ensure Validator hasn't leaked into Infra
        if root_folder == "apps_shared" and "validator" in file_path.name.lower():
            return False, "GRAVITY ERROR: Validator must remain at Root (Key 0). Do not hide the General in apps_shared."
        
        # Unknown folder
        return False, f"VOID VIOLATION: File in unknown/disallowed root folder '{root_folder}'"
        
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


def check_single_child_violations(project_root: Path) -> List[Tuple[Path, str]]:
    """
    Detect "single-child" antipattern: L2/L3 folders containing only one item.
    These should be collapsed into parent to maintain flat-velocity.
    
    Args:
        project_root: Project root directory
        
    Returns:
        List of (folder_path, violation_reason) tuples
    """
    violations = []
    
    for root_folder in ALLOWED_ROOT_FOLDERS:
        folder_path = project_root / root_folder
        if not folder_path.exists():
            continue
            
        # Check all subdirectories
        for dirpath, dirnames, filenames in os.walk(folder_path):
            current_dir = Path(dirpath)
            
            # Count immediate children (dirs + files, excluding __pycache__)
            children_dirs = [d for d in dirnames if d != "__pycache__"]
            children_files = [f for f in filenames if not f.startswith(".")]
            total_children = len(children_dirs) + len(children_files)
            
            # Single-child violation
            if total_children == 1:
                child_name = children_dirs[0] if children_dirs else children_files[0]
                violations.append((
                    current_dir,
                    f"Single-child antipattern: '{current_dir.name}' contains only '{child_name}' - should be collapsed"
                ))
    
    return violations


def check_import_waterfall_violations(file_path: Path, project_root: Path) -> List[str]:
    """
    [L6 PHYSICS] Gravity Rule: 
    Sovereign Layers (Core, Law, Contracts) MUST NOT import Downstream Domains (Apps).
    """
    violations = []
    try:
        rel_path = file_path.relative_to(project_root)
        
        # Define Sovereign Roots (The 'Upstream')
        sovereign_roots = {"agentic_core", "prompt_governance", "schemas", "config"}
        
        # If file is not in a Sovereign root, it is downstream and safe.
        if rel_path.parts[0] not in sovereign_roots:
            return []

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        # Forbidden Downstream Imports
        forbidden = ["apps_rg", "apps_lic", "apps_shared"]
        
        for bad_lib in forbidden:
            if f"import {bad_lib}" in content or f"from {bad_lib}" in content:
                violations.append(f"GRAVITY VIOLATION: Sovereign '{rel_path.parts[0]}' cannot import downstream '{bad_lib}'")
                
    except Exception as e:
        logger.warning(f"Could not check import waterfall for {file_path}: {e}")
        
    return violations
