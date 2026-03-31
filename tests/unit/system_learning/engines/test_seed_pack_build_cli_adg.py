"""ADG-driven tests for system_learning/engines/seed_pack_build_cli.py — fan_in=0."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit

def test_module_importable():
    """Module seed_pack_build_cli must be importable."""
    import system_learning.engines.seed_pack_build_cli
    assert system_learning.engines.seed_pack_build_cli is not None
