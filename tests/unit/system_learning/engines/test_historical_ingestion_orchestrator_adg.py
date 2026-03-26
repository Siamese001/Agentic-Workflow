"""ADG importability contract for system_learning/engines/historical_ingestion_orchestrator.py."""
from __future__ import annotations



def test_module_importable():
    """Module historical_ingestion_orchestrator must be importable."""
    import system_learning.engines.historical_ingestion_orchestrator  # noqa: F401

    assert system_learning.engines.historical_ingestion_orchestrator is not None