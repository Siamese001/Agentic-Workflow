"""Exhaustive L4 edge-case sweep across all 8 doctrinal documents.

Goes beyond shape-tests: exercises every enum value, every boundary,
every fail-closed branch, and every digest determinism property.
"""

from __future__ import annotations

import threading
from dataclasses import replace
from typing import List

import pytest

from agentic_core.L4_state.audit.audit_ledger import (
    AuditLedger,
    AuditLedgerSequenceGapError,
)
from agentic_core.L4_state.contracts import (
    AliasResolutionError,
    BlueprintRecord,
    CacheEntry,
    CacheInvalidationReceipt,
    CacheLookupReceipt,
    CapabilityRegistryRecord,
    DeprecatedEntryError,
    ExactCacheEntry,
    InMemoryL4Store,
    ModelRegistryRecord,
    PolicyManifest,
    ReadSurfaceRefreshReceipt,
    RegistrySnapshot,
    ReplaySnapshotRecord,
    SchemaRegistryRecord,
    SemanticCacheEntry,
    StateDiff,
    TenantScopeError,
    ToolRegistryRecord,
    UnknownEntryError,
    UWGCommitReceipt,
    canonical_json_dumps,
    compute_deterministic_digest,
    get_default_store,
    reset_default_store,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.refresh.refresh_coordinator import (
    REFRESH_ORDER,
    RefreshCoordinator,
    RefreshExecutionError,
)


# =====================================================================
# 00.1 — Record digest determinism + immutability boundaries
# =====================================================================


class TestDigestDeterminism:
    def test_canonical_json_is_sorted_and_compact(self) -> None:
        """canonical_json_dumps MUST sort keys and use compact separators."""
        a = canonical_json_dumps({"b": 1, "a": 2})
        b = canonical_json_dumps({"a": 2, "b": 1})
        assert a == b
        assert " " not in a  # compact separators
        assert a == '{"a":2,"b":1}'

    def test_digest_changes_when_field_changes(self) -> None:
        a = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:1")
        )
        b = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v2", policy_hash="ph:1")
        )
        assert a.deterministic_digest != b.deterministic_digest

    def test_digest_stable_for_nested_tuples(self) -> None:
        """Nested tuple ordering must be preserved exactly."""
        rec_a = stamp_digest(
            ModelRegistryRecord(
                model_id="m:1",
                provider_id="p:1",
                provider_lane="lane:1",
                context_limit=8192,
                tool_calling_capability=True,
                structured_output_capability=True,
                egress_class="none",
                data_retention_class="zero",
                deprecation_state="active",
                fallback_policy_ref="fp:1",
                allowed_risk_tiers=("low", "medium", "high"),
            )
        )
        rec_b = stamp_digest(
            ModelRegistryRecord(
                model_id="m:1",
                provider_id="p:1",
                provider_lane="lane:1",
                context_limit=8192,
                tool_calling_capability=True,
                structured_output_capability=True,
                egress_class="none",
                data_retention_class="zero",
                deprecation_state="active",
                fallback_policy_ref="fp:1",
                allowed_risk_tiers=("low", "medium", "high"),
            )
        )
        assert rec_a.deterministic_digest == rec_b.deterministic_digest

    def test_digest_differs_when_tuple_order_differs(self) -> None:
        """Tuples are sequence-typed: order is part of identity (NOT a set)."""
        rec_a = stamp_digest(
            ModelRegistryRecord(
                model_id="m:1",
                provider_id="p:1",
                provider_lane="lane:1",
                context_limit=8192,
                tool_calling_capability=True,
                structured_output_capability=True,
                egress_class="none",
                data_retention_class="zero",
                deprecation_state="active",
                fallback_policy_ref="fp:1",
                allowed_risk_tiers=("low", "high"),
            )
        )
        rec_b = stamp_digest(
            ModelRegistryRecord(
                model_id="m:1",
                provider_id="p:1",
                provider_lane="lane:1",
                context_limit=8192,
                tool_calling_capability=True,
                structured_output_capability=True,
                egress_class="none",
                data_retention_class="zero",
                deprecation_state="active",
                fallback_policy_ref="fp:1",
                allowed_risk_tiers=("high", "low"),
            )
        )
        assert rec_a.deterministic_digest != rec_b.deterministic_digest

    def test_compute_deterministic_digest_idempotent(self) -> None:
        payload = {"a": 1, "b": [1, 2, 3], "c": {"nested": True}}
        d1 = compute_deterministic_digest(payload)
        d2 = compute_deterministic_digest(payload)
        assert d1 == d2
        assert len(d1) == 64  # SHA-256 hex


