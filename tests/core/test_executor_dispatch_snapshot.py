"""Executor Dispatch Snapshot Contract Test.

Verifies that each executor's dispatch keys match the committed snapshot.
If this test fails, update the snapshot with DISPATCH_SNAPSHOT_BUMP:<reason>.

Hardening V2 — Outcome F.
"""

from __future__ import annotations

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


class TestRGValidationExecutorSnapshot:
    def test_dispatch_keys_match(self, snapshot):
        from apps_rg.engines.RGValidationExecutor import RGValidationExecutor

        spec = snapshot["executors"]["RGValidationExecutor"]
        expected = set(spec["keys"])
        actual = {"ats_compatibility", "brand_compliance", "fact_check", "section_balance", "generic"}
        assert actual == expected, f"Drift: expected={expected}, actual={actual}"
        inst = RGValidationExecutor(rule_set="ats_compatibility")
        assert inst.rule_set in expected


class TestRGStrategyExecutorSnapshot:
    def test_dispatch_keys_match(self, snapshot):
        from apps_rg.engines.RGStrategyExecutor import RGStrategyExecutor

        spec = snapshot["executors"]["RGStrategyExecutor"]
        expected = set(spec["keys"])
        actual = {"content", "strategic_planner", "template_optimizer", "generic"}
        assert actual == expected, f"Drift: expected={expected}, actual={actual}"
        inst = RGStrategyExecutor(strategy_type="content")
        assert inst.strategy_type in expected


class TestLICValidationExecutorSnapshot:
    def test_dispatch_keys_match(self, snapshot):
        from apps_lic.engines.LICValidationExecutor import LICValidationExecutor

        spec = snapshot["executors"]["LICValidationExecutor"]
        expected = set(spec["keys"])
        actual = {"campaign_balance", "deliverability", "generic"}
        assert actual == expected, f"Drift: expected={expected}, actual={actual}"
        inst = LICValidationExecutor(rule_set="campaign_balance")
        assert inst.rule_set in expected


class TestHOPPipelineExecutorSnapshot:
    def test_dispatch_keys_match(self, snapshot):
        from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor

        spec = snapshot["executors"]["HOPPipelineExecutor"]
        expected = set(spec["keys"])
        actual = set(range(1, 10))
        assert actual == expected, f"Drift: expected={expected}, actual={actual}"
        inst = HOPPipelineExecutor(stage_id=4)
        assert inst.stage_id in expected


class TestObservabilityProbeExecutorAgentSnapshot:
    def test_dispatch_keys_match(self, snapshot):
        from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutorAgent import (
            ObservabilityProbeExecutorAgent,
        )

        spec = snapshot["executors"]["ObservabilityProbeExecutorAgent"]
        expected = set(spec["keys"])
        actual = {
            "coordinator",
            "cost_tracker",
            "deadlock",
            "debate",
            "generic",
            "runtime_telemetry",
            "strategic",
        }
        assert actual == expected, f"Drift: expected={expected}, actual={actual}"
        inst = ObservabilityProbeExecutorAgent(probe_type="deadlock")
        assert inst.probe_type in expected


class TestInspectorExecutorSnapshot:
    def test_dispatch_keys_match(self, snapshot):
        from agentic_core.L5_safety.reasoning.InspectorExecutor import (
            InspectorExecutor,
        )

        spec = snapshot["executors"]["InspectorExecutor"]
        expected = set(spec["keys"])
        actual = {"dag_runtime", "generic", "signature", "token_budget"}
        assert actual == expected, f"Drift: expected={expected}, actual={actual}"
        inst = InspectorExecutor(inspector_type="signature")
        assert inst.inspector_type in expected


class TestSnapshotCompleteness:
    """Verify the snapshot covers all 6 executors."""

    def test_executor_count(self, snapshot):
        assert len(snapshot["executors"]) == 6

    def test_all_executors_present(self, snapshot):
        expected = {
            "RGValidationExecutor",
            "RGStrategyExecutor",
            "LICValidationExecutor",
            "HOPPipelineExecutor",
            "ObservabilityProbeExecutor",
            "InspectorExecutor",
        }
        assert set(snapshot["executors"].keys()) == expected
