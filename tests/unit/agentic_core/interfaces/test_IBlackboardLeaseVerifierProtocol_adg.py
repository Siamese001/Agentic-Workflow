"""ADG importability contract for agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py."""
from __future__ import annotations

import agentic_core.interfaces.IBlackboardLeaseVerifierProtocol  # noqa: F401


def test_module_importable():
    """Module IBlackboardLeaseVerifierProtocol must be importable."""
    assert agentic_core.interfaces.IBlackboardLeaseVerifierProtocol is not None