class TestRecordImmutability:
    def test_frozen_dataclass_rejects_mutation(self) -> None:
        pm = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:1")
        )
        with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError subtype
            pm.policy_hash = "ph:HIJACKED"  # type: ignore[misc]

    def test_replace_returns_new_instance_with_new_digest(self) -> None:
        pm = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:1")
        )
        pm2 = stamp_digest(replace(pm, policy_hash="ph:2", deterministic_digest=""))
        assert pm.deterministic_digest != pm2.deterministic_digest
        assert pm.policy_hash == "ph:1"  # original unchanged


# =====================================================================
# 00.1 — Lookup API exhaustive edge cases
# =====================================================================


class TestLookupAPIBoundaries:
    def test_deprecated_schema_fails_closed(self) -> None:
        store = InMemoryL4Store()
        store.install_schema(
            stamp_digest(
                SchemaRegistryRecord(
                    schema_id="sch:1",
                    schema_version="1",
                    schema_hash="sh:1",
                    contract_type="output",
                    owner_surface="L2",
                    backward_compatibility="strict",
                    deprecation_state="deprecated",
                )
            )
        )
        with pytest.raises(DeprecatedEntryError):
            store.resolve_schema(
                schema_id="sch:1", schema_version="1", policy_hash="ph:1"
            )

    def test_deprecated_tool_fails_closed(self) -> None:
        store = InMemoryL4Store()
        store.install_tool(
            stamp_digest(
                ToolRegistryRecord(
                    tool_id="tl:1",
                    tool_version="1.0",
                    tool_provider="prov:1",
                    input_schema_ref="sch:in@1",
                    output_schema_ref="sch:out@1",
                    side_effect_class="read",
                    sandbox_class_required="basic",
                    credential_scope="none",
                    network_scope="none",
                    egress_policy_ref="egress:none",
                    deprecation_state="deprecated",
                )
            )
        )
        with pytest.raises(DeprecatedEntryError):
            store.resolve_allowed_tool(
                tool_id="tl:1", route_id="r:1", capability_id="cap:1", policy_hash="ph:1"
            )

    def test_tool_with_empty_allowed_route_ids_accepts_any_route(self) -> None:
        """Doctrine 00.1: empty allowed_route_ids = no route restriction."""
        store = InMemoryL4Store()
        store.install_tool(
            stamp_digest(
                ToolRegistryRecord(
                    tool_id="tl:wide",
                    tool_version="1.0",
                    tool_provider="prov:1",
                    input_schema_ref="sch:in@1",
                    output_schema_ref="sch:out@1",
                    side_effect_class="read",
                    sandbox_class_required="basic",
                    credential_scope="none",
                    network_scope="none",
                    egress_policy_ref="egress:none",
                    deprecation_state="active",
                    allowed_route_ids=(),  # empty = any route
                )
            )
        )
        store.install_capability(
            stamp_digest(
                CapabilityRegistryRecord(
                    capability_id="cap:wide",
                    capability_class="read",
                    side_effect_class="none",
                    sandbox_required=False,
                    egress_policy_ref="egress:none",
                    deprecation_state="active",
                    allowed_tools=("tl:wide",),
                )
            )
        )
        # Any route_id should resolve
        for route in ("r:any1", "r:any2", "r:third"):
            tool = store.resolve_allowed_tool(
                tool_id="tl:wide", route_id=route, capability_id="cap:wide", policy_hash="ph:1"
            )
            assert tool.tool_id == "tl:wide"

    def test_capability_excludes_tool_fails_closed(self) -> None:
        store = InMemoryL4Store()
        store.install_tool(
            stamp_digest(
                ToolRegistryRecord(
                    tool_id="tl:active",
                    tool_version="1.0",
                    tool_provider="prov:1",
                    input_schema_ref="sch:in@1",
                    output_schema_ref="sch:out@1",
                    side_effect_class="read",
                    sandbox_class_required="basic",
                    credential_scope="none",
                    network_scope="none",
                    egress_policy_ref="egress:none",
                    deprecation_state="active",
                    allowed_route_ids=("r:1",),
                )
            )
        )
        store.install_capability(
            stamp_digest(
                CapabilityRegistryRecord(
                    capability_id="cap:strict",
                    capability_class="read",
                    side_effect_class="none",
                    sandbox_required=False,
                    egress_policy_ref="egress:none",
                    deprecation_state="active",
                    allowed_tools=("tl:OTHER",),  # tool not in this capability
                )
            )
        )
        with pytest.raises(UnknownEntryError, match="not in capability"):
            store.resolve_allowed_tool(
                tool_id="tl:active",
                route_id="r:1",
                capability_id="cap:strict",
                policy_hash="ph:1",
            )

    def test_default_store_singleton_semantics(self) -> None:
        a = get_default_store()
        b = get_default_store()
        assert a is b
        # Reset gives a fresh instance
        reset_default_store()
        c = get_default_store()
        assert c is not a

    def test_concurrent_reads_do_not_deadlock(self) -> None:
        """Read APIs are thread-safe; many concurrent reads complete."""
        store = InMemoryL4Store()
        pm = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:1")
        )
        store.install_policy(pm, tenant_id="t:1", route_id="r:1", risk_tier="medium")

        results: List[bool] = []

        def reader() -> None:
            try:
                resolved = store.get_active_policy_manifest(
                    tenant_id="t:1", route_id="r:1", risk_tier="medium"
                )
                results.append(resolved.policy_hash == "ph:1")
            except Exception:  # guardian: allow-broad -- test-only thread-safety probe
                results.append(False)

        threads = [threading.Thread(target=reader) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=2.0)
            assert not t.is_alive(), "reader thread deadlocked"
        assert all(results)
        assert len(results) == 20

    def test_repeated_install_overwrites(self) -> None:
        store = InMemoryL4Store()
        pm_v1 = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:v1")
        )
        pm_v2 = stamp_digest(
            PolicyManifest(policy_manifest_id="pm:1", policy_version="v2", policy_hash="ph:v2")
        )
        store.install_policy(pm_v1, tenant_id="t:1", route_id="r:1", risk_tier="medium")
        store.install_policy(pm_v2, tenant_id="t:1", route_id="r:1", risk_tier="medium")
        # Last write wins
        resolved = store.get_active_policy_manifest(
            tenant_id="t:1", route_id="r:1", risk_tier="medium"
        )
        assert resolved.policy_hash == "ph:v2"


