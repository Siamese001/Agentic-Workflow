"""Foundational behavioral tests for agentic_core/prompt_governance/security/detectors/injection_detector.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.prompt_governance.security.detectors.injection_detector  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.security.detectors.injection_detector  # noqa: F401
    """Module injection_detector must be importable."""
    assert agentic_core.prompt_governance.security.detectors.injection_detector is not None
