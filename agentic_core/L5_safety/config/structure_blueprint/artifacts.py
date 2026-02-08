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


def has_forbidden_layer_prefix(filename: str) -> str | None:
    """Check if filename starts with a forbidden layer/priority prefix."""
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
