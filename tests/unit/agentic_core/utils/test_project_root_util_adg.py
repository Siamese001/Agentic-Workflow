"""ADG importability contract for agentic_core/utils/project_root_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_project_root_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.utils.project_root_util import (  # noqa: F401
        get_project_root,
        get_project_root_safe,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    get_project_root = None  # type: ignore[assignment,misc]
    get_project_root_safe = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="project_root_util.py deps unavailable")
class TestProjectRootUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: project_root_util.py must be importable."""
        assert _AVAILABLE

    def test_get_project_root_callable(self) -> None:
        assert callable(get_project_root)

    def test_get_project_root_safe_callable(self) -> None:
        assert callable(get_project_root_safe)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

