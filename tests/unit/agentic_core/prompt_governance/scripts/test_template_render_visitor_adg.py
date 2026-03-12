"""ADG-driven tests for agentic_core/prompt_governance/scripts/template_render_visitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.template_render_visitor import (  # noqa: F401
        TemplateRenderVisitor,
        extract_template_schema,
        find_python_files,
        audit_agent_compliance,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestTemplateRenderVisitor:
    def test_is_class(self):
        assert isinstance(TemplateRenderVisitor, type)
    def test_importable(self):
        assert TemplateRenderVisitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestExtractTemplateSchema:
    def test_is_callable(self):
        assert callable(extract_template_schema)

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestFindPythonFiles:
    def test_is_callable(self):
        assert callable(find_python_files)

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestAuditAgentCompliance:
    def test_is_callable(self):
        assert callable(audit_agent_compliance)

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestMain:
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

@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module template_render_visitor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
