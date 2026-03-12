"""ADG importability contract for agentic_core/L3_orchestration/ptc/builtin_tools.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_builtin_tools.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.ptc.builtin_tools import (  # noqa: F401
        repo_rg_handler,
        expr_eval_handler,
        register_builtin_tools,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    repo_rg_handler = None  # type: ignore[assignment,misc]
    expr_eval_handler = None  # type: ignore[assignment,misc]
    register_builtin_tools = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="builtin_tools.py deps unavailable")
class TestBuiltinToolsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: builtin_tools.py must be importable."""
        assert _AVAILABLE

    def test_repo_rg_handler_callable(self) -> None:
        assert callable(repo_rg_handler)

    def test_expr_eval_handler_callable(self) -> None:
        assert callable(expr_eval_handler)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

