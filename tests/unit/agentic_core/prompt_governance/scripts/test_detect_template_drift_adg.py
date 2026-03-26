"""ADG-driven tests for agentic_core/prompt_governance/scripts/detect_template_drift.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.scripts.detect_template_drift  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.scripts.detect_template_drift  # noqa: F401
        """Module detect_template_drift must be importable."""
        assert agentic_core.prompt_governance.scripts.detect_template_drift is not None

    assert agentic_core.prompt_governance.scripts.detect_template_drift is not None
