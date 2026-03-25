"""ADG importability contract for agentic_core/prompt_governance/scripts/import_violation_visitor.py."""
from __future__ import annotations

import agentic_core.prompt_governance.scripts.import_violation_visitor  # noqa: F401


def test_module_importable():
    """Module import_violation_visitor must be importable."""
    assert agentic_core.prompt_governance.scripts.import_violation_visitor is not None
