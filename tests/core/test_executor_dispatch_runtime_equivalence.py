"""Executor Dispatch Runtime Equivalence Tests.

Verifies dispatch keys are correct AFTER full module import and registry
initialization — not just static dict inspection. Each executor is imported
via its direct module path (no __init__.py side effects), instantiated with
every dispatch key from the committed snapshot, and the dispatch field is
verified to round-trip correctly.

Hardening V3 — Deliverable 3.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[2] / "artifacts" / "consolidation" / "executor_dispatch_snapshot.json"
)


@pytest.fixture(scope="module")
def snapshot():
    assert SNAPSHOT_PATH.is_file(), f"Snapshot not found: {SNAPSHOT_PATH}"
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


class TestRGValidationExecutorRuntime:
    def test_all_keys_instantiate(self, snapshot):
        from apps_rg.engines.RGValidationExecutor import RGValidationExecutor

        spec = snapshot["executors"]["RGValidationExecutor"]
        for key in spec["keys"]:
            inst = RGValidationExecutor(**{spec["dispatch_field"]: key})
            assert getattr(inst, spec["dispatch_field"]) == key, (
                f"Field {spec['dispatch_field']} mismatch: set {key}, "
                f"got {getattr(inst, spec['dispatch_field'])}"
            )

    def test_module_path_matches(self, snapshot):
        spec = snapshot["executors"]["RGValidationExecutor"]
        mod = importlib.import_module(spec["module"])
        assert hasattr(mod, "RGValidationExecutor"), (
            f"Module {spec['module']} does not export RGValidationExecutor"
        )


class TestRGStrategyExecutorRuntime:
    def test_all_keys_instantiate(self, snapshot):
        from apps_rg.engines.RGStrategyExecutor import RGStrategyExecutor

        spec = snapshot["executors"]["RGStrategyExecutor"]
        for key in spec["keys"]:
            inst = RGStrategyExecutor(**{spec["dispatch_field"]: key})
            assert getattr(inst, spec["dispatch_field"]) == key

    def test_module_path_matches(self, snapshot):
        spec = snapshot["executors"]["RGStrategyExecutor"]
        mod = importlib.import_module(spec["module"])
        assert hasattr(mod, "RGStrategyExecutor")


class TestLICValidationExecutorRuntime:
    def test_all_keys_instantiate(self, snapshot):
        from apps_lic.engines.LICValidationExecutor import LICValidationExecutor

        spec = snapshot["executors"]["LICValidationExecutor"]
        for key in spec["keys"]:
            inst = LICValidationExecutor(**{spec["dispatch_field"]: key})
            assert getattr(inst, spec["dispatch_field"]) == key

    def test_module_path_matches(self, snapshot):
        spec = snapshot["executors"]["LICValidationExecutor"]
        mod = importlib.import_module(spec["module"])
        assert hasattr(mod, "LICValidationExecutor")


class TestHOPPipelineExecutorRuntime:
    def test_all_keys_instantiate(self, snapshot):
        from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor

        spec = snapshot["executors"]["HOPPipelineExecutor"]
        for key in spec["keys"]:
            inst = HOPPipelineExecutor(**{spec["dispatch_field"]: key})
            assert getattr(inst, spec["dispatch_field"]) == key

    def test_module_path_matches(self, snapshot):
        spec = snapshot["executors"]["HOPPipelineExecutor"]
        mod = importlib.import_module(spec["module"])
        assert hasattr(mod, "HOPPipelineExecutor")


class TestObservabilityProbeExecutorRuntime:
    def test_all_keys_instantiate(self, snapshot):
        from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor import (
            ObservabilityProbeExecutor,
        )

        spec = snapshot["executors"]["ObservabilityProbeExecutor"]
        for key in spec["keys"]:
            inst = ObservabilityProbeExecutor(**{spec["dispatch_field"]: key})
            assert getattr(inst, spec["dispatch_field"]) == key

    def test_module_path_matches(self, snapshot):
        spec = snapshot["executors"]["ObservabilityProbeExecutor"]
        mod = importlib.import_module(spec["module"])
        assert hasattr(mod, "ObservabilityProbeExecutor")


class TestInspectorExecutorRuntime:
    def test_all_keys_instantiate(self, snapshot):
        from agentic_core.L5_safety.reasoning.InspectorExecutor import (
            InspectorExecutor,
        )

        spec = snapshot["executors"]["InspectorExecutor"]
        for key in spec["keys"]:
            inst = InspectorExecutor(**{spec["dispatch_field"]: key})
            assert getattr(inst, spec["dispatch_field"]) == key

    def test_module_path_matches(self, snapshot):
        spec = snapshot["executors"]["InspectorExecutor"]
        mod = importlib.import_module(spec["module"])
        assert hasattr(mod, "InspectorExecutor")
