"""ADG importability contract for agentic_core/adg/runtime/execution_proof.py."""
from __future__ import annotations

import agentic_core.adg.runtime.execution_proof  # noqa: F401


def test_module_importable():
    """Module execution_proof must be importable."""
    assert agentic_core.adg.runtime.execution_proof is not None
