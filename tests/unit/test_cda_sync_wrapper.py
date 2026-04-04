"""
Wave 1 Invariant: CognitiveDispositionAgent must expose sync analyze_violation()
and async analyze_violations() so execute_ssot.py callers don't use asyncio.run directly.
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR

CDA_PATH = (
    Path(__file__).parent.parent.parent
    / AGENTIC_CORE_DIR
    / "L5_safety"
    / "reasoning"
    / "CognitiveDispositionAgent.py"
)


def _ast_method_names() -> list[str]:
    src = CDA_PATH.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    names = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
    return names


def test_analyze_violation_sync_exists():
    """Wave 1: sync analyze_violation() must be defined (not async)."""

    src = CDA_PATH.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    sync_defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "analyze_violation" in sync_defs, (
        "sync analyze_violation() not found in CognitiveDispositionAgent — "
        "callers are forced to use asyncio.run() directly"
    )


def test_analyze_violations_async_exists():
    """Wave 1: async analyze_violations() must be defined."""
    src = CDA_PATH.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    async_defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
    assert "analyze_violations" in async_defs, (
        "async analyze_violations() not found in CognitiveDispositionAgent — "
        "EnhancedAutonomousDecisionEngine.analyze_violations_with_cognitive_disposition() will fail"
    )


def test_analyze_violation_async_still_exists():
    """Wave 1: original analyze_violation_async() must not be removed."""
    names = _ast_method_names()
    assert "analyze_violation_async" in names, (
        "analyze_violation_async() was removed — existing callers (heal()) will break"
    )


def test_get_analytics_still_exists():
    """Regression: get_analytics() must not be removed by Wave 1 edits."""
    names = _ast_method_names()
    assert "get_analytics" in names, "get_analytics() was removed — execute_ssot.py caller will break"
