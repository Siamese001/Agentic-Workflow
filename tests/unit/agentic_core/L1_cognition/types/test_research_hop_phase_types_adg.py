"""ADG-driven tests for L1_cognition/types/research_hop_phase_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L1_cognition.types.research_hop_phase_types import (
    ResearchHopPhase,
    ValidationRejectionReason,
)


class TestResearchHopPhase:
    def test_is_enum(self):
        from agentic_core.L1_cognition.types.research_hop_phase_types import (
        import enum
        assert issubclass(ResearchHopPhase, enum.Enum)

    def test_is_str_enum(self):
        assert issubclass(ResearchHopPhase, str)


class TestValidationRejectionReason:
    def test_is_enum(self):
        import enum
        assert issubclass(ValidationRejectionReason, enum.Enum)

    def test_is_str_enum(self):
        assert issubclass(ValidationRejectionReason, str)
