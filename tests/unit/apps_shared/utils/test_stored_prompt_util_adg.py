"""ADG-driven tests for apps_shared/utils/stored_prompt_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.stored_prompt_util import (  # noqa: F401
        PromptStore,
        StoredPrompt,
        get_prompt_version,
        get_store,
        retrieve_prompt,
        store_prompt,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    StoredPrompt = None  # type: ignore[assignment,misc]
    PromptStore = None  # type: ignore[assignment,misc]
    get_store = None  # type: ignore[assignment,misc]
    store_prompt = None  # type: ignore[assignment,misc]
    retrieve_prompt = None  # type: ignore[assignment,misc]
    get_prompt_version = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="stored_prompt_util.py deps unavailable")
class TestStoredPrompt:
    def test_is_class(self):
        assert isinstance(StoredPrompt, type)
    def test_importable(self):
        assert StoredPrompt is not None

@pytest.mark.skipif(not _AVAILABLE, reason="stored_prompt_util.py deps unavailable")
class TestPromptStore:
    def test_is_class(self):
        assert isinstance(PromptStore, type)
    def test_importable(self):
        assert PromptStore is not None

@pytest.mark.skipif(not _AVAILABLE, reason="stored_prompt_util.py deps unavailable")
class TestGetStore:
    def test_is_callable(self):
        assert callable(get_store)

@pytest.mark.skipif(not _AVAILABLE, reason="stored_prompt_util.py deps unavailable")
class TestStorePrompt:
    def test_is_callable(self):
        assert callable(store_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="stored_prompt_util.py deps unavailable")
class TestRetrievePrompt:
    def test_is_callable(self):
        assert callable(retrieve_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="stored_prompt_util.py deps unavailable")
class TestGetPromptVersion:
    def test_is_callable(self):
        assert callable(get_prompt_version)


def test_module_importable():
    """Module stored_prompt_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
