"""ADG importability contract for system_learning/adapters/l4_meta_prior_provider.py."""
from __future__ import annotations



def test_module_importable():
    """Module l4_meta_prior_provider must be importable."""
    import system_learning.adapters.l4_meta_prior_provider  # noqa: F401

    assert system_learning.adapters.l4_meta_prior_provider is not None