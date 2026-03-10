"""
Phase 5 tests for heal telemetry and budget caps.

Tests deterministic telemetry emission and budget enforcement.
"""

import json
import os
from unittest import mock

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance


class TestHealTelemetrySchema:
    """Tests for HealTelemetryRecord schema and determinism."""

    def test_telemetry_record_schema(self):
        """HealTelemetryRecord has all required fields."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import HealTelemetryRecord

        record = HealTelemetryRecord(
            run_kind="heal_repository",
            agent_class="TestAgent",
            target_path="/path/to/repo",
            inputs_hash="abc123def456",
            policy_hash="xyz789uvw012",
            baseline_ops_count=10,
            applied_ops_count=5,
            changed_files_count=3,
            idempotent_second_pass=True,
            outcome="applied",
        )

        as_dict = record.to_dict()
        required_keys = {
            "run_kind",
            "agent_class",
            "target_path",
            "inputs_hash",
            "policy_hash",
            "baseline_ops_count",
            "applied_ops_count",
            "changed_files_count",
            "idempotent_second_pass",
            "outcome",
        }
        assert set(as_dict.keys()) == required_keys

    def test_telemetry_hash_deterministic(self):
        """Telemetry hash is deterministic for same inputs."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import HealTelemetryRecord

        record1 = HealTelemetryRecord(
            run_kind="heal",
            agent_class="TestAgent",
            target_path="",
            inputs_hash="abc123",
            policy_hash="xyz789",
            baseline_ops_count=0,
            applied_ops_count=0,
            changed_files_count=0,
            idempotent_second_pass=False,
            outcome="plan_only",
        )

        record2 = HealTelemetryRecord(
            run_kind="heal",
            agent_class="TestAgent",
            target_path="",
            inputs_hash="abc123",
            policy_hash="xyz789",
            baseline_ops_count=0,
            applied_ops_count=0,
            changed_files_count=0,
            idempotent_second_pass=False,
            outcome="plan_only",
        )

        assert record1.telemetry_hash() == record2.telemetry_hash()
        assert len(record1.telemetry_hash()) == 16

    def test_telemetry_json_serializable(self):
        """Telemetry record can be serialized to deterministic JSON."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import HealTelemetryRecord

        record = HealTelemetryRecord(
            run_kind="heal_repository",
            agent_class="TestAgent",
            target_path="/repo",
            inputs_hash="hash1",
            policy_hash="hash2",
            baseline_ops_count=5,
            applied_ops_count=3,
            changed_files_count=2,
            idempotent_second_pass=True,
            outcome="applied",
        )

        json1 = json.dumps(record.to_dict(), sort_keys=True)
        json2 = json.dumps(record.to_dict(), sort_keys=True)
        assert json1 == json2


class TestTelemetryEmission:
    """Tests for deterministic telemetry artifact emission."""

    def test_emit_creates_artifact(self, tmp_path):
        """emit_heal_telemetry creates artifact file."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealTelemetryRecord,
            emit_heal_telemetry,
        )

        record = HealTelemetryRecord(
            run_kind="heal",
            agent_class="TestAgent",
            target_path="",
            inputs_hash="test_hash_001",
            policy_hash="policy_001",
            baseline_ops_count=0,
            applied_ops_count=0,
            changed_files_count=0,
            idempotent_second_pass=False,
            outcome="plan_only",
        )

        filepath = emit_heal_telemetry(record, artifacts_root=tmp_path)

        assert filepath.exists()
        assert filepath.name == "test_hash_001.json"

        # Verify content
        content = json.loads(filepath.read_text())
        assert content["agent_class"] == "TestAgent"
        assert content["outcome"] == "plan_only"

    def test_emit_idempotent_same_content(self, tmp_path):
        """emit_heal_telemetry is idempotent for same content."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealTelemetryRecord,
            emit_heal_telemetry,
        )

        record = HealTelemetryRecord(
            run_kind="heal_repository",
            agent_class="IdempotentAgent",
            target_path="/repo",
            inputs_hash="idem_hash_001",
            policy_hash="policy_001",
            baseline_ops_count=5,
            applied_ops_count=5,
            changed_files_count=0,
            idempotent_second_pass=True,
            outcome="applied",
        )

        filepath1 = emit_heal_telemetry(record, artifacts_root=tmp_path)
        filepath2 = emit_heal_telemetry(record, artifacts_root=tmp_path)

        assert filepath1 == filepath2
        assert filepath1.exists()

    def test_emit_fails_on_conflict(self, tmp_path):
        """emit_heal_telemetry fails if file exists with different content."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealTelemetryRecord,
            emit_heal_telemetry,
        )

        # Create first record
        record1 = HealTelemetryRecord(
            run_kind="heal",
            agent_class="Agent1",
            target_path="",
            inputs_hash="conflict_hash",
            policy_hash="policy_001",
            baseline_ops_count=0,
            applied_ops_count=0,
            changed_files_count=0,
            idempotent_second_pass=False,
            outcome="plan_only",
        )

        emit_heal_telemetry(record1, artifacts_root=tmp_path)

        # Create second record with same inputs_hash but different content
        record2 = HealTelemetryRecord(
            run_kind="heal",
            agent_class="Agent2",  # Different!
            target_path="",
            inputs_hash="conflict_hash",  # Same hash
            policy_hash="policy_001",
            baseline_ops_count=0,
            applied_ops_count=0,
            changed_files_count=0,
            idempotent_second_pass=False,
            outcome="plan_only",
        )

        with pytest.raises(ValueError, match="Telemetry artifact conflict"):
            emit_heal_telemetry(record2, artifacts_root=tmp_path)


