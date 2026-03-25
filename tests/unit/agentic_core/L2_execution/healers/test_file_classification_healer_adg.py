"""ADG importability contract for agentic_core/L2_execution/healers/file_classification_healer.py."""
from __future__ import annotations

import agentic_core.L2_execution.healers.file_classification_healer  # noqa: F401


def test_module_importable():
    """Module file_classification_healer must be importable."""
    assert agentic_core.L2_execution.healers.file_classification_healer is not None
