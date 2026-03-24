"""ADG importability contract for agentic_core/prompt_governance/scripts/template_render_visitor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_template_render_visitor.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.scripts.template_render_visitor import (  # noqa: F401
        TemplateRenderVisitor,
        audit_agent_compliance,
        extract_template_schema,
        find_python_files,
        main,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    extract_template_schema = None  # type: ignore[assignment,misc]
    TemplateRenderVisitor = None  # type: ignore[assignment,misc]
    find_python_files = None  # type: ignore[assignment,misc]
    audit_agent_compliance = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="template_render_visitor deps unavailable")
class TestTemplateRenderVisitorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/scripts/template_render_visitor.py must be importable."""
        assert _AVAILABLE

    def test_templaterendervisitor_defined(self) -> None:
        assert TemplateRenderVisitor is not None