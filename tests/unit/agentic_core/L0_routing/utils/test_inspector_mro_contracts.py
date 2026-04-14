"""MRO regression guards for inspector agents."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit_min_deps

INSPECTOR_SPECS = [
    ("agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent", "DagRuntimeInspectorAgent"),
]


def _import_class(module_path: str, class_name: str):
    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        pytest.skip(f"Unable to import {module_path}: {exc}")
    value = getattr(module, class_name, None)
    if value is None:
        pytest.skip(f"{class_name} not exported by {module_path}")
    return value


@pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[spec[1] for spec in INSPECTOR_SPECS])
def test_subatomic_testing_mixin_is_present_in_mro(module_path: str, class_name: str) -> None:
    cls = _import_class(module_path, class_name)
    mixin_mod = pytest.importorskip("agentic_core.L5_safety.testing.subatomic_testing_mixin")
    mixin = getattr(mixin_mod, "SubatomicTestingMixin", None)
    assert isinstance(mixin, type)
    assert mixin in cls.__mro__


@pytest.mark.parametrize("module_path,class_name", INSPECTOR_SPECS, ids=[spec[1] for spec in INSPECTOR_SPECS])
def test_subatomic_testing_mixin_is_not_a_direct_base(module_path: str, class_name: str) -> None:
    cls = _import_class(module_path, class_name)
    mixin_mod = pytest.importorskip("agentic_core.L5_safety.testing.subatomic_testing_mixin")
    mixin = getattr(mixin_mod, "SubatomicTestingMixin", None)
    assert mixin not in cls.__bases__


def test_sovereign_base_agent_mro_contains_required_mixins() -> None:
    sovereign_mod = pytest.importorskip("agentic_core.L5_safety.enforcement.governance.sovereign_base_agent")
    config_mod = pytest.importorskip("agentic_core.L5_safety.config.config_mixin")
    testing_mod = pytest.importorskip("agentic_core.L5_safety.testing.subatomic_testing_mixin")
    sovereign = getattr(sovereign_mod, "SovereignBaseAgent", None)
    config_mixin = getattr(config_mod, "ConfigMixin", None)
    test_mixin = getattr(testing_mod, "SubatomicTestingMixin", None)
    assert isinstance(sovereign, type)
    assert config_mixin in sovereign.__mro__
    assert test_mixin in sovereign.__mro__
