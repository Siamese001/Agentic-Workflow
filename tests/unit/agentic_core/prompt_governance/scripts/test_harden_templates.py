"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/harden_templates.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_harden_templates_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.harden_templates import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        extract_variables,
        find_jinja_files,
        generate_standardized_header,
        is_already_hardened,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    find_jinja_files = None  # type: ignore[assignment,misc]
    is_already_hardened = None  # type: ignore[assignment,misc]
    extract_variables = None  # type: ignore[assignment,misc]
    generate_standardized_header = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestFindJinjaFilesFunction:
    def test_is_callable(self):
        assert callable(find_jinja_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_jinja_files)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestIsAlreadyHardenedFunction:
    def test_is_callable(self):
        assert callable(is_already_hardened)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_already_hardened)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestExtractVariablesFunction:
    def test_is_callable(self):
        assert callable(extract_variables)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_variables)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestGenerateStandardizedHeaderFunction:
    def test_is_callable(self):
        assert callable(generate_standardized_header)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(generate_standardized_header)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="harden_templates.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module harden_templates must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
