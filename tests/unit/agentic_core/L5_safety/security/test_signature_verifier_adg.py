"""ADG importability contract for agentic_core/L5_safety/security/signature_verifier.py."""
from __future__ import annotations

import agentic_core.L5_safety.security.signature_verifier  # noqa: F401


def test_module_importable():
    """Module signature_verifier must be importable."""
    assert agentic_core.L5_safety.security.signature_verifier is not None