# =====================================================================
# 00.4 — Cache exhaustive edge cases
# =====================================================================


class TestCacheBoundaries:
    @pytest.mark.parametrize("freshness", ["FRESH", "WARM", "STALE", "EXPIRED"])
    def test_all_freshness_status_values_round_trip(self, freshness) -> None:
        r = stamp_digest(
            CacheLookupReceipt(
                lookup_id="lk:1",
                cache_entry_ref="ce:1",
                lookup_surface="L0",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                normalized_request_hash="nrh:1",
                freshness_status=freshness,
                policy_compatibility_status="COMPATIBLE",
                source_snapshot_compatibility_status="COMPATIBLE",
                decision_hint="compatible",
                similarity_score=1.0,
            )
        )
        assert r.freshness_status == freshness

    @pytest.mark.parametrize(
        "policy_compat,source_compat,hint",
        [
            ("COMPATIBLE", "COMPATIBLE", "compatible"),
            ("INCOMPATIBLE", "COMPATIBLE", "incompatible_policy"),
            ("COMPATIBLE", "INCOMPATIBLE", "incompatible_source"),
            ("COMPATIBLE", "COMPATIBLE", "stale"),
            ("COMPATIBLE", "COMPATIBLE", "not_found"),
        ],
    )
    def test_decision_hint_combinations_round_trip(
        self, policy_compat, source_compat, hint
    ) -> None:
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
                policy_compatibility_status=policy_compat,
                source_snapshot_compatibility_status=source_compat,
                decision_hint=hint,
                similarity_score=1.0,
            )
        )
        assert r.decision_hint == hint

    def test_exact_cache_entry_round_trip(self) -> None:
        e = stamp_digest(
            ExactCacheEntry(
                cache_entry_id="ce:exact",
                normalized_request_hash="nrh:exact",
                request_shape_hash="rsh:exact",
                answer_ref="ans:1",
                tenant_scope="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                output_schema_ref="sch:out@1",
                freshness_class="hot",
                replay_key="rk:1",
            )
        )
        assert e.normalized_request_hash == "nrh:exact"
        assert e.replay_key == "rk:1"
        assert e.deterministic_digest

    def test_semantic_cache_entry_requires_embedding_model_id(self) -> None:
        # SemanticCacheEntry requires embedding_model_id/version (no defaults)
        with pytest.raises(TypeError):
            SemanticCacheEntry(  # type: ignore[call-arg]
                cache_entry_id="ce:semantic",
                semantic_embedding_ref="emb_ref:1",
                # missing embedding_model_id / embedding_model_version
                task_class="answer",
                answer_ref="ans:1",
                similarity_threshold_profile_ref="thr:1",
                tenant_scope="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                freshness_class="hot",
            )

    def test_semantic_cache_entry_full_construction(self) -> None:
        e = stamp_digest(
            SemanticCacheEntry(
                cache_entry_id="ce:semantic",
                semantic_embedding_ref="emb_ref:1",
                embedding_model_id="emb:bge",
                embedding_model_version="1.5",
                task_class="answer",
                answer_ref="ans:1",
                similarity_threshold_profile_ref="thr:0.92",
                tenant_scope="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                freshness_class="hot",
            )
        )
        assert e.embedding_model_id == "emb:bge"
        assert e.similarity_threshold_profile_ref == "thr:0.92"

    def test_cache_invalidation_receipt_carries_required_lineage(self) -> None:
        r = stamp_digest(
            CacheInvalidationReceipt(
                invalidation_id="inv:1",
                reason_code="policy_rotation",
                before_snapshot="snap:0",
                after_snapshot="snap:1",
                affected_cache_refs=("ce:a", "ce:b", "ce:c"),
                source_commit_receipt_ref="cr:1",
            )
        )
        assert len(r.affected_cache_refs) == 3
        assert r.reason_code == "policy_rotation"


