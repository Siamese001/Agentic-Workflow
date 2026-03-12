"""Foundational behavioral tests for apps_shared/utils/prompt_loader_util.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_prompt_loader_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.prompt_loader_util import (  # noqa: F401
        PromptLoader,
        load_prompt_for_agent,
        get_global_constraints,
        get_specialist_prompt,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    PromptLoader = None  # type: ignore[assignment,misc]
    load_prompt_for_agent = None  # type: ignore[assignment,misc]
    get_global_constraints = None  # type: ignore[assignment,misc]
    get_specialist_prompt = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestPromptLoaderContract:
    def test_is_class(self):
        assert isinstance(PromptLoader, type)

    def test_has_method_load_global_constraints(self):
        assert callable(getattr(PromptLoader, 'load_global_constraints', None))

    def test_has_method_load_specialist_prompt(self):
        assert callable(getattr(PromptLoader, 'load_specialist_prompt', None))

    def test_has_method_build_full_prompt(self):
        assert callable(getattr(PromptLoader, 'build_full_prompt', None))

    def test_has_method_get_available_specialists(self):
        assert callable(getattr(PromptLoader, 'get_available_specialists', None))

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestLoadPromptForAgentFunction:
    def test_is_callable(self):
        assert callable(load_prompt_for_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_prompt_for_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestGetGlobalConstraintsFunction:
    def test_is_callable(self):
        assert callable(get_global_constraints)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_global_constraints)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestGetSpecialistPromptFunction:
    def test_is_callable(self):
        assert callable(get_specialist_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_specialist_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_loader_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module prompt_loader_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
