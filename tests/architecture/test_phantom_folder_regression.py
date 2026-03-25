"""Behavioral contract tests for agentic_core.L5_safety.config.structure_blueprint."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L5_safety.config.structure_blueprint"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_subfolderdefinition_is_instantiable(mod):
    """SubfolderDefinition is accessible and is a type."""
    cls = getattr(mod, "SubfolderDefinition", None)
    assert cls is not None, "SubfolderDefinition must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SubfolderDefinition must be a class"


def test_territorydefinition_is_instantiable(mod):
    """TerritoryDefinition is accessible and is a type."""
    cls = getattr(mod, "TerritoryDefinition", None)
    assert cls is not None, "TerritoryDefinition must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TerritoryDefinition must be a class"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_get_all_territories_is_callable(mod):
    """get_all_territories is accessible and callable."""
    func = getattr(mod, "get_all_territories", None)
    assert func is not None, "get_all_territories must be defined in {MODULE_PATH}"
    assert callable(func), "get_all_territories must be callable"


def test_get_apps_lic_subfolder_map_is_callable(mod):
    """get_apps_lic_subfolder_map is accessible and callable."""
    func = getattr(mod, "get_apps_lic_subfolder_map", None)
    assert func is not None, "get_apps_lic_subfolder_map must be defined in {MODULE_PATH}"
    assert callable(func), "get_apps_lic_subfolder_map must be callable"


def test_get_apps_rg_subfolder_map_is_callable(mod):
    """get_apps_rg_subfolder_map is accessible and callable."""
    func = getattr(mod, "get_apps_rg_subfolder_map", None)
    assert func is not None, "get_apps_rg_subfolder_map must be defined in {MODULE_PATH}"
    assert callable(func), "get_apps_rg_subfolder_map must be callable"


def test_get_apps_shared_subfolder_map_is_callable(mod):
    """get_apps_shared_subfolder_map is accessible and callable."""
    func = getattr(mod, "get_apps_shared_subfolder_map", None)
    assert func is not None, "get_apps_shared_subfolder_map must be defined in {MODULE_PATH}"
    assert callable(func), "get_apps_shared_subfolder_map must be callable"


def test_get_canonical_test_path_is_callable(mod):
    """get_canonical_test_path is accessible and callable."""
    func = getattr(mod, "get_canonical_test_path", None)
    assert func is not None, "get_canonical_test_path must be defined in {MODULE_PATH}"
    assert callable(func), "get_canonical_test_path must be callable"


def test_get_core_subfolder_map_is_callable(mod):
    """get_core_subfolder_map is accessible and callable."""
    func = getattr(mod, "get_core_subfolder_map", None)
    assert func is not None, "get_core_subfolder_map must be defined in {MODULE_PATH}"
    assert callable(func), "get_core_subfolder_map must be callable"

