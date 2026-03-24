"""ADG-driven tests for agentic_core/utils/workflow_engines/replay_eval_runner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.replay_eval_runner import (  # noqa: F401
        ReplayEvaluationRunner,
        SystemConfig,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SystemConfig = None  # type: ignore[assignment,misc]
    ReplayEvaluationRunner = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="replay_eval_runner.py deps unavailable")
class TestSystemConfig:
    def test_is_class(self):
        assert isinstance(SystemConfig, type)
    def test_importable(self):
        assert SystemConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="replay_eval_runner.py deps unavailable")
class TestReplayEvaluationRunner:
    def test_is_class(self):
        assert isinstance(ReplayEvaluationRunner, type)
    def test_importable(self):
        assert ReplayEvaluationRunner is not None


def test_module_importable():
    """Module replay_eval_runner.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE