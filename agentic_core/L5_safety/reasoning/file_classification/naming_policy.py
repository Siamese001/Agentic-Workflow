"""Filename and path recommendation logic.

This module contains pure string/path operations for filename normalization
and compliant name generation.
"""

import re
from pathlib import Path

from .models import Violation


def _to_pascal_case(name: str) -> str:
    """Convert string to PascalCase.

    TODO: Extract implementation from FileClassificationAgent._to_pascal_case.
    """
    # Simple implementation for now
    return "".join(word.capitalize() for word in name.split("_"))


def _to_smart_snake_case(name: str) -> str:
    """Convert string to smart snake_case.

    TODO: Extract implementation from FileClassificationAgent._to_smart_snake_case.
    """
    # Simple implementation for now
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.

    TODO: Extract implementation from FileClassificationAgent._sanitize_filename.
    """
    # Simple implementation for now
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def normalize_filename(name: str) -> str:
    """
    Smart normalization that fixes root cause naming violations.

    Fixes:
    1. Stuttering acronyms: s_s_o_t_ → ssot_ (naive CamelCase split)
    2. Multiple underscores: ___ → _ (unsanitized concatenation)
    3. Leading underscores: _cc_visitor → cc_visitor (legacy convention)

    Args:
        name: The filename (with or without .py extension)

    Returns:
        Normalized filename with root cause violations corrected.

    Examples:
        - "s_s_o_t_consolidation_analyzer.py" → "ssot_consolidation_analyzer.py"
        - "setup___init___util.py" → "setup_init_util.py"
        - "_cc_visitor.py" → "cc_visitor.py"
    """
    # Exempt __init__.py entirely — it's a Python convention
    if name == "__init__.py" or name == "__init__":
        return name

    # Separate extension
    stem = name
    ext = ""
    if name.endswith(".py"):
        stem = name[:-3]
        ext = ".py"

    # 1. Fix stuttering acronyms: collapse runs of single-char_single-char segments
    # Matches sequences like a_b_c_d and collapses to abcd
    # Uses iterative approach to catch overlapping patterns
    prev = None
    while prev != stem:
        prev = stem
        stem = re.sub(r"\b([a-z])_([a-z])_([a-z])_([a-z])\b", r"\1\2\3\4", stem)
        stem = re.sub(r"\b([a-z])_([a-z])_([a-z])_([a-z])(?=_)", r"\1\2\3\4", stem)

    # 2. Fix multiple underscores: collapse __ or ___ to single _
    stem = re.sub(r"_{2,}", "_", stem)

    # 3. Fix leading underscores
    stem = stem.lstrip("_")

    # 4. Fix trailing underscores
    stem = stem.rstrip("_")

    return f"{stem}{ext}" if stem else name  # Fallback to original if empty


def _check_forbidden_patterns(filename: str) -> list[str]:
    """Check for forbidden patterns in filename.

    TODO: Extract implementation from FileClassificationAgent._check_forbidden_patterns.
    """
    return []


def get_compliant_name(
    path: Path,
    file_type: str,
    project_root: Path,
) -> str | None:
    """Get compliant filename for a file based on its type.

    TODO: Extract implementation from FileClassificationAgent.get_compliant_name.
    """
    # Temporary: delegate to original implementation
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationHealerAgent

    classifier = FileClassificationHealerAgent(project_root=project_root)
    return classifier.get_compliant_name(path, file_type)
