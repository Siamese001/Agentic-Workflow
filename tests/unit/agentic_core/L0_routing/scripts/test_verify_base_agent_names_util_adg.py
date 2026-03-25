"""ADG-driven tests for agentic_core/L0_routing/scripts/verify_base_agent_names_util.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    import agentic_core.L0_routing.scripts.verify_base_agent_names_util as _mod
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None

def test_module_importable():
    """Module verify_base_agent_names_util.py is importable (or deps unavailable)."""
    if _mod is None:
        pytest.skip('verify_base_agent_names_util not available')
    assert _mod.__name__ == 'agentic_core.L0_routing.scripts.verify_base_agent_names_util'

def test_module_exposes_public_api():
    """verify_base_agent_names_util module exposes expected public symbols."""
    if _mod is None:
        pytest.skip('verify_base_agent_names_util not available')
    public_symbols = [n for n in dir(_mod) if not n.startswith('_')]
    assert len(public_symbols) >= 1, 'verify_base_agent_names_util must expose at least one public symbol'