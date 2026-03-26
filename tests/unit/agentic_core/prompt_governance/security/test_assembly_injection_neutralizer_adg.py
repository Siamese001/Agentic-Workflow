"""ADG-driven tests for agentic_core/prompt_governance/security/assembly_injection_neutralizer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.security.assembly_injection_neutralizer  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.security.assembly_injection_neutralizer  # noqa: F401
        """Module assembly_injection_neutralizer must be importable."""
        assert agentic_core.prompt_governance.security.assembly_injection_neutralizer is not None

    assert agentic_core.prompt_governance.security.assembly_injection_neutralizer is not None
