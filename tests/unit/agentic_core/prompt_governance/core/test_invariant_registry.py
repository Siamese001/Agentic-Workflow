"""Foundational behavioral tests for agentic_core/prompt_governance/core/invariant_registry.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.core.invariant_registry  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.core.invariant_registry  # noqa: F401
        """Module invariant_registry must be importable."""
        assert agentic_core.prompt_governance.core.invariant_registry is not None

    assert agentic_core.prompt_governance.core.invariant_registry is not None
