"""ADG importability contract for system_learning/invariants/commit_proof_invariant.py."""
from __future__ import annotations

import system_learning.invariants.commit_proof_invariant  # noqa: F401


def test_module_importable():
    """Module commit_proof_invariant must be importable."""
    assert system_learning.invariants.commit_proof_invariant is not None
