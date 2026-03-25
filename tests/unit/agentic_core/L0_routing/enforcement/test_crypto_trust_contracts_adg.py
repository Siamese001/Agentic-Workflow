"""ADG importability contract for agentic_core/L0_routing/enforcement/crypto_trust_contracts.py."""
from __future__ import annotations

import agentic_core.L0_routing.enforcement.crypto_trust_contracts  # noqa: F401


def test_module_importable():
    """Module crypto_trust_contracts must be importable."""
    assert agentic_core.L0_routing.enforcement.crypto_trust_contracts is not None
