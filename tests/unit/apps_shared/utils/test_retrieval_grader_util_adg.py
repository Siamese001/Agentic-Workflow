"""ADG-driven tests for apps_shared/utils/retrieval_grader_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module retrieval_grader_util must be importable."""
    import apps_shared.utils.retrieval_grader_util  # noqa: F401

    assert apps_shared.utils.retrieval_grader_util is not None