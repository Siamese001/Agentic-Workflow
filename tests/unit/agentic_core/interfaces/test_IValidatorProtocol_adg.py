"""ADG importability contract for agentic_core/interfaces/IValidatorProtocol.py."""
from __future__ import annotations

import agentic_core.interfaces.IValidatorProtocol  # noqa: F401


def test_module_importable():
    """Module IValidatorProtocol must be importable."""
    assert agentic_core.interfaces.IValidatorProtocol is not None
