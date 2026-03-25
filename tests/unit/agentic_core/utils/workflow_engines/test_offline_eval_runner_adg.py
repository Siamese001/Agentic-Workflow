"""ADG-driven tests for agentic_core/utils/workflow_engines/offline_eval_runner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.offline_eval_runner  # noqa: F401


def test_module_importable():
    """Module offline_eval_runner must be importable."""
    assert agentic_core.utils.workflow_engines.offline_eval_runner is not None
