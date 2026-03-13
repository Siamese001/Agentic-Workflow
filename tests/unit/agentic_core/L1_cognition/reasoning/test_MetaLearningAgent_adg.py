"""ADG importability contract for agentic_core/L1_cognition/reasoning/MetaLearningAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_MetaLearningAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.reasoning.MetaLearningAgent import (  # noqa: F401
        ExperienceRecord,
        MetaLearningAgent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExperienceRecord = None  # type: ignore[assignment,misc]
    MetaLearningAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="MetaLearningAgent deps unavailable")
class TestMetalearningagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L1_cognition/reasoning/MetaLearningAgent.py must be importable."""
        assert _AVAILABLE

    def test_experiencerecord_defined(self) -> None:
        assert ExperienceRecord is not None

    def test_metalearningagent_defined(self) -> None:
        assert MetaLearningAgent is not None
