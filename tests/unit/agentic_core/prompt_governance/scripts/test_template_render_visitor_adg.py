"""ADG importability contract for agentic_core/prompt_governance/scripts/template_render_visitor.py."""
from __future__ import annotations

import agentic_core.prompt_governance.scripts.template_render_visitor  # noqa: F401


def test_module_importable():
    """Module template_render_visitor must be importable."""
    assert agentic_core.prompt_governance.scripts.template_render_visitor is not None
