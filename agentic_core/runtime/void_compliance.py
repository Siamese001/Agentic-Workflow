#!/usr/bin/env python3
"""
L6 Runtime: Void Compliance Enforcer
Ensures files only exist in ALLOWED_ROOT_FOLDERS and enforces key-to-folder mapping.
"""
from typing import Any, Optional, Protocol, Dict, List


import logging
import os
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


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
    [SSOT] Provides the LLM with the canonical target based on code signatures.
    Used by agents to prevent architectural hallucinations.
    """
    if "import pinecone" in content_preview or "upsert" in content_preview:
        return "apps_shared/infrastructure/vector"
    if "class HealerAgent" in content_preview or "mission" in content_preview:
        return "agentic_core/L1_cognition/strategy"
    if "def split_file" in content_preview:
        return "agentic_core/L3_orchestration/fission"
    return "UNKNOWN: Consult CANONICAL_HIERARCHY for placement."

def check_span_violation(folder_path: Path) -> Tuple[bool, str]:
    """Enforces Minimum Span of 2: prevents redundant single-child nesting."""
    if not folder_path.is_dir(): return True, ""
    children = [x for x in folder_path.iterdir() if x.name not in {".git", "__pycache__"}]
    
    # [KEY 49 VIOLATION] Detect single-child antipattern
    if len(children) == 1 and children[0].is_dir():
        return False, f"SPAN VIOLATION: '{folder_path.name}' is a single-child tunnel to '{children[0].name}'. Flatten."
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
    """Enforces the 'Span-of-Two' rule: Folders must have ≥2 meaningful children or be a leaf."""
    violations = []
    SYSTEM_FOLDERS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}
    
    for root_name in ALLOWED_ROOT_FOLDERS:
        root_path = project_root / root_name
        if not root_path.is_dir(): continue
            
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter out system junk
            dirnames[:] = [d for d in dirnames if d not in SYSTEM_FOLDERS and not d.startswith(".")]
            current_dir = Path(dirpath)
            
            # Count meaningful children (dirs + files)
            meaningful_files = [f for f in filenames if not f.startswith(".")]
            total_children = len(dirnames) + len(meaningful_files)
            
            if total_children == 1:
                child_name = dirnames[0] if dirnames else meaningful_files[0]
                violations.append((current_dir, f"SPAN-OF-TWO: '{current_dir.name}' only contains '{child_name}'. Flatten this structure."))
    
    return violations


def check_import_waterfall_violations(file_path: Path, project_root: Path) -> List[str]:
    """
    Enforces the Gravity Model: Upstream (Sovereign) roots cannot import 
    from Downstream (App) roots or lower-ranked Sovereigns.
    """
    violations = []
    SYSTEM_FOLDERS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache"}

    try:
        rel_path = file_path.relative_to(project_root)
        if not rel_path.parts or rel_path.parts[0] in SYSTEM_FOLDERS:
            return []
    except ValueError:
        return []

    # [RANKED GRAVITY] Higher index cannot be imported by lower index
    SOVEREIGN_RANKING = ["agentic_core", "prompt_governance", "schemas", "config", "scripts"]
    DOWNSTREAM_APPS = {"apps_rg", "apps_lic", "apps_shared"}
    
    current_root = rel_path.parts[0]
    if current_root not in SOVEREIGN_RANKING:
        return [] 
        
    current_rank = SOVEREIGN_RANKING.index(current_root)
    forbidden_roots = set(SOVEREIGN_RANKING[current_rank + 1:]) | DOWNSTREAM_APPS

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            file_content = f.read()
            tree = ast.parse(file_content, filename=str(file_path))
            
        # 1. AST Validation (Static Imports)
        for node in ast.walk(tree):
            module_name = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.level == 0: # Catch absolute imports only
                    module_name = node.module.split('.')[0]
                
            if module_name in forbidden_roots:
                violations.append(f"GRAVITY VIOLATION (static): '{current_root}' -> '{module_name}' (Line {node.lineno})")

        # 2. Raw String Safety Net (Catches dynamic/hidden imports)
        for forbidden in forbidden_roots:
            if f"'{forbidden}'" in file_content or f'"{forbidden}"' in file_content:
                violations.append(f"GRAVITY VIOLATION (dynamic/string): Forbidden root '{forbidden}' detected in string literal.")
                
    except (SyntaxError, Exception) as e:
        if not isinstance(e, SyntaxError):
            logger.warning(f"Waterwall check error on {file_path.name}: {e}")
        
    return violations
