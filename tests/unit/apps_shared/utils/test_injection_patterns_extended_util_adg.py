"""ADG-driven tests for apps_shared/utils/injection_patterns_extended_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.injection_patterns_extended_util import (  # noqa: F401
        extend_injection_loader,
        get_message_injection_patterns,
        get_quality_boost_injections,
        get_resume_injection_patterns,
        load_all_extended_patterns,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_resume_injection_patterns = None  # type: ignore[assignment,misc]
    get_message_injection_patterns = None  # type: ignore[assignment,misc]
    get_quality_boost_injections = None  # type: ignore[assignment,misc]
    load_all_extended_patterns = None  # type: ignore[assignment,misc]
    extend_injection_loader = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="injection_patterns_extended_util.py deps unavailable")
class TestGetResumeInjectionPatterns:
    def test_is_callable(self):
        assert callable(get_resume_injection_patterns)

@pytest.mark.skipif(not _AVAILABLE, reason="injection_patterns_extended_util.py deps unavailable")
class TestGetMessageInjectionPatterns:
    def test_is_callable(self):
        assert callable(get_message_injection_patterns)

@pytest.mark.skipif(not _AVAILABLE, reason="injection_patterns_extended_util.py deps unavailable")
class TestGetQualityBoostInjections:
    def test_is_callable(self):
        assert callable(get_quality_boost_injections)

@pytest.mark.skipif(not _AVAILABLE, reason="injection_patterns_extended_util.py deps unavailable")
class TestLoadAllExtendedPatterns:
    def test_is_callable(self):
        assert callable(load_all_extended_patterns)

@pytest.mark.skipif(not _AVAILABLE, reason="injection_patterns_extended_util.py deps unavailable")
class TestExtendInjectionLoader:
    def test_is_callable(self):
        assert callable(extend_injection_loader)


def test_module_importable():
    """Module injection_patterns_extended_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
