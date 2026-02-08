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

pytestmark = pytest.mark.unit_min_deps

INSPECTOR_SPECS = [
    (
        "agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent",
        "DagRuntimeInspectorAgent",
    ),
    (
        "agentic_core.L5_safety.reasoning.TokenBudgetInspectorAgent",
        "TokenBudgetInspectorAgent",
    ),
    (
        "agentic_core.L5_safety.reasoning.SignatureVerifierAgent",
        "SignatureVerifierAgent",
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
        cls = _import_class(module_path, class_name)
        mro_names = [c.__name__ for c in cls.__mro__]
        assert "SubatomicTestingMixin" in mro_names, (
            f"{class_name} MRO must include SubatomicTestingMixin.\nActual MRO: {mro_names}"
        )


# ---------------------------------------------------------------------------
# 2. SubatomicTestingMixin must NOT be a direct base of any inspector
# ---------------------------------------------------------------------------


class TestSubatomicNotDirectBase:
    """SubatomicTestingMixin must be inherited via SovereignBaseAgent, not listed directly."""

    @pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[s[1] for s in INSPECTOR_SPECS])
    def test_subatomic_not_direct_base(self, module_path: str, class_name: str) -> None:
        cls = _import_class(module_path, class_name)
        direct_base_names = [b.__name__ for b in cls.__bases__]
        assert "SubatomicTestingMixin" not in direct_base_names, (
            f"{class_name} lists SubatomicTestingMixin as a direct base.\n"
            f"It must be inherited via SovereignBaseAgent to avoid MRO conflicts.\n"
            f"Direct bases: {direct_base_names}"
        )


# ---------------------------------------------------------------------------
# 3. No duplicate class entries in MRO
# ---------------------------------------------------------------------------


class TestNoDuplicatesInMRO:
    """Every class must appear exactly once in the MRO chain."""

    @pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[s[1] for s in INSPECTOR_SPECS])
    def test_no_mro_duplicates(self, module_path: str, class_name: str) -> None:
        cls = _import_class(module_path, class_name)
        mro = cls.__mro__
        seen: set[type] = set()
        duplicates: list[str] = []
        for c in mro:
            if c in seen:
                duplicates.append(c.__name__)
            seen.add(c)
        assert not duplicates, f"{class_name} has duplicate entries in MRO: {duplicates}"


# ---------------------------------------------------------------------------
# 4. SovereignBaseAgent MRO includes SubatomicTestingMixin and ConfigMixin
# ---------------------------------------------------------------------------


class TestSovereignBaseAgentMRO:
    """SovereignBaseAgent must provide SubatomicTestingMixin and ConfigMixin to subclasses."""

    def test_sovereign_has_subatomic_testing_mixin(self) -> None:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        mro_names = [c.__name__ for c in SovereignBaseAgent.__mro__]
        assert "SubatomicTestingMixin" in mro_names, (
            f"SovereignBaseAgent MRO must include SubatomicTestingMixin.\nActual MRO: {mro_names}"
        )

    def test_sovereign_has_config_mixin(self) -> None:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        mro_names = [c.__name__ for c in SovereignBaseAgent.__mro__]
        assert "ConfigMixin" in mro_names, (
            f"SovereignBaseAgent MRO must include ConfigMixin.\nActual MRO: {mro_names}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
