"""ADG importability contract for system_learning/engines/in_memory_scoring_report_store.py."""
from __future__ import annotations



def test_module_importable():
    """Module in_memory_scoring_report_store must be importable."""
    import system_learning.engines.in_memory_scoring_report_store  # noqa: F401

    assert system_learning.engines.in_memory_scoring_report_store is not None