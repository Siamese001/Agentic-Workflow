from __future__ import annotations

#!/usr/bin/env python3
"""
L6 Runtime: Void Compliance Enforcer
Ensures files only exist in ALLOWED_ROOT_FOLDERS and enforces key-to-folder mapping.
"""
import ast
import logging
import os
import re
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint_config import (
    CORE_SUBFOLDER_MAP,
    FORBIDDEN_PATTERNS,
    FORBIDDEN_ROOT_FOLDERS,
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
    SOVEREIGN_REGISTRY,
)
from agentic_core.utils.ssot_discovery_validator import get_python_files

Logger = logging.getLogger(__name__)

# [ULTRA-HARDENING] All structural facts are derived exclusively from SSOT
CANONICAL_HIERARCHY = {root: cfg["subfolders"] for root, cfg in SOVEREIGN_REGISTRY.items()}
CANONICAL_DEPTH_MAP = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
# [PURGE] All hardcoded sets deleted - now derived from blueprint
FORBIDDEN_FILE_PATTERNS = FORBIDDEN_PATTERNS
HIGH_SIGNAL_KEYWORDS = {
    "healing",
    "testing",
    "validation",
    "execution",
    "orchestration",
    "state",
    "safety",
    "cognition",
    "intent",
    "learning",
    "planning",
}  # DEPRECATED: Replaced hardcoded CANON_SIGNALS

# [DESIGN UNIFICATION] Derive all allowed stages from the SSOT
ALLOWED_CORE_STAGES = set()
for stages in CORE_SUBFOLDER_MAP.values():
    ALLOWED_CORE_STAGES.update(stages)
ALLOWED_CORE_STAGES.update(CORE_SUBFOLDER_MAP.keys())

# Removed canon key mapping - deprecated system

# ==============================================================================
# FILE NAMING CONVENTIONS (Key 49 Hardening)
# ==============================================================================


def validate_file_naming(file_path: Path, project_root: Path) -> tuple[bool, str]:
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
        protected = ROOT_PROTECTED_FILES  # [GAP 16]
        if file_name in protected:
            return True, "Protected root file (Key 0 exempt)"

        # Sovereign markers are required for any root-level python logic
        sovereign_markers = {"validator", "compliance", "healer", "enforcer", "governor"}
        if not any(m in lower_stem for m in sovereign_markers):
            return (
                False,
                f"SOVEREIGN VIOLATION: Root file '{file_name}' Missing marker {sovereign_markers}.",
            )
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
GUIDANCE_EXAMPLES: dict[str, str] = {
    "agentic_core/L1_cognition/strategy": "Generic reasoning loops, high-level mission goal planning, and Task decomposition.",
    "agentic_core/L3_orchestration/fission": "Logic that splits large files into smaller modules or manages atomic code shifts.",
    "agentic_core/L4_state/memory": "Interfaces for persistent vector storage (Pinecone) used for long-term meta-learning.",
    "apps_shared/utils/validation": "Shared Pydantic models or regex patterns used across multiple app domains.",
    "apps_rg/agents/rankers": "scoring logic specifically for resume-to-JD matching (Domain-specific).",
    "config/agents/prompts": "System instructions and persona definitions used to initialize LLM sessions.",
    "scripts/operations/integrity": "Utilities that check for structural drift or 'Span of Two' violations.",
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

    return "agentic_core/L1_cognition"  # Default safe-haven for generic logic


def check_span_of_two_violation(folder_path: Path) -> tuple[bool, str]:
    """
    [NAMING RULE HARDENING] Enforces Minimum Span of 2.
    A Violation occurs ONLY if a folder contains exactly one meaningful child AND that child is a directory (a redundant tunnel).
    Folders containing only one file are valid 'leaves'.
    """
    if not folder_path.is_dir():
        return True, ""

    meaningful_children = [
        x
        for x in folder_path.iterdir()
        if x.name not in {".git", "__pycache__", ".pytest_cache", ".ruff_cache"}
        and not x.name.startswith(".")
    ]

    if len(meaningful_children) == 1 and meaningful_children[0].is_dir():
        return (
            False,
            f"SPAN-OF-TWO VIOLATION: Redundant tunnel '{folder_path.name}' -> flatten",
        )  # [GAP 4/13]

    return True, ""


# ==============================================================================
# KEY-TO-FOLDER MAPPING: Canon Key Enforcement
# ==============================================================================

# Removed canon key mapping - deprecated system


# ==============================================================================
# IMPORT CONVENTIONS ENFORCEMENT (Key 40/42 Hardening – Full Version)
# ==============================================================================

STDLIB_MODULES = {
    "os",
    "sys",
    "pathlib",
    "logging",
    "asyncio",
    "typing",
    "dataclasses",
    "collections",
    "json",
    "re",
    "datetime",
    "functools",
    "itertools",
    "abc",
    "enum",
    "contextlib",
    "threading",
    "time",
    "random",
    "math",
    "urllib",
    "http",
    "socket",
    "subprocess",
    "shutil",
}


def validate_import_conventions(file_path: Path, project_root: Path) -> list[str]:
    """
    Enforces L6 import conventions + expanded circular import detection.
    Exceptions:
    - Relative imports are allowed in __init__.py files (Facade Pattern)
    - __init__.py at root depth is allowed (package requirement)
    """
    violations = []
    try:
        rel_path = file_path.relative_to(project_root)
        own_root = rel_path.parts[0] if rel_path.parts else None
    except ValueError:
        return violations

    filename = file_path.name
    is_init_file = filename == "__init__.py"

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except Exception as e:
        violations.append(f"PARSE ERROR: Cannot analyze imports in {file_path.name}: {e}")
        return violations

    import_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Import | ast.ImportFrom)]
    import_nodes.sort(key=lambda n: n.lineno if hasattr(n, "lineno") else 0)

    # 1. No relative/star imports (except relative imports in __init__.py)
    for node in import_nodes:
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                # Relative imports are explicitly allowed in __init__.py files
                # as they are standard for exposing package APIs (Facade Pattern)
                if not is_init_file:
                    violations.append(
                        f"RELATIVE IMPORT FORBIDDEN (Line {node.lineno}): Use absolute paths (allowed in __init__.py only)."
                    )
            if any(a.name == "*" for a in node.names):
                violations.append(
                    f"STAR IMPORT FORBIDDEN (Line {node.lineno}): 'import *' detected."
                )

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
                violations.append(
                    f"IMPORT ORDER VIOLATION: {cat.capitalize()} appears before {prev_cat}."
                )
        if categories[cat]:
            prev_cat = cat

    # 3. Expanded Circular Risk
    if own_root and own_root in imported_roots:
        violations.append(f"DIRECT CIRCULAR RISK: File imports own root '{own_root}'.")

    return violations


