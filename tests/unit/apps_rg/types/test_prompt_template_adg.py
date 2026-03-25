"""ADG contract tests for apps_rg/types/PromptTemplate.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.types.PromptTemplate  # noqa: F401


def test_module_importable():
    """Module PromptTemplate must be importable."""
    assert apps_rg.types.PromptTemplate is not None
