"""ADG-driven tests for agentic_core/utils/workflow_engines/evaluation_dataset_schema.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.evaluation_dataset_schema  # noqa: F401


def test_module_importable():
    """Module evaluation_dataset_schema must be importable."""
    assert agentic_core.utils.workflow_engines.evaluation_dataset_schema is not None
