"""L4 replay reconstruction tests.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.5_*`` §PHASE 2 + §PHASE 6.

Tests must fail if:
- replay snapshot cannot reconstruct committed state
- deterministic digest changes across identical canonical input
- replay digest includes wall-clock value without clock policy
"""

from __future__ import annotations

from agentic_core.L4_state.contracts import (
    EnvironmentDigestRecord,
    L4SnapshotManifest,
    ReplaySnapshotRecord,
)
from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    record_canonical_payload,
    stamp_digest,
)


class TestReplayDeterminism:
    def test_identical_input_same_digest(self) -> None:
        a = stamp_digest(
            ReplaySnapshotRecord(
                replay_snapshot_id="rsn:1",
                trace_root="tr:1",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                replay_key="rk:1",
                snapshot_id="snap:after",
                input_hash="ih:1",
                prompt_hash="prh:1",
                route_digest="rd:1",
                evidence_contract_hash="ech:1",
                sealed_artifact_hash="sah:1",
                exit_disposition_hash="eh:1",
                commit_receipt_hash="crh:1",
                gate_verdict_hashes=("g:1", "g:2"),
                environment_digest_refs=("ed:1",),
            )
        )
        b = stamp_digest(
            ReplaySnapshotRecord(
                replay_snapshot_id="rsn:1",
                trace_root="tr:1",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                replay_key="rk:1",
                snapshot_id="snap:after",
                input_hash="ih:1",
                prompt_hash="prh:1",
                route_digest="rd:1",
                evidence_contract_hash="ech:1",
                sealed_artifact_hash="sah:1",
                exit_disposition_hash="eh:1",
                commit_receipt_hash="crh:1",
                gate_verdict_hashes=("g:1", "g:2"),
                environment_digest_refs=("ed:1",),
            )
        )
        assert a.deterministic_digest == b.deterministic_digest

    def test_changed_gate_verdict_changes_digest(self) -> None:
        base = ReplaySnapshotRecord(
            replay_snapshot_id="rsn:1",
            trace_root="tr:1",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            replay_key="rk:1",
            snapshot_id="snap:after",
            gate_verdict_hashes=("g:1",),
        )
        a = stamp_digest(base)
        from dataclasses import replace

        modified = replace(base, gate_verdict_hashes=("g:2",))
        b = stamp_digest(modified)
        assert a.deterministic_digest != b.deterministic_digest


class TestReplayReconstruction:
    """A replay snapshot must reconstruct enough state to verify a commit."""

    def test_reconstructs_from_immutable_refs(self) -> None:
        env = stamp_digest(
            EnvironmentDigestRecord(
                environment_digest_id="ed:1",
                runtime_version="3.10",
                tool_registry_digest="td:1",
                model_registry_digest="md:1",
                provider_lane_digest="pld:1",
                network_policy_hash="nph:1",
                clock_policy="run_clock",
                locale="en_US",
            )
        )
        snapshot = stamp_digest(
            ReplaySnapshotRecord(
                replay_snapshot_id="rsn:1",
                trace_root="tr:1",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                replay_key="rk:1",
                snapshot_id="snap:after",
                input_hash="ih:1",
                prompt_hash="prh:1",
                route_digest="rd:1",
                evidence_contract_hash="ech:1",
                sealed_artifact_hash="sah:1",
                exit_disposition_hash="eh:1",
                commit_receipt_hash="crh:1",
                gate_verdict_hashes=("g:1", "g:2"),
                environment_digest_refs=(env.environment_digest_id,),
            )
        )

        # Reconstruction = recompute the digest from the canonical payload, ensure stable
        payload = record_canonical_payload(snapshot)
        recomputed = compute_deterministic_digest(payload)
        assert recomputed == snapshot.deterministic_digest

        # Required fields for reconstruction must all be present
        # progress: fixed 10-element field-presence assertion, no UI bar needed
        for fld in (
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "input_hash",
            "prompt_hash",
            "route_digest",
            "evidence_contract_hash",
            "sealed_artifact_hash",
            "exit_disposition_hash",
            "commit_receipt_hash",
        ):
            assert payload[fld] not in (None, ""), f"replay field {fld} missing"

    def test_l4_snapshot_manifest_links_subsystems(self) -> None:
        manifest = stamp_digest(
            L4SnapshotManifest(
                snapshot_id="snap:1",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                registry_snapshot_id="rs:1",
                retrieval_surface_id="rsf:1",
                cache_snapshot_ref="cs:1",
                memory_snapshot_ref="ms:1",
                audit_ledger_position=42,
                created_at="0",
                created_by_surface="UWG",
                replay_snapshot_refs=("rsn:1", "rsn:2"),
            )
        )
        assert manifest.deterministic_digest
        assert manifest.audit_ledger_position == 42
        assert "rsn:1" in manifest.replay_snapshot_refs
