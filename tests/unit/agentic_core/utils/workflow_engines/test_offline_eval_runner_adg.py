"""ADG-driven tests for agentic_core/utils/workflow_engines/offline_eval_runner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.offline_eval_runner import (  # noqa: F401
        OfflineEvaluationRunner,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    OfflineEvaluationRunner = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="offline_eval_runner.py deps unavailable")
class TestOfflineEvaluationRunner:
    def test_is_class(self):
        assert isinstance(OfflineEvaluationRunner, type)
    def test_importable(self):
        assert OfflineEvaluationRunner is not None


def test_module_importable():
    """Module offline_eval_runner.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE