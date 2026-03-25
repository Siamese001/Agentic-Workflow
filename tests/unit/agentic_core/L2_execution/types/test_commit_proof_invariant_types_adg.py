"""ADG importability contract for agentic_core/L2_execution/types/commit_proof_invariant_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.commit_proof_invariant_types  # noqa: F401


def test_module_importable():
    """Module commit_proof_invariant_types must be importable."""
    assert agentic_core.L2_execution.types.commit_proof_invariant_types is not None
