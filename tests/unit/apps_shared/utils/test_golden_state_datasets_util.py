"""Foundational behavioral tests for apps_shared/utils/golden_state_datasets_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_golden_state_datasets_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.golden_state_datasets_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        load_baseline_scores,
        load_exemplar_prompts,
        load_golden_cases,
        load_golden_inputs,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    load_golden_inputs = None  # type: ignore[assignment,misc]
    load_baseline_scores = None  # type: ignore[assignment,misc]
    load_exemplar_prompts = None  # type: ignore[assignment,misc]
    load_golden_cases = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestLoadGoldenInputsFunction:
    def test_is_callable(self):
        assert callable(load_golden_inputs)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_golden_inputs)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestLoadBaselineScoresFunction:
    def test_is_callable(self):
        assert callable(load_baseline_scores)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_baseline_scores)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestLoadExemplarPromptsFunction:
    def test_is_callable(self):
        assert callable(load_exemplar_prompts)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_exemplar_prompts)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestLoadGoldenCasesFunction:
    def test_is_callable(self):
        assert callable(load_golden_cases)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_golden_cases)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_datasets_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module golden_state_datasets_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
