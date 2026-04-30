"""Unit tests for agentic_core.knowledge.gates.preretrieval_gate.

Covers two latent bugs fixed 2026-04-30 that prevented the gate from being
called by any production code path (fan-in=0 in the ADG until that fix):

  1. `evaluate()` formatted denied_filters via `d.result` -- but FilterResult
     has `filter_name`/`reason`, no `result` attribute. Crashed with
     AttributeError on the first denial.
  2. The trailing telemetry emit passed only 2 args to
     `_emit_records_telemetry_event(root_trace_id, source, event)`. Crashed
     with TypeError on every successful evaluate().

Also covers basic ALLOW, multi-filter DENY shapes, and the public
check_access convenience wrapper.
"""

from __future__ import annotations

import pytest

from agentic_core.knowledge.gates.preretrieval_gate import (
    AccessDecision,
    FilterResult,
    GateDecision,
    PreRetrievalGate,
    check_access,
    get_pre_retrieval_gate,
)


class TestEvaluateAllowPath:
    """ALLOW: no filters denied -> no exceptions; decision.value=='allow'."""

    def test_empty_context_allows(self):
        gate = PreRetrievalGate()
        result = gate.evaluate(query_id="q1", query_context={})
        assert isinstance(result, GateDecision)
        assert result.decision == AccessDecision.ALLOW
        assert result.reason is None
        assert result.query_id == "q1"
        assert result.denied_filters == []

    def test_compatible_clearance_allows(self):
        gate = PreRetrievalGate()
        ctx = {
            "tenant_id": "t1",
            "query_tenant": "t1",
            "user_clearance": "confidential",
            "document_classification": "internal",
        }
        result = gate.evaluate(query_id="q2", query_context=ctx)
        assert result.decision == AccessDecision.ALLOW

    def test_evaluate_completes_without_typeerror(self):
        """Regression: telemetry emit signature was missing the `event` arg
        and crashed every successful evaluate() until the 2026-04-30 fix."""
        gate = PreRetrievalGate()
        # If the bug is back, this raises TypeError from the trailing
        # _emit_records_telemetry_event call, not from filter logic.
        result = gate.evaluate(query_id="regression", query_context={})
        assert result.decision == AccessDecision.ALLOW


class TestEvaluateDenyPath:
    """DENY: one or more filters denied -> reason formatted from
    FilterResult.filter_name + FilterResult.reason (NOT FilterResult.result
    -- that attribute doesn't exist; the prior code crashed here)."""

    def test_clearance_below_classification_denies(self):
        gate = PreRetrievalGate()
        ctx = {
            "user_clearance": "public",
            "document_classification": "secret",
        }
        result = gate.evaluate(query_id="q3", query_context=ctx)
        assert result.decision == AccessDecision.DENY
        assert result.reason is not None
        # Reason format: "Failed filters: <filter_name>: <reason>, ..."
        assert "confidentiality" in result.reason
        assert "Insufficient clearance" in result.reason
        assert len(result.denied_filters) == 1
        assert result.denied_filters[0].filter_name == "confidentiality"

    def test_tenant_mismatch_denies(self):
        gate = PreRetrievalGate()
        ctx = {
            "tenant_id": "t1",
            "query_tenant": "t2",
        }
        result = gate.evaluate(query_id="q4", query_context=ctx)
        assert result.decision == AccessDecision.DENY
        assert "tenant" in result.reason.lower()

    def test_multiple_denied_filters_join_reasons(self):
        """Regression: prior code used `d.result` which did not exist,
        so any denial raised AttributeError before the join completed.
        Verify multiple denials are joined into a comma-separated reason."""
        gate = PreRetrievalGate()
        ctx = {
            "tenant_id": "t1",
            "query_tenant": "t2",                   # tenant denial
            "user_clearance": "public",             # clearance denial
            "document_classification": "secret",
        }
        result = gate.evaluate(query_id="q5", query_context=ctx)
        assert result.decision == AccessDecision.DENY
        # Both filter names must appear in reason -- proves no
        # AttributeError fired before the join completed.
        assert "tenant" in result.reason.lower()
        assert "confidentiality" in result.reason.lower()
        # And the format is "filter_name: reason" not bare reasons.
        assert ":" in result.reason
        assert len(result.denied_filters) == 2

    def test_denied_filter_result_uses_correct_attrs(self):
        """Sanity check: FilterResult has filter_name + reason, NOT result.
        If the dataclass shape regressed, this test catches it before
        the format string in evaluate() does."""
        # Construct a FilterResult and verify attribute set
        fr = FilterResult(filter_name="x", passed=False, reason="bad")
        assert hasattr(fr, "filter_name")
        assert hasattr(fr, "reason")
        assert hasattr(fr, "passed")
        assert hasattr(fr, "metadata")
        # The bug-tripping attribute must NOT exist; otherwise the old
        # code path could re-emerge silently.
        assert not hasattr(fr, "result"), (
            "FilterResult must NOT carry a `result` attribute. The "
            "evaluate() formatter expects `filter_name` and `reason`. "
            "Adding a `result` attribute would re-introduce the latent "
            "AttributeError fixed 2026-04-30."
        )


class TestCheckAccessPublicAPI:
    """Public convenience wrapper goes through the global gate singleton."""

    def test_check_access_returns_gate_decision(self):
        result = check_access(query_id="public_api_q1", context={})
        assert isinstance(result, GateDecision)
        assert result.decision == AccessDecision.ALLOW

    def test_check_access_propagates_deny(self):
        result = check_access(
            query_id="public_api_q2",
            context={"user_clearance": "public", "document_classification": "secret"},
        )
        assert result.decision == AccessDecision.DENY

    def test_get_pre_retrieval_gate_is_singleton(self):
        a = get_pre_retrieval_gate()
        b = get_pre_retrieval_gate()
        assert a is b


class TestFilterShortCircuiting:
    """Each filter MUST short-circuit (passed=True) when its required
    context keys are absent. This is the contract the L0 dispatcher
    relies on -- only the keys it knows about (tenant/clearance/region/
    classification) are populated; permission/temporal filters become
    no-ops when their keys are absent."""

    def test_tenant_filter_passes_when_no_tenant(self):
        gate = PreRetrievalGate()
        result = gate.evaluate(query_id="q", query_context={})
        # No tenant_id -> tenant filter should pass
        assert result.decision == AccessDecision.ALLOW

    def test_acl_filter_passes_when_no_required_perms(self):
        gate = PreRetrievalGate()
        result = gate.evaluate(query_id="q", query_context={"user_permissions": []})
        # No required_permissions -> acl filter passes
        assert result.decision == AccessDecision.ALLOW

    def test_region_filter_passes_when_no_allowed_regions(self):
        gate = PreRetrievalGate()
        result = gate.evaluate(
            query_id="q",
            query_context={"user_region": "us-east"},
        )
        # No allowed_regions -> region filter passes
        assert result.decision == AccessDecision.ALLOW