# =====================================================================
# 00.5 — Audit ledger exhaustive edge cases
# =====================================================================


class TestAuditLedgerEdgeCases:
    @staticmethod
    def _append(ledger: AuditLedger, **kwargs):
        """Append helper that returns the record (audit_ledger.append returns (record, receipt))."""
        defaults = dict(
            event_type="atomic_commit_applied",
            state_surface="memory",
            operation_type="commit",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            snapshot_before="snap:0",
            snapshot_after="snap:1",
            actor_surface="UWG",
            mutation_source="Exit",
        )
        defaults.update(kwargs)
        record, _receipt = ledger.append(**defaults)
        return record

    def test_long_sequence_preserves_monotonic_order(self) -> None:
        ledger = AuditLedger()
        for i in range(100):
            self._append(
                ledger, snapshot_before=f"snap:{i}", snapshot_after=f"snap:{i+1}"
            )
        records = ledger.read()
        assert len(records) == 100
        seqs = [r.ledger_sequence for r in records]
        assert seqs == sorted(seqs)
        assert seqs[0] == 1
        assert seqs[-1] == 100

    def test_supersedes_ref_chain_two_corrections(self) -> None:
        """Correction-of-correction: append-only, all three records remain readable."""
        ledger = AuditLedger()
        a = self._append(ledger, snapshot_after="snap:1")
        b = self._append(
            ledger,
            snapshot_after="snap:1_corrected",
            supersedes_ref=a.audit_record_id,
        )
        c = self._append(
            ledger,
            snapshot_after="snap:1_re_corrected",
            supersedes_ref=b.audit_record_id,
        )
        records = ledger.read()
        assert len(records) == 3  # all three preserved
        # Chain: c.supersedes_ref == b.id, b.supersedes_ref == a.id
        # (records[0] has None per dataclass default for Optional[str])
        assert records[1].supersedes_ref == a.audit_record_id
        assert records[2].supersedes_ref == b.audit_record_id
        assert c.supersedes_ref == b.audit_record_id

    def test_read_returned_list_mutation_does_not_affect_ledger(self) -> None:
        """Append-only invariant: even if read() returns a list copy, mutating it does NOT remove records."""
        ledger = AuditLedger()
        for _ in range(3):
            self._append(ledger)
        snapshot1 = ledger.read()
        snapshot1.clear()  # mutate the returned reference
        snapshot2 = ledger.read()
        assert len(snapshot2) == 3, "ledger state must be unaffected by external list mutation"

    def test_sequence_gap_message_includes_position_and_expected_sequence(self) -> None:
        """Doctrine 00.5 §PHASE 4: gap detection must name position + expected sequence."""
        ledger = AuditLedger()
        for _ in range(3):
            self._append(ledger)
        # Surgically inject a gap by direct mutation (fault-injection for the gap-detection test)
        ledger._records[2] = replace(  # noqa: SLF001
            ledger._records[2], ledger_sequence=999
        )
        with pytest.raises(AuditLedgerSequenceGapError, match=r"position 2.*sequence 999"):
            ledger.sequence_check()


