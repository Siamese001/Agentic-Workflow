"""ADG-driven tests for system_learning/engines/seed_pack_build_cli.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.seed_pack_build_cli  # noqa: F401


def test_module_importable():
    """Module seed_pack_build_cli must be importable."""
    assert system_learning.engines.seed_pack_build_cli is not None
