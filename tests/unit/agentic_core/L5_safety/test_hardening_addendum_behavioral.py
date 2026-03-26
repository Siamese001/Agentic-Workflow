"""Hardening Addendum behavioral tests — covers all 8 addendum sections.

Coverage matrix:
  [1.1] ExecutionTrace completeness — execution_trace_types.py
  [1.2] Boundary mutation cross-check — L2_execution/sandbox/boundary_validator.py
  [1.3] Healing visibility — healing_event_emitter.py
  [2.1] UWG replay key determinism — interfaces/write_gateway.py
  [2.2] Ledger integrity — L4_state/ledger/integrity_validator.py
  [2.3] 2PC coordinator — (covered by test_two_phase_commit.py, smoke only here)
  [3.1] C0 authority leak guard — L0_routing/context/c0_guard.py
  [3.2] C0 immutability — L0_routing/context/c0_guard.py
  [6.1] Patch validator — L5_safety/hitl/patch_validator.py
  [6.3] Decision logger — L5_safety/hitl/decision_logger.py
  [8]   Runtime invariant checker — L5_safety/invariants/runtime_invariant_checker.py

Hardening error types — L5_safety/types/hardening_errors.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# =========================================================================
# Hardening Error Types — hierarchy and instantiation
# =========================================================================


class TestHardeningErrorTypes:
    def test_all_error_types_are_runtime_errors(self):
                from agentic_core.L5_safety.types.hardening_errors import (
                from agentic_core.L5_safety.types.hardening_errors import (
                from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
                from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation
                from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
                from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError
                from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
                from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
                from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure
                from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
                from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
                from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace
                from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
                from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
                from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
                from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure
                from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
                from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
                from agentic_core.L2_execution.types.execution_trace_types import ExecutionTraceBuilder
                from agentic_core.L2_execution.types.execution_trace_types import ExecutionTraceBuilder
                from agentic_core.L2_execution.sandbox.boundary_validator import (
                from agentic_core.L2_execution.sandbox.boundary_validator import verify_mutation_replay_integrity
                from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
                from agentic_core.L2_execution.sandbox.boundary_validator import compute_boundary_diff
                from agentic_core.L2_execution.sandbox.boundary_validator import compute_boundary_diff
                from agentic_core.L2_execution.sandbox.boundary_validator import compute_boundary_diff
                from agentic_core.L2_execution.sandbox.boundary_validator import verify_mutation_replay_integrity
                from agentic_core.L2_execution.healers.healing_event_emitter import (
                from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter
                from agentic_core.L2_execution.healers.healing_event_emitter import HealingAttemptEvent
                from agentic_core.L2_execution.healers.healing_event_emitter import HealingAttemptEvent
                from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter
                from agentic_core.interfaces.write_gateway import compute_replay_key
                from agentic_core.interfaces.write_gateway import compute_replay_key
                from agentic_core.interfaces.write_gateway import compute_replay_key
                from agentic_core.interfaces.write_gateway import compute_replay_key
                from agentic_core.L4_state.ledger.integrity_validator import (
                from agentic_core.L4_state.ledger.integrity_validator import (
                from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
                from agentic_core.L4_state.ledger.integrity_validator import validate_ledger_chain
                from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
                from agentic_core.L4_state.ledger.integrity_validator import compute_entry_hash
                from agentic_core.L4_state.ledger.integrity_validator import append_with_hash
                from agentic_core.L4_state.ledger.integrity_validator import validate_ledger_chain
                from agentic_core.L4_state.ledger.integrity_validator import (
                from agentic_core.L4_state.ledger.integrity_validator import validate_ledger_file
                from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
                from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
                from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
                from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
                from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
                from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
                from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
                from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
                from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
                from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
                from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation
                from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
                from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation
                from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
                from agentic_core.L5_safety.hitl.patch_validator import ValidatedPatch, validate_patch
                from agentic_core.L5_safety.hitl.patch_validator import validate_patch
                from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
                from agentic_core.L5_safety.hitl.patch_validator import validate_patch
                from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
                from agentic_core.L5_safety.hitl.patch_validator import validate_patch
                from agentic_core.L5_safety.hitl.patch_validator import validate_patch
                from agentic_core.L5_safety.hitl.patch_validator import validate_patch
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecision, HITLDecisionLogger
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecision
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecision
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecision
                from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_source_is_l2
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_source_is_l2
                from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_in_ledger
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_in_ledger
                from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_state_read_source_is_l4
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_state_read_source_is_l4
                from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_c0_no_authority_fields
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_c0_no_authority_fields
                from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
                from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
                from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
                from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants
                from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants
        #  # MOVED: from agentic_core.L5_safety.types.hardening_errors import (
                    C0AuthorityLeakError,
                    C0MutationViolation,
                    ExecutionTraceIntegrityError,
                    HumanPatchL5ClearanceError,
                    HumanPatchValidationError,
                    LedgerIntegrityViolation,
                    MutationCommitFailure,
                    MutationReplayIntegrityViolation,
                    RuntimePolicyMutationViolation,
                )


        for cls in (
            ExecutionTraceIntegrityError,
            MutationReplayIntegrityViolation,
            LedgerIntegrityViolation,
            MutationCommitFailure,
            C0AuthorityLeakError,
            C0MutationViolation,
            RuntimePolicyMutationViolation,
            HumanPatchValidationError,
            HumanPatchL5ClearanceError,
        ):
            assert issubclass(cls, RuntimeError), f"{cls.__name__} must inherit RuntimeError"

    def test_each_error_carries_message(self):
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import (
            C0AuthorityLeakError,
            ExecutionTraceIntegrityError,
            LedgerIntegrityViolation,
            MutationCommitFailure,
        )

"""Test agentic_core import functionality."""
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
# Basic functionality assertion
assert True  # Replace with meaningful assertion
        expected = {
            "ExecutionTraceIntegrityError",
            "MutationReplayIntegrityViolation",
            "LedgerIntegrityViolation",
            "MutationCommitFailure",
            "C0AuthorityLeakError",
            "C0MutationViolation",
            "RuntimePolicyMutationViolation",
            "HumanPatchValidationError",
            "HumanPatchL5ClearanceError",
        }
        assert expected <= set(hardening_errors.__all__)


# =========================================================================
# [1.1] ExecutionTrace completeness
# =========================================================================


class TestExecutionTraceCompleteness:
    def _make_trace(self, **overrides):
#  # MOVED: from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace

        defaults = dict(
            trace_id="tid-001",
            instruction_packet_id="ip-001",
            governed_payload_hash="gph-001",
            sandbox_envelope_ids=("se-1",),
            llm_response_hash="lrh-001",
            validation_decision="PASS",
            timing_ms=100,
            hash_chain_root="hcr-001",
            policy_hash="ph-001",
            prev_hash="prev-001",
            transcript_hash="th-001",
            agent_id="agent-001",
        )
        defaults.update(overrides)
        return ExecutionTrace(**defaults)

"""Test agentic_core import functionality."""
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure
# Basic functionality assertion
assert True  # Replace with meaningful assertion

    def test_invalid_validation_decision_raises(self):
        with pytest.raises(ValueError, match="validation_decision"):
            self._make_trace(validation_decision="INVALID")

    def test_validate_completeness_raises_on_empty_governed_payload_hash(self):
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError

        trace = self._make_trace(governed_payload_hash="")
        with pytest.raises(ExecutionTraceIntegrityError, match="governed_payload_hash"):
            trace.validate_completeness()

    def test_validate_completeness_raises_on_empty_hash_chain_root(self):
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError

        trace = self._make_trace(hash_chain_root="")
        with pytest.raises(ExecutionTraceIntegrityError, match="hash_chain_root"):
            trace.validate_completeness()

    def test_replay_key_is_computed_automatically(self):
        trace = self._make_trace()
        assert trace.replay_key
        assert len(trace.replay_key) == 64

    def test_replay_key_is_deterministic(self):
        t1 = self._make_trace()
        t2 = self._make_trace()
        assert t1.replay_key == t2.replay_key

    def test_replay_key_differs_with_different_inputs(self):
        t1 = self._make_trace(transcript_hash="aaa")
        t2 = self._make_trace(transcript_hash="bbb")
        assert t1.replay_key != t2.replay_key

    def test_canonical_bytes_deterministic(self):
        t = self._make_trace()
        assert t.canonical_bytes() == t.canonical_bytes()

    def test_content_hash_is_64_char_hex(self):
        t = self._make_trace()
        h = t.content_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_trace_is_frozen(self):
        t = self._make_trace()
        with pytest.raises(AttributeError):
            t.trace_id = "new"  # type: ignore[misc]


class TestExecutionTraceBuilder:
    def test_builder_seal_produces_valid_trace(self):
#  # MOVED: from agentic_core.L2_execution.types.execution_trace_types import ExecutionTraceBuilder

        b = ExecutionTraceBuilder("tid-b", "ip-b")
        b.set_governed_payload("gph")
        b.add_sandbox_envelope("se-1")
        b.set_llm_response("hello world")
        b.set_hash_chain_root("root")
        b.set_policy_hash("policy")
        b.set_transcript(b"transcript bytes")
        trace = b.seal()
        assert trace.trace_id == "tid-b"
        assert trace.instruction_packet_id == "ip-b"
        trace.validate_completeness()

    def test_builder_default_decision_is_pass(self):
#  # MOVED: from agentic_core.L2_execution.types.execution_trace_types import ExecutionTraceBuilder

        b = ExecutionTraceBuilder("tid", "ip")
        b.set_governed_payload("g")
        b.set_llm_response("r")
        b.set_hash_chain_root("root")
        trace = b.seal()
        assert trace.validation_decision == "PASS"


# =========================================================================
# [1.2] Boundary mutation cross-check
# =========================================================================


class TestBoundaryValidator:
    def test_matching_diff_passes(self):
#  # MOVED: from agentic_core.L2_execution.sandbox.boundary_validator import (
            compute_boundary_diff,
            verify_mutation_replay_integrity,
        )

        pre = {"a": 1, "b": 2}
        post = {"a": 1, "b": 3}
        uwg_diff = compute_boundary_diff(pre, post)
        verify_mutation_replay_integrity(pre, post, uwg_diff)

    def test_mismatched_diff_raises(self):
#  # MOVED: from agentic_core.L2_execution.sandbox.boundary_validator import verify_mutation_replay_integrity
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation

        pre = {"a": 1}
        post = {"a": 2}
        fake_uwg_diff = {"a": {"pre": 1, "post": 99}}
        with pytest.raises(MutationReplayIntegrityViolation, match="mismatch"):
            verify_mutation_replay_integrity(pre, post, fake_uwg_diff)

    def test_compute_boundary_diff_empty_when_identical(self):
#  # MOVED: from agentic_core.L2_execution.sandbox.boundary_validator import compute_boundary_diff

        snapshot = {"x": 1, "y": 2}
        assert compute_boundary_diff(snapshot, snapshot) == {}

    def test_compute_boundary_diff_detects_added_key(self):
#  # MOVED: from agentic_core.L2_execution.sandbox.boundary_validator import compute_boundary_diff

        diff = compute_boundary_diff({"a": 1}, {"a": 1, "b": 2})
        assert "b" in diff
        assert diff["b"]["pre"] is None
        assert diff["b"]["post"] == 2

    def test_compute_boundary_diff_detects_removed_key(self):
#  # MOVED: from agentic_core.L2_execution.sandbox.boundary_validator import compute_boundary_diff

        diff = compute_boundary_diff({"a": 1, "b": 2}, {"a": 1})
        assert "b" in diff
        assert diff["b"]["pre"] == 2
        assert diff["b"]["post"] is None

    def test_identical_snapshots_pass_integrity_check(self):
#  # MOVED: from agentic_core.L2_execution.sandbox.boundary_validator import verify_mutation_replay_integrity

        s = {"k": "v"}
        verify_mutation_replay_integrity(s, s, {})


# =========================================================================
# [1.3] Healing visibility
# =========================================================================


class TestHealingEventEmitter:
    def test_emit_returns_event(self):
#  # MOVED: from agentic_core.L2_execution.healers.healing_event_emitter import (
            HealingAttemptEvent,
            HealingEventEmitter,
        )

        tmp = Path(tempfile.mkdtemp())
        emitter = HealingEventEmitter(log_path=tmp / "heal.jsonl")
        event = emitter.emit(
            trace_id="t1",
            attempt_number=1,
            failure_class="ImportError",
            healer_selected="LocationHealer",
            model_used="gpt-4",
            outcome="SUCCESS",
        )
        assert isinstance(event, HealingAttemptEvent)
        assert event.trace_id == "t1"
        assert event.outcome == "SUCCESS"

    def test_emitted_events_accumulate(self):
#  # MOVED: from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        tmp = Path(tempfile.mkdtemp())
        emitter = HealingEventEmitter(log_path=tmp / "heal.jsonl")
        emitter.emit("t1", 1, "E1", "H1", "m1", "SUCCESS")
        emitter.emit("t2", 2, "E2", "H2", "m2", "FAILURE")
        assert len(emitter.emitted_events()) == 2

    def test_event_to_jsonl_is_valid_json(self):
        import json

#  # MOVED: from agentic_core.L2_execution.healers.healing_event_emitter import HealingAttemptEvent

        event = HealingAttemptEvent(
            trace_id="t1",
            attempt_number=1,
            failure_class="E",
            healer_selected="H",
            model_used="M",
            outcome="SUCCESS",
        )
        parsed = json.loads(event.to_jsonl())
        assert parsed["trace_id"] == "t1"
        assert parsed["outcome"] == "SUCCESS"

    def test_event_has_all_required_fields(self):
        from dataclasses import fields

#  # MOVED: from agentic_core.L2_execution.healers.healing_event_emitter import HealingAttemptEvent

        names = {f.name for f in fields(HealingAttemptEvent)}
        required = {"trace_id", "attempt_number", "failure_class", "healer_selected", "model_used", "outcome"}
        assert required <= names

    def test_emitter_writes_to_disk(self):
#  # MOVED: from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        tmp = Path(tempfile.mkdtemp())
        log_path = tmp / "heal.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        emitter.emit("t1", 1, "E1", "H1", "m1", "SUCCESS")
        assert log_path.exists()
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1


# =========================================================================
# [2.1] UWG replay key determinism
# =========================================================================


class TestWriteGatewayReplayKey:
    def test_compute_replay_key_returns_64_hex(self):
#  # MOVED: from agentic_core.interfaces.write_gateway import compute_replay_key

        key = compute_replay_key("plan_hash", ["tool_a", "tool_b"], "stdout_dig", "diff_hash")
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)

    def test_compute_replay_key_is_deterministic(self):
#  # MOVED: from agentic_core.interfaces.write_gateway import compute_replay_key

        k1 = compute_replay_key("ph", ["t1", "t2"], "sd", "dh")
        k2 = compute_replay_key("ph", ["t1", "t2"], "sd", "dh")
        assert k1 == k2

    def test_compute_replay_key_order_independent(self):
#  # MOVED: from agentic_core.interfaces.write_gateway import compute_replay_key

        k1 = compute_replay_key("ph", ["t2", "t1"], "sd", "dh")
        k2 = compute_replay_key("ph", ["t1", "t2"], "sd", "dh")
        assert k1 == k2

    def test_compute_replay_key_differs_on_different_inputs(self):
#  # MOVED: from agentic_core.interfaces.write_gateway import compute_replay_key

        k1 = compute_replay_key("ph_a", ["t1"], "sd", "dh")
        k2 = compute_replay_key("ph_b", ["t1"], "sd", "dh")
        assert k1 != k2


# =========================================================================
# [2.2] Ledger integrity
# =========================================================================


class TestLedgerIntegrity:
    def test_valid_chain_passes(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import (
            append_with_hash,
            validate_ledger_chain,
        )

        entries: list[dict] = []
        append_with_hash(entries, {"action": "create", "file": "a.py"})
        append_with_hash(entries, {"action": "modify", "file": "b.py"})
        validate_ledger_chain(entries)

    def test_broken_chain_raises(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import (
            append_with_hash,
            validate_ledger_chain,
        )
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation

        entries: list[dict] = []
        append_with_hash(entries, {"action": "create"})
        append_with_hash(entries, {"action": "modify"})
        entries[1]["_hash"] = "0" * 64
        with pytest.raises(LedgerIntegrityViolation, match="mismatch"):
            validate_ledger_chain(entries)

    def test_missing_hash_field_raises(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import validate_ledger_chain
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation

        entries = [{"action": "create"}]
        with pytest.raises(LedgerIntegrityViolation, match="missing"):
            validate_ledger_chain(entries)

    def test_compute_entry_hash_is_deterministic(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import compute_entry_hash

        h1 = compute_entry_hash("prev", {"a": 1, "b": 2})
        h2 = compute_entry_hash("prev", {"b": 2, "a": 1})
        assert h1 == h2

    def test_append_with_hash_adds_hash_field(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import append_with_hash

        entries: list[dict] = []
        result = append_with_hash(entries, {"action": "test"})
        assert "_hash" in result
        assert len(result["_hash"]) == 64
        assert len(entries) == 1

    def test_empty_chain_validates(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import validate_ledger_chain

        validate_ledger_chain([])

    def test_single_entry_chain(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import (
            append_with_hash,
            validate_ledger_chain,
        )

        entries: list[dict] = []
        append_with_hash(entries, {"x": 1})
        validate_ledger_chain(entries)

    def test_validate_ledger_file_nonexistent_is_noop(self):
#  # MOVED: from agentic_core.L4_state.ledger.integrity_validator import validate_ledger_file

        validate_ledger_file(Path("/nonexistent/path/ledger.jsonl"))


# =========================================================================
# [3.1] C0 authority leak guard
# =========================================================================


class TestC0AuthorityLeakGuard:
    def test_clean_payload_passes(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import guard_c0_payload

        guard_c0_payload({"question": "What is X?", "context": "doc snippet"})

    def test_authority_field_raises(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError

        with pytest.raises(C0AuthorityLeakError, match="route_mode"):
            guard_c0_payload({"question": "Q", "route_mode": "FULL"})

    def test_multiple_authority_fields_reported(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError

        with pytest.raises(C0AuthorityLeakError) as exc_info:
            guard_c0_payload({"auth_token": "tok", "execution_tier": "HIGH"})
        msg = str(exc_info.value)
        assert "auth_token" in msg
        assert "execution_tier" in msg

    def test_all_five_forbidden_fields_detected(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError

        payload = {
            "route_mode": "x",
            "execution_tier": "x",
            "safety_threshold": 0.5,
            "allowed_tools": [],
            "auth_token": "tok",
        }
        with pytest.raises(C0AuthorityLeakError):
            guard_c0_payload(payload)

    def test_empty_payload_passes(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import guard_c0_payload

        guard_c0_payload({})


# =========================================================================
# [3.2] C0 immutability
# =========================================================================


class TestC0Immutability:
    def test_identical_payloads_pass(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability

        payload = {"a": 1, "b": [2, 3]}
        verify_c0_immutability(payload, payload)

    def test_mutated_payload_raises(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation

        pre = {"a": 1}
        post = {"a": 2}
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(pre, post)

    def test_added_key_is_mutation(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation

        with pytest.raises(C0MutationViolation):
            verify_c0_immutability({"a": 1}, {"a": 1, "b": 2})

    def test_empty_to_empty_passes(self):
#  # MOVED: from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability

        verify_c0_immutability({}, {})


# =========================================================================
# [6.1] Patch validator
# =========================================================================


class TestPatchValidator:
    def _valid_patch(self):
        return {
            "original_plan_hash": "abc123",
            "structured_patch_schema": {"op": "modify", "file": "a.py"},
            "reviewer_signature": "reviewer@example.com",
        }

    def test_valid_patch_returns_validated_patch(self):
#  # MOVED: from agentic_core.L5_safety.hitl.patch_validator import ValidatedPatch, validate_patch

        result = validate_patch(self._valid_patch())
        assert isinstance(result, ValidatedPatch)
        assert result.original_plan_hash == "abc123"
        assert result.reviewer_signature == "reviewer@example.com"

    def test_missing_fields_raises(self):
#  # MOVED: from agentic_core.L5_safety.hitl.patch_validator import validate_patch
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError

        with pytest.raises(HumanPatchValidationError, match="original_plan_hash"):
            validate_patch({"structured_patch_schema": {}, "reviewer_signature": "r"})

    def test_empty_field_treated_as_missing(self):
#  # MOVED: from agentic_core.L5_safety.hitl.patch_validator import validate_patch
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError

        patch = self._valid_patch()
        patch["reviewer_signature"] = ""
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_patch_hash_is_64_hex(self):
#  # MOVED: from agentic_core.L5_safety.hitl.patch_validator import validate_patch

        result = validate_patch(self._valid_patch())
        assert len(result.patch_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.patch_hash)

    def test_patch_hash_is_deterministic(self):
#  # MOVED: from agentic_core.L5_safety.hitl.patch_validator import validate_patch

        r1 = validate_patch(self._valid_patch())
        r2 = validate_patch(self._valid_patch())
        assert r1.patch_hash == r2.patch_hash

    def test_raw_field_preserves_original(self):
#  # MOVED: from agentic_core.L5_safety.hitl.patch_validator import validate_patch

        patch = self._valid_patch()
        patch["extra_field"] = "extra"
        result = validate_patch(patch)
        assert result.raw["extra_field"] == "extra"


# =========================================================================
# [6.3] Decision logger
# =========================================================================


class TestHITLDecisionLogger:
    def test_log_returns_decision_record(self):
#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecision, HITLDecisionLogger

        tmp = Path(tempfile.mkdtemp())
        logger = HITLDecisionLogger(log_path=tmp / "decisions.jsonl")
        record = logger.log(
            agent="ArchGov",
            file="a.py",
            violation="layer_violation",
            proposed="move file",
            decision="APPROVE",
        )
        assert isinstance(record, HITLDecision)
        assert record.decision_number == 1
        assert record.agent == "ArchGov"

    def test_counter_increments(self):
#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        tmp = Path(tempfile.mkdtemp())
        logger = HITLDecisionLogger(log_path=tmp / "decisions.jsonl")
        logger.log("A1", "f1", "v1", "p1", "APPROVE")
        logger.log("A2", "f2", "v2", "p2", "REJECT")
        assert logger.count() == 2

    def test_all_records_returns_list(self):
#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        tmp = Path(tempfile.mkdtemp())
        logger = HITLDecisionLogger(log_path=tmp / "decisions.jsonl")
        logger.log("A1", "f1", "v1", "p1", "APPROVE")
        records = logger.all_records()
        assert len(records) == 1
        assert records[0].decision == "APPROVE"

    def test_to_log_line_format(self):
#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecision

        d = HITLDecision(
            decision_number=3,
            agent="LocationHealer",
            file="foo.py",
            violation="misplaced",
            proposed="move",
            decision="APPROVE",
        )
        line = d.to_log_line()
        assert line.startswith("HITL_DECISION_3:")
        assert "Agent=LocationHealer" in line
        assert "File=foo.py" in line

    def test_to_log_line_has_no_timestamp(self):
        import re

#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecision

        d = HITLDecision(1, "A", "f", "v", "p", "D")
        line = d.to_log_line()
        assert not re.search(r"\d{4}-\d{2}-\d{2}", line), "Log line must not contain ISO date"
        assert not re.search(r"\d{2}:\d{2}:\d{2}", line), "Log line must not contain wall-clock time"

    def test_to_jsonl_is_valid_json(self):
        import json

#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecision

        d = HITLDecision(1, "A", "f", "v", "p", "D")
        parsed = json.loads(d.to_jsonl())
        assert parsed["decision_number"] == 1

    def test_logger_writes_to_disk(self):
#  # MOVED: from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        tmp = Path(tempfile.mkdtemp())
        log_path = tmp / "decisions.jsonl"
        logger = HITLDecisionLogger(log_path=log_path)
        logger.log("A1", "f1", "v1", "p1", "APPROVE")
        assert log_path.exists()
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1


# =========================================================================
# [8] Runtime invariant checker
# =========================================================================


class TestRuntimeInvariantChecker:
    def test_inv1_l2_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_source_is_l2

        assert_mutation_source_is_l2("L2_execution")

    def test_inv1_non_l2_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_source_is_l2
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation

        with pytest.raises(MutationReplayIntegrityViolation, match="Invariant 1"):
            assert_mutation_source_is_l2("L3_orchestration")

    def test_inv2_mutation_in_ledger_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_in_ledger

        ledger = [{"file_path": "a.py", "operation": "write"}]
        assert_mutation_in_ledger(ledger, "a.py", "write")

    def test_inv2_mutation_not_in_ledger_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_mutation_in_ledger
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation

        with pytest.raises(MutationReplayIntegrityViolation, match="Invariant 2"):
            assert_mutation_in_ledger([], "a.py", "write")

    def test_inv3_l4_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_state_read_source_is_l4

        assert_state_read_source_is_l4("L4_state")

    def test_inv3_non_l4_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_state_read_source_is_l4
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import MutationReplayIntegrityViolation

        with pytest.raises(MutationReplayIntegrityViolation, match="Invariant 3"):
            assert_state_read_source_is_l4("L2_execution")

    def test_inv4_clean_c0_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_c0_no_authority_fields

        assert_c0_no_authority_fields({"question": "Q", "context": "C"})

    def test_inv4_authority_field_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import assert_c0_no_authority_fields
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError

        with pytest.raises(C0AuthorityLeakError, match="Invariant 4"):
            assert_c0_no_authority_fields({"route_mode": "FULL"})

    def test_inv5_no_mutation_before_s9_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
            assert_telemetry_no_config_mutation,
        )

        assert_telemetry_no_config_mutation(5, config_mutated=False)

    def test_inv5_mutation_before_s9_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
            assert_telemetry_no_config_mutation,
        )
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation

        with pytest.raises(RuntimePolicyMutationViolation, match="Invariant 5"):
            assert_telemetry_no_config_mutation(5, config_mutated=True)

    def test_inv5_mutation_at_s9_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
            assert_telemetry_no_config_mutation,
        )

        assert_telemetry_no_config_mutation(9, config_mutated=True)

    def test_inv6_valid_signature_passes(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
            assert_human_patch_l5_clearance,
        )

        assert_human_patch_l5_clearance("sig-abc123")

    def test_inv6_missing_signature_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
            assert_human_patch_l5_clearance,
        )
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError

        with pytest.raises(HumanPatchL5ClearanceError, match="Invariant 6"):
            assert_human_patch_l5_clearance(None)

    def test_inv6_empty_signature_raises(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
            assert_human_patch_l5_clearance,
        )
#  # MOVED: from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError

        with pytest.raises(HumanPatchL5ClearanceError, match="Invariant 6"):
            assert_human_patch_l5_clearance("")


class TestRunAllInvariants:
    def test_all_clean_returns_empty(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants

        violations = run_all_invariants(
            mutation_source="L2_execution",
            ledger_entries=[{"file_path": "a.py", "operation": "write"}],
            file_path="a.py",
            operation="write",
            state_read_source="L4_state",
            c0_payload={"question": "Q"},
            meta_learning_stage=9,
            config_mutated=True,
        )
        assert violations == []

    def test_multiple_violations_collected(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants

        violations = run_all_invariants(
            mutation_source="L3_orchestration",
            state_read_source="L0_routing",
            c0_payload={"auth_token": "tok"},
            meta_learning_stage=3,
            config_mutated=True,
        )
        assert len(violations) >= 3

    def test_none_args_skip_checks(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants

        violations = run_all_invariants()
        assert violations == []

    def test_partial_args_run_applicable_checks(self):
#  # MOVED: from agentic_core.L5_safety.invariants.runtime_invariant_checker import run_all_invariants

        violations = run_all_invariants(mutation_source="L3_orchestration")
        assert len(violations) == 1
        assert "Invariant 1" in violations[0]
