"""
agentic_core/utils/ast_fuzzy.py

Thin module exposing threshold configuration for the AST fuzzy-matching utilities.
Re-exports all symbols from ast_fuzzy_util for backward compatibility.
"""

from __future__ import annotations

import os

from agentic_core.utils.ast_fuzzy_util import (  # noqa: F401
    ast_dump_hash,
    normalize_repo_path,
    parse_ast_safe,
    similarity_score,
    tokenize_simple,
)

_DEFAULT_THRESHOLD = 0.6


def get_threshold() -> float:
    """Return the similarity threshold, overridable via AST_FUZZY_THRESHOLD env var."""
    raw = os.environ.get("AST_FUZZY_THRESHOLD")
    if raw is not None:
        try:
            return float(raw)
        except ValueError as e:
            # TODO: Add proper input validation
            logger.warning(f"Invalid input: {e}")
        pass
    return _DEFAULT_THRESHOLD
