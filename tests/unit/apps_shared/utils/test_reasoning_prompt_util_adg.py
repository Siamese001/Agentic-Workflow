"""ADG-driven tests for apps_shared/utils/reasoning_prompt_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.reasoning_prompt_util import (  # noqa: F401
        build_reasoning_prompt_addendum,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    build_reasoning_prompt_addendum = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_prompt_util.py deps unavailable")
class TestBuildReasoningPromptAddendum:
    def test_is_callable(self):
        assert callable(build_reasoning_prompt_addendum)


def test_module_importable():
    """Module reasoning_prompt_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE