"""ADG contract tests for apps_lic/types/TraceRegistry.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.TraceRegistry  # noqa: F401


def test_module_importable():
    """Module TraceRegistry must be importable."""
    assert apps_lic.types.TraceRegistry is not None
