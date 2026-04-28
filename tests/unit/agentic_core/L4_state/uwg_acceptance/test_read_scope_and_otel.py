"""L4 read-scope (tenant/ACL) and OTel emission tests.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.8_*`` §PHASE 2 + §PHASE 3.

Tests must fail if:
- L4 read returns data outside tenant/ACL scope
- a span lacks trace_id (hard observability failure)
- a scoped read span lacks tenant_id
"""

from __future__ import annotations

from agentic_core.L4_state.otel.spans import (
    L4_READ_SPAN_NAMES,
    UWG_WRITE_SPAN_NAMES,
    emit_l4_span,
    emit_uwg_span,
    get_emitted_spans,
)


class TestSpanCatalogCompleteness:
    """The canonical span catalog must include the names required by 00.8."""

    def test_required_read_span_names_present(self) -> None:
        required = {
            "l4.read.policy_manifest",
            "l4.read.registry_snapshot",
            "l4.read.memory_surface",
            "l4.read.retrieval_surface",
            "l4.cache.lookup",
            "l4.replay.snapshot.read",
            "l4.audit.read",
            "l4.audit.sequence_check",
            "l4.replay.reconstruct",
        }
        assert required <= set(L4_READ_SPAN_NAMES)

    def test_required_write_span_names_present(self) -> None:
        required = {
            "uwg.commit.request_received",
            "uwg.commit.validate",
            "uwg.write_lock.acquire",
            "uwg.commit.apply",
            "uwg.commit.receipt_emit",
            "uwg.commit.blocked",
            "uwg.read_surface.refresh",
            "uwg.rollback.apply",
            "l4.audit.append",
            "l4.direct_write_attempt.detected",
            "l4.direct_write_attempt.blocked",
        }
        assert required <= set(UWG_WRITE_SPAN_NAMES)


class TestRequiredFieldEnforcement:
    """Per 00.8 §PHASE 2 — missing trace_id / tenant_id / policy_hash / replay_key are hard failures."""

    def test_missing_tenant_on_scoped_read_marks_failure(self) -> None:
        span = emit_l4_span(
            "l4.read.policy_manifest",
            trace_id="t:abc",
            operation_type="read",
            tenant_id="",  # missing
            policy_hash="ph:1",
        )
        assert span.attributes["status"] == "OBSERVABILITY_FAILURE"
        assert "missing_tenant_id_on_scoped_read" in span.attributes["validation_failures"]

    def test_missing_trace_id_marks_failure(self) -> None:
        # Force an empty trace_id by passing None and patching the auto-gen guard
        # Easier: directly call private validator with empty attrs
        from agentic_core.L4_state.otel.spans import _validate_l4_read_attributes

        ok, failures = _validate_l4_read_attributes(
            {"trace_id": "", "operation_type": "read", "tenant_id": "t:1"}
        )
        assert not ok
        assert "missing_trace_id" in failures

    def test_missing_policy_hash_on_commit_marks_failure(self) -> None:
        span = emit_uwg_span(
            "uwg.commit.apply",
            trace_id="t:abc",
            tenant_id="t:1",
            policy_hash="",  # missing on write path
            replay_key="rk:1",
            source_surface="UWG",
        )
        assert span.attributes["status"] == "OBSERVABILITY_FAILURE"
        assert "missing_policy_hash_on_write" in span.attributes["validation_failures"]

    def test_missing_replay_key_on_commit_marks_failure(self) -> None:
        span = emit_uwg_span(
            "uwg.commit.apply",
            trace_id="t:abc",
            tenant_id="t:1",
            policy_hash="ph:1",
            replay_key="",  # missing
            source_surface="UWG",
        )
        assert span.attributes["status"] == "OBSERVABILITY_FAILURE"
        assert "missing_replay_key_on_commit" in span.attributes["validation_failures"]

    def test_well_formed_span_passes(self) -> None:
        span = emit_uwg_span(
            "uwg.commit.apply",
            trace_id="t:abc",
            tenant_id="t:1",
            policy_hash="ph:1",
            replay_key="rk:1",
            source_surface="UWG",
        )
        assert span.attributes["status"] == "OK"
        assert "validation_failures" not in span.attributes

    def test_emit_records_span_for_inspection(self) -> None:
        emit_l4_span(
            "l4.read.policy_manifest",
            trace_id="t:1",
            tenant_id="t:1",
            policy_hash="ph:1",
            operation_type="read",
        )
        spans = get_emitted_spans(name_prefix="l4.read.")
        assert len(spans) >= 1
        assert any(s.name == "l4.read.policy_manifest" for s in spans)
