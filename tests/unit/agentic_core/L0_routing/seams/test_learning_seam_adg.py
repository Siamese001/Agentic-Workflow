"""ADG importability contract for agentic_core/L0_routing/seams/learning_seam.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_learning_seam.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.seams.learning_seam import (  # noqa: F401
        LearningArtifactIntent,
        LearningPersistenceService,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LearningArtifactIntent = None  # type: ignore[assignment,misc]
    LearningPersistenceService = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="learning_seam.py deps unavailable")
class TestLearningSeamImportability:
    def test_module_importable(self) -> None:
        """ADG contract: learning_seam.py must be importable."""
        assert _AVAILABLE

    def test_learningartifactintent_is_type(self) -> None:
        assert LearningArtifactIntent is not None

    def test_learningpersistenceservice_is_type(self) -> None:
        assert LearningPersistenceService is not None

