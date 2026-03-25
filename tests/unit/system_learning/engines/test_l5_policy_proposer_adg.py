"""ADG importability contract for system_learning/engines/l5_policy_proposer.py."""
from __future__ import annotations

import system_learning.engines.l5_policy_proposer  # noqa: F401


def test_module_importable():
    """Module l5_policy_proposer must be importable."""
    assert system_learning.engines.l5_policy_proposer is not None
