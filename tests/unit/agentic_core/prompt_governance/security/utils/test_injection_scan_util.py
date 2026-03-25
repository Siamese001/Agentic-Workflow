"""Foundational behavioral tests for agentic_core/prompt_governance/security/utils/injection_scan_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.prompt_governance.security.utils.injection_scan_util  # noqa: F401


def test_module_importable():
    """Module injection_scan_util must be importable."""
    assert agentic_core.prompt_governance.security.utils.injection_scan_util is not None
