"""ADG importability contract for system_learning/engines/l5_policy_proposer.py."""
from __future__ import annotations

def test_module_importable():
    """Module l5_policy_proposer must be importable."""
    import system_learning.engines.l5_policy_proposer
    assert system_learning.engines.l5_policy_proposer is not None