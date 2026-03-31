"""ADG importability contract for system_learning/invariants/commit_proof_invariant.py."""
from __future__ import annotations

def test_module_importable():
    """Module commit_proof_invariant must be importable."""
    import system_learning.invariants.commit_proof_invariant
    assert system_learning.invariants.commit_proof_invariant is not None
