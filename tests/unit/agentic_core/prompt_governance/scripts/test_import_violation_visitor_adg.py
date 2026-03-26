"""ADG importability contract for agentic_core/prompt_governance/scripts/import_violation_visitor.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.scripts.import_violation_visitor  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.scripts.import_violation_visitor  # noqa: F401
        """Module import_violation_visitor must be importable."""
        assert agentic_core.prompt_governance.scripts.import_violation_visitor is not None

    assert agentic_core.prompt_governance.scripts.import_violation_visitor is not None
