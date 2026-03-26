"""ADG contract tests for apps_lic/types/code_quality_guardrail_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module code_quality_guardrail_types must be importable."""
    import apps_lic.types.code_quality_guardrail_types  # noqa: F401

    assert apps_lic.types.code_quality_guardrail_types is not None
