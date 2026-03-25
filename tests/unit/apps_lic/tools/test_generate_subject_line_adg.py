"""ADG-driven tests for apps_lic/tools/generate_subject_line.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.generate_subject_line  # noqa: F401


def test_module_importable():
    """Module generate_subject_line must be importable."""
    assert apps_lic.tools.generate_subject_line is not None