# ==============================================================================
# ENFORCEMENT FUNCTIONS
# ==============================================================================


def validate_file_location(file_path: Path, project_root: Path) -> tuple[bool, str]:
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
        depth = len(parts)
        root_folder = parts[0]

        # Rule 0: Exempt the root structure
        if file_path.name == "__init__.py" or depth == 1:
            return True, "Sovereign Structural Component"

        # [ETERNAL DEPTH 4] Universal enforcement for all L-layers
        if root_folder == "agentic_core":
            agentic_core_exact_depth = SOVEREIGN_REGISTRY["agentic_core"][
                "depth"
            ]  # Legacy bridge – migrate to SOVEREIGN_REGISTRY
            if depth != agentic_core_exact_depth:
                reason = "SHALLOW" if depth < agentic_core_exact_depth else "DEEP"
                return (
                    False,
                    f"{reason} VIOLATION: '{rel_path}' depth {depth} != {agentic_core_exact_depth}",
                )

        # [ETERNAL DEPTH 3] All apps_* folders — exact depth 3
        if root_folder.startswith("apps_"):
            if depth != 3:
                reason = "SHALLOW" if depth < 3 else "DEEP"
                return False, f"{reason} VIOLATION (apps_*): '{rel_path}' depth {depth} != 3"

        # [ETERNAL DEPTH 3] tests/ folder lockdown
        if root_folder == "tests":
            if depth != 3:
                reason = "SHALLOW" if depth < 3 else "DEEP"
                return False, f"{reason} VIOLATION (tests): '{rel_path}' depth {depth} != 3"

        # Rule 1a: Core Stage Enforcement (Identity/Inference/Meta or P/S/L)
        if root_folder == "agentic_core":
            stage = parts[2]
            # Check against authorized list AND standard P/S/L naming convention
            if stage not in ALLOWED_CORE_STAGES and not (
                stage.startswith("P") or stage.startswith("S") or stage.startswith("L")
            ):
                return (
                    False,
                    f"UNAUTHORIZED STAGE: '{stage}' is not a recognized Sovereign territory.",
                )

        return True, f"{root_folder} depth verified"

        if root_folder in ALLOWED_ROOT_FOLDERS:
            return True, f"File in allowed root folder: {root_folder}"

        # Check if in forbidden folder
        if root_folder in FORBIDDEN_ROOT_FOLDERS:
            return False, f"VOID VIOLATION: Forbidden root folder '{root_folder}' (legacy numbered)"

        # [GAP FIX] Recursive Numbered Folder Check
        for part in parts:
            # Check if part is in FORBIDDEN_ROOT_FOLDERS
            if part in FORBIDDEN_ROOT_FOLDERS:
                return False, f"VOID VIOLATION: Forbidden folder '{part}' at any depth."

        # Check for numbered prefix pattern (NOT APPROVED)
        if root_folder and root_folder[0:2].isdigit() and root_folder[2:3] == "_":
            return (
                False,
                f"VOID VIOLATION: Numbered folder '{root_folder}' not approved (use approved folders only)",
            )

        # SOVEREIGN PROTECTION: Key 0 (General) must remain at Project Root
        validator_markers = {"validator", "compliance", "canon"}
        if root_folder.startswith("apps_") and any(
            m in file_path.name.lower() for m in validator_markers
        ):
            return (
                False,
                f"GRAVITY ERROR: Sovereign compliance logic ('{file_path.name}') leaked into downstream '{root_folder}'.",
            )

        # [L6 HARDENING] Strict Naming Enforcement
        is_name_valid, name_reason = validate_file_naming(file_path, project_root)
        if not is_name_valid:
            return False, name_reason

        return True, "Path and Name compliant."

    except ValueError:
        # File is outside project root
        return False, "VOID VIOLATION: File outside project root"


