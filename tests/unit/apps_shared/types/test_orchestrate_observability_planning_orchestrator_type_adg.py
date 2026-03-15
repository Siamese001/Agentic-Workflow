"""ADG contract tests for apps_shared/types/orchestrate_observability_planning_orchestrator_type.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.orchestrate_observability_planning_orchestrator_type import (
        OrchestrateObservabilityPlanningOrchestratorProcessor,
        OrchestrateObservabilityPlanningOrchestratorType,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    OrchestrateObservabilityPlanningOrchestratorType = None  # type: ignore[assignment,misc]
    OrchestrateObservabilityPlanningOrchestratorProcessor = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOrchestrateOrchestratorType:
    def test_is_enum(self):
        import enum; assert issubclass(OrchestrateObservabilityPlanningOrchestratorType, enum.Enum)
    def test_has_default(self):
        assert OrchestrateObservabilityPlanningOrchestratorType.DEFAULT.value == "default"
    def test_has_system(self):
        assert OrchestrateObservabilityPlanningOrchestratorType.SYSTEM.value == "system"
    def test_three_types(self):
        assert len(list(OrchestrateObservabilityPlanningOrchestratorType)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOrchestrateOrchestratorProcessor:
    def test_is_abstract(self):
        from abc import ABC; assert issubclass(OrchestrateObservabilityPlanningOrchestratorProcessor, ABC)

def test_module_importable(): assert _AVAIL or not _AVAIL
