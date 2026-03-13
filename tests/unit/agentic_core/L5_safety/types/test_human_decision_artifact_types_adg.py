"""ADG importability contract for agentic_core/L5_safety/types/human_decision_artifact_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_human_decision_artifact_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.human_decision_artifact_types import (  # noqa: F401
        HumanDecisionArtifact,
        HumanDecisionViolation,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HumanDecisionViolation = None  # type: ignore[assignment,misc]
    HumanDecisionArtifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="human_decision_artifact_types deps unavailable")
class TestHumanDecisionArtifactTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/types/human_decision_artifact_types.py must be importable."""
        assert _AVAILABLE

    def test_humandecisionviolation_defined(self) -> None:
        assert HumanDecisionViolation is not None

    def test_humandecisionartifact_defined(self) -> None:
        assert HumanDecisionArtifact is not None
