"""
agentic_core/utils/ast_fuzzy.py

Thin module exposing threshold configuration for the AST fuzzy-matching utilities.
Re-exports all symbols from ast_fuzzy_util for backward compatibility.
"""

from __future__ import annotations

import logging
import os

from agentic_core.utils.ast_fuzzy_util import (  # noqa: F401
    ast_dump_hash,
    normalize_repo_path,
    parse_ast_safe,
    similarity_score,
    tokenize_simple,
)

_DEFAULT_THRESHOLD = 0.6
logger = logging.getLogger(__name__)


def _parse_threshold(raw: str | None) -> float:
    if raw is None:
        return _DEFAULT_THRESHOLD
    try:
        value = float(raw)
    except ValueError:
        logger.warning(
            "Invalid AST_FUZZY_THRESHOLD %r; using default %.2f",
            raw,
            _DEFAULT_THRESHOLD,
        )
        return _DEFAULT_THRESHOLD
    if not 0.0 <= value <= 1.0:
        logger.warning(
            "Out-of-range AST_FUZZY_THRESHOLD %r; expected 0.0..1.0; using default %.2f",
            raw,
            _DEFAULT_THRESHOLD,
        )
        return _DEFAULT_THRESHOLD
    return value


def get_threshold() -> float:
    """Return the similarity threshold, overridable via AST_FUZZY_THRESHOLD env var."""
    return _parse_threshold(os.environ.get("AST_FUZZY_THRESHOLD"))
