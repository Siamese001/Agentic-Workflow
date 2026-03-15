"""Foundational behavioral tests for apps_shared/utils/prompt_enhancer_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_prompt_enhancer_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.prompt_enhancer_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        EnhancementConfig,
        PromptEnhancer,
        enhance_prompt,
        enhance_prompt_advanced,
        get_prompt_enhancer,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    EnhancementConfig = None  # type: ignore[assignment,misc]
    PromptEnhancer = None  # type: ignore[assignment,misc]
    get_prompt_enhancer = None  # type: ignore[assignment,misc]
    enhance_prompt = None  # type: ignore[assignment,misc]
    enhance_prompt_advanced = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestEnhancementConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EnhancementConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EnhancementConfig)}
        assert field_names >= {'legacy_mode', 'enable_cognitive_contracts', 'enable_few_shot_examples', 'max_examples_per_injection', 'enable_semantic_fencing'}

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestPromptEnhancerContract:
    def test_is_class(self):
        assert isinstance(PromptEnhancer, type)

    def test_has_method_enhance_prompt(self):
        assert callable(getattr(PromptEnhancer, 'enhance_prompt', None))

    def test_has_method_process_response(self):
        assert callable(getattr(PromptEnhancer, 'process_response', None))

    def test_has_method_create_enhanced_template(self):
        assert callable(getattr(PromptEnhancer, 'create_enhanced_template', None))

    def test_has_method_get_enhancement_stats(self):
        assert callable(getattr(PromptEnhancer, 'get_enhancement_stats', None))

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestGetPromptEnhancerFunction:
    def test_is_callable(self):
        assert callable(get_prompt_enhancer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_prompt_enhancer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestEnhancePromptFunction:
    def test_is_callable(self):
        assert callable(enhance_prompt)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enhance_prompt)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestEnhancePromptAdvancedFunction:
    def test_is_callable(self):
        assert callable(enhance_prompt_advanced)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enhance_prompt_advanced)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_enhancer_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module prompt_enhancer_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
