"""ADG contract tests for apps_shared/types/pipeline_stage_status_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.pipeline_stage_status_types  # noqa: F401


def test_module_importable():
    """Module pipeline_stage_status_types must be importable."""
    assert apps_shared.types.pipeline_stage_status_types is not None
