"""Foundational behavioral tests for agentic_core/utils/detection_protocol_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.utils.detection_protocol_util  # noqa: F401


def test_module_importable():
        import agentic_core.utils.detection_protocol_util  # noqa: F401
        """Module detection_protocol_util must be importable."""
        assert agentic_core.utils.detection_protocol_util is not None

    assert agentic_core.utils.detection_protocol_util is not None
