"""
Structure Blueprint Config - Backward Compatible Shim

This module re-exports all public names from the refactored structure_blueprint
package for backward compatibility. All existing imports will continue to work.

The heavy data and regex patterns are now lazy-loaded from cold modules,
reducing import-time cost significantly.

MIGRATION GUIDE:
- Old: from agentic_core.L5_safety.config.structure_blueprint_config import X
- New: from agentic_core.L5_safety.config.structure_blueprint import X

Both paths will work, but the new path is preferred.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from re import Pattern
from typing import Any, Final

from agentic_core.L5_safety.config.structure_blueprint.artifacts import (
    get_app_specific_patterns_compiled,
    get_forbidden_backup_patterns_compiled,
)
from agentic_core.L5_safety.config.structure_blueprint.derived import (
    L4_APPROVED_FOLDERS,
    L4_SUBFOLDER_MAP,
)

# ============================================================================
# HOT IMPORTS (Always loaded - minimal cost)
# ============================================================================
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    # Layer validation
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    RUNTIME_STATE_JSON,
)
from agentic_core.L5_safety.config.structure_blueprint.territories import (
    SOVEREIGN_TERRITORIES,
)

# ============================================================================
# BACKWARD COMPATIBILITY - Compiled patterns (lazy)
# ============================================================================


# These are accessed as module-level variables but compiled lazily
def _get_app_specific_patterns():
    return get_app_specific_patterns_compiled()


def _get_forbidden_backup_patterns():
    return get_forbidden_backup_patterns_compiled()


# Expose as module attributes via __getattr__
_lazy_cache: dict[str, Any] = {}


def __getattr__(name: str):
    """Lazy load compiled patterns on first access."""
    if name == "APP_SPECIFIC_PATTERNS":
        if "APP_SPECIFIC_PATTERNS" not in _lazy_cache:
            _lazy_cache["APP_SPECIFIC_PATTERNS"] = get_app_specific_patterns_compiled()
        return _lazy_cache["APP_SPECIFIC_PATTERNS"]

    if name == "FORBIDDEN_BACKUP_PATTERNS":
        if "FORBIDDEN_BACKUP_PATTERNS" not in _lazy_cache:
            _lazy_cache["FORBIDDEN_BACKUP_PATTERNS"] = get_forbidden_backup_patterns_compiled()
        return _lazy_cache["FORBIDDEN_BACKUP_PATTERNS"]

    if name == "ROOT_WHITELIST":
        return set(SOVEREIGN_TERRITORIES.keys())

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ============================================================================
# REMAINING EXPORTS FROM ORIGINAL FILE (kept inline for now)
# These will be migrated to appropriate cold modules in future phases
# ============================================================================

VALIDATED_FILE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py",
        ".jinja",
        ".jinja2",
        ".j2",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".md",
        ".txt",
        ".rst",
        ".html",
        ".css",
        ".js",
        ".ts",
    },
)

NAMING_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "setup.py",
        "pyproject.toml",
        ".env",
        ".gitignore",
        ".dockerignore",
        "Dockerfile",
        "Makefile",
        "requirements.txt",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "LICENSE.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        ".editorconfig",
        ".prettierrc",
        ".eslintrc",
        ".gitattributes",
    },
)

NAMING_EXEMPT_DIRS: frozenset[str] = frozenset(
    {
        "archives",
        "data",
        "docs",
        "legacy_code",
        "legacy_engines",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        ".tox",
        "logs",
    },
)

FORBIDDEN_PATTERNS: Final[Sequence[Pattern]] = [
    re.compile("^utils\\.py$"),
    re.compile("^helper\\.py$"),
    re.compile("^temp\\.py$"),
    re.compile(".*_v\\d+\\.py$"),
    re.compile("^main\\.py$"),
    re.compile("^test\\.py$"),
    re.compile(".*_final\\.py$"),
    re.compile(".*_new\\.py$"),
    re.compile(".*_old\\.py$"),
    re.compile(".*_copy\\.py$"),
    re.compile(".*_backup\\.py$"),
    re.compile("^legacy_.*\\.py$"),
    re.compile("^.+_\\d+\\.py$"),
    re.compile("^draft_.*\\.py$"),
    re.compile(r"^utilities_.*"),
    re.compile(r".*_util_util\.py$"),
]

_STATIC_ROOT_PROTECTED_FILES: frozenset[str] = frozenset(
    {
        "canon_validator_agentic_v2.py",
        "canon_validator_agentic_v2_thin.py",
        "pyproject.toml",
        "README.md",
        "langgraph.json",
        ".env",
        "windsurfrules.md",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".coverage",
        "pytest.ini",
        "tox.ini",
        ".python-version",
        ".schema_violations_tracking.yaml",
        ".secrets.baseline",
        "archives_restoration_manifest.json",
        "audit_residual_rglob_results.json",
        "git.code-workspace",
        "current_test_status.txt",
        "mission_audit.csv",
    },
)

_DYNAMIC_ROOT_PROTECTED_FILES: frozenset[str] = frozenset(
    {
        AGENT_DISCOVERY_JSON,
        AGENT_DISCOVERY_MANIFEST_JSON,
        RUNTIME_STATE_JSON,
    },
)

ROOT_PROTECTED_FILES: frozenset[str] = _STATIC_ROOT_PROTECTED_FILES | _DYNAMIC_ROOT_PROTECTED_FILES

PROJECT_ROOT_WHITELIST: Final[frozenset[str]] = frozenset(
    {
        "agentic_core",
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "ops_scripts",
        "tests",
        "docs",
        "data",
        "archives",
        ".git",
        ".github",
        ".gravity_state",
        ".backup",
        ".vscode",
    },
)

ROOT_ALLOWED_PATTERNS: Final[Sequence[Pattern]] = [
    re.compile(r"^trace_.*\.jsonl$"),
    re.compile(r"^mission_.*\.log$"),
    re.compile(r"^.*\.bat$"),
    re.compile(r"^.*\.sh$"),
    re.compile(r"^root_drift_.*\.py$"),
]

SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "venv_stable",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        ".mypy_cache",
        ".tox",
        "archives",
        "legacy_code",
        "legacy_engines",
        "legacy_resume_gen",
        "data",
        "docs",
        "env",
        "build",
        "dist",
        "_build",
        "Lib",
        "site-packages",
        "google",
        "gapic",
        "logging",
        "licenses",
        "src",
        "pip",
        "dist-info",
        "raw",
        "golden_state",
        "logs",
        "processed",
        "shared",
        "refs",
        "remotes",
        "v",
        "stubs",
        ".sovereign_healing_backup",
        ".idea",
        ".vscode",
        ".DS_Store",
        "Thumbs.db",
    },
)

FORBIDDEN_FOLDER_PATTERN: Pattern = re.compile(r"^\d+_")

FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset(
    {
        "legacy_code",
        "legacy_engines",
        "legacy_resume_gen",
        "old_core",
    },
)

TESTS_ROOT_FILE_WHITELIST: frozenset[str] = frozenset(
    {
        "conftest.py",
        "pytest.ini",
        "sovereign_smoke_test.py",
        "test_autonomous_improvements.py",
    },
)

AUTONOMOUS_AGENT_WHITELIST: frozenset[str] = frozenset(
    {
        "autonomous_checkpoint_manager.py",
        "autonomous_state_guardian.py",
        "self_updating_safety_engine.py",
        "neural_auto_immune_agent.py",
    },
)

protected_folders: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS
ignore_dirs: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS
sovereign_ignored_folders: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS

HEALING_CONFIG: Final[Mapping[str, int]] = {
    "max_rounds": int(os.getenv("MAX_HEALING_ROUNDS", "10")),
    "max_per_file": int(os.getenv("MAX_HEALING_PER_FILE", "8")),
    "global_budget": int(os.getenv("GLOBAL_HEALING_BUDGET", "500")),
    "max_moves_per_run": 250,
    "max_shared_upgrades_per_run": 10,
    "max_fissions_per_run": 50,
    "dust_threshold": 40,
}

AGENT_RESILIENCE_CONFIG: Final[Mapping[str, int | float]] = {
    "retry_count": int(os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5")),
}

MISSION_CONFIG: Final[Mapping[str, bool | int]] = {
    "GRAVITY_SURGERY_ENABLED": True,
    "hierarchy_healing_enabled": True,
    "span_surgery_enabled": True,
    "fission_enabled": True,
    "run_full_mission": True,
    "run_hierarchy_healing": True,
    "run_gravity_refactor": True,
    "run_sprawl_surgery": True,
    "structural_only_mode": False,
    "timeout_seconds": int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800")),
}

MCP_CAPABILITIES: Final[Mapping[str, Mapping[str, bool | str]]] = {
    "router": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "marketplace_filter": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "filesystem": {"enabled": True, "path": "agentic_core.L4_state.filesystem"},
    "figma": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "fetch": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "semantic_cache": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
}

SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset(
    {
        "stubs",
        ".sovereign_healing_backup",
        "__pycache__",
    },
)

ALLOWED_DUPLICATE_FILENAMES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "context.py",
        "config.py",
        "constants.py",
        "exceptions.py",
        "types.py",
        "models.py",
        "base.py",
        "utils.py",
        "helpers.py",
        "common.py",
        "observability.py",
        "metrics.py",
        "logging.py",
        "tracing.py",
        "proactive.py",
        "autonomous.py",
        "self_healing.py",
        "prompts.py",
        "templates.py",
    },
)

DISCOVERY_EXCLUDED_TERRITORIES: frozenset[str] = frozenset(
    {
        "runtime_shared",
        "legacy_code",
        "legacy_engines",
        "archives",
        "stubs",
        "examples",
    },
)

PYTHON_STDLIB_MODULES: frozenset[str] = frozenset(
    {
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
        "hashlib",
        "uuid",
        "copy",
        "io",
        "traceback",
        "inspect",
        "importlib",
        "warnings",
        "pickle",
    },
)

GLOBAL_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "build",
        "dist",
        ".eggs",
        ".git",
        ".svn",
        ".hg",
        ".venv",
        "venv",
        "env",
        ".env",
        "node_modules",
        "coverage_html",
        "htmlcov",
        ".coverage",
        "reports",
        "archives",
        ".sovereign_healing_backup",
        "tests",
    },
)

GRAVITY_CONFIG: Any = {
    "enabled": True,
    "UPSTREAM_SOVEREIGN_ROOTS": ["agentic_core"],
    "downstream_domains": ["apps_rg", "apps_lic", "apps_shared", "tests"],
    "exemptions": [],
}

GRAVITY_SURGERY_ENABLED: Any = GRAVITY_CONFIG["enabled"]
UPSTREAM_SOVEREIGN_ROOTS: Any = frozenset(GRAVITY_CONFIG["UPSTREAM_SOVEREIGN_ROOTS"])
DOWNSTREAM_ROOTS: Any = frozenset(GRAVITY_CONFIG["downstream_domains"])


def safe_prefixed_filename(prefix: str, filename: str) -> str:
    """Generate a prefixed filename WITHOUT duplicate prefixes."""
    if not prefix:
        return filename
    prefix = prefix.rstrip("_")
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    if stem.startswith(prefix + "_") or stem == prefix:
        return filename
    return f"{prefix}_{filename}"


def validate_no_duplicate_prefix(filename: str) -> tuple[bool, str]:
    """Detect if a filename has duplicate prefixes."""
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    parts = stem.split("_")
    for i in range(len(parts) - 1):
        if parts[i] == parts[i + 1] and parts[i]:
            return True, f"Duplicate prefix detected: '{parts[i]}_' repeated in '{filename}'"
    return False, ""


def is_path_allowed(rel_path: str | Path) -> bool:
    """Determines if a path conforms to SOVEREIGN_TERRITORIES."""
    original_path = str(rel_path).replace("\\", "/")
    if "//" in original_path:
        return False
    normalized_path = os.path.normpath(original_path).replace("\\", "/")
    if not normalized_path or normalized_path.startswith("..") or normalized_path == ".":
        return False
    parts = [p for p in normalized_path.split("/") if p]
    if not parts:
        return False
    if len(parts) == 1:
        if parts[0] in SOVEREIGN_TERRITORIES:
            return True
        return parts[0] in ROOT_PROTECTED_FILES or parts[0] in ALLOWED_DUPLICATE_FILENAMES
    root = parts[0]
    if root not in SOVEREIGN_TERRITORIES:
        return False
    config = SOVEREIGN_TERRITORIES[root]
    filename = parts[-1]
    if root == "agentic_core":
        if filename.startswith(("rg_", "lic_", "test_")):
            if not (filename == "__init__.py" or "L0_maintenance/scripts" in normalized_path):
                return False
    path_depth = len(parts)
    folder_depth = path_depth - 1 if "." in filename else path_depth
    if folder_depth > config["depth"] + 1 and not is_l4_approved(normalized_path):
        return False
    if folder_depth > config["depth"] + 2:
        return False
    if len(parts) > 1:
        sub_name = parts[1]
        allowed_subs = config["subfolders"]
        if isinstance(allowed_subs, dict) and sub_name in allowed_subs:
            sub_cfg = allowed_subs[sub_name]
            if isinstance(sub_cfg, dict):
                patterns = sub_cfg.get("forbidden_patterns", [])
                if any(re.search(p, normalized_path) for p in patterns):
                    return False
        if isinstance(allowed_subs, dict):
            if sub_name not in allowed_subs:
                return sub_name.endswith(".py")
        elif isinstance(allowed_subs, list):
            if sub_name not in allowed_subs:
                if "." in sub_name and len(parts) <= config["depth"] + 1:
                    return True
                return False
    return True


def is_l4_approved(path: str) -> bool:
    """Helper to verify L4 specializations."""
    parts = [p for p in path.split("/") if p]
    if len(parts) < 4:
        return False
    root, l2, l3, l4 = parts[0], parts[1], parts[2], parts[3]
    folder_parts = parts[:-1] if parts and "." in parts[-1] else parts
    if len(folder_parts) != 4:
        return False
    try:
        full_folder_path = f"{root}/{l2}/{l3}"
        if full_folder_path in L4_APPROVED_FOLDERS:
            l4_structure = L4_SUBFOLDER_MAP.get(l2, {})
            if isinstance(l4_structure, dict) and l3 in l4_structure:
                l3_structure = l4_structure[l3]
                if isinstance(l3_structure, dict):
                    if l4 in l3_structure:
                        return True
                    for subfolder_list in l3_structure.values():
                        if isinstance(subfolder_list, list) and l4 in subfolder_list:
                            return True
        root_cfg = SOVEREIGN_TERRITORIES.get(root, {})
        subs = root_cfg.get("subfolders", {})
        if not isinstance(subs, dict):
            return False
        l2_cfg = subs.get(l2, {})
        if isinstance(l2_cfg, dict):
            l3_cfg = l2_cfg.get(l3, {})
            if isinstance(l3_cfg, dict):
                specs = l3_cfg.get("l4_specializations", [])
                if l4 in specs:
                    return True
        return False
    except (KeyError, TypeError, AttributeError):
        return False


# Placeholder for remaining large exports - will be migrated in future phases
# These are kept as stubs to maintain import compatibility

L2_TO_L1_MAP: Final[Mapping[str, str]] = {
    "reasoning": "CONTEXT_DEPENDENT",
    "enforcement": "CONTEXT_DEPENDENT",
    "validators": "CONTEXT_DEPENDENT",
    "utils": "CONTEXT_DEPENDENT",
    "config": "CONTEXT_DEPENDENT",
    "types": "CONTEXT_DEPENDENT",
    "scripts": "L0_maintenance",
    "tools": "L2_execution",
    "memory": "L4_state",
    "dashboards": "L6_observability",
    "templates": "prompt_governance",
    "meta_prompts": "prompt_governance",
    "rendering": "prompt_governance",
    "version_registry": "prompt_governance",
    "environments": "config",
    "feature_flags": "config",
    "models": "runtime",
    "messages": "runtime",
}

EXERCISER_REGISTRY: Final[Mapping[str, str]] = {
    "L5_safety": "L5SafetyExerciserAgent",
    "L4_state": "L4StateExerciserAgent",
    "L1_cognition": "L1CognitionExerciserAgent",
    "L2_execution": "GeneralExerciserAgent",
    "L3_orchestration": "GeneralExerciserAgent",
    "L0_maintenance": "GeneralExerciserAgent",
    "observability": "GeneralExerciserAgent",
    "utils": "GeneralExerciserAgent",
    "config": "GeneralExerciserAgent",
    "prompt_governance": "GeneralExerciserAgent",
    "patterns": "GeneralExerciserAgent",
    "semantic_memory": "GeneralExerciserAgent",
    "knowledge": "GeneralExerciserAgent",
}

PLACEMENT_CONFIDENCE = {
    "HIGH": 0.8,
    "MEDIUM": 0.5,
    "LOW": 0.3,
    "REJECT": 0.0,
}

# Stub for ROOT_WHITELIST - derived from SOVEREIGN_TERRITORIES
ROOT_WHITELIST: set[str] = set(SOVEREIGN_TERRITORIES.keys())
