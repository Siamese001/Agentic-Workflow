"""Test for DagRuntimeInspectorAgent importability."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

import agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent as _mod  # noqa: F401


def test_module_importable():
    """Module DagRuntimeInspectorAgent must be importable."""
    assert _mod is not None
