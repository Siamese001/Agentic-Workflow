"""ADG importability contract for agentic_core/L3_orchestration/types/human_decision_artifact_types.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.types.human_decision_artifact_types  # noqa: F401


def test_module_importable():
    """Module human_decision_artifact_types must be importable."""
    assert agentic_core.L3_orchestration.types.human_decision_artifact_types is not None
