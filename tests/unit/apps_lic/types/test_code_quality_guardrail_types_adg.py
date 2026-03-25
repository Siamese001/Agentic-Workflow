"""ADG contract tests for apps_lic/types/code_quality_guardrail_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.code_quality_guardrail_types  # noqa: F401


def test_module_importable():
    """Module code_quality_guardrail_types must be importable."""
    assert apps_lic.types.code_quality_guardrail_types is not None