def enforce_void_compliance(
    files: list[Path], project_root: Path
) -> tuple[list[Path], list[tuple[Path, str]]]:
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
            Logger.warning(f"   [VOID] {file_path.name}: {reason}")

    return valid_files, violations


def get_folder_scope_summary(project_root: Path) -> dict[str, int]:
    """
    Generate summary of files per allowed folder.

    Args:
        project_root: Project root directory

    Returns:
        Dictionary mapping folder names to file counts
    """
    summary = dict.fromkeys(ALLOWED_ROOT_FOLDERS, 0)

    all_py = get_python_files(project_root)
    for folder in ALLOWED_ROOT_FOLDERS:
        folder_path = project_root / folder
        if folder_path.exists() and folder_path.is_dir():
            py_files = [f for f in all_py if str(f).startswith(str(folder_path))]
            summary[folder] = len(py_files)

    return summary


def generate_ascii_tree(start_path: Path, max_depth: int = 3) -> str:
    """[VISUALIZER] Returns the physical directory structure as an ASCII tree string."""
    tree = []
    start_path = start_path.resolve()
    tree.append(f"{start_path.name}/")

    def _add(path, prefix, depth):
        if depth > max_depth:
            return
        items = sorted([x for x in path.iterdir() if x.name not in {".git", "__pycache__"}])
        for i, item in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            tree.append(f"{prefix}{connector}{item.name}")
            if item.is_dir():
                _add(item, prefix + ("    " if i == len(items) - 1 else "│   "), depth + 1)

    _add(start_path, "", 1)
    return "\n".join(tree)


def check_span_of_two_violations(project_root: Path) -> list[tuple[Path, str]]:
    """
    Scans Sovereign Roots for Span of Two violations.
    Replaces the buggy total_children == 1 check to allow single-file leaves.
    """
    violations = []
    IGNORE_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".ruff_cache",
    }

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


