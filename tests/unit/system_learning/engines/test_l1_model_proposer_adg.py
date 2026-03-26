"""ADG importability contract for system_learning/engines/l1_model_proposer.py."""
from __future__ import annotations



def test_module_importable():
    """Module l1_model_proposer must be importable."""
    import system_learning.engines.l1_model_proposer  # noqa: F401

    assert system_learning.engines.l1_model_proposer is not None