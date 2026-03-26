"""ADG-driven tests for agentic_core/L5_safety/reasoning/CredentialScannerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.reasoning.CredentialScannerAgent  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.reasoning.CredentialScannerAgent  # noqa: F401
        """Module CredentialScannerAgent must be importable."""
        assert agentic_core.L5_safety.reasoning.CredentialScannerAgent is not None

    assert agentic_core.L5_safety.reasoning.CredentialScannerAgent is not None
