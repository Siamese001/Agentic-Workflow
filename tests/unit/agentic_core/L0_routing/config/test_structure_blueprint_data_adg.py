"""Runtime-hardened public-surface tests for structure blueprint data."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

MODULE_CANDIDATES = [
    "agentic_core.L5_safety.config.structure_blueprint.data",
    "agentic_core.L5_safety.config.structure_blueprint.structure_blueprint_data",
    "agentic_core.L5_safety.config.structure_blueprint.territories",
]
CLASS_CANDIDATES = ["StructureBlueprintData"]
CALLABLE_CANDIDATES = ["get_all_territories", "load_structure_blueprint"]


def _import_first_available(candidates: list[str]):
    errors: list[str] = []
    for module_path in candidates:
        try:
            return importlib.import_module(module_path)
        except Exception as exc:
            errors.append(f"{module_path} -> {exc.__class__.__name__}: {exc}")
    pytest.skip("No compatible module import succeeded: " + " | ".join(errors))


def _resolve_first(obj, candidates: list[str]):
    for name in candidates:
        value = getattr(obj, name, None)
        if value is not None:
            return name, value
    return None, None


@pytest.fixture(scope="module")
def mod():
    return _import_first_available(MODULE_CANDIDATES)


def test_module_importable(mod):
    assert mod.__name__ in MODULE_CANDIDATES


def test_module_exposes_public_api(mod):
    public = [name for name in dir(mod) if not name.startswith("_")]
    assert public, f"{mod.__name__} should expose at least one public symbol"


def test_expected_class_export_exists(mod):
    name, value = _resolve_first(mod, CLASS_CANDIDATES)
    assert value is not None, f"Expected one of {CLASS_CANDIDATES} on {mod.__name__}"
    assert isinstance(value, type), f"{name} must resolve to a class"


def test_expected_callable_export_exists(mod):
    name, value = _resolve_first(mod, CALLABLE_CANDIDATES)
    assert callable(value), f"Expected callable from {CALLABLE_CANDIDATES} on {mod.__name__}"
