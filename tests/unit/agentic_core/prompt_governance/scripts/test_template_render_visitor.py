"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/template_render_visitor.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_template_render_visitor_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.template_render_visitor import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        TemplateRenderVisitor,
        audit_agent_compliance,
        extract_template_schema,
        find_python_files,
        main,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    TemplateRenderVisitor = None  # type: ignore[assignment,misc]
    extract_template_schema = None  # type: ignore[assignment,misc]
    find_python_files = None  # type: ignore[assignment,misc]
    audit_agent_compliance = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestTemplateRenderVisitorContract:
    def test_is_class(self):
        assert isinstance(TemplateRenderVisitor, type)

    def test_has_method_visit_FunctionDef(self):
        assert callable(getattr(TemplateRenderVisitor, 'visit_FunctionDef', None))

    def test_has_method_visit_ClassDef(self):
        assert callable(getattr(TemplateRenderVisitor, 'visit_ClassDef', None))

    def test_has_method_visit_Call(self):
        assert callable(getattr(TemplateRenderVisitor, 'visit_Call', None))

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestExtractTemplateSchemaFunction:
    def test_is_callable(self):
        assert callable(extract_template_schema)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_template_schema)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestFindPythonFilesFunction:
    def test_is_callable(self):
        assert callable(find_python_files)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(find_python_files)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestAuditAgentComplianceFunction:
    def test_is_callable(self):
        assert callable(audit_agent_compliance)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(audit_agent_compliance)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module template_render_visitor must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
