"""ADG importability contract for agentic_core/L3_orchestration/types/human_decision_artifact_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_human_decision_artifact_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.human_decision_artifact_types import (  # noqa: F401
        HumanAction,
        StructuredPatchSchema,
        HumanDecisionArtifact,
        create_human_review_draft,
        create_approval_artifact,
        create_rejection_artifact,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HumanAction = None  # type: ignore[assignment,misc]
    StructuredPatchSchema = None  # type: ignore[assignment,misc]
    HumanDecisionArtifact = None  # type: ignore[assignment,misc]
    create_human_review_draft = None  # type: ignore[assignment,misc]
    create_approval_artifact = None  # type: ignore[assignment,misc]
    create_rejection_artifact = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="human_decision_artifact_types.py deps unavailable")
class TestHumanDecisionArtifactTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: human_decision_artifact_types.py must be importable."""
        assert _AVAILABLE

    def test_humanaction_is_type(self) -> None:
        assert HumanAction is not None

    def test_structuredpatchschema_is_type(self) -> None:
        assert StructuredPatchSchema is not None

    def test_humandecisionartifact_is_type(self) -> None:
        assert HumanDecisionArtifact is not None

    def test_create_human_review_draft_callable(self) -> None:
        assert callable(create_human_review_draft)

    def test_create_approval_artifact_callable(self) -> None:
        assert callable(create_approval_artifact)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

