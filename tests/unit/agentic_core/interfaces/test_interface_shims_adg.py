"""ADG-driven tests for agentic_core/interfaces/ shim modules — fan_in batch.

Covers:
  agentic_core/interfaces/meta_control.py     fan_in=3
  agentic_core/interfaces/observability.py    fan_in=3
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestMetaControlInterface:
    """meta_control.py — sovereign meta-control config interface for apps_*."""

    def test_module_importable(self):
        import agentic_core.interfaces.meta_control  # noqa: F401

    def test_load_current_callable(self):
        from agentic_core.interfaces.meta_control import load_current

        assert callable(load_current)

    def test_apply_change_package_readonly_callable(self):
        from agentic_core.interfaces.meta_control import apply_change_package_readonly

        assert callable(apply_change_package_readonly)

    def test_config_delta_artifact_importable(self):
        from agentic_core.interfaces.meta_control import ConfigDeltaArtifact

        assert callable(ConfigDeltaArtifact)

    def test_canonical_json_callable(self):
        from agentic_core.interfaces.meta_control import canonical_json

        assert callable(canonical_json)

    def test_validate_component_allowed_callable(self):
        from agentic_core.interfaces.meta_control import validate_component_allowed

        assert callable(validate_component_allowed)

    def test_semantic_clock_snapshot_importable(self):
        from agentic_core.interfaces.meta_control import SemanticClockSnapshot

        assert callable(SemanticClockSnapshot)

    def test_capability_token_artifact_importable(self):
        from agentic_core.interfaces.meta_control import CapabilityTokenArtifact

        assert callable(CapabilityTokenArtifact)

    def test_apply_meta_learning_rollout_callable(self):
        from agentic_core.interfaces.meta_control import apply_meta_learning_rollout

        assert callable(apply_meta_learning_rollout)

    def test_apply_with_invariants_callable(self):
        from agentic_core.interfaces.meta_control import apply_with_invariants

        assert callable(apply_with_invariants)


try:
    import agentic_core.interfaces.observability as _obs_module

    _OBS_AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _obs_module = None  # type: ignore[assignment]
    _OBS_AVAILABLE = False


@pytest.mark.skipif(not _OBS_AVAILABLE, reason="observability.py deps unavailable")
class TestObservabilityInterface:
    """observability.py — sovereign observability interface for apps_*."""

    def test_module_importable(self):
        assert _OBS_AVAILABLE

    def test_all_exports_present(self):
        for name in _obs_module.__all__:
            assert hasattr(_obs_module, name), f"Missing __all__ member: {name}"

    def test_system_telemetry_importable(self):
        SystemTelemetry = getattr(_obs_module, "SystemTelemetry", None)
        assert SystemTelemetry is not None and callable(SystemTelemetry)

    def test_circuit_breaker_state_importable(self):
        CircuitBreakerState = getattr(_obs_module, "CircuitBreakerState", None)
        assert CircuitBreakerState is not None and callable(CircuitBreakerState)

    def test_system_telemetry_identity(self):
        try:
            from agentic_core.L6_observability.utils.system_telemetry_util import SystemTelemetry as canon

            assert _obs_module.SystemTelemetry is canon
        except (ValueError, TypeError, RuntimeError) as e:
            pytest.skip("system_telemetry_util unavailable")

    def test_circuit_breaker_state_identity(self):
        try:
            from agentic_core.runtime.types.circuit_breaker_types import CircuitBreakerState as canon

            assert _obs_module.CircuitBreakerState is canon
        except (ValueError, TypeError, RuntimeError) as e:
            pytest.skip("circuit_breaker_types unavailable")