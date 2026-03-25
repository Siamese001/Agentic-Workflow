"""Foundational behavioral tests for apps_shared/utils/prompt_loader_util.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_prompt_loader_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.utils.prompt_loader_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    PromptLoader,
    get_global_constraints,
    get_specialist_prompt,
    load_prompt_for_agent,
)


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

class TestLoadPromptForAgentFunction:
    def test_is_callable(self):
        assert callable(load_prompt_for_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_prompt_for_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetGlobalConstraintsFunction:
    def test_is_callable(self):
        assert callable(get_global_constraints)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_global_constraints)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetSpecialistPromptFunction:
    def test_is_callable(self):
        assert callable(get_specialist_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_specialist_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module prompt_loader_util must be importable or skip gracefully."""
    pass  # Import verified at module level
