"""Canonical AST + Fuzzy Matching Utilities

Consolidates duplicated AST parsing and fuzzy matching logic across the codebase.
Provides deterministic primitives for structural hashing, similarity scoring, and normalization.
"""

import ast
import difflib
import hashlib
import os

AST_FUZZY_THRESHOLD = float(os.environ.get("AST_FUZZY_THRESHOLD", "0.6"))


def parse_ast_safe(source: str) -> ast.AST | None:
    """Parse source code to AST with error handling.

    Args:
        source: Python source code as string

    Returns:
        Parsed AST module or None if parsing fails
    """
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError):
        return None


def ast_dump_hash(node: ast.AST) -> str:
    """Compute deterministic SHA256 hash of AST structure.

    Uses ast.dump with include_attributes=False for structural comparison.

    Args:
        node: AST node to hash

    Returns:
        SHA256 hex digest of normalized AST dump
    """
    dump_str = ast.dump(node, include_attributes=False)
    return hashlib.sha256(dump_str.encode("utf-8")).hexdigest()


def tokenize_simple(text: str) -> list[str]:
    """Simple tokenization: split on whitespace and punctuation.

    Args:
        text: Text to tokenize

    Returns:
        List of tokens
    """
    import re

    tokens = re.split("[\\s\\W]+", text.lower())
    return [t for t in tokens if t and t.isalpha()]


def similarity_score(text_a: str, text_b: str) -> float:
    """Compute fuzzy similarity score using difflib.SequenceMatcher.

    Args:
        text_a: First text
        text_b: Second text

    Returns:
        Similarity ratio in [0.0, 1.0]
    """
    tokens_a = tokenize_simple(text_a)
    tokens_b = tokenize_simple(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    return matcher.ratio()


def normalize_repo_path(path: str) -> str:
    """Normalize repository path to forward slashes.

    Args:
        path: File path (may contain backslashes on Windows)

    Returns:
        Normalized path with forward slashes
    """
    return path.replace("\\", "/")


def get_threshold() -> float:
    """Get current fuzzy similarity threshold.

    Returns:
        Threshold value (configurable via AST_FUZZY_THRESHOLD env var)
    """
    return AST_FUZZY_THRESHOLD


def parse_evidence(check: dict) -> dict:
    """Extract and normalize evidence from a check dict.

    Args:
        check: Check result dictionary

    Returns:
        Evidence dict (empty dict if not found or invalid)
    """
    evidence = check.get("evidence", {})
    if not isinstance(evidence, dict):
        return {}
    return evidence


def safe_unparse(node: ast.AST) -> str | None:
    """Safely unparse AST node to source code.

    Args:
        node: AST node to unparse

    Returns:
        Source code string or None if unparsing fails
    """
    try:
        return ast.unparse(node)
    except (AttributeError, TypeError, ValueError):
        return None


def compute_file_hash(path: str) -> str:
    """Compute SHA256 hash of a file.

    Args:
        path: File path to hash

    Returns:
        SHA256 hex digest
    """
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_path(path: str) -> str:
    """Normalize file path to forward slashes.

    Args:
        path: File path (may contain backslashes on Windows)

    Returns:
        Normalized path with forward slashes
    """
    return path.replace("\\", "/").replace("//", "/")
