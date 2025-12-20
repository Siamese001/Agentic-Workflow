#!/usr/bin/env python3
"""
L6 Runtime: Void Compliance Enforcer
Ensures files only exist in ALLOWED_ROOT_FOLDERS and enforces key-to-folder mapping.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


# ==============================================================================
# CANONICAL FOLDER STRUCTURE: The Single Source of Truth
# ==============================================================================

ALLOWED_ROOT_FOLDERS = {
    # [THE BRAIN] Domain-Agnostic Framework
    "agentic_core",
    
    # [THE LAW] Governance & Configuration
    "prompt_governance",
    "config",
    "schemas",
    
    # [THE TELEMETRY] Observability
    "observability",
    
    # [THE INFRASTRUCTURE] Shared Application Code
    "apps_shared",
    
    # [TARGET DOMAINS] Application-Specific Code
    "apps_rg",
    "apps_lic",
    
    # [THE TOOLS] Execution Utilities
    "scripts",
    
    # [TESTING] Functional Assurance
    "tests",
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
}


# ==============================================================================
# KEY-TO-FOLDER MAPPING: Canon Key Enforcement
# ==============================================================================

KEY_TO_FOLDER_MAP: Dict[int, List[str]] = {
    # Keys 0-10: Global Configuration (THE SETTINGS)
    0: ["config"],                          # Root config
    1: ["config/models"],                   # Model configs (gemini_params.yaml, model_router.json)
    2: ["config/policy"],                   # Policy configs (token_budgets.yaml, fission_rules.yaml)
    3: ["config"],                          # General config
    4: ["config"],                          # General config
    5: ["config"],                          # General config
    6: ["config"],                          # General config
    7: ["config"],                          # General config
    8: ["config"],                          # General config
    9: ["config"],                          # General config
    10: ["config"],                         # General config
    
    # Keys 11-20: Agent Personas (THE LAW - Identity/Soul)
    11: ["prompt_governance/personas/architectural"],  # Surgeon, Architect personas
    12: ["prompt_governance/personas/operational"],    # Janitor, Healer personas
    13: ["prompt_governance/personas/architectural"],
    14: ["prompt_governance/personas/operational"],
    15: ["prompt_governance/personas/architectural"],
    16: ["prompt_governance/personas/operational"],
    17: ["prompt_governance/personas/architectural"],
    18: ["prompt_governance/personas/operational"],
    19: ["prompt_governance/personas/architectural"],
    20: ["prompt_governance/personas/operational"],
    
    # Keys 21-25: Instructional Logic (THE LAW - Task Directives)
    21: ["prompt_governance/logic/instructional"],     # Task directives, workflow logic
    22: ["prompt_governance/logic/instructional"],
    23: ["prompt_governance/logic/instructional"],
    24: ["prompt_governance/logic/negative"],          # Constraints, exclusion lists
    25: ["prompt_governance/logic/negative"],
    
    # Keys 26-30: Security Prompts (THE LAW - Shield/Guardrails)
    26: ["prompt_governance/security/defensive"],      # System integrity, safety rules
    27: ["prompt_governance/security/defensive"],
    28: ["prompt_governance/security/injections"],     # Jailbreak tests, adversarial cases
    29: ["prompt_governance/security/injections"],
    30: ["prompt_governance/security/defensive"],
    
    # Keys 31-35: Canon Schemas (THE CONTRACTS - Mission Contracts)
    31: ["schemas/canon/blueprints"],       # Fission blueprints, module maps
    32: ["schemas/canon/blueprints"],
    33: ["schemas/canon/reports"],          # Validation reports, audit logs
    34: ["schemas/canon/reports"],
    35: ["schemas/canon"],                  # General canon schemas
    
    # Keys 36-39: API Schemas (THE CONTRACTS - Communication Contracts)
    36: ["schemas/api/internal"],           # Bus events, inter-agent messages
    37: ["schemas/api/internal"],
    38: ["schemas/api/external"],           # Tool specs, OpenAI schemas
    39: ["schemas/api/external"],
    
    # Keys 40-42: Core Architecture (THE BRAIN - All L1-L5 Layers)
    40: ["agentic_core"],                   # Architecture checks (depth, nesting)
    41: ["agentic_core"],                   # Atomicity checks (file size, LOC)
    42: ["agentic_core"],                   # Complexity checks (cyclomatic, cognitive)
    
    # Keys 43-45: Application Code (TARGET DOMAINS)
    43: ["apps_shared", "apps_rg", "apps_lic"],  # Application core logic
    44: ["apps_shared", "apps_rg", "apps_lic"],  # Application agents
    45: ["apps_shared", "apps_rg", "apps_lic"],  # Application utilities
    
    # Key 46: Execution Utilities (THE LABOR)
    46: ["scripts"],                        # Maintenance, deployment scripts
    
    # Key 47: Test Coverage (QA)
    47: ["tests"],                          # Unit, integration, e2e, adversarial tests
    
    # Keys 48-50: Telemetry (THE TELEMETRY)
    48: ["observability/logs"],             # Execution traces, error stacks
    49: ["observability/metrics"],          # Token usage, latency stats
    50: ["observability"],                  # General observability
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
        root_folder = rel_path.parts[0] if rel_path.parts else ""
        
        # Check if in allowed folder
        if root_folder in ALLOWED_ROOT_FOLDERS:
            return True, f"File in allowed folder: {root_folder}"
        
        # Check if in forbidden folder
        if root_folder in FORBIDDEN_ROOT_FOLDERS:
            return False, f"VOID VIOLATION: File in forbidden folder '{root_folder}' (out of scope)"
        
        # Unknown folder
        return False, f"VOID VIOLATION: File in unknown folder '{root_folder}' (not in ALLOWED_ROOT_FOLDERS)"
        
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
    Enforce Dependency Waterfall: Sovereign directories must NEVER import from apps_*.
    
    Waterfall Rule:
    - agentic_core/ (Sovereign) -> Can import: nothing from apps
    - prompt_governance/ (Sovereign) -> Can import: nothing from apps
    - schemas/ (Sovereign) -> Can import: nothing from apps
    - apps_shared/ -> Can import: agentic_core, schemas
    - apps_rg/, apps_lic/ -> Can import: agentic_core, schemas, apps_shared
    
    Args:
        file_path: Path to Python file
        project_root: Project root directory
        
    Returns:
        List of violation messages
    """
    violations = []
    
    try:
        rel_path = file_path.relative_to(project_root)
        parts = rel_path.parts
        
        # Check if file is in a sovereign directory
        is_sovereign = any(sov in parts for sov in ["agentic_core", "prompt_governance", "schemas"])
        
        if not is_sovereign:
            return violations
            
        # Read file and check imports
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Check for forbidden imports from apps
        forbidden_patterns = [
            "from apps_rg",
            "from apps_lic", 
            "from apps_shared",
            "import apps_rg",
            "import apps_lic",
            "import apps_shared",
        ]
        
        for pattern in forbidden_patterns:
            if pattern in content:
                violations.append(
                    f"WATERFALL VIOLATION (Key 40): Sovereign file imports from apps domain: '{pattern}'"
                )
                
    except Exception as e:
        logger.warning(f"Could not check import waterfall for {file_path}: {e}")
        
    return violations
