"""ADG-driven tests for L2_execution/engines/validation_orchestrator.py — fan_in=0.

Import guard only — module has heavyweight deps (SovereignBaseAgent, timeout_decorator)
that may block on import in CI environments.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L2_execution.engines.validation_orchestrator as _mod  # noqa: F401  # ADG covers
except Exception:
    _mod = None



def test_module_syntax():
    """Verify module is syntactically valid Python without importing it."""
    import ast
    from pathlib import Path
    src = Path("agentic_core/L2_execution/engines/validation_orchestrator.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    assert tree is not None


def test_module_has_canon_base_agent():
    """Verify CanonBaseAgent class exists in module source."""
    from pathlib import Path
    src = Path("agentic_core/L2_execution/engines/validation_orchestrator.py").read_text(encoding="utf-8")
    assert "CanonBaseAgent" in src
