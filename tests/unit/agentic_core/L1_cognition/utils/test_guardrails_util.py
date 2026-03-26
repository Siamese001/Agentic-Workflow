"""Foundational behavioral tests for agentic_core/L1_cognition/utils/guardrails_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.utils.guardrails_util  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.utils.guardrails_util  # noqa: F401
    """Module guardrails_util must be importable."""
    assert agentic_core.L1_cognition.utils.guardrails_util is not None
