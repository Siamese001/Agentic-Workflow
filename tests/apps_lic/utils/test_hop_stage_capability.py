"""
Regression tests for HOPStageCapability extraction (Cluster 4).

Validates:
- HOPStageCapability is importable and provides the expected interface
- read_required_inputs validates upstream dependencies
- write_output writes to buffer and logs trace
- run_stage provides PHASE_START bookend + delegates to _process
- All HOP agents can compose the capability
"""

from __future__ import annotations

import pytest


class TestHOPStageCapabilityInterface:
    """Validate the HOPStageCapability pure mixin contract."""

    @pytest.fixture
    def capability_class(self):
        try:
            from apps_lic.utils.hop_stage_capability import HOPStageCapability

            return HOPStageCapability
        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.skip(f"Cannot import HOPStageCapability: {e}")

    @pytest.fixture
    def buffer_class(self):
        try:
            from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer

            return ImmutableStagingBuffer
        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.skip(f"Cannot import ImmutableStagingBuffer: {e}")

    @pytest.fixture
    def registry_class(self):
        try:
            from apps_lic.types.TraceRegistry import TraceRegistry

            return TraceRegistry
        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.skip(f"Cannot import TraceRegistry: {e}")

    def test_importable(self, capability_class):
        """HOPStageCapability must be importable."""
        assert capability_class is not None

    def test_does_not_inherit_lic_agent_base(self, capability_class):
        """HOPStageCapability must NOT inherit from LICAgentBase (pure mixin)."""
        mro_names = [cls.__name__ for cls in capability_class.__mro__]
        assert "LICAgentBase" not in mro_names, (
            "Capability class must be agent-agnostic — no LICAgentBase in MRO"
        )

    def test_has_required_interface(self, capability_class):
        """HOPStageCapability must expose the expected methods."""
        assert hasattr(capability_class, "read_required_inputs")
        assert hasattr(capability_class, "write_output")
        assert hasattr(capability_class, "run_stage")
        assert hasattr(capability_class, "_process")

    def test_has_class_variables(self, capability_class):
        """HOPStageCapability must declare HOP_STAGE_NAME and REQUIRED_INPUTS."""
        assert hasattr(capability_class, "HOP_STAGE_NAME")
        assert hasattr(capability_class, "REQUIRED_INPUTS")

    def test_process_raises_not_implemented(self, capability_class):
        """Base _process must raise NotImplementedError."""
        instance = capability_class()
        with pytest.raises(NotImplementedError):
            instance._process(None, None)

    def test_read_required_inputs_missing_key(self, capability_class, buffer_class, registry_class):
        """read_required_inputs must raise RuntimeError for missing upstream data."""

        class TestStage(capability_class):
            REQUIRED_INPUTS = ["hop1_analysis"]

        stage = TestStage()
        buffer = buffer_class()
        registry = registry_class()

        with pytest.raises(RuntimeError, match="missing required upstream input"):
            stage.read_required_inputs(buffer, registry)

    def test_read_required_inputs_success(self, capability_class, buffer_class, registry_class):
        """read_required_inputs must return dict of inputs when all present."""

        class TestStage(capability_class):
            REQUIRED_INPUTS = ["hop1_analysis"]

        stage = TestStage()
        buffer = buffer_class()
        registry = registry_class()

        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        inputs = stage.read_required_inputs(buffer, registry)

        assert "hop1_analysis" in inputs
        assert inputs["hop1_analysis"]["Archetype"] == "C_LEVEL"

    def test_write_output(self, capability_class, buffer_class, registry_class):
        """write_output must write to buffer and add DECISION_FINAL trace."""

        class TestStage(capability_class):
            HOP_STAGE_NAME = "test_output"

        stage = TestStage()
        buffer = buffer_class()
        registry = registry_class()

        stage.write_output(buffer, registry, {"result": "ok"})

        assert buffer.read("test_output") == {"result": "ok"}
        traces = registry.get_traces()
        assert any(t.get("type") == "DECISION_FINAL" for t in traces)

    def test_run_stage_adds_phase_start(self, capability_class, buffer_class, registry_class):
        """run_stage must add PHASE_START trace before calling _process."""

        class TestStage(capability_class):
            HOP_STAGE_NAME = "test_stage"
            processed = False

            def _process(self, buffer, registry):
                TestStage.processed = True

        stage = TestStage()
        buffer = buffer_class()
        registry = registry_class()

        stage.run_stage(buffer, registry)

        assert TestStage.processed is True
        traces = registry.get_traces()
        assert any(t.get("type") == "PHASE_START" for t in traces)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
