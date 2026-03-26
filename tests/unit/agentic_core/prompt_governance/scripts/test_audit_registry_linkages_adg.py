"""ADG-driven tests for agentic_core/prompt_governance/scripts/audit_registry_linkages.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.scripts.audit_registry_linkages  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.scripts.audit_registry_linkages  # noqa: F401
    """Module audit_registry_linkages must be importable."""
    assert agentic_core.prompt_governance.scripts.audit_registry_linkages is not None
