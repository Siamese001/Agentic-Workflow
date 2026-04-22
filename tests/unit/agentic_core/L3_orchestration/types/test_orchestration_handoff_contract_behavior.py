"""Behavioral tests for agentic_core.L3_orchestration.types.orchestration_handoff_contract.

Covers the mandatory P0/L3 agent-to-agent handoff artifact:
  - `HandoffOutcome` enum membership + str-enum semantics
  - `OrchestrationHandoffContract` immutability + field contract
  - `OrchestrationHandoffContract.create` factory hashing semantics
  - `to_dict` redaction (capability_token truncation)
  - `emit_agent_executes_agent` convenience wrapper
  - `emit_agent_executes_agent` (instance method) idempotent ADG log

L3 is a ×1.75 criticality layer. Module ranked in top-10 by fan-in (12) in
the Stage 1 risk-weighted gap report.
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def oh():
    return pytest.importorskip(
        "agentic_core.L3_orchestration.types.orchestration_handoff_contract"
    )


# --------------------------------------------------------------------------- #
# Public surface                                                              #
# --------------------------------------------------------------------------- #


class TestPublicSurface:
    def test_exports(self, oh):
        for name in ("OrchestrationHandoffContract", "HandoffOutcome", "emit_agent_executes_agent"):
            assert name in oh.__all__, f"missing export: {name}"


# --------------------------------------------------------------------------- #
# HandoffOutcome                                                              #
# --------------------------------------------------------------------------- #


class TestHandoffOutcome:
    @pytest.mark.parametrize(
        "member,value",
        [
            ("PENDING", "pending"),
            ("DISPATCHED", "dispatched"),
            ("COMPLETED", "completed"),
            ("FAILED", "failed"),
            ("DENIED", "denied"),
            ("CANCELLED", "cancelled"),
        ],
    )
    def test_members(self, oh, member, value):
        assert getattr(oh.HandoffOutcome, member).value == value

    def test_is_str_enum(self, oh):
        assert oh.HandoffOutcome.PENDING == "pending"

    def test_member_count(self, oh):
        # Guard against silent additions that break downstream exhaustiveness checks.
        assert len(list(oh.HandoffOutcome)) == 6


# --------------------------------------------------------------------------- #
# Contract construction                                                       #
# --------------------------------------------------------------------------- #


def _mk_contract(oh, **overrides):
    defaults = dict(
        handoff_id="h-1",
        parent_agent_id="AgentA",
        child_agent_id="AgentB",
        run_id="run-1",
        capability_token="token-abcdefgh1234",
        handoff_reason_hash="rh-hash",
        input_payload_hash="ip-hash",
        policy_hash="pol-hash",
        trace_id="t-1",
    )
    defaults.update(overrides)
    return oh.OrchestrationHandoffContract(**defaults)


class TestContractShape:
    def test_direct_construction(self, oh):
        c = _mk_contract(oh)
        assert c.handoff_id == "h-1"
        assert c.parent_agent_id == "AgentA"
        assert c.child_agent_id == "AgentB"

    def test_is_frozen(self, oh):
        c = _mk_contract(oh)
        with pytest.raises((AttributeError, Exception)):
            c.handoff_id = "h-2"  # type: ignore[misc]

    def test_workflow_stage_defaults_empty(self, oh):
        c = _mk_contract(oh)
        assert c.workflow_stage == ""

    def test_metadata_defaults_empty_dict(self, oh):
        c = _mk_contract(oh)
        assert c.metadata == {}

    def test_created_epoch_is_float(self, oh):
        c = _mk_contract(oh)
        assert isinstance(c.created_epoch, float)


# --------------------------------------------------------------------------- #
# Factory: OrchestrationHandoffContract.create                                #
# --------------------------------------------------------------------------- #


class TestCreateFactory:
    """Every create() call passes an explicit trace_id.

    PRODUCTION BUG (see TestKnownBugs): calling create() with empty trace_id
    crashes because the fallback import path `agentic_core.runtime.trace_context`
    does not exist (real path has `.utils.`), and the except clause does not
    include ImportError. Tests here all pass trace_id explicitly to avoid
    exercising the broken fallback.
    """

    def test_basic_factory_call(self, oh):
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="AgentA",
            child_agent_id="AgentB",
            run_id="run-42",
            capability_token="cap-token-123",
            handoff_reason="delegate validation",
            input_payload={"k": "v"},
            policy_hash="pol-hash",
            trace_id="trace-basic",
        )
        assert c.parent_agent_id == "AgentA"
        assert c.child_agent_id == "AgentB"
        assert c.run_id == "run-42"
        assert c.policy_hash == "pol-hash"

    def test_handoff_id_is_24_hex(self, oh):
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="reason",
            input_payload={}, policy_hash="p", trace_id="t-hid",
        )
        assert len(c.handoff_id) == 24
        assert all(ch in "0123456789abcdef" for ch in c.handoff_id)

    def test_reason_hash_matches_sha256_16(self, oh):
        reason = "delegate to child agent"
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason=reason,
            input_payload="payload", policy_hash="p", trace_id="t-rhash",
        )
        expected = hashlib.sha256(reason.encode()).hexdigest()[:16]
        assert c.handoff_reason_hash == expected

    def test_input_payload_hash_matches_sha256_16(self, oh):
        payload = {"key": "value", "nested": [1, 2, 3]}
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload=payload, policy_hash="p", trace_id="t-phash",
        )
        expected = hashlib.sha256(str(payload).encode()).hexdigest()[:16]
        assert c.input_payload_hash == expected

    def test_explicit_trace_id_preserved(self, oh):
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload={}, policy_hash="p",
            trace_id="trace-abc-123",
        )
        assert c.trace_id == "trace-abc-123"

    def test_metadata_none_becomes_empty_dict(self, oh):
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload={}, policy_hash="p", trace_id="t-meta",
            metadata=None,
        )
        assert c.metadata == {}

    def test_metadata_passed_through(self, oh):
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload={}, policy_hash="p", trace_id="t-mpass",
            metadata={"key": "val", "n": 1},
        )
        assert c.metadata == {"key": "val", "n": 1}

    def test_workflow_stage_passed_through(self, oh):
        c = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload={}, policy_hash="p", trace_id="t-ws",
            workflow_stage="preflight",
        )
        assert c.workflow_stage == "preflight"

    def test_reason_hash_differs_with_reason(self, oh):
        a = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="reason-1",
            input_payload={}, policy_hash="p", trace_id="t-rd1",
        )
        b = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="reason-2",
            input_payload={}, policy_hash="p", trace_id="t-rd2",
        )
        assert a.handoff_reason_hash != b.handoff_reason_hash

    def test_payload_hash_differs_with_payload(self, oh):
        a = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload={"a": 1}, policy_hash="p", trace_id="t-pd1",
        )
        b = oh.OrchestrationHandoffContract.create(
            parent_agent_id="A", child_agent_id="B", run_id="r",
            capability_token="t", handoff_reason="x",
            input_payload={"a": 2}, policy_hash="p", trace_id="t-pd2",
        )
        assert a.input_payload_hash != b.input_payload_hash


# --------------------------------------------------------------------------- #
# to_dict                                                                     #
# --------------------------------------------------------------------------- #


class TestToDict:
    def test_redacts_capability_token(self, oh):
        c = _mk_contract(oh, capability_token="supersecret-token-12345")
        d = c.to_dict()
        assert d["capability_token"].endswith("...")
        # First 8 chars preserved, rest redacted
        assert d["capability_token"] == "supersec..."
        assert "supersecret-token-12345" not in d["capability_token"]

    def test_short_token_still_truncated(self, oh):
        c = _mk_contract(oh, capability_token="abc")
        d = c.to_dict()
        # Slice [:8] on "abc" returns "abc", then "..." appended
        assert d["capability_token"] == "abc..."

    def test_contains_all_public_fields(self, oh):
        c = _mk_contract(oh)
        d = c.to_dict()
        expected_keys = {
            "handoff_id", "parent_agent_id", "child_agent_id", "run_id",
            "capability_token", "handoff_reason_hash", "input_payload_hash",
            "policy_hash", "trace_id", "workflow_stage", "created_epoch",
        }
        assert set(d.keys()) == expected_keys

    def test_returns_dict_type(self, oh):
        c = _mk_contract(oh)
        assert isinstance(c.to_dict(), dict)


# --------------------------------------------------------------------------- #
# emit_agent_executes_agent (instance method)                                 #
# --------------------------------------------------------------------------- #


class TestInstanceEmit:
    def test_idempotent_no_raise(self, oh):
        c = _mk_contract(oh)
        # Re-emit should be side-effect-logging-only and not raise
        c.emit_agent_executes_agent()
        c.emit_agent_executes_agent()  # idempotent

    def test_returns_none(self, oh):
        c = _mk_contract(oh)
        assert c.emit_agent_executes_agent() is None


# --------------------------------------------------------------------------- #
# Known production bugs — pinned as regression markers                        #
# --------------------------------------------------------------------------- #


class TestKnownBugs:
    """Regression markers for bugs discovered while writing this suite.

    These tests DOCUMENT broken production behavior. When the production code
    is fixed, these will fail and must be updated to reflect the new contract.
    """

    def test_BUG_create_with_empty_trace_id_raises_module_not_found(self, oh):
        """Production bug: the fallback path in create() imports
        `agentic_core.runtime.trace_context` but the real module lives at
        `agentic_core.runtime.utils.trace_context`. Additionally, the except
        clause catches only (ValueError, TypeError, RuntimeError) — missing
        ImportError — so the fallback never recovers.

        Effect: every create() call with empty trace_id (or omitted) raises
        ModuleNotFoundError. The module-level `emit_agent_executes_agent`
        wrapper has no trace_id parameter, so it ALWAYS crashes.

        Fix requires: correcting the import path AND adding ImportError to
        the except clause. Author-Gate required (L3 safety-contract change).
        """
        with pytest.raises(ModuleNotFoundError, match=r"trace_context"):
            oh.OrchestrationHandoffContract.create(
                parent_agent_id="A", child_agent_id="B", run_id="r",
                capability_token="t", handoff_reason="x",
                input_payload={}, policy_hash="p",
                # trace_id omitted -> triggers broken fallback
            )

    def test_BUG_emit_agent_executes_agent_wrapper_always_crashes(self, oh):
        """The module-level convenience wrapper has no trace_id parameter
        and always delegates to create() with default empty trace_id, so
        it always triggers the bug above."""
        with pytest.raises(ModuleNotFoundError, match=r"trace_context"):
            oh.emit_agent_executes_agent("A", "B")
