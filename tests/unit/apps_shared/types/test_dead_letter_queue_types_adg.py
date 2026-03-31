"""ADG contract tests for apps_shared/types/dead_letter_queue_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module dead_letter_queue_types must be importable."""
    import apps_shared.types.dead_letter_queue_types  # noqa: F401

    assert apps_shared.types.dead_letter_queue_types is not None