class TestHealBudgetCaps:
    """Tests for heal budget caps enforcement."""

    def test_budget_caps_from_env_defaults(self):
        """HealBudgetCaps loads defaults correctly."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import HealBudgetCaps

        # Clear env vars for test
        with mock.patch.dict(os.environ, {}, clear=True):
            caps_no_llm = HealBudgetCaps.from_env(enable_llm=False)
            caps_with_llm = HealBudgetCaps.from_env(enable_llm=True)

        assert caps_no_llm.max_escalations_per_run == 1
        assert caps_no_llm.max_high_tier_per_run == 0  # 0 when enable_llm=False

        assert caps_with_llm.max_escalations_per_run == 1
        assert caps_with_llm.max_high_tier_per_run == 1  # 1 when enable_llm=True

    def test_budget_caps_from_env_custom(self):
        """HealBudgetCaps respects env var overrides."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import HealBudgetCaps

        env = {
            "HEAL_MAX_ESCALATIONS_PER_RUN": "3",
            "HEAL_MAX_HIGH_TIER_PER_RUN": "2",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            caps = HealBudgetCaps.from_env(enable_llm=True)

        assert caps.max_escalations_per_run == 3
        assert caps.max_high_tier_per_run == 2

    def test_escalation_budget_enforcement(self):
        """Second escalation in one run fails closed."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealBudgetCaps,
            HealBudgetExceededError,
            increment_escalation_count,
            reset_heal_budget_counters,
            set_heal_budget_caps,
        )

        caps = HealBudgetCaps(max_escalations_per_run=1, max_high_tier_per_run=1)
        set_heal_budget_caps(caps)
        reset_heal_budget_counters()

        try:
            # First escalation succeeds
            increment_escalation_count(tier="LOW")

            # Second escalation fails
            with pytest.raises(HealBudgetExceededError, match="Escalation budget exceeded"):
                increment_escalation_count(tier="LOW")
        finally:
            reset_heal_budget_counters()

    def test_high_tier_budget_enforcement(self):
        """HIGH-tier use beyond cap fails closed."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealBudgetCaps,
            HealBudgetExceededError,
            increment_escalation_count,
            reset_heal_budget_counters,
            set_heal_budget_caps,
        )

        # Allow 2 escalations but only 1 HIGH-tier
        caps = HealBudgetCaps(max_escalations_per_run=3, max_high_tier_per_run=1)
        set_heal_budget_caps(caps)
        reset_heal_budget_counters()

        try:
            # First HIGH-tier succeeds
            increment_escalation_count(tier="HIGH")

            # Second HIGH-tier fails
            with pytest.raises(HealBudgetExceededError, match="HIGH-tier budget exceeded"):
                increment_escalation_count(tier="HIGH")
        finally:
            reset_heal_budget_counters()

    def test_budget_counters_tracked(self):
        """Budget counters are tracked correctly."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealBudgetCaps,
            get_budget_counters,
            increment_escalation_count,
            reset_heal_budget_counters,
            set_heal_budget_caps,
        )

        caps = HealBudgetCaps(max_escalations_per_run=5, max_high_tier_per_run=3)
        set_heal_budget_caps(caps)
        reset_heal_budget_counters()

        try:
            counters = get_budget_counters()
            assert counters["escalation_count"] == 0
            assert counters["high_tier_count"] == 0

            increment_escalation_count(tier="LOW")
            increment_escalation_count(tier="HIGH")

            counters = get_budget_counters()
            assert counters["escalation_count"] == 2
            assert counters["high_tier_count"] == 1
        finally:
            reset_heal_budget_counters()

    def test_enable_llm_false_budgets_zero(self):
        """enable_llm=False => HIGH-tier budget is zero."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealBudgetCaps,
            HealBudgetExceededError,
            increment_escalation_count,
            reset_heal_budget_counters,
            set_heal_budget_caps,
        )

        caps = HealBudgetCaps.from_env(enable_llm=False)
        set_heal_budget_caps(caps)
        reset_heal_budget_counters()

        try:
            # HIGH-tier immediately fails with enable_llm=False
            with pytest.raises(HealBudgetExceededError, match="HIGH-tier budget exceeded"):
                increment_escalation_count(tier="HIGH")
        finally:
            reset_heal_budget_counters()


class TestBudgetAndSeamIntegration:
    """Tests for budget + seam guard integration."""

    def test_seam_guard_still_enforced_with_budgets(self):
        """Seam guard is still enforced even with budgets set."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealBudgetCaps,
            HealLlmRequest,
            HealSeamBypassError,
            guarded_heal_llm_call,
            reset_heal_budget_counters,
            set_heal_budget_caps,
        )

        caps = HealBudgetCaps(max_escalations_per_run=5, max_high_tier_per_run=3)
        set_heal_budget_caps(caps)
        reset_heal_budget_counters()

        request = HealLlmRequest(
            prompt="test",
            model_id="test-model",
            metadata={"source": "test"},
        )

        try:
            # Seam guard should still block direct calls
            with pytest.raises(HealSeamBypassError):
                guarded_heal_llm_call(request)
        finally:
            reset_heal_budget_counters()

    def test_no_network_calls_in_budget_checks(self):
        """Budget checks make no network calls."""
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            HealBudgetCaps,
            increment_escalation_count,
            reset_heal_budget_counters,
            set_heal_budget_caps,
        )

        # This test relies on the network tripwire fixture from conftest.py
        # If any network call is made, it will raise NetworkTripwireError

        caps = HealBudgetCaps(max_escalations_per_run=2, max_high_tier_per_run=1)
        set_heal_budget_caps(caps)
        reset_heal_budget_counters()

        try:
            increment_escalation_count(tier="LOW")
            increment_escalation_count(tier="LOW")
            # No exception = no network calls made
        finally:
            reset_heal_budget_counters()
            assert True  # no-exception contract
