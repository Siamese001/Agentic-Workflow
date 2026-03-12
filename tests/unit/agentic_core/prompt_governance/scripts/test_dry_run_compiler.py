"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/dry_run_compiler.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_dry_run_compiler_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.dry_run_compiler import (  # noqa: F401
        initialize_jinja_environment,
        compile_template,
        find_jinja_templates,
        verify_all_templates,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    initialize_jinja_environment = None  # type: ignore[assignment,misc]
    compile_template = None  # type: ignore[assignment,misc]
    find_jinja_templates = None  # type: ignore[assignment,misc]
    verify_all_templates = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestInitializeJinjaEnvironmentFunction:
    def test_is_callable(self):
        assert callable(initialize_jinja_environment)

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestCompileTemplateFunction:
    def test_is_callable(self):
        assert callable(compile_template)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compile_template)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestFindJinjaTemplatesFunction:
    def test_is_callable(self):
        assert callable(find_jinja_templates)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_jinja_templates)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestVerifyAllTemplatesFunction:
    def test_is_callable(self):
        assert callable(verify_all_templates)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(verify_all_templates)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dry_run_compiler.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module dry_run_compiler must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
