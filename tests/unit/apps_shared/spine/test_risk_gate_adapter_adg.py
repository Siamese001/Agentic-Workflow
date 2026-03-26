"""ADG importability contract for apps_shared/spine/risk_gate_adapter.py."""
from __future__ import annotations



def test_module_importable():
    """Module risk_gate_adapter must be importable."""
    import apps_shared.spine.risk_gate_adapter  # noqa: F401

    assert apps_shared.spine.risk_gate_adapter is not None
