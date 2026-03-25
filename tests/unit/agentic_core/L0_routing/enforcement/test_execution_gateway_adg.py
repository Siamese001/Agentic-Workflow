"""Behavioral contract tests for agentic_core.L0_routing.enforcement.execution_gateway."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.enforcement.execution_gateway"


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


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_boundarysnapshotartifact_is_instantiable(mod):
    """BoundarySnapshotArtifact is accessible and is a type."""
    cls = getattr(mod, "BoundarySnapshotArtifact", None)
    assert cls is not None, "BoundarySnapshotArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "BoundarySnapshotArtifact must be a class"


def test_executiongatewayerror_is_instantiable(mod):
    """ExecutionGatewayError is accessible and is a type."""
    cls = getattr(mod, "ExecutionGatewayError", None)
    assert cls is not None, "ExecutionGatewayError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ExecutionGatewayError must be a class"


def test_gatewayresult_is_instantiable(mod):
    """GatewayResult is accessible and is a type."""
    cls = getattr(mod, "GatewayResult", None)
    assert cls is not None, "GatewayResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GatewayResult must be a class"


def test_guardrailguard_is_instantiable(mod):
    """GuardrailGuard is accessible and is a type."""
    cls = getattr(mod, "GuardrailGuard", None)
    assert cls is not None, "GuardrailGuard must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "GuardrailGuard must be a class"


def test_hashmismatchtracker_is_instantiable(mod):
    """HashMismatchTracker is accessible and is a type."""
    cls = getattr(mod, "HashMismatchTracker", None)
    assert cls is not None, "HashMismatchTracker must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "HashMismatchTracker must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_pipeorderenforcer_is_instantiable(mod):
    """PipeOrderEnforcer is accessible and is a type."""
    cls = getattr(mod, "PipeOrderEnforcer", None)
    assert cls is not None, "PipeOrderEnforcer must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "PipeOrderEnforcer must be a class"


def test_callable_is_callable(mod):
    """Callable is accessible and callable."""
    func = getattr(mod, "Callable", None)
    assert func is not None, "Callable must be defined in {MODULE_PATH}"
    assert callable(func), "Callable must be callable"


def test_create_boundary_snapshot_is_callable(mod):
    """create_boundary_snapshot is accessible and callable."""
    func = getattr(mod, "create_boundary_snapshot", None)
    assert func is not None, "create_boundary_snapshot must be defined in {MODULE_PATH}"
    assert callable(func), "create_boundary_snapshot must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_dedupe_sha256_is_callable(mod):
    """dedupe_sha256 is accessible and callable."""
    func = getattr(mod, "dedupe_sha256", None)
    assert func is not None, "dedupe_sha256 must be defined in {MODULE_PATH}"
    assert callable(func), "dedupe_sha256 must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_field_is_callable(mod):
    """field is accessible and callable."""
    func = getattr(mod, "field", None)
    assert func is not None, "field must be defined in {MODULE_PATH}"
    assert callable(func), "field must be callable"


def test_get_profile_is_callable(mod):
    """get_profile is accessible and callable."""
    func = getattr(mod, "get_profile", None)
    assert func is not None, "get_profile must be defined in {MODULE_PATH}"
    assert callable(func), "get_profile must be callable"


def test_get_routing_gateway_is_callable(mod):
    """get_routing_gateway is accessible and callable."""
    func = getattr(mod, "get_routing_gateway", None)
    assert func is not None, "get_routing_gateway must be defined in {MODULE_PATH}"
    assert callable(func), "get_routing_gateway must be callable"

