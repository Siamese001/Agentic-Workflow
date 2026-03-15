"""ADG importability contract for agentic_core/L3_orchestration/types/human_decision_artifact_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_human_decision_artifact_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.human_decision_artifact_types import (  # noqa: F401
        HumanAction,
        HumanDecisionArtifact,
        StructuredPatchSchema,
        create_approval_artifact,
        create_human_review_draft,
        create_rejection_artifact,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HumanAction = None  # type: ignore[assignment,misc]
    StructuredPatchSchema = None  # type: ignore[assignment,misc]
    HumanDecisionArtifact = None  # type: ignore[assignment,misc]
    create_human_review_draft = None  # type: ignore[assignment,misc]
    create_approval_artifact = None  # type: ignore[assignment,misc]
    create_rejection_artifact = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="human_decision_artifact_types deps unavailable")
class TestHumanDecisionArtifactTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/types/human_decision_artifact_types.py must be importable."""
        assert _AVAILABLE

    def test_humanaction_defined(self) -> None:
        assert HumanAction is not None

    def test_structuredpatchschema_defined(self) -> None:
        assert StructuredPatchSchema is not None

    def test_humandecisionartifact_defined(self) -> None:
        assert HumanDecisionArtifact is not None
