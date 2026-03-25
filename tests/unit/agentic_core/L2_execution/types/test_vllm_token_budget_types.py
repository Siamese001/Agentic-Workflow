"""Foundational behavioral tests for agentic_core/L2_execution/types/vllm_token_budget_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.types.vllm_token_budget_types  # noqa: F401


def test_module_importable():
    """Module vllm_token_budget_types must be importable."""
    assert agentic_core.L2_execution.types.vllm_token_budget_types is not None
