"""
MRO regression guards for inspector agents.

Enforced invariants:
    1. Each inspector agent has SubatomicTestingMixin in its MRO.
    2. None list SubatomicTestingMixin as a direct base (inherited via SovereignBaseAgent).
    3. No duplicate class entries in any MRO chain.
    4. SovereignBaseAgent MRO includes SubatomicTestingMixin and ConfigMixin.
"""

from __future__ import annotations

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

INSPECTOR_SPECS = [
    (
        "agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent",
        "DagRuntimeInspectorAgent",
    ),
]


def _import_class(module_path: str, class_name: str) -> type:
    """Import a class by module path and class name."""
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


# ---------------------------------------------------------------------------
# 1. SubatomicTestingMixin MUST be in each inspector's MRO
# ---------------------------------------------------------------------------


class TestSubatomicTestingMixinInMRO:
    """SubatomicTestingMixin must appear in the MRO of every inspector agent."""

    @pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[s[1] for s in INSPECTOR_SPECS])
    def test_subatomic_in_mro(self, module_path: str, class_name: str) -> None:
        """Test subatomic_in_mro contract compliance."""
        cls = _import_class(module_path, class_name)
        from agentic_core.L5_safety.testing.subatomic_testing_mixin import SubatomicTestingMixin
        assert SubatomicTestingMixin in cls.__mro__, f"{class_name} missing SubatomicTestingMixin"

    @pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[s[1] for s in INSPECTOR_SPECS])
    def test_subatomic_not_direct_base(self, module_path: str, class_name: str) -> None:
        """Test subatomic_not_direct_base contract compliance."""
        cls = _import_class(module_path, class_name)
        from agentic_core.L5_safety.testing.subatomic_testing_mixin import SubatomicTestingMixin
        assert SubatomicTestingMixin not in cls.__bases__, f"{class_name} should not list SubatomicTestingMixin as direct base"


class TestNoDuplicatesInMRO:
    """Every class must appear exactly once in the MRO chain."""

    @pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[s[1] for s in INSPECTOR_SPECS])
    def test_no_mro_duplicates(self, module_path: str, class_name: str) -> None:
        """Test no_mro_duplicates contract compliance."""
        cls = _import_class(module_path, class_name)
        mro = cls.__mro__
        assert len(mro) == len(set(mro)), f"{class_name} has duplicate classes in MRO"


class TestSovereignBaseAgentMRO:
    """SovereignBaseAgent must provide SubatomicTestingMixin and ConfigMixin to subclasses."""

    def test_sovereign_has_subatomic_testing_mixin(self) -> None:
        """Test that SovereignBaseAgent has SubatomicTestingMixin in MRO."""
        from agentic_core.L5_safety.enforcement.governance.sovereign_base_agent import SovereignBaseAgent
        from agentic_core.L5_safety.testing.subatomic_testing_mixin import SubatomicTestingMixin
        assert SubatomicTestingMixin in SovereignBaseAgent.__mro__, "SovereignBaseAgent missing SubatomicTestingMixin"

    def test_sovereign_has_config_mixin(self) -> None:
        """Test that SovereignBaseAgent has ConfigMixin in MRO."""
        from agentic_core.L5_safety.config.config_mixin import ConfigMixin
        from agentic_core.L5_safety.enforcement.governance.sovereign_base_agent import SovereignBaseAgent
        assert ConfigMixin in SovereignBaseAgent.__mro__, "SovereignBaseAgent missing ConfigMixin"
