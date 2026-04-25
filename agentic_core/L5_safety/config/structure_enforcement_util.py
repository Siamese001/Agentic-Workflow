"""
L5 Structure Enforcement Utility ΓÇö Thin extraction from structure_blueprint.

Contains ONLY the complex enforcement functions needed by L5 reasoning agents
(location_validator, hierarchy_healer, etc.) after the structure_blueprint
package was archived as part of Method A SSOT revamp.

No lifecycle trace imports. No dependency on archived package.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from re import Pattern
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import (
    ALLOWED_DUPLICATE_FILENAMES,
    PROJECT_ROOT_WHITELIST,
    ROOT_PROTECTED_FILES,
)
from tqdm import tqdm

# ============================================================================
# APP-SPECIFIC CONSTANTS (extracted from artifacts.py)
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

APP_SPECIFIC_TARGET_SUBFOLDER: str = "reasoning"

APP_SPECIFIC_PATTERN_STRINGS: Final[Sequence[str]] = [
    "^rg_.*\\.py$",
    "^lic_.*\\.py$",
    "^resume_.*\\.py$",
    "^outreach_.*\\.py$",
    "^dispatch_(resume|outreach).*\\.py$",
]

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

LAYER_PREFIX_FILENAME_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {"l2_phase_spec.py", "l4_registries.py", "l1_meta_adapter.py"},
)

# ============================================================================
# ARTIFACT ROUTING MAP (extracted from artifacts.py)
# ============================================================================

ARTIFACT_ROUTING_MAP: Final[Mapping[str, Mapping[str, Any]]] = {
    "docs/reports/assessments": {
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "naming_patterns": [re.compile(".*assessment.*"), re.compile(".*analysis.*"), re.compile(".*gap.*")],
        "content_signals": {"keywords": ["assessment", "analysis", "gap", "architecture", "strategic"]},
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/audit": {
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "naming_patterns": [
            re.compile(".*audit.*"),
            re.compile(".*drift.*"),
            re.compile(".*variance.*"),
            re.compile(".*compliance.*"),
        ],
        "content_signals": {
            "headers": ["# Audit Report", "## Violations", "## Drift"],
            "keywords": ["audit", "drift", "variance", "compliance", "SSOT"],
        },
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/coverage": {
        "file_extensions": [".md", ".json", ".html", ".xml", ".txt"],
        "naming_patterns": [re.compile(".*coverage.*"), re.compile(".*test.*"), re.compile(".*quality.*")],
        "content_signals": {"keywords": ["coverage", "test", "quality", "percentage", "htmlcov"]},
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/security": {
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "naming_patterns": [
            re.compile(".*security.*"),
            re.compile(".*vulnerability.*"),
            re.compile(".*hardened.*"),
            re.compile(".*hardening.*"),
        ],
        "content_signals": {"keywords": ["security", "vulnerability", "safety", "hardened", "guardrails"]},
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/telemetry": {
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "naming_patterns": [
            re.compile(".*telemetry.*"),
            re.compile(".*metrics.*"),
            re.compile(".*performance.*"),
        ],
        "content_signals": {"keywords": ["telemetry", "metrics", "performance", "observability"]},
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/missions": {
        "file_extensions": [".jsonl", ".trace", ".log", ".json"],
        "naming_patterns": [re.compile(".*mission.*"), re.compile(".*trace.*"), re.compile(".*execution.*")],
        "content_signals": {
            "json_keys": ["mission_id", "trace_id", "execution_log"],
            "keywords": ["mission", "trace", "execution"],
        },
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "agentic_core/L0_routing/utils": {
        "file_extensions": [".log", ".err", ".out", ".txt"],
        "naming_patterns": [re.compile(".*debug.*"), re.compile(".*error.*"), re.compile(".*crash.*")],
        "content_signals": {
            "keywords": ["DEBUG", "ERROR", "Traceback (most recent call)", "Exception", "Stack trace"]
        },
        "forbidden_extensions": [".py", ".pyc", ".pyo"],
        "forbidden_keywords": ["def main", "if __name__", "import sys", "class "],
    },
    "agentic_core/L0_routing/scripts": {
        "file_extensions": [".py"],
        "naming_patterns": [
            re.compile(".*script.*"),
            re.compile(".*fixer.*"),
            re.compile(".*tool.*"),
            re.compile(".*util.*"),
            re.compile(".*cleaner.*"),
            re.compile(".*migrat.*"),
        ],
        "content_signals": {
            "keywords": [
                "def main(",
                "if __name__",
                "#!/usr/bin/env python",
                "import sys",
                "argparse",
                "click",
                "typer",
            ]
        },
        "forbidden_keywords": [
            "class Test",
            "def test_",
            "import unittest",
            "import pytest",
            "class BaseAgent",
            "class Sovereign",
        ],
    },
    "logs": {
        "file_extensions": [".jsonl", ".trace"],
        "naming_patterns": [re.compile("^trace_.*"), re.compile("^mission_.*")],
        "content_signals": {"json_keys": ["mission_id", "step_count", "agent_action", "thought_process"]},
        "forbidden_keywords": ["Traceback", "Exception", "dataset_version"],
    },
    "data/processed": {
        "file_extensions": [".json", ".csv", ".parquet"],
        "naming_patterns": [
            re.compile(".*dataset.*"),
            re.compile(".*processed.*"),
            re.compile("agent_discovery.*\\.json$"),
            re.compile(".*manifest.*\\.json$"),
        ],
        "content_signals": {
            "json_keys": ["dataset_version", "record_count", "processed_at", "schema_version"]
        },
        "forbidden_keywords": ["def ", "class ", "api_key", "secret"],
    },
}


# ============================================================================
# ENFORCEMENT FUNCTIONS
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


def has_forbidden_layer_prefix(filename: str) -> str | None:
    """Check if filename starts with a forbidden layer/priority prefix."""
    if filename in LAYER_PREFIX_FILENAME_ALLOWLIST:
        return None
    if filename.startswith(FORBIDDEN_LAYER_PREFIXES):
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if filename.startswith(prefix):
                return prefix
    return None


@lru_cache(maxsize=1)
def get_app_specific_patterns_compiled() -> list[Pattern]:
    """Compile and cache app-specific patterns."""
    return [re.compile(p) for p in APP_SPECIFIC_PATTERN_STRINGS]


def is_app_specific_file(filename: str) -> bool:
    """Check if a file should be in an app folder, not agentic_core."""
    patterns = get_app_specific_patterns_compiled()
    return any(pattern.match(filename) for pattern in patterns)


def validate_artifact_routing(
    filename: str,
    content: str | None = None,
) -> tuple[bool, str | None, str | None]:
    """
    Validate file against ARTIFACT_ROUTING_MAP negative logic.

    Returns:
        Tuple of (is_valid, matched_destination, rejection_reason)
    """
    file_ext = Path(filename).suffix.lower()
    for dest, rules in tqdm(ARTIFACT_ROUTING_MAP.items(), desc="Processing", unit="item"):
        allowed_exts = rules.get("file_extensions", [])
        matches_positive = False
        if allowed_exts and file_ext in allowed_exts:
            matches_positive = True
        naming_patterns = rules.get("naming_patterns", [])
        if naming_patterns:
            for pattern in naming_patterns:
                if pattern.match(filename):
                    matches_positive = True
                    break
        if content and matches_positive:
            content_signals = rules.get("content_signals", {})
            headers = content_signals.get("headers", [])
            if headers and any(header in content for header in headers):
                matches_positive = True
            keywords = content_signals.get("keywords", [])
            if keywords and any(keyword in content for keyword in keywords):
                matches_positive = True
        if matches_positive:
            forbidden_exts = rules.get("forbidden_extensions", [])
            if forbidden_exts and file_ext in forbidden_exts:
                return (False, None, f"Forbidden extension {file_ext} for destination {dest}")
            if content:
                forbidden_keywords = rules.get("forbidden_keywords", [])
                if forbidden_keywords:
                    for keyword in forbidden_keywords:
                        if keyword in content:
                            return (False, None, f"Forbidden keyword '{keyword}' for destination {dest}")
            return (True, dest, None)
    return (True, None, None)


def check_forbidden_signals(filename: str, content: str | None = None) -> str | None:
    """
    Quick check for forbidden signals across all routing rules.

    Returns rejection reason if file matches any forbidden_extensions or forbidden_keywords,
    None otherwise.
    """
    is_valid, _, rejection_reason = validate_artifact_routing(filename, content)
    return rejection_reason if not is_valid else None


def is_path_allowed(rel_path: str | Path) -> bool:
    """
    Determines if a path conforms to sovereign territory structure.

    Simplified version: validates root folder is in PROJECT_ROOT_WHITELIST
    and applies basic path normalization/security checks.
    (Full territory-aware validation was retired with structure_blueprint archive.)
    """
    original_path = str(rel_path).replace("\\", "/")

    if "//" in original_path:
        return False

    # guardian: allow-path-string
    normalized_path = os.path.normpath(original_path).replace("\\", "/")

    if not normalized_path or normalized_path.startswith("..") or normalized_path == ".":
        return False

    parts = [p for p in normalized_path.split("/") if p]
    if not parts:
        return False

    if len(parts) == 1:
        if parts[0] in PROJECT_ROOT_WHITELIST:
            return True
        return parts[0] in ROOT_PROTECTED_FILES or parts[0] in ALLOWED_DUPLICATE_FILENAMES

    root = parts[0]
    if root not in PROJECT_ROOT_WHITELIST:
        return False

    # Cross-sovereign deportation: prevent App/Test leakage into Core
    filename = parts[-1]
    if root == "agentic_core":
        if filename.startswith(("rg_", "lic_", "test_")):
            if not (filename == "__init__.py" or "L0_routing/scripts" in normalized_path):
                return False

    return True