def validate_canonical_hierarchy(project_root: Path) -> list[tuple[Path, str]]:
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
        root_files = [p.name for p in root_path.iterdir() if p.is_file() and p.suffix == ".py"]
        if root_files:
            violations.append(
                (
                    root_path,
                    f"DEPTH VIOLATION (Key 41): Files directly under Root '{root_key}' (depth 1). Found: {root_files}",
                )
            )

        # 2. Level 1 Validation (e.g., agentic_core -> L1_cognition)
        # layers is now a list of allowed L1 folders from SOVEREIGN_REGISTRY
        expected_l1 = set(layers) if isinstance(layers, list) else set(layers.keys())
        actual_l1 = {
            p.name for p in root_path.iterdir() if p.is_dir() and not p.name.startswith(".")
        }

        # Whitelist L6_meta for autonomous agents
        if "L6_meta" in actual_l1:
            expected_l1.add("L6_meta")

        unexpected_l1 = actual_l1 - expected_l1
        for bad in unexpected_l1:
            violations.append(
                (
                    root_path / bad,
                    f"HIERARCHY DRIFT: Unapproved L1 folder '{bad}'. Allowed: {expected_l1}",
                )
            )

        # 3. Level 2 Validation + Min Depth Enforcement
        # For L2 validation, we need to check CORE_SUBFOLDER_MAP for agentic_core
        if root_key == "agentic_core" and isinstance(layers, list):
            for l1_name in layers:
                l1_path = root_path / l1_name
                if not l1_path.exists():
                    continue

                # Get expected L2 folders from CORE_SUBFOLDER_MAP
                expected_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
                actual_l2_dirs = {
                    p.name for p in l1_path.iterdir() if p.is_dir() and not p.name.startswith(".")
                }
                actual_l2_files = [
                    p.name for p in l1_path.iterdir() if p.is_file() and p.suffix == ".py"
                ]

                # Whitelist autonomous agents to prevent drift violations
                AUTONOMOUS_WHITELIST = {
                    "autonomous_checkpoint_manager.py",
                    "autonomous_state_guardian.py",
                    "self_updating_safety_engine.py",
                    "neural_auto_immune_agent.py",
                }

                # Filter out whitelisted autonomous agents from violations
                actual_l2_files = [f for f in actual_l2_files if f not in AUTONOMOUS_WHITELIST]

                # Unexpected L2 folders
                unexpected_l2 = actual_l2_dirs - expected_l2
                for bad in unexpected_l2:
                    violations.append(
                        (
                            l1_path / bad,
                            f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}",
                        )
                    )
        elif isinstance(layers, dict):
            # Legacy dict format support
            for l1_name, l2_list in layers.items():
                l1_path = root_path / l1_name
                if not l1_path.exists():
                    continue

                expected_l2 = set(l2_list)
                actual_l2_dirs = {
                    p.name for p in l1_path.iterdir() if p.is_dir() and not p.name.startswith(".")
                }
                actual_l2_files = [
                    p.name for p in l1_path.iterdir() if p.is_file() and p.suffix == ".py"
                ]

                # Whitelist autonomous agents to prevent drift violations
                AUTONOMOUS_WHITELIST = {
                    "autonomous_checkpoint_manager.py",
                    "autonomous_state_guardian.py",
                    "self_updating_safety_engine.py",
                    "neural_auto_immune_agent.py",
                }

                # Filter out whitelisted autonomous agents from violations
                actual_l2_files = [f for f in actual_l2_files if f not in AUTONOMOUS_WHITELIST]

                # Unexpected L2 folders
                unexpected_l2 = actual_l2_dirs - expected_l2
                for bad in unexpected_l2:
                    violations.append(
                        (
                            l1_path / bad,
                            f"HIERARCHY DRIFT: Unapproved subfolder '{bad}' under '{l1_name}'. Allowed: {expected_l2}",
                        )
                    )

    return violations


def check_import_waterfall_violations(file_path: Path, project_root: Path) -> list[str]:
    """
    Unified Integrity Pass: Enforces Gravity (Waterfall) + Style (Conventions).
    """
    violations = []
    SYSTEM_FOLDERS = {
        ".venv",
        "venv",
        ".git",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".ruff_cache",
    }

    try:
        rel_path = file_path.relative_to(project_root)
        if not rel_path.parts or rel_path.parts[0] in SYSTEM_FOLDERS:
            return []
    except ValueError:
        return []

    # [PHASE 1] Gravity (Waterfall) Enforcement – FULLY DERIVED FROM structure_blueprint.py SSOT
    # Rationale (windsurfrules.md §2): Upstream sovereign roots MUST NOT import from downstream domains.
    # - Dynamically derive from SOVEREIGN_REGISTRY.keys() → zero drift on blueprint changes
    # - Upstream sovereign: non-apps_* roots and not 'tests' (currently only 'agentic_core')
    # - Downstream: all apps_* + 'tests'
    # - Regex catches root-level imports including submodules (e.g., 'from apps_shared.utils import X')
    # - No false positives within same root

    # [SSOT DERIVATION] Pull all root folders directly from the master blueprint
    all_registry_roots = set(SOVEREIGN_REGISTRY.keys())

    # Upstream sovereign: brain core + any future non-domain sovereign supports (e.g., prompt_governance, schemas)
    upstream_sovereign_roots = {
        root for root in all_registry_roots if not root.startswith("apps_") and root != "tests"
    }

    # Downstream: everything else (domains + tests)
    downstream_roots = all_registry_roots - upstream_sovereign_roots

    try:
        current_root = rel_path.parts[0]
    except IndexError:
        return violations

    # Gravity restriction applies only to files in upstream sovereign roots
    if current_root not in upstream_sovereign_roots:
        return violations

    # Read file content once
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return violations  # Skip unreadable files

    # Build regex only if there are downstream roots (defensive)
    if downstream_roots:
        forbidden_pattern = re.compile(
            r"^(?:import|from)\s+("
            + "|".join(map(re.escape, sorted(downstream_roots)))
            + r")(?:\.\w|\s|$)",
            re.MULTILINE,
        )

        matches = forbidden_pattern.findall(content)
        if matches:
            unique_matches = sorted(set(matches))
            violations.append(
                f"GRAVITY VIOLATION (SSOT Enforced): Upstream sovereign root '{current_root}' imports from downstream root(s): {unique_matches}. "
                "Rationale: Prevents core contamination. Move shared logic to apps_shared or sovereign runtime/utils."
            )

    # [PHASE 2] Convention Enforcement
    violations.extend(validate_import_conventions(file_path, project_root))

    return violations


def validate_sovereign_roots(project_root: Path) -> list[tuple[Path, str]]:
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
