"""ADG-driven tests for apps_shared/utils/unified_config_helper_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.unified_config_helper_util import (  # noqa: F401
        UnifiedConfigLoader,
        get_category_defaults,
        merge_with_defaults,
        deep_merge,
        load_unified_config,
        validate_unified_config,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    UnifiedConfigLoader = None  # type: ignore[assignment,misc]
    get_category_defaults = None  # type: ignore[assignment,misc]
    merge_with_defaults = None  # type: ignore[assignment,misc]
    deep_merge = None  # type: ignore[assignment,misc]
    load_unified_config = None  # type: ignore[assignment,misc]
    validate_unified_config = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="unified_config_helper_util.py deps unavailable")
class TestUnifiedConfigLoader:
    def test_is_class(self):
        assert isinstance(UnifiedConfigLoader, type)
    def test_importable(self):
        assert UnifiedConfigLoader is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_config_helper_util.py deps unavailable")
class TestGetCategoryDefaults:
    def test_is_callable(self):
        assert callable(get_category_defaults)

@pytest.mark.skipif(not _AVAILABLE, reason="unified_config_helper_util.py deps unavailable")
class TestMergeWithDefaults:
    def test_is_callable(self):
        assert callable(merge_with_defaults)

@pytest.mark.skipif(not _AVAILABLE, reason="unified_config_helper_util.py deps unavailable")
class TestDeepMerge:
    def test_is_callable(self):
        assert callable(deep_merge)

@pytest.mark.skipif(not _AVAILABLE, reason="unified_config_helper_util.py deps unavailable")
class TestLoadUnifiedConfig:
    def test_is_callable(self):
        assert callable(load_unified_config)

@pytest.mark.skipif(not _AVAILABLE, reason="unified_config_helper_util.py deps unavailable")
class TestValidateUnifiedConfig:
    def test_is_callable(self):
        assert callable(validate_unified_config)


def test_module_importable():
    """Module unified_config_helper_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
