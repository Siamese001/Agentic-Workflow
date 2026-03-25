"""ADG importability contract for agentic_core/evaluation/metrics/__init__.py."""
from __future__ import annotations

import agentic_core.evaluation.metrics.__init__  # noqa: F401


def test_module_importable():
    """Module metrics must be importable."""
    assert agentic_core.evaluation.metrics.__init__ is not None