# =====================================================================
# 00.7 — Refresh exhaustive edge cases
# =====================================================================


class TestRefreshEdgeCases:
    def test_refresh_order_has_canonical_12_entries(self) -> None:
        assert len(REFRESH_ORDER) == 12
        # First entries are policy/schema/registry aliases (doctrine 00.7 §PHASE 3)
        first_three = REFRESH_ORDER[:3]
        assert all("alias" in e for e in first_three)

    @pytest.mark.parametrize("alias_type", ["policy", "registry", "route"])
    def test_each_alias_type_emits_receipt(self, alias_type) -> None:
        coord = RefreshCoordinator()
        commit = stamp_digest(
            UWGCommitReceipt(
                commit_receipt_id="cr:proof",
                commit_request_ref="creq:proof",
                write_lock_receipt_ref="wlr:proof",
                uwg_validation_receipt_ref="uvr:proof",
                snapshot_before="snap:before",
                snapshot_after="snap:after",
                read_surface_refresh_plan_ref="rfp:proof",
                audit_append_receipt_ref="aar:proof",
                committed_at="0",
            )
        )
        r = coord.issue_alias_refresh(
            alias_type=alias_type,
            commit_receipt=commit,
            alias_before="alias:old",
            alias_after="alias:new",
            target_record_ref="rec:1",
        )
        assert r.alias_type == alias_type

    @pytest.mark.parametrize("index_type", ["vector", "sparse", "metadata"])
    def test_each_index_type_emits_receipt(self, index_type) -> None:
        coord = RefreshCoordinator()
        commit = stamp_digest(
            UWGCommitReceipt(
                commit_receipt_id="cr:proof",
                commit_request_ref="creq:proof",
                write_lock_receipt_ref="wlr:proof",
                uwg_validation_receipt_ref="uvr:proof",
                snapshot_before="snap:before",
                snapshot_after="snap:after",
                read_surface_refresh_plan_ref="rfp:proof",
                audit_append_receipt_ref="aar:proof",
                committed_at="0",
            )
        )
        r = coord.issue_index_refresh(
            index_type=index_type,
            commit_receipt=commit,
            source_snapshot_before="src:before",
            source_snapshot_after="src:after",
        )
        assert r.index_type == index_type

    def test_failed_refresh_status_round_trip(self) -> None:
        """ReadSurfaceRefreshReceipt MUST accept FAILED status and surface it."""
        r = stamp_digest(
            ReadSurfaceRefreshReceipt(
                refresh_receipt_id="rrr:1",
                refresh_plan_ref="rfp:1",
                source_commit_receipt_ref="cr:1",
                state_surface="vector_index",
                refresh_type="vector_index",
                before_snapshot="snap:before",
                status="FAILED",
                retry_count=3,
                started_at="0",
                after_snapshot="snap:before",  # no progress on FAILED
                reason_codes=("vector_rebuild_timeout",),
            )
        )
        assert r.status == "FAILED"
        assert "vector_rebuild_timeout" in r.reason_codes

    def test_graph_projection_with_multiple_source_snapshot_refs_preserved(self) -> None:
        coord = RefreshCoordinator()
        commit = stamp_digest(
            UWGCommitReceipt(
                commit_receipt_id="cr:proof",
                commit_request_ref="creq:proof",
                write_lock_receipt_ref="wlr:proof",
                uwg_validation_receipt_ref="uvr:proof",
                snapshot_before="snap:before",
                snapshot_after="snap:after",
                read_surface_refresh_plan_ref="rfp:proof",
                audit_append_receipt_ref="aar:proof",
                committed_at="0",
            )
        )
        refs = ("src:1", "src:2", "src:3", "src:4", "src:5")
        r = coord.issue_graph_projection_refresh(
            commit_receipt=commit,
            graph_projection_before="gp:before",
            projection_version_before="pv:1",
            relation_type_manifest_ref="rtm:1",
            source_snapshot_refs=refs,
        )
        assert r.source_snapshot_refs == refs


