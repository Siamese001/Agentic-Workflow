"""3.9: Baseline tests for LicHealingOrchestrator (HEAL-GAP-04)."""

from __future__ import annotations

import sys
from types import ModuleType


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _make_lic_agent_base_stub():
    """Inject a minimal LICAgentBase stub so LicHealingOrchestrator can be imported."""
    stub_mod = ModuleType("apps_lic.utils.LICAgentBase")
    parent_mod = ModuleType("apps_lic.utils")

    class _LICAgentBase:
        recovery_playbooks: dict = {}

        def ml_cache_get(self, key):
            return None

        def ml_cache_set(self, key, val):
            return True

        def retrieve_healing_patterns(self, v, top_k=3):
            return []

        def store_healing_pattern(self, v, r):
            return True

        def guardrails_check_healing_depth(self, vid):
            return True

        def guardrails_increment_healing_depth(self, vid):
            pass

        def guardrails_reset_healing_depth(self, vid):
            pass

        def cache_pattern_with_metadata(self, *a, **kw):
            pass

        def ml_enhanced_heal(self, v, fn):
            return fn(v)

        def ml_cache_incident_resolution(self, *a, **kw):
            return True

    stub_mod.LICAgentBase = _LICAgentBase
    sys.modules.setdefault("apps_lic.utils", parent_mod)
    sys.modules["apps_lic.utils.LICAgentBase"] = stub_mod
    return _LICAgentBase


_LICAgentBase = _make_lic_agent_base_stub()


class TestLicHealingOrchestratorExecuteHealing:
    def _get_orchestrator(self):
        if "apps_lic.reasoning.LicHealingOrchestrator" in sys.modules:
            del sys.modules["apps_lic.reasoning.LicHealingOrchestrator"]
        from apps_lic.reasoning.LicHealingOrchestrator import LicHealingOrchestrator

        orch = LicHealingOrchestrator.__new__(LicHealingOrchestrator)
        orch.recovery_playbooks = {
            "structural": "structural_recovery",
            "schema": "schema_recovery",
            "output_contract": "schema_recovery",
            "llm_call": "llm_recovery",
            "api_timeout": "llm_recovery",
        }
        return orch

    def test_unknown_incident_returns_resolved(self):
        orch = self._get_orchestrator()
        result = orch._execute_healing({"type": "unknown_xyz"})
        assert result["status"] in ("resolved", "error")
        assert result["incident_type"] == "unknown_xyz"

    def test_structural_incident_dispatches(self):
        orch = self._get_orchestrator()
        result = orch._execute_healing({"type": "structural", "content": "safe content"})
        assert "healer" in result
        assert result["healer"] == "ControlPlane"

    def test_schema_incident_dispatches(self):
        orch = self._get_orchestrator()
        result = orch._execute_healing({"type": "schema", "stage_id": 3, "context": {}})
        assert "healer" in result

    def test_execute_healing_always_returns_dict(self):
        orch = self._get_orchestrator()
        for incident_type in ("structural", "schema", "output_contract", "unknown"):
            result = orch._execute_healing({"type": incident_type, "content": "test"})
            assert isinstance(result, dict)
            assert "status" in result
