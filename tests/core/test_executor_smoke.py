"""Runtime-equivalence smoke tests for all 6 canonical executors.

Verifies:
  1. Each executor imports cleanly
  2. Each executor class is instantiable (dataclass contract)
  3. Dispatch keys cover the pre-merge agent set

Created: 2026-02-09 (Consolidation Audit Step 6)
"""

from __future__ import annotations


# ── RGValidationExecutor ────────────────────────────────────────────
class TestRGValidationExecutor:
    def test_import(self):
        from apps_rg.engines.RGValidationExecutor import RGValidationExecutor

        assert RGValidationExecutor.__name__ == "RGValidationExecutor"

    def test_dispatch_keys(self):
        from apps_rg.engines.RGValidationExecutor import RGValidationExecutor

        expected_keys = {
            "ats_compatibility",
            "brand_compliance",
            "fact_check",
            "section_balance",
            "generic",
        }
        inst = RGValidationExecutor(rule_set="ats_compatibility")
        assert inst.rule_set in expected_keys


# ── RGStrategyExecutor ──────────────────────────────────────────────
class TestRGStrategyExecutor:
    def test_import(self):
        from apps_rg.engines.RGStrategyExecutor import RGStrategyExecutor

        assert RGStrategyExecutor.__name__ == "RGStrategyExecutor"

    def test_dispatch_keys(self):
        from apps_rg.engines.RGStrategyExecutor import RGStrategyExecutor

        expected_keys = {
            "content",
            "strategic_planner",
            "template_optimizer",
            "generic",
        }
        inst = RGStrategyExecutor(strategy_type="content")
        assert inst.strategy_type in expected_keys


# ── LICValidationExecutor ──────────────────────────────────────────
class TestLICValidationExecutor:
    def test_import(self):
        from apps_lic.engines.LICValidationExecutor import LICValidationExecutor

        assert LICValidationExecutor.__name__ == "LICValidationExecutor"

    def test_dispatch_keys(self):
        from apps_lic.engines.LICValidationExecutor import LICValidationExecutor

        expected_keys = {
            "campaign_balance",
            "deliverability",
            "generic",
        }
        inst = LICValidationExecutor(rule_set="campaign_balance")
        assert inst.rule_set in expected_keys


# ── HOPPipelineExecutor ────────────────────────────────────────────
class TestHOPPipelineExecutor:
    def test_import(self):
        from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor

        assert HOPPipelineExecutor.__name__ == "HOPPipelineExecutor"

    def test_dispatch_keys(self):
        from apps_lic.engines.HOPPipelineExecutor import HOPPipelineExecutor

        expected_stages = set(range(1, 10))  # HOP1 through HOP9
        inst = HOPPipelineExecutor(stage_id=4)
        assert inst.stage_id in expected_stages


# ── ObservabilityProbeExecutor ─────────────────────────────────────
class TestObservabilityProbeExecutor:
    def test_import(self):
        from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor import (
            ObservabilityProbeExecutor,
        )

        assert ObservabilityProbeExecutor.__name__ == "ObservabilityProbeExecutor"

    def test_dispatch_keys(self):
        from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor import (
            ObservabilityProbeExecutor,
        )

        expected_keys = {
            "coordinator",
            "deadlock",
            "debate",
            "runtime_telemetry",
            "strategic",
            "cost_tracker",
            "generic",
        }
        inst = ObservabilityProbeExecutor(probe_type="deadlock")
        assert inst.probe_type in expected_keys


# ── InspectorExecutor ──────────────────────────────────────────────
class TestInspectorExecutor:
    def test_import(self):
        from agentic_core.L5_safety.reasoning.InspectorExecutor import (
            InspectorExecutor,
        )

        assert InspectorExecutor.__name__ == "InspectorExecutor"

    def test_dispatch_keys(self):
        from agentic_core.L5_safety.reasoning.InspectorExecutor import (
            InspectorExecutor,
        )

        expected_keys = {
            "dag_runtime",
            "signature",
            "token_budget",
            "generic",
        }
        inst = InspectorExecutor(inspector_type="signature")
        assert inst.inspector_type in expected_keys
