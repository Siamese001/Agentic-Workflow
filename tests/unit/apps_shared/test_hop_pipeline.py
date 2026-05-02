"""Unit tests for apps_shared.orchestration.hop_pipeline.

Covers the three public types of the Wave 1 shared substrate:

- ``HopStageSpec``      — snake_case validation, frozen semantics
- ``HopRegistry``       — dup-ID rejection, ordering, circular-skip rejection
- ``HopPipelineExecutor`` — happy path, skip, gate, fail-required,
  fail-optional, replay_stage, seal_step integration

Engine plugins under test live in this module as lightweight classes;
the lazy importer resolves them via ``engine_module=__name__``.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRegistry,
    HopRegistryValidationError,
    HopRunRecord,
    HopStageSpec,
    StageStatus,
)
from apps_shared.orchestration import hop_pipeline as _hp


# =============================================================================
# Engine fixtures — resolved via engine_module=__name__
# =============================================================================


class _EchoEngine:
    """Emits a deterministic output keyed by its class name."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return {"echo": context.get("seed", 0) + 1, "last": "echo"}


class _DoubleEngine:
    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return {"doubled": context.get("echo", 0) * 2, "last": "double"}


class _GateEngine:
    """Returns ``passed`` from the context so tests can drive the gate."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return {"passed": context.get("force_pass", True), "last": "gate"}


class _RaisingEngine:
    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("boom")


class _FinalEngine:
    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return {"final": True, "last": "final"}


@pytest.fixture(autouse=True)
def _clear_engine_cache() -> None:
    """Keep the module-level engine cache from leaking across tests."""
    _hp._ENGINE_CACHE.clear()
    yield
    _hp._ENGINE_CACHE.clear()


def _spec(stage_id: int, name: str, cls_name: str, **kwargs: Any) -> HopStageSpec:
    """Build a spec whose engine resolves to a class in this test module."""
    return HopStageSpec(
        stage_id=stage_id,
        stage_name=name,
        engine_module=__name__,
        engine_class=cls_name,
        **kwargs,
    )


# =============================================================================
# HopStageSpec
# =============================================================================


class TestHopStageSpec:
    def test_minimal_spec_builds(self) -> None:
        spec = HopStageSpec(
            stage_id=1, stage_name="foo", engine_module="m", engine_class="E"
        )
        assert spec.stage_id == 1
        assert spec.required is True
        assert spec.gate is False
        assert spec.optional_skip_if is None

    def test_uppercase_stage_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            HopStageSpec(
                stage_id=1, stage_name="Foo", engine_module="m", engine_class="E"
            )

    def test_dash_stage_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            HopStageSpec(
                stage_id=1, stage_name="foo-bar", engine_module="m", engine_class="E"
            )

    def test_spec_is_frozen(self) -> None:
        spec = HopStageSpec(
            stage_id=1, stage_name="foo", engine_module="m", engine_class="E"
        )
        with pytest.raises(ValidationError):
            spec.stage_id = 2  # type: ignore[misc]

    def test_negative_stage_id_rejected(self) -> None:
        with pytest.raises(ValidationError):
            HopStageSpec(
                stage_id=-1, stage_name="foo", engine_module="m", engine_class="E"
            )


# =============================================================================
# HopRegistry
# =============================================================================


class TestHopRegistry:
    def test_register_single(self) -> None:
        reg = HopRegistry("demo")
        reg.register(_spec(1, "first", "_EchoEngine"))
        assert reg.stage_count() == 1
        assert reg.get(1).stage_name == "first"

    def test_duplicate_stage_id_rejected_via_register(self) -> None:
        reg = HopRegistry("demo")
        reg.register(_spec(1, "first", "_EchoEngine"))
        with pytest.raises(HopRegistryValidationError, match="duplicate stage_id"):
            reg.register(_spec(1, "other", "_DoubleEngine"))

    def test_duplicate_stage_id_rejected_via_register_all(self) -> None:
        reg = HopRegistry("demo")
        with pytest.raises(HopRegistryValidationError, match="duplicate stage_id"):
            reg.register_all(
                [
                    _spec(1, "first", "_EchoEngine"),
                    _spec(1, "second", "_DoubleEngine"),
                ]
            )

    def test_ordered_by_stage_id_ascending(self) -> None:
        reg = HopRegistry("demo")
        reg.register_all(
            [
                _spec(3, "third", "_FinalEngine"),
                _spec(1, "first", "_EchoEngine"),
                _spec(2, "second", "_DoubleEngine"),
            ]
        )
        ids = [s.stage_id for s in reg.ordered()]
        assert ids == [1, 2, 3]

    def test_empty_registry_fails_validate(self) -> None:
        reg = HopRegistry("demo")
        with pytest.raises(HopRegistryValidationError, match="empty"):
            reg.validate()

    def test_circular_skip_ref_rejected(self) -> None:
        reg = HopRegistry("demo")
        spec = _spec(
            1,
            "self_ref",
            "_EchoEngine",
            outputs=("flag",),
            optional_skip_if="flag",
        )
        with pytest.raises(HopRegistryValidationError, match="circular skip ref"):
            reg.register(spec)

    def test_get_missing_returns_none(self) -> None:
        reg = HopRegistry("demo")
        assert reg.get(999) is None

    def test_app_name_exposed(self) -> None:
        reg = HopRegistry("apps_lic")
        assert reg.app_name == "apps_lic"


# =============================================================================
# HopPipelineExecutor — happy / skip / gate / fail
# =============================================================================


class TestHopPipelineExecutorHappyPath:
    def test_three_stage_walk(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(1, "echo", "_EchoEngine"),
                _spec(2, "double", "_DoubleEngine"),
                _spec(3, "final", "_FinalEngine"),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={"seed": 10})

        assert isinstance(record, HopRunRecord)
        assert record.success is True
        assert record.terminal_error == ""
        assert [cp.stage_id for cp in record.checkpoints] == [1, 2, 3]
        assert all(cp.status is StageStatus.COMPLETED for cp in record.checkpoints)
        # echo=11, doubled=22
        assert record.final_context["echo"] == 11
        assert record.final_context["doubled"] == 22
        assert record.final_context["final"] is True

    def test_run_id_propagates(self) -> None:
        reg = HopRegistry("demo").register_all(
            [_spec(1, "echo", "_EchoEngine")]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={}, run_id="abc123")
        assert record.run_id == "abc123"

    def test_run_id_auto_generated_when_missing(self) -> None:
        reg = HopRegistry("demo").register_all(
            [_spec(1, "echo", "_EchoEngine")]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={})
        assert len(record.run_id) == 16  # uuid4().hex[:16]


class TestHopPipelineExecutorSkip:
    def test_skip_when_flag_truthy(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(
                    1,
                    "maybe_echo",
                    "_EchoEngine",
                    optional_skip_if="skip_stage_1",
                ),
                _spec(2, "final", "_FinalEngine"),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={"skip_stage_1": True})

        assert record.checkpoints[0].status is StageStatus.SKIPPED
        assert record.checkpoints[0].duration_ms == 0
        assert record.checkpoints[1].status is StageStatus.COMPLETED
        assert record.success is True

    def test_no_skip_when_flag_absent(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(
                    1,
                    "maybe_echo",
                    "_EchoEngine",
                    optional_skip_if="skip_stage_1",
                ),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={})
        assert record.checkpoints[0].status is StageStatus.COMPLETED


class TestHopPipelineExecutorGate:
    def test_gate_halts_on_failure(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(1, "gate", "_GateEngine", gate=True),
                _spec(2, "final", "_FinalEngine"),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={"force_pass": False})

        assert record.checkpoints[0].status is StageStatus.GATED
        assert len(record.checkpoints) == 1  # halted before stage 2
        assert "gated run halt" in record.terminal_error
        assert record.success is False

    def test_gate_passes_when_passed_true(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(1, "gate", "_GateEngine", gate=True),
                _spec(2, "final", "_FinalEngine"),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={"force_pass": True})

        assert record.checkpoints[0].status is StageStatus.COMPLETED
        assert record.checkpoints[1].status is StageStatus.COMPLETED
        assert record.success is True


class TestHopPipelineExecutorFailure:
    def test_required_failure_halts(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(1, "echo", "_EchoEngine"),
                _spec(2, "boom", "_RaisingEngine"),
                _spec(3, "final", "_FinalEngine"),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={"seed": 0})

        statuses = [cp.status for cp in record.checkpoints]
        assert statuses == [StageStatus.COMPLETED, StageStatus.FAILED]
        assert "RuntimeError" in record.checkpoints[1].error
        assert "stage 2" in record.terminal_error
        assert record.success is False

    def test_optional_failure_continues(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(1, "echo", "_EchoEngine"),
                _spec(2, "boom", "_RaisingEngine", required=False),
                _spec(3, "final", "_FinalEngine"),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={"seed": 0})

        statuses = [cp.status for cp in record.checkpoints]
        assert statuses == [
            StageStatus.COMPLETED,
            StageStatus.FAILED,
            StageStatus.COMPLETED,
        ]
        # Not-required stage failed but final_context carries stage-3 output.
        assert record.final_context["final"] is True
        # terminal_error remains empty since no required stage halted.
        assert record.terminal_error == ""
        # success is still False because one checkpoint is FAILED.
        assert record.success is False

    def test_missing_engine_module_raises_in_load(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                HopStageSpec(
                    stage_id=1,
                    stage_name="bogus",
                    engine_module="nonexistent.module.xxxx",
                    engine_class="Nope",
                ),
            ]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={})

        assert record.checkpoints[0].status is StageStatus.FAILED
        assert "engine load failed" in record.checkpoints[0].error

    def test_missing_engine_class_fails(self) -> None:
        reg = HopRegistry("demo").register_all(
            [_spec(1, "ghost", "_NotARealClass")]
        )
        ex = HopPipelineExecutor(registry=reg)
        record = ex.run(context={})

        assert record.checkpoints[0].status is StageStatus.FAILED
        assert "engine load failed" in record.checkpoints[0].error


# =============================================================================
# Replay
# =============================================================================


class TestHopPipelineExecutorReplay:
    def test_replay_stage_happy_path(self) -> None:
        reg = HopRegistry("demo").register_all(
            [_spec(1, "echo", "_EchoEngine")]
        )
        ex = HopPipelineExecutor(registry=reg)
        cp = ex.replay_stage(1, {"seed": 5})
        assert isinstance(cp, Checkpoint)
        assert cp.status is StageStatus.COMPLETED
        assert cp.output["echo"] == 6

    def test_replay_missing_stage(self) -> None:
        reg = HopRegistry("demo").register_all(
            [_spec(1, "echo", "_EchoEngine")]
        )
        ex = HopPipelineExecutor(registry=reg)
        cp = ex.replay_stage(999, {})
        assert cp.status is StageStatus.FAILED
        assert "not found in registry" in cp.error


# =============================================================================
# seal_step integration
# =============================================================================


class TestSealStepIntegration:
    def test_seal_step_invoked_per_stage(self) -> None:
        reg = HopRegistry("demo").register_all(
            [
                _spec(1, "echo", "_EchoEngine"),
                _spec(2, "double", "_DoubleEngine"),
            ]
        )

        # Minimal fake seal-step context manager that records calls.
        calls: list[tuple[str, str, str]] = []

        class _FakeCM:
            def __init__(self, step_id: str, trace_id: str, component: str) -> None:
                self.step_id = step_id
                self.trace_id = trace_id
                self.component = component
                self.bag: dict[str, Any] = {}

            def __enter__(self) -> dict[str, Any]:
                calls.append((self.step_id, self.trace_id, self.component))
                return self.bag

            def __exit__(self, *exc: Any) -> None:
                return None

        def _factory() -> Any:
            return _FakeCM

        ex = HopPipelineExecutor(registry=reg, seal_step_provider=_factory)
        record = ex.run(context={"seed": 1}, trace_id="trace-123")

        assert record.success is True
        assert len(calls) == 2
        step_ids = [c[0] for c in calls]
        assert step_ids == ["hop_stage_1_echo", "hop_stage_2_double"]
        trace_ids = {c[1] for c in calls}
        assert trace_ids == {"trace-123"}
        components = {c[2] for c in calls}
        assert components == {"demo.HopPipelineExecutor"}
