"""Guard test: importing L6 observability agents must not raise MRO TypeError.

This test validates that the redundant SubatomicTestingMixin removal
from agent class hierarchies does not regress. SovereignBaseAgent already
includes SubatomicTestingMixin in its MRO, so subclasses must NOT
re-declare it as a direct base.
"""

import importlib

import pytest

L6_MODULES = [
    "agentic_core.L6_observability.reasoning.TelemetryAgent",
    "agentic_core.L6_observability.reasoning.TracingAgent",
    "agentic_core.L6_observability.reasoning.MetricsAgent",
    "agentic_core.L6_observability.reasoning.PerformanceAnalystAgent",
    "agentic_core.L6_observability.reasoning.AutonomicMonitorAgent",
]

SAMPLE_AGENTS = [
    "agentic_core.L0_maintenance.reasoning.BootstrapAgent",
    "agentic_core.L0_maintenance.reasoning.DocstringComplianceAgent",
    "agentic_core.L0_maintenance.reasoning.GospelSyncAgent",
]


class TestNoMROErrorOnImport:
    """Importing agents must not raise TypeError due to MRO conflicts."""

    @pytest.mark.parametrize("module_path", L6_MODULES + SAMPLE_AGENTS)
    def test_import_no_mro_crash(self, module_path: str):
        """Import must succeed without MRO TypeError."""
        mod = importlib.import_module(module_path)
        assert mod is not None

    @pytest.mark.parametrize("module_path", L6_MODULES)
    def test_l6_agent_has_subatomic_in_mro(self, module_path: str):
        """L6 agents must still have SubatomicTestingMixin in MRO via SovereignBaseAgent."""
        mod = importlib.import_module(module_path)
        # Get the main class (last component of module path)
        class_name = module_path.rsplit(".", 1)[-1]
        cls = getattr(mod, class_name)
        mro_names = [c.__name__ for c in cls.__mro__]
        assert "SubatomicTestingMixin" in mro_names, (
            f"{class_name} must have SubatomicTestingMixin in MRO (inherited via SovereignBaseAgent)"
        )

    @pytest.mark.parametrize("module_path", L6_MODULES)
    def test_l6_agent_no_redundant_subatomic_base(self, module_path: str):
        """L6 agents must NOT have SubatomicTestingMixin as a direct base."""
        mod = importlib.import_module(module_path)
        class_name = module_path.rsplit(".", 1)[-1]
        cls = getattr(mod, class_name)
        direct_bases = [b.__name__ for b in cls.__bases__]
        assert "SubatomicTestingMixin" not in direct_bases, (
            f"{class_name} has SubatomicTestingMixin as direct base — "
            f"this is redundant since SovereignBaseAgent already includes it"
        )
