"""Smoke tests for time utility exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestTimeUtilsImplAdg:
    """Validate time utility symbols without invoking live runtime behavior."""

    def test_get_current_time(self) -> None:
        """Import get_current_time export."""
        func = import_attr_or_skip("agentic_core.L2_execution.utils", "get_current_time")
        assert callable(func)

    def test_convert_time(self) -> None:
        """Import convert_time export."""
        func = import_attr_or_skip("agentic_core.L2_execution.utils", "convert_time")
        assert callable(func)

    def test_TimeTools_init(self) -> None:
        """Import TimeTools class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.utils", "TimeTools")
        assert klass is not None

    def test_TimeTools_get_current_time(self) -> None:
        """Validate TimeTools.get_current_time method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.utils", "TimeTools")
        assert hasattr(klass, "get_current_time")
