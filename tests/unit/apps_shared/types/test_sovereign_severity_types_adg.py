"""ADG contract tests for apps_shared/types/sovereign_severity_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.sovereign_severity_types  # noqa: F401


def test_module_importable():
    """Module sovereign_severity_types must be importable."""
    assert apps_shared.types.sovereign_severity_types is not None
