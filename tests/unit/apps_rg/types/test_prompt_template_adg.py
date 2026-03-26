"""ADG contract tests for apps_rg/types/PromptTemplate.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module PromptTemplate must be importable."""
    import apps_rg.types.PromptTemplate  # noqa: F401

    assert apps_rg.types.PromptTemplate is not None