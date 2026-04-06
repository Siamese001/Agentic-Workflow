"""Filename and path recommendation logic.

This module contains pure string/path operations for filename normalization
and compliant name generation.
"""

import re
from pathlib import Path

from .models import Violation


def _to_pascal_case(name: str) -> str:
    """Convert snake_case or mixed case to PascalCase.

    Example: 'pii_sanitizer' -> 'PiiSanitizer', 'PDFLoader' -> 'PdfLoader'
    """
    # If already PascalCase, return as-is
    if name and name[0].isupper() and "_" not in name:
        return name

    # Split on underscores and capitalize each part
    parts = name.split("_")
    return "".join(word.capitalize() for word in parts if word)


def _to_smart_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case while preserving acronyms.

    Example: 'PIISanitizer' -> 'pii_sanitizer', 'PDFLoader' -> 'pdf_loader'

    Hardening: Recognizes project-specific atomic words to prevent false positives.
    - "Grounding" stays as "grounding", not "g_r_ounding"
    - "Routing" stays as "routing", not "r_outing"
    """
    # Project-specific atomic words that should not be split
    atomic_words = {
        "Grounding": "grounding",
        "Routing": "routing",
        "Sender": "sender",
        "Receiver": "receiver",
        "Planner": "planner",
        "Scheduler": "scheduler",
        "RG": "rg",  # Resume Generation acronym protection
    }

    # Check if the entire name is an atomic word
    if name in atomic_words:
        return atomic_words[name]

    # Replace atomic words with placeholders before processing
    placeholders = {}
    temp_name = name
    for idx, (word, replacement) in enumerate(atomic_words.items()):
        if word in temp_name:
            placeholder = f"__ATOMIC_{idx}__"
            placeholders[placeholder] = replacement
            temp_name = temp_name.replace(word, placeholder)

    # Pass 1: Handle acronym boundaries (PDFLoader -> PDF_Loader)
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", temp_name)
    # Pass 2: Handle standard camel boundaries (LoaderFile -> Loader_File)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    # Restore atomic words from placeholders
    result = s2
    for placeholder, replacement in placeholders.items():
        result = result.replace(placeholder.lower(), replacement)

    return result


def _sanitize_filename(stem: str) -> str:
    """Strip known architectural suffixes from a filename stem to prevent stuttering.

    This prevents "stuttering" (e.g., feature_flags_config_util.py) and
    "hybrid suffixes" (e.g., embedding_config_types_config.py).

    Logic: Iteratively remove known suffixes until none remain.

    IMPORTANT: Only strips TRAILING architectural suffixes, not semantic content.
    For example, "agent_discovery" keeps "agent" because it's semantic, not a suffix.

    Args:
        stem: The filename stem (without .py extension)

    Returns:
        The sanitized core name with trailing architectural suffixes removed.

    Examples:
        - "feature_flags_config_util" -> "feature_flags"
        - "embedding_config_types_config" -> "embedding"
        - "user_profile_types" -> "user_profile"
        - "agent_discovery_util" -> "agent_discovery" (keeps semantic "agent")
    """
    # Known architectural suffixes to strip (trailing only)
    # These are file-type markers, not semantic content
    known_suffixes = [
        "_config",
        "_util",
        "_types",
        "_mixin",
        "_base",
        "_validator",
        "_protocol",
        "_strategy",
        "_adapter",
        "_factory",
        "_orchestrator",
        "_engine",
        "_gateway",
        "_stub",
        "_test",
        "Config",
        "Util",
        "Types",
        "Script",
        "Mixin",
        "Base",
        "Validator",
        "Protocol",
        "Strategy",
        "Adapter",
        "Factory",
        "Orchestrator",
        "Engine",
        "Gateway",
        "Stub",
        "Test",
    ]

    # NOTE: "_agent" and "Agent" are NOT stripped because they often carry
    # semantic meaning (e.g., "agent_discovery" describes what the utility does)
    # Only strip "_agent" if it's a trailing suffix AND followed by another suffix

    sanitized = stem
    changed = True

    # Iteratively strip suffixes until no more are found
    while changed:
        changed = False
        for suffix in known_suffixes:
            if sanitized.endswith(suffix) and len(sanitized) > len(suffix):
                sanitized = sanitized[: -len(suffix)]
                changed = True
                break  # Restart from beginning of suffix list

    # Special case: Strip trailing "_agent" or "Agent" if it appears AFTER a known suffix pattern
    # This catches cases like "healing_mixin_agent" (mixin before agent) but not "agent_discovery"
    # Check if the original stem had a pattern like *_mixin_agent, *_config_agent, etc.
    agent_after_suffix_patterns = [
        "_mixin_agent",
        "_config_agent",
        "_types_agent",
        "_util_agent",
        "_validator_agent",
        "_base_agent",
    ]
    for pattern in agent_after_suffix_patterns:
        if stem.endswith(pattern):
            # Strip the trailing _agent since it was after another suffix
            if sanitized.endswith("_agent"):
                sanitized = sanitized[:-6]
            elif sanitized.endswith("Agent"):
                sanitized = sanitized[:-5]
            break

    # Clean up trailing underscores
    sanitized = sanitized.rstrip("_")

    return sanitized if sanitized else stem  # Fallback to original if fully stripped


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


def _check_forbidden_patterns(filename: str) -> list[dict[str, str]]:
    """Check a filename against FORBIDDEN_FILENAME_PATTERNS from the constitution.

    Args:
        filename: The filename to check (without directory path)

    Returns:
        List of violation dicts with 'pattern' and 'reason' for each match.
    """
    from agentic_core.L5_safety.config.structure_blueprint import (
        FORBIDDEN_FILENAME_PATTERNS,
    )

    violations: list[dict[str, str]] = []
    # Skip __init__.py — always exempt
    if filename == "__init__.py":
        return violations

    stem = filename.removesuffix(".py")
    for rule in FORBIDDEN_FILENAME_PATTERNS:
        if re.search(rule["pattern"], stem):
            violations.append(
                {
                    "pattern": rule["pattern"],
                    "reason": rule["reason"],
                    "filename": filename,
                },
            )
    return violations


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
