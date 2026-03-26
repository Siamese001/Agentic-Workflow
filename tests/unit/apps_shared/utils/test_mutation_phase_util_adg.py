"""ADG-driven tests for apps_shared/utils/mutation_phase_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module mutation_phase_util must be importable."""
    import apps_shared.utils.mutation_phase_util  # noqa: F401

    assert apps_shared.utils.mutation_phase_util is not None