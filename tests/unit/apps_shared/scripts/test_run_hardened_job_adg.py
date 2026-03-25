"""ADG-driven tests for apps_shared/scripts/run_hardened_job.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.run_hardened_job  # noqa: F401


def test_module_importable():
    """Module run_hardened_job must be importable."""
    assert apps_shared.scripts.run_hardened_job is not None
