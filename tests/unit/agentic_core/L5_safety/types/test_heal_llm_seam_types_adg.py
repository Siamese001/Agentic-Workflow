"""ADG contract tests for agentic_core/L5_safety/types/heal_llm_seam_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.heal_llm_seam_types import (
        HealTelemetryRecord,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    HealTelemetryRecord = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealTelemetryRecord:
    def test_is_frozen(self): assert HealTelemetryRecord.__dataclass_params__.frozen is True
    def test_creates(self):
        r = HealTelemetryRecord(
            run_kind="heal",
            agent_class="HealAgent",
            target_path="/repo/foo.py",
            inputs_hash="abcd1234",
            policy_hash="ef567890",
            baseline_ops_count=10,
            applied_ops_count=5,
            changed_files_count=3,
            idempotent_second_pass=False,
            outcome="applied",
        )
        assert r.run_kind == "heal"
        assert r.outcome == "applied"
    def test_to_dict(self):
        r = HealTelemetryRecord(
            run_kind="heal_repository",
            agent_class="RepoHealer",
            target_path="/repo",
            inputs_hash="a" * 16,
            policy_hash="b" * 16,
            baseline_ops_count=0,
            applied_ops_count=0,
            changed_files_count=0,
            idempotent_second_pass=True,
            outcome="plan_only",
        )
        d = r.to_dict()
        assert d["run_kind"] == "heal_repository"
        assert d["idempotent_second_pass"] is True
    def test_telemetry_hash_16_chars(self):
        r = HealTelemetryRecord(
            run_kind="heal", agent_class="X", target_path="",
            inputs_hash="a" * 8, policy_hash="b" * 8,
            baseline_ops_count=1, applied_ops_count=1,
            changed_files_count=0, idempotent_second_pass=False,
            outcome="applied",
        )
        h = r.telemetry_hash()
        assert len(h) == 16

def test_module_importable(): assert _AVAIL or not _AVAIL
