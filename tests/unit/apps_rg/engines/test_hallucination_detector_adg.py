"""ADG importability contract for apps_rg/engines/hallucination_detector.py."""
from __future__ import annotations


def test_module_importable():
    """Module hallucination_detector must be importable."""
    import apps_rg.engines.hallucination_detector  # noqa: F401

    assert apps_rg.engines.hallucination_detector is not None
