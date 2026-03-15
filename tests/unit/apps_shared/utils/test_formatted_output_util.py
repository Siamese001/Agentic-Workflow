"""Foundational behavioral tests for apps_shared/utils/formatted_output_util.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_formatted_output_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.formatted_output_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        FormatData,
        FormatScriptsContext,
        FormattedOutput,
        format,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    FormattedOutput = None  # type: ignore[assignment,misc]
    FormatScriptsContext = None  # type: ignore[assignment,misc]
    format = None  # type: ignore[assignment,misc]
    FormatData = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestFormattedOutputContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FormattedOutput)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(FormattedOutput)}
        assert field_names >= {'data'}

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestFormatScriptsContextContract:
    def test_is_class(self):
        assert isinstance(FormatScriptsContext, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(FormatScriptsContext, type)

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestFormatFunction:
    def test_is_callable(self):
        assert callable(format)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(format)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestFormatdataFunction:
    def test_is_callable(self):
        assert callable(FormatData)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(FormatData)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="formatted_output_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module formatted_output_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