# =====================================================================
# 00.5 — Replay snapshot exhaustive edge cases
# =====================================================================


class TestReplaySnapshotEdgeCases:
    def _full_replay_snapshot(self) -> ReplaySnapshotRecord:
        return stamp_digest(
            ReplaySnapshotRecord(
                replay_snapshot_id="rsn:1",
                trace_root="trace:1",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                replay_key="rk:1",
                snapshot_id="snap:1",
                normalized_request_hash="nrh:1",
                input_hash="ih:1",
                prompt_hash="pmh:1",
                route_digest="rd:1",
                evidence_contract_hash="ech:1",
                sealed_artifact_hash="sah:1",
                gate_verdict_hashes=("gvh:1", "gvh:2"),
                exit_disposition_hash="edh:1",
                commit_receipt_hash="crh:1",
            )
        )

    def test_full_record_digest_stable_across_two_constructions(self) -> None:
        a = self._full_replay_snapshot()
        b = self._full_replay_snapshot()
        assert a.deterministic_digest == b.deterministic_digest

    @pytest.mark.parametrize(
        "field",
        [
            "normalized_request_hash",
            "input_hash",
            "prompt_hash",
            "route_digest",
            "evidence_contract_hash",
            "policy_hash",
            "blueprint_hash",
            "sealed_artifact_hash",
            "exit_disposition_hash",
            "commit_receipt_hash",
        ],
    )
    def test_each_stable_hash_field_change_alters_digest(self, field) -> None:
        """Each of the 12 stable hash inputs is part of the digest identity."""
        original = self._full_replay_snapshot()
        # Re-stamp with replaced field
        mutated = stamp_digest(
            replace(original, **{field: f"{field}:mutated"}, deterministic_digest="")
        )
        assert original.deterministic_digest != mutated.deterministic_digest, (
            f"changing {field} did not alter digest — replay reconstruction is broken"
        )


# =====================================================================
# 00.6 — State diff target_surface exhaustive
# =====================================================================


class TestStateDiffSurfaceCoverage:
    """Each canonical state surface name is acceptable as target_surface."""

    @pytest.mark.parametrize(
        "surface",
        [
            "memory",
            "cache",
            "policy",
            "blueprint",
            "registry",
            "schema",
            "route_baseline",
            "audit",
            "snapshot",
        ],
    )
    def test_each_surface_name_round_trips(self, surface) -> None:
        sd = stamp_digest(
            StateDiff(
                state_diff_id=f"sd:{surface}",
                target_surface=surface,
                operation_type="memory_episode_append",
                after_candidate="rec:after",
                schema_ref="sch:1",
                blast_radius="single_surface",
                rollback_plan_ref="rp:1",
                proposed_by_surface="Exit",
                created_at="0",
            )
        )
        assert sd.target_surface == surface


# 00.6 concurrent gateway commit isolation tests live in tests/uwg/test_edge_cases.py
# (this file is L4-scoped and does not import the uwg `gateway` fixture).
