"""ADG-driven tests for agentic_core/utils/workflow_engines/dpo_batch_builder.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.dpo_batch_builder  # noqa: F401


def test_module_importable():
    """Module dpo_batch_builder must be importable."""
    assert agentic_core.utils.workflow_engines.dpo_batch_builder is not None
