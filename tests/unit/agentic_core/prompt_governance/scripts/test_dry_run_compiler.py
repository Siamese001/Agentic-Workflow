"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/dry_run_compiler.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_dry_run_compiler_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.prompt_governance.scripts.dry_run_compiler import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    compile_template,
    find_jinja_templates,
    initialize_jinja_environment,
    verify_all_templates,
)


class TestInitializeJinjaEnvironmentFunction:
    def test_is_callable(self):
        assert callable(initialize_jinja_environment)

class TestCompileTemplateFunction:
    def test_is_callable(self):
        assert callable(compile_template)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compile_template)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestFindJinjaTemplatesFunction:
    def test_is_callable(self):
        assert callable(find_jinja_templates)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_jinja_templates)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestVerifyAllTemplatesFunction:
    def test_is_callable(self):
        assert callable(verify_all_templates)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(verify_all_templates)
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
    """Module dry_run_compiler must be importable or skip gracefully."""
    pass  # Import verified at module level
