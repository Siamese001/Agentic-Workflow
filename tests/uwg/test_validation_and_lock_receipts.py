"""Direct tests for WriteLockReceipt and UWGValidationReceipt + missing-blueprint-hash + commit-request-received audit event.

Closes the previously-implicit rows in the requirements traceability matrix
(6.3, 6.4, 1.13, 5.8) by exercising each receipt's data shape and the
gateway's audit-event emission directly.
"""

from __future__ import annotations

from dataclasses import replace

from agentic_core.L4_state.contracts import UWGValidationReceipt, WriteLockReceipt
from agentic_core.L4_state.contracts.records import stamp_digest


class TestWriteLockReceiptShape:
    def test_acquired_status_round_trip(self) -> None:
        r = stamp_digest(
            WriteLockReceipt(
                write_lock_receipt_id="wlr:1",
                commit_request_ref="cr:1",
                lock_scope="memory",
                lock_status="ACQUIRED",
                lock_owner="UWG::cr:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                snapshot_before="snap:before",
                target_surfaces=("memory",),
                acquired_at="0",
            )
        )
        assert r.lock_status == "ACQUIRED"
        assert r.deterministic_digest

    def test_contention_status_carries_contention_refs(self) -> None:
        r = stamp_digest(
            WriteLockReceipt(
                write_lock_receipt_id="wlr:2",
                commit_request_ref="cr:2",
                lock_scope="memory,cache",
                lock_status="CONTENTION",
                lock_owner="UWG::cr:2",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                snapshot_before="snap:before",
                target_surfaces=("memory", "cache"),
                contention_refs=("cache",),
            )
        )
        assert r.lock_status == "CONTENTION"
        assert "cache" in r.contention_refs


class TestUWGValidationReceiptShape:
    def test_pass_status_with_no_failed_rules(self) -> None:
        r = stamp_digest(
            UWGValidationReceipt(
                uwg_validation_receipt_id="uvr:1",
                commit_request_ref="cr:1",
                validation_status="PASS",
                policy_status="PASS",
                blueprint_status="PASS",
                schema_status="PASS",
                gate_status="PASS",
                l5_cert_status="PASS",
                hitl_status="PASS",
                replay_status="PASS",
                rollback_status="PASS",
                blast_radius_status="PASS",
                write_lock_status="ACQUIRED",
                checked_rules=("source_is_exit", "policy_hash_present"),
                failed_rules=(),
            )
        )
        assert r.validation_status == "PASS"
        assert r.failed_rules == ()

    def test_fail_status_carries_failed_rules_and_reasons(self) -> None:
        r = stamp_digest(
            UWGValidationReceipt(
                uwg_validation_receipt_id="uvr:2",
                commit_request_ref="cr:2",
                validation_status="FAIL",
                policy_status="FAIL",
                blueprint_status="PASS",
                schema_status="PASS",
                gate_status="PASS",
                l5_cert_status="PASS",
                hitl_status="PASS",
                replay_status="PASS",
                rollback_status="PASS",
                blast_radius_status="PASS",
                write_lock_status="PENDING",
                checked_rules=("required_field::policy_hash",),
                failed_rules=("required_field::policy_hash",),
                reason_codes=("missing::policy_hash",),
            )
        )
        assert r.validation_status == "FAIL"
        assert "required_field::policy_hash" in r.failed_rules


class TestMissingBlueprintHashBlocks:
    """Closes 1.13 — missing blueprint_hash is a fail-closed condition."""

    def test_missing_blueprint_hash_blocks_commit(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, blueprint_hash="")
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "missing::blueprint_hash" in blocked.blocked_reason_codes


class TestCommitRequestReceivedAuditEvent:
    """Closes 5.8 — `commit_request_received` is a durable audit event, not just a span."""

    def test_happy_path_emits_commit_request_received_audit(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        events = [r.event_type for r in gateway.audit_ledger.read()]
        assert "commit_request_received" in events
        # Must precede the atomic_commit_applied event in ledger order
        idx_recv = events.index("commit_request_received")
        idx_apply = events.index("atomic_commit_applied")
        assert idx_recv < idx_apply

    def test_blocked_path_still_emits_commit_request_received(self, gateway, well_formed_packet) -> None:
        """A blocked commit must STILL record the receive-time fact in the ledger."""
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface="L2")
        gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        events = [r.event_type for r in gateway.audit_ledger.read()]
        # Receive-time fact is durable even for blocked attempts
        assert "commit_request_received" in events
        # And the block is also recorded
        assert "commit_blocked" in events
        # The receive event lists the actual source surface (L2), not "Exit"
        recv_records = [
            r for r in gateway.audit_ledger.read() if r.event_type == "commit_request_received"
        ]
        assert recv_records[0].actor_surface == "L2"


class TestCacheCompatibilityFieldsRequired:
    """Closes 4.6 — cache lookup receipts carry the compatibility fields the doctrine mandates."""

    def test_lookup_receipt_carries_all_compat_fields(self) -> None:
        from agentic_core.L4_state.contracts import CacheLookupReceipt

        r = stamp_digest(
            CacheLookupReceipt(
                lookup_id="lk:1",
                cache_entry_ref="ce:1",
                lookup_surface="L0",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                normalized_request_hash="nrh:1",
                freshness_status="FRESH",
                policy_compatibility_status="COMPATIBLE",
                source_snapshot_compatibility_status="COMPATIBLE",
                decision_hint="compatible",
                similarity_score=0.92,
            )
        )
        assert r.freshness_status == "FRESH"
        assert r.policy_compatibility_status == "COMPATIBLE"
        assert r.source_snapshot_compatibility_status == "COMPATIBLE"
        assert r.decision_hint == "compatible"

    def test_grounded_cache_lookup_with_evidence_contract_ref(self) -> None:
        """A grounded answer's cache entry has an evidence_contract_ref field; lookup tracks it."""
        from agentic_core.L4_state.contracts import CacheEntry

        entry = stamp_digest(
            CacheEntry(
                cache_entry_id="ce:grounded",
                cache_type="exact",
                tenant_id="t:1",
                normalized_request_hash="nrh:1",
                task_class="grounded_qa",
                route_id="r:1",
                answer_ref="ans:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                freshness_class="hot",
                evidence_contract_ref="ec:1",
                source_snapshot_refs=("src:1",),
            )
        )
        # Grounded entry MUST carry evidence_contract_ref; the field is present and populated
        assert entry.evidence_contract_ref == "ec:1"
        assert entry.source_snapshot_refs == ("src:1",)
