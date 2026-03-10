"""
Artifacts Module - COLD PATH (File Patterns and Prefixes)

This module contains app-specific patterns, forbidden patterns, and
file artifact routing rules. Regex patterns are stored as strings
and compiled lazily.

Loaded lazily on first access.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from re import Pattern
from typing import Final

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ============================================================================
# APP-SPECIFIC PREFIXES
# ============================================================================

APP_SPECIFIC_PREFIXES: Final[Mapping[str, str]] = {
    "rg_": "apps_rg",
    "lic_": "apps_lic",
    "resume_": "apps_rg",
    "outreach_": "apps_rg",
    "dispatch_resume": "apps_rg",
    "dispatch_outreach": "apps_rg",
    "contact_research": "apps_rg",
    "company_research": "apps_rg",
}

STUTTERING_PREFIX_MAP: Final[Mapping[str, str]] = {
    "r_g_": "rg_",
    "l_i_c_": "lic_",
}

APP_SPECIFIC_TARGET_SUBFOLDER: str = "reasoning"


# ============================================================================
# APP-SPECIFIC PATTERNS (Strings - Compiled Lazily)
# ============================================================================

APP_SPECIFIC_PATTERN_STRINGS: Final[Sequence[str]] = [
    r"^rg_.*\.py$",
    r"^lic_.*\.py$",
    r"^resume_.*\.py$",
    r"^outreach_.*\.py$",
    r"^dispatch_(resume|outreach).*\.py$",
]


# ============================================================================
# FORBIDDEN LAYER PREFIXES
# ============================================================================

FORBIDDEN_LAYER_PREFIXES: Final[tuple[str, ...]] = (
    "l0_",
    "l1_",
    "l2_",
    "l3_",
    "l4_",
    "l5_",
    "l6_",
    "L0_",
    "L1_",
    "L2_",
    "L3_",
    "L4_",
    "L5_",
    "L6_",
    "p0_",
    "p1_",
    "p2_",
    "p3_",
    "P0_",
    "P1_",
    "P2_",
    "P3_",
)


# ============================================================================
# FORBIDDEN BACKUP PATTERNS (Strings - Compiled Lazily)
# ============================================================================

FORBIDDEN_BACKUP_PATTERN_STRINGS: Final[Sequence[str]] = [
    r".*\.bak\.\d+$",
    r".*\.backup\.\d+$",
    r".*\.old\.\d+$",
    r".*\.tmp\.\d+$",
]


# ============================================================================
# FORBIDDEN FILENAME PATTERNS
# ============================================================================

FORBIDDEN_FILENAME_PATTERNS: Final[Sequence[Mapping[str, str]]] = [
    {
        "pattern": r"(?<![a-z])[a-z]_[a-z]_[a-z]_[a-z]",
        "reason": "Stuttering Acronym Violation (naive CamelCase split). "
        "Fix: collapse single-char segments (e.g., s_s_o_t → ssot).",
    },
    {
        "pattern": r"(?<!^)_{2,}(?!init__|pycache__)",
        "reason": "Multiple Underscore Violation (unsanitized concatenation). "
        "Fix: collapse to single underscore (e.g., setup___init___ → setup_init).",
    },
    {
        "pattern": r"^_[a-z]",
        "reason": "Leading Underscore Violation (non-__init__ file). "
        "Fix: remove leading underscore or rename to descriptive name.",
    },
]


# ============================================================================
# FORBIDDEN EPHEMERAL PATTERNS
# ============================================================================

FORBIDDEN_EPHEMERAL_PATTERNS: Final[Sequence[str]] = [
    r"(?i)phase\s*\d",
    r"(?i)wave\s*[\d_]",
    r"(?i)sprint\d",
]

EPHEMERAL_PATTERN_EXEMPTIONS: Final[Sequence[str]] = [
    r"(?i)two_?phase",
    r"(?i)execution_phase",
    r"(?i)mutation_phase",
    r"(?i)research_hop_phase",
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_correct_app_folder(filename: str) -> str | None:
    """Return the correct root app folder for a file based on prefix."""
    for prefix, folder in APP_SPECIFIC_PREFIXES.items():
        if filename.startswith(prefix):
            return folder
    return None


def get_correct_app_path(filename: str) -> str | None:
    """Return the full recommended path for app-specific files."""
    root = get_correct_app_folder(filename)
    if root:
        return f"{root}/{APP_SPECIFIC_TARGET_SUBFOLDER}"
    return None


# Files explicitly allowed to carry layer prefixes because they ARE canonical
# spec/type modules that document which layer they belong to.
# Adding here prevents them being flagged as cross-layer naming violations.
LAYER_PREFIX_FILENAME_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        "l2_phase_spec.py",   # agentic_core/L2_execution/types/ — L2 execution plan spec
        "l4_registries.py",   # agentic_core/evaluation/retrieval/ — L4 state registries
        "l1_meta_adapter.py", # system_learning/adapters/ — L1 cognition meta adapter
    }
)


def has_forbidden_layer_prefix(filename: str) -> str | None:
    """Check if filename starts with a forbidden layer/priority prefix."""
    if filename in LAYER_PREFIX_FILENAME_ALLOWLIST:
        return None
    if filename.startswith(FORBIDDEN_LAYER_PREFIXES):
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if filename.startswith(prefix):
                return prefix
    return None


# ============================================================================
# LAZY COMPILED PATTERN ACCESSORS
# ============================================================================


@lru_cache(maxsize=1)
def get_app_specific_patterns_compiled() -> list[Pattern]:
    """Compile and cache app-specific patterns."""
    return [re.compile(p) for p in APP_SPECIFIC_PATTERN_STRINGS]


@lru_cache(maxsize=1)
def get_forbidden_backup_patterns_compiled() -> list[Pattern]:
    """Compile and cache forbidden backup patterns."""
    return [re.compile(p) for p in FORBIDDEN_BACKUP_PATTERN_STRINGS]


@lru_cache(maxsize=1)
def get_forbidden_ephemeral_patterns_compiled() -> list[Pattern]:
    """Compile and cache forbidden ephemeral patterns."""
    return [re.compile(p) for p in FORBIDDEN_EPHEMERAL_PATTERNS]


@lru_cache(maxsize=1)
def get_ephemeral_exemption_patterns_compiled() -> list[Pattern]:
    """Compile and cache ephemeral exemption patterns."""
    return [re.compile(p) for p in EPHEMERAL_PATTERN_EXEMPTIONS]


def is_app_specific_file(filename: str) -> bool:
    """Check if a file should be in an app folder, not agentic_core."""
    patterns = get_app_specific_patterns_compiled()
    return any(pattern.match(filename) for pattern in patterns)


def is_broken_backup_file(filename: str) -> bool:
    """Check if filename matches broken backup pattern."""
    patterns = get_forbidden_backup_patterns_compiled()
    return any(pattern.match(filename) for pattern in patterns)


# Backward compatibility - expose compiled patterns as APP_SPECIFIC_PATTERNS
# This is a property that compiles on first access
@property
def APP_SPECIFIC_PATTERNS() -> list[Pattern]:
    """Backward compatibility accessor for compiled patterns."""
    return get_app_specific_patterns_compiled()


@property
def FORBIDDEN_BACKUP_PATTERNS() -> list[Pattern]:
    """Backward compatibility accessor for compiled patterns."""
    return get_forbidden_backup_patterns_compiled()


# ============================================================================
# MIGRATED FROM MONOLITH (structure_blueprint_config.py) — 2026-02-08
# ============================================================================

# ============================================================================
# ARTIFACT ROUTING MAP (The "Customs" Agent Logic)
# ============================================================================
# Routes non-code artifacts and standalone scripts based on INTELLIGENT CONTENT SIGNATURES.
# [SSOT 2026-01-27] Ultra-Hardened: Includes strict 'forbidden_signals' to prevent gravity leakage.
ARTIFACT_ROUTING_MAP: Final[Mapping[str, Mapping[str, Any]]] = {
    # === DOCS & REPORTS ===
    "docs/reports/assessments": {
        "description": "Gap analyses, architectural assessments, and strategic reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "keywords": ["assessment", "analysis", "gap", "architecture", "strategic"],
        },
        "naming_patterns": [
            re.compile(r".*assessment.*"),
            re.compile(r".*analysis.*"),
            re.compile(r".*gap.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/audit": {
        "description": "Structural audits, drift analysis, and compliance reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "headers": ["# Audit Report", "## Violations", "## Drift"],
            "json_keys": ["critical_violations", "compliance_score", "drift_metrics"],
            "keywords": ["audit", "drift", "variance", "compliance", "SSOT"],
        },
        "naming_patterns": [
            re.compile(r".*audit.*"),
            re.compile(r".*drift.*"),
            re.compile(r".*variance.*"),
            re.compile(r".*compliance.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/coverage": {
        "description": "Test coverage reports and code quality metrics.",
        "file_extensions": [".md", ".json", ".html", ".xml", ".txt"],
        "content_signals": {
            "keywords": ["coverage", "test", "quality", "percentage", "htmlcov"],
        },
        "naming_patterns": [
            re.compile(r".*coverage.*"),
            re.compile(r".*test.*"),
            re.compile(r".*quality.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/security": {
        "description": "Security assessments, vulnerability scans, and safety reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "keywords": ["security", "vulnerability", "safety", "hardened", "guardrails"],
        },
        "naming_patterns": [
            re.compile(r".*security.*"),
            re.compile(r".*vulnerability.*"),
            re.compile(r".*hardened.*"),
            re.compile(r".*hardening.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/telemetry": {
        "description": "System telemetry, performance metrics, and observability data.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "keywords": ["telemetry", "metrics", "performance", "observability"],
        },
        "naming_patterns": [
            re.compile(r".*telemetry.*"),
            re.compile(r".*metrics.*"),
            re.compile(r".*performance.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/missions": {
        "description": "High-level mission execution traces and runtime logs (Deported from Root).",
        "file_extensions": [".jsonl", ".trace", ".log", ".json"],
        "content_signals": {
            "json_keys": ["mission_id", "trace_id", "execution_log"],
            "keywords": ["mission", "trace", "execution"],
        },
        "naming_patterns": [
            re.compile(r".*mission.*"),
            re.compile(r".*trace.*"),
            re.compile(r".*execution.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    # === DATA & LOGS (Runtime Debugging) ===
    "agentic_core/L0_routing/utils": {
        "description": "Runtime debug logs, error dumps, and stack traces.",
        "file_extensions": [".log", ".err", ".out", ".txt"],
        "content_signals": {
            "keywords": [
                "DEBUG",
                "ERROR",
                "Traceback (most recent call)",
                "Exception",
                "Stack trace",
            ],
        },
        "naming_patterns": [
            re.compile(r".*debug.*"),
            re.compile(r".*error.*"),
            re.compile(r".*crash.*"),
        ],
        # HARDENING: Explicitly forbid Python scripts even if they contain the word "error"
        "forbidden_extensions": [".py", ".pyc", ".pyo"],
        "forbidden_keywords": ["def main", "if __name__", "import sys", "class "],
    },
    # === PYTHON UTILITY SCRIPTS (Standalone) ===
    "agentic_core/L0_routing/scripts": {
        "description": "Python utility scripts, maintenance tools, and standalone executables.",
        "file_extensions": [".py"],
        "content_signals": {
            "keywords": [
                "def main(",
                "if __name__",
                "#!/usr/bin/env python",
                "import sys",
                "argparse",
                "click",
                "typer",
            ],
            "imports": ["os", "sys", "shutil", "pathlib", "logging"],
        },
        "naming_patterns": [
            re.compile(r".*script.*"),
            re.compile(r".*fixer.*"),
            re.compile(r".*tool.*"),
            re.compile(r".*util.*"),
            re.compile(r".*cleaner.*"),
            re.compile(r".*migrat.*"),
        ],
        # HARDENING: Prevent Tests and Core Modules from being misclassified as scripts
        "forbidden_keywords": [
            "class Test",
            "def test_",
            "import unittest",
            "import pytest",  # Not a Test
            "class BaseAgent",
            "class Sovereign",  # Not a Core Agent
        ],
    },
    # === MISSION TRACES (Root Approved) ===
    "logs": {
        "description": "High-level Mission Execution Traces (Approved for Root).",
        "file_extensions": [".jsonl", ".trace"],
        "content_signals": {
            "json_keys": ["mission_id", "step_count", "agent_action", "thought_process"],
        },
        "naming_patterns": [re.compile(r"^trace_.*"), re.compile(r"^mission_.*")],
        # HARDENING: Prevent generic JSON data or debug logs
        "forbidden_keywords": ["Traceback", "Exception", "dataset_version"],
    },
    # === DATASETS ===
    "data/processed": {
        "description": "Structured data outputs and intermediate processing states.",
        "file_extensions": [".json", ".csv", ".parquet"],
        "content_signals": {
            "json_keys": ["dataset_version", "record_count", "processed_at", "schema_version"],
        },
        "naming_patterns": [
            re.compile(r".*dataset.*"),
            re.compile(r".*processed.*"),
            re.compile(r"agent_discovery.*\.json$"),
            re.compile(r".*manifest.*\.json$"),
        ],
        # HARDENING: Prevent config files or code
        "forbidden_keywords": ["def ", "class ", "api_key", "secret"],
    },
}


# ============================================================================
# ARTIFACT ROUTING VALIDATION UTILITIES
# ============================================================================


def validate_artifact_routing(
    filename: str,
    content: str | None = None,
) -> tuple[bool, str | None, str | None]:
    """
    Validate file against ARTIFACT_ROUTING_MAP negative logic.

    Implements HARD REJECT for files that match forbidden_extensions or forbidden_keywords
    ONLY when they would otherwise match the positive signals for that destination.
    This prevents gravity leakage where code files get misclassified as reports/logs/data.

    Args:
        filename: Name of the file to validate
        content: Optional file content for keyword checking

    Returns:
        Tuple of (is_valid, matched_destination, rejection_reason)
        - is_valid: False if file matches forbidden signals (HARD REJECT)
        - matched_destination: Destination path if positive match found
        - rejection_reason: Reason for rejection if is_valid is False

    Example:
        >>> validate_artifact_routing("test_report.py", "def main():")
        (False, None, "Forbidden extension .py for destination docs/reports")

        >>> validate_artifact_routing("audit_results.md", "# Assessment Report")
        (True, "docs/reports", None)
    """
    file_ext = Path(filename).suffix.lower()

    for dest, rules in ARTIFACT_ROUTING_MAP.items():
        # First check if file would match positive signals for this destination
        allowed_exts = rules.get("file_extensions", [])
        matches_positive = False

        # Check extension match
        if allowed_exts and file_ext in allowed_exts:
            matches_positive = True

        # Check naming patterns
        naming_patterns = rules.get("naming_patterns", [])
        if naming_patterns:
            for pattern in naming_patterns:
                if pattern.match(filename):
                    matches_positive = True
                    break

        # Check content signals if provided
        if content and matches_positive:
            content_signals = rules.get("content_signals", {})

            # Check headers
            headers = content_signals.get("headers", [])
            if headers and any(header in content for header in headers):
                matches_positive = True

            # Check keywords
            keywords = content_signals.get("keywords", [])
            if keywords and any(keyword in content for keyword in keywords):
                matches_positive = True

        # ONLY apply negative checks if file matches positive signals
        if matches_positive:
            # 1. NEGATIVE EXTENSION CHECK (HARD REJECT)
            forbidden_exts = rules.get("forbidden_extensions", [])
            if forbidden_exts and file_ext in forbidden_exts:
                return (False, None, f"Forbidden extension {file_ext} for destination {dest}")

            # 2. NEGATIVE CONTENT CHECK (HARD REJECT)
            if content:
                forbidden_keywords = rules.get("forbidden_keywords", [])
                if forbidden_keywords:
                    for keyword in forbidden_keywords:
                        if keyword in content:
                            return (
                                False,
                                None,
                                f"Forbidden keyword '{keyword}' for destination {dest}",
                            )

            # Passed all checks - return positive match
            return (True, dest, None)

    # No match found (neither positive nor negative)
    return (True, None, None)


def check_forbidden_signals(filename: str, content: str | None = None) -> str | None:
    """
    Quick check for forbidden signals across all routing rules.

    Returns rejection reason if file matches any forbidden_extensions or forbidden_keywords,
    None otherwise.

    This is a fast-path check for agents that only need to know if a file is forbidden,
    without needing the full routing destination.

    Args:
        filename: Name of the file to check
        content: Optional file content for keyword checking

    Returns:
        Rejection reason string if forbidden, None if allowed
    """
    is_valid, _, rejection_reason = validate_artifact_routing(filename, content)
    return rejection_reason if not is_valid else None


# =============================================================================
# PROJECT ROOT STRUCTURE
# =============================================================================

# Project root subfolders that are not part of agentic_core or apps_*
PROJECT_ROOT_SUBFOLDERS: Final[Mapping[str, Sequence[str]]] = {
    "logs": [],  # Mission execution logs and trace files
    "ops_scripts": [  # [ADDED] The new legal location for standalone scripts
        "ci",
        "maintenance",
        "security",
        "setup",
    ],
    "data": [
        "raw",  # Raw input data and sources
        "processed",  # Processed and transformed data
        "datasets",  # Structured datasets and test data
        "configurations",  # Configuration files and settings
        "governance",  # Governance and security data
        "cache",  # Temporary cache files
        "archives",  # Archived historical data
        "logs",  # Data processing logs
    ],
    "docs": [
        "technical",  # Technical documentation
        "project",  # Project management docs
        "analysis",  # Analysis and research
        "guides",  # User and developer guides
        "archive",  # Archived documentation
    ],
    "tests": [],  # Test files (separate from scripts)
    "archives": [],  # Archived files and historical data
}


# Project root metadata for clarity
PROJECT_ROOT_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "logs": {
        "purpose": "Mission execution logs and trace files",
        "content_types": ["mission_logs", "trace_files", "execution_logs"],
        "execution_allowed": False,
        "notes": "Contains trace.jsonl files for various mission executions",
        "file_patterns": ["*.log", "*.jsonl", "*.trace"],
        "keywords": ["transcript", "log", "trace", "execution"],
    },
    "scripts": {
        "purpose": "Project-level utility scripts (standalone, no core dependencies)",
        "content_types": ["setup_scripts", "deployment_tools", "ci_scripts", "migration_tools"],
        "execution_allowed": True,
        "notes": "Standalone utilities only - NO agentic_core imports allowed",
        "file_patterns": ["*.py", "*.sh", "*.bat", "*.cmd"],
        "keywords": ["setup", "install", "ci", "build", "deploy", "migration", "run"],
    },
    "data": {
        "purpose": "Data files and datasets used by the project",
        "content_types": [
            "raw_data",
            "processed_data",
            "datasets",
            "configurations",
            "governance_data",
        ],
        "execution_allowed": False,
        "notes": "Organized by data lifecycle: raw → processed → datasets → configurations",
        "file_patterns": [
            "*.csv",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.xml",
            "*.parquet",
            "*.db",
            "*.sqlite",
        ],
        "keywords": ["data", "dataset", "config", "settings", "parameters"],
    },
    "docs": {
        "purpose": "Project documentation and reports organized by purpose",
        "content_types": ["technical_docs", "project_docs", "analysis_reports", "user_guides"],
        "execution_allowed": False,
        "notes": "Categorized documentation: technical, project, analysis, and guides",
        "file_patterns": ["*.md", "*.rst", "*.txt", "*.pdf", "*.docx", "*.html"],
        "keywords": ["doc", "guide", "manual", "readme", "tutorial", "specification"],
    },
    "reports": {
        "purpose": "Generated reports, analysis outputs, and implementation plans",
        "content_types": [
            "coverage_reports",
            "telemetry_data",
            "audit_reports",
            "implementation_plans",
        ],
        "execution_allowed": False,
        "notes": "SSOT location for all implementation plans and generated reports",
        "file_patterns": ["*.html", "*.json", "*.md", "*.xml", "*.csv"],
        "keywords": ["report", "coverage", "telemetry", "audit", "plan", "implementation"],
    },
    "tests": {
        "purpose": "Test files and test data",
        "content_types": ["test_files", "test_data", "fixtures"],
        "execution_allowed": True,
        "notes": "Test files separate from execution scripts",
        "file_patterns": ["test_*.py", "*_test.py", "conftest.py", "*.fixture"],
        "keywords": ["test", "spec", "fixture", "mock"],
        "naming_convention": "snake_case_test",  # Enforce consistent test naming
    },
    "enforcement": {  # LCD+ CONTENT TYPE FOR L5 SAFETY (was guardrails)
        "purpose": "L5 safety enforcement agents and components (guardrails, gravity, gates)",
        "content_types": ["safety_agent", "membrane", "sanitizer", "hygiene_agent", "guardrail", "gate"],
        "execution_allowed": True,  # Operational agents
        "notes": "Sovereign operational safety components - snake_case_agent naming mandatory",
        "file_patterns": ["*_agent.py"],
        "keywords": ["guardrail", "membrane", "sanitizer", "hygiene", "redact", "scrub", "pii", "threat"],
        "naming_convention": "snake_case_agent",
    },
    "archives": {
        "purpose": "Archived files and historical data",
        "content_types": ["archived_code", "historical_data", "backups"],
        "execution_allowed": False,
        "notes": "Legacy files and historical archives",
        "file_patterns": ["*.bak", "*.old", "*.backup", "*.archive", "*.zip", "*.tar.gz"],
        "keywords": ["archive", "backup", "old", "legacy", "retired"],
    },
}


# Detailed subfolder metadata for data and docs directories
DATA_SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "raw": {
        "purpose": "Raw input data and external sources",
        "content_types": ["external_references", "input_files", "source_data"],
        "execution_allowed": False,
        "notes": "Contains external/ reference materials and raw inputs",
    },
    "processed": {
        "purpose": "Processed and transformed data artifacts",
        "content_types": ["audit_results", "evaluations", "manifests", "outputs"],
        "execution_allowed": False,
        "notes": "Data that has been processed or transformed",
    },
    "datasets": {
        "purpose": "Structured datasets for testing and reference",
        "content_types": ["golden_datasets", "test_data", "reference_data"],
        "execution_allowed": False,
        "notes": "Curated datasets for testing and validation",
    },
    "configurations": {
        "purpose": "Configuration files and settings",
        "content_types": ["sdk_configs", "mcp_configs", "prompt_configs", "task_definitions"],
        "execution_allowed": False,
        "notes": "Configuration files for various components",
    },
    "governance": {
        "purpose": "Governance and security-related data",
        "content_types": ["prompt_governance", "injection_data", "safety_data", "registry_data"],
        "execution_allowed": False,
        "notes": "Security, governance, and compliance data",
    },
    "cache": {
        "purpose": "Temporary cache files",
        "content_types": ["temp_files", "cache_data"],
        "execution_allowed": False,
        "notes": "Temporary storage that can be cleared",
    },
    "archives": {
        "purpose": "Archived historical data",
        "content_types": ["historical_data", "backups", "legacy_files"],
        "execution_allowed": False,
        "notes": "Long-term storage of historical data",
    },
    "logs": {
        "purpose": "Data processing logs and traces",
        "content_types": ["processing_logs", "error_logs", "trace_files"],
        "execution_allowed": False,
        "notes": "Logs from data processing operations",
    },
}


DOCS_SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "technical": {
        "purpose": "Technical documentation and specifications",
        "content_types": [
            "architecture_docs",
            "integration_guides",
            "api_docs",
            "configuration_guides",
        ],
        "execution_allowed": False,
        "notes": "Technical documentation for developers and architects",
    },
    "project": {
        "purpose": "Project management and governance documentation",
        "content_types": ["phase_docs", "planning_docs", "governance_docs", "milestone_tracking"],
        "execution_allowed": False,
        "notes": "Project management and planning documentation",
    },
    "analysis": {
        "purpose": "Analysis reports and research documentation",
        "content_types": ["analysis_reports", "metrics_docs", "investigation_reports", "rca_docs"],
        "execution_allowed": False,
        "notes": "Analysis, research, and investigation reports",
    },
    "guides": {
        "purpose": "User and developer guides",
        "content_types": ["user_guides", "developer_guides", "deployment_guides", "tutorials"],
        "execution_allowed": False,
        "notes": "Instructional documentation for users and developers",
    },
    "archive": {
        "purpose": "Archived and outdated documentation",
        "content_types": ["legacy_docs", "outdated_specs", "historical_docs"],
        "execution_allowed": False,
        "notes": "Documentation kept for historical reference",
    },
}
