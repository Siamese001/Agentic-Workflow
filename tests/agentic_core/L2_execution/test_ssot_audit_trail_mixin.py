"""
Phase 1 — SSOT AuditTrail Mixin Tests.

Validates:
  - ExecutionTrace-compatible entry schema
  - SHA-256 canonical JSON hashing
  - prev_hash chaining correctness
  - replay_key stability (same inputs → same key)
  - Policy hash scoping in entries
  - Chain integrity verification
  - Tamper detection
  - Deterministic timestamps under replay mode
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest

from agentic_core.L2_execution.deterministic_providers import (
    unpatch_deterministic,
)
from agentic_core.mixins.replay_guard_mixin import ReplayGuardMixin
from agentic_core.mixins.ssot_audit_trail_mixin import SSOTAuditTrailMixin


@dataclass
class _TestExecutionContext:
    """Minimal ExecutionContext stand-in for unit tests."""

    mission_id: str = ""
    step_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    parent_span_id: str | None = None
    replay_mode: bool = False
    active_policy_hash: str | None = None
    safety_status: str = "PENDING"


class _AuditedStateManager(SSOTAuditTrailMixin, ReplayGuardMixin):
    """Test class combining SSOTAuditTrail + ReplayGuard with state dict."""

    def __init__(self, execution_context=None):
        self.state = {"audit_chain": []}
        super().__init__(execution_context=execution_context)


# ---------------------------------------------------------------------------
# Schema Tests
# ---------------------------------------------------------------------------


class TestAuditEntrySchema:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_entry_has_all_execution_trace_fields(self):
        """Audit entry contains all ExecutionTrace-compatible fields."""
        ctx = _TestExecutionContext(
            trace_id="trace-schema",
            active_policy_hash="ph-schema",
            safety_status="CLEARED",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("HEAL", "target.py", diff={"line": 42})

        required_fields = {
            "trace_id",
            "plan_hash",
            "actor",
            "target",
            "diff",
            "policy_hash",
            "timestamp",
            "prev_hash",
            "replay_key",
            "curr_hash",
        }
        assert required_fields.issubset(entry.keys())

    @pytest.mark.unit_min_deps
    def test_entry_values_correct(self):
        """Entry values match injected context."""
        ctx = _TestExecutionContext(
            trace_id="trace-vals",
            active_policy_hash="ph-vals",
            safety_status="CLEARED",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("VALIDATE", "module.py")

        assert entry["trace_id"] == "trace-vals"
        assert entry["policy_hash"] == "ph-vals"
        assert entry["actor"] == "_AuditedStateManager"
        assert entry["target"] == "module.py"
        assert entry["plan_hash"] == "ph-vals"  # Falls back to policy_hash

    @pytest.mark.unit_min_deps
    def test_custom_plan_hash(self):
        """plan_hash can be overridden."""
        ctx = _TestExecutionContext(
            trace_id="trace-plan",
            active_policy_hash="ph-plan",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("HEAL", "f.py", plan_hash="custom-plan")
        assert entry["plan_hash"] == "custom-plan"
        assert entry["policy_hash"] == "ph-plan"


# ---------------------------------------------------------------------------
# SHA-256 Chain Tests
# ---------------------------------------------------------------------------


class TestSHA256Chaining:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_first_entry_links_to_genesis(self):
        """First entry's prev_hash is the genesis hash (64 zeros)."""
        ctx = _TestExecutionContext(trace_id="trace-gen", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("BOOT", "system")
        assert entry["prev_hash"] == "0" * 64

    @pytest.mark.unit_min_deps
    def test_chain_links_correctly(self):
        """Each entry's prev_hash equals the previous entry's curr_hash."""
        ctx = _TestExecutionContext(trace_id="trace-chain", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)

        e1 = obj.emit_ssot_audit_entry("ACTION_1", "t1")
        e2 = obj.emit_ssot_audit_entry("ACTION_2", "t2")
        e3 = obj.emit_ssot_audit_entry("ACTION_3", "t3")

        assert e2["prev_hash"] == e1["curr_hash"]
        assert e3["prev_hash"] == e2["curr_hash"]

    @pytest.mark.unit_min_deps
    def test_curr_hash_is_sha256_of_canonical_json(self):
        """curr_hash is SHA-256 of canonical JSON (excluding curr_hash)."""
        ctx = _TestExecutionContext(trace_id="trace-hash", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("TEST", "target")

        # Recompute
        entry_copy = {k: v for k, v in entry.items() if k != "curr_hash"}
        canonical = json.dumps(entry_copy, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert entry["curr_hash"] == expected

    @pytest.mark.unit_min_deps
    def test_audit_count_increments(self):
        """ssot_audit_count increments with each entry."""
        ctx = _TestExecutionContext(trace_id="trace-count", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        assert obj.ssot_audit_count == 0
        obj.emit_ssot_audit_entry("A", "t")
        assert obj.ssot_audit_count == 1
        obj.emit_ssot_audit_entry("B", "t")
        assert obj.ssot_audit_count == 2

    @pytest.mark.unit_min_deps
    def test_audit_head_advances(self):
        """ssot_audit_head updates to latest curr_hash."""
        ctx = _TestExecutionContext(trace_id="trace-head", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        assert obj.ssot_audit_head == "0" * 64
        e1 = obj.emit_ssot_audit_entry("A", "t")
        assert obj.ssot_audit_head == e1["curr_hash"]


# ---------------------------------------------------------------------------
# Replay Key Tests
# ---------------------------------------------------------------------------


class TestReplayKey:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_replay_key_stable(self):
        """Same inputs produce identical replay_key."""
        ctx = _TestExecutionContext(
            trace_id="trace-rk",
            active_policy_hash="ph-rk",
        )
        obj1 = _AuditedStateManager(execution_context=ctx)
        obj2 = _AuditedStateManager(execution_context=ctx)

        e1 = obj1.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj2.emit_ssot_audit_entry("HEAL", "file.py")
        assert e1["replay_key"] == e2["replay_key"]

    @pytest.mark.unit_min_deps
    def test_replay_key_differs_on_different_action(self):
        """Different action produces different replay_key."""
        ctx = _TestExecutionContext(
            trace_id="trace-rk2",
            active_policy_hash="ph-rk2",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        e1 = obj.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj.emit_ssot_audit_entry("VALIDATE", "file.py")
        assert e1["replay_key"] != e2["replay_key"]

    @pytest.mark.unit_min_deps
    def test_replay_key_differs_on_different_policy(self):
        """Different policy_hash produces different replay_key."""
        ctx1 = _TestExecutionContext(trace_id="trace-rk3", active_policy_hash="ph-A")
        ctx2 = _TestExecutionContext(trace_id="trace-rk3", active_policy_hash="ph-B")
        obj1 = _AuditedStateManager(execution_context=ctx1)
        obj2 = _AuditedStateManager(execution_context=ctx2)
        e1 = obj1.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj2.emit_ssot_audit_entry("HEAL", "file.py")
        assert e1["replay_key"] != e2["replay_key"]


# ---------------------------------------------------------------------------
# Chain Verification Tests
# ---------------------------------------------------------------------------


class TestChainVerification:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_valid_chain_passes(self):
        """Valid chain passes verification."""
        ctx = _TestExecutionContext(trace_id="trace-verify", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("A", "t1")
        obj.emit_ssot_audit_entry("B", "t2")
        obj.emit_ssot_audit_entry("C", "t3")

        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is True
        assert broken_idx is None

    @pytest.mark.unit_min_deps
    def test_tampered_entry_detected(self):
        """Tampered curr_hash is detected."""
        ctx = _TestExecutionContext(trace_id="trace-tamper", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("A", "t1")
        obj.emit_ssot_audit_entry("B", "t2")

        # Tamper with second entry
        obj.state["audit_chain"][1]["curr_hash"] = "deadbeef" * 8

        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is False
        assert broken_idx == 1

    @pytest.mark.unit_min_deps
    def test_broken_chain_link_detected(self):
        """Broken prev_hash linkage is detected."""
        ctx = _TestExecutionContext(trace_id="trace-broken", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("A", "t1")
        obj.emit_ssot_audit_entry("B", "t2")
        obj.emit_ssot_audit_entry("C", "t3")

        # Break chain link at index 2
        obj.state["audit_chain"][2]["prev_hash"] = "0" * 64

        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is False
        assert broken_idx == 2

    @pytest.mark.unit_min_deps
    def test_empty_chain_valid(self):
        """Empty chain passes verification."""
        ctx = _TestExecutionContext(trace_id="trace-empty", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is True
        assert broken_idx is None

    @pytest.mark.unit_min_deps
    def test_entries_appended_to_state(self):
        """Entries are appended to self.state['audit_chain']."""
        ctx = _TestExecutionContext(trace_id="trace-state", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("X", "y")
        obj.emit_ssot_audit_entry("Z", "w")
        assert len(obj.state["audit_chain"]) == 2


# ---------------------------------------------------------------------------
# Policy Hash Scoping Tests
# ---------------------------------------------------------------------------


class TestPolicyHashScoping:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_policy_hash_in_every_entry(self):
        """Every audit entry includes the active policy_hash."""
        ctx = _TestExecutionContext(
            trace_id="trace-ph",
            active_policy_hash="scoped-hash",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        for i in range(5):
            obj.emit_ssot_audit_entry(f"ACTION_{i}", f"target_{i}")

        for entry in obj.state["audit_chain"]:
            assert entry["policy_hash"] == "scoped-hash"

    @pytest.mark.unit_min_deps
    def test_different_policy_hash_different_chains(self):
        """Different policy hashes produce different curr_hash values."""
        ctx1 = _TestExecutionContext(trace_id="trace-iso", active_policy_hash="ph-1")
        ctx2 = _TestExecutionContext(trace_id="trace-iso", active_policy_hash="ph-2")
        obj1 = _AuditedStateManager(execution_context=ctx1)
        obj2 = _AuditedStateManager(execution_context=ctx2)

        e1 = obj1.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj2.emit_ssot_audit_entry("HEAL", "file.py")

        # Different policy_hash → different curr_hash (even same action/target)
        assert e1["curr_hash"] != e2["curr_hash"]
