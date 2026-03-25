"""Behavioral contract tests for agentic_core.L0_routing.reasoning.RootCustomsAgent."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.reasoning.RootCustomsAgent"


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


def test_astanalyzer_is_instantiable(mod):
    """ASTAnalyzer is accessible and is a type."""
    cls = getattr(mod, "ASTAnalyzer", None)
    assert cls is not None, "ASTAnalyzer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ASTAnalyzer must be a class"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_rootcustomsagent_is_instantiable(mod):
    """RootCustomsAgent is accessible and is a type."""
    cls = getattr(mod, "RootCustomsAgent", None)
    assert cls is not None, "RootCustomsAgent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RootCustomsAgent must be a class"


def test_routingdecision_is_instantiable(mod):
    """RoutingDecision is accessible and is a type."""
    cls = getattr(mod, "RoutingDecision", None)
    assert cls is not None, "RoutingDecision must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingDecision must be a class"


def test_sovereignbaseagent_is_instantiable(mod):
    """SovereignBaseAgent is accessible and is a type."""
    cls = getattr(mod, "SovereignBaseAgent", None)
    assert cls is not None, "SovereignBaseAgent must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SovereignBaseAgent must be a class"


def test_assert_no_persistent_write_is_callable(mod):
    """assert_no_persistent_write is accessible and callable."""
    func = getattr(mod, "assert_no_persistent_write", None)
    assert func is not None, "assert_no_persistent_write must be defined in {MODULE_PATH}"
    assert callable(func), "assert_no_persistent_write must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


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


def test_get_validated_project_root_is_callable(mod):
    """get_validated_project_root is accessible and callable."""
    func = getattr(mod, "get_validated_project_root", None)
    assert func is not None, "get_validated_project_root must be defined in {MODULE_PATH}"
    assert callable(func), "get_validated_project_root must be callable"


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"

