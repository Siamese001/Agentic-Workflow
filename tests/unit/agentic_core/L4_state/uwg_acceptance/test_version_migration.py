"""00B.9 Blueprint / Policy Version Migration tests.

Doctrine refs:
- ``docs/reference/00B_L4_State_Archive_and_UWG/00B.9_L4_Blueprint_Policy_Version_Migration.md``

Implements all 5 test contracts grandfathered in
``ops_scripts/ci/baselines/reference_test_contract_baseline.json``:

- ``test_policy_publish_creates_new_version_not_overwrite``
- ``test_blueprint_alias_swap_requires_uwg_receipt``
- ``test_breaking_version_requires_migration_plan``
- ``test_deprecated_policy_version_blocks_new_run_start_after_window``
- ``test_replay_bound_runtime_detects_policy_version_mismatch``

Plus record-shape / immutability / digest tests for the 3 new records.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.contracts import (
    DeprecationWindowRecord,
    PolicyBlueprintMigrationPlan,
    PolicyManifest,
    PolicyVersionRecord,
    ReplaySnapshotRecord,
    VersionCompatibilityRecord,
    detect_policy_version_mismatch,
)
from agentic_core.L4_state.contracts.records import (
    COMPATIBILITY_MODES,
    VERSION_MIGRATION_SURFACES,
    stamp_digest,
)


# ============================================================================
# 9.T1 — policy publish creates a new version, never overwrites
# ============================================================================


def test_policy_publish_creates_new_version_not_overwrite() -> None:
    """00B.9 §RULES line 100: 'No in-place mutation of policy or blueprint records.'

    Publishing a new policy version MUST create a new ``PolicyVersionRecord``
    pointing at a new ``PolicyManifest``; the prior manifest's frozen
    fields cannot be mutated.
    """
    v1_manifest = stamp_digest(
        PolicyManifest(
            policy_manifest_id="pm:v1",
            policy_version="v1",
            policy_hash="hash:v1",
        )
    )
    v1_version = stamp_digest(
        PolicyVersionRecord(
            policy_version_id="pv:v1",
            policy_manifest_ref="pm:v1",
            policy_hash="hash:v1",
            valid_from="2026-01-01T00:00:00Z",
            publish_commit_receipt_ref="commit:v1",
            alias_swap_receipt_ref="alias:v1",
            tenant_scope="all",
            policy_diff_ref="diff:v1",
        )
    )

    # Attempting to mutate v1 manifest must fail (frozen dataclass)
    with pytest.raises((AttributeError, TypeError)):
        v1_manifest.policy_hash = "hash:v1_tampered"  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        v1_version.policy_hash = "hash:v1_tampered"  # type: ignore[misc]

    # New version is a NEW record with a different digest
    v2_manifest = stamp_digest(
        PolicyManifest(
            policy_manifest_id="pm:v2",
            policy_version="v2",
            policy_hash="hash:v2",
            previous_alias_ref="pm:v1",
        )
    )
    assert v2_manifest.policy_manifest_id != v1_manifest.policy_manifest_id
    assert v2_manifest.deterministic_digest != v1_manifest.deterministic_digest
    assert v2_manifest.previous_alias_ref == "pm:v1"


# ============================================================================
# 9.T2 — alias swap requires UWG commit receipt linkage
# ============================================================================


def test_blueprint_alias_swap_requires_uwg_receipt() -> None:
    """00B.9 §RULES line 101: 'Alias swaps require UWG commit receipt and
    audit ledger append.'

    A ``PolicyBlueprintMigrationPlan`` with ``activation_policy='aliased'``
    MUST carry both ``alias_swap_plan_ref`` AND ``UWG_commit_request_ref``;
    omitting either must raise at construction time.
    """
    # Missing alias_swap_plan_ref -> rejected
    with pytest.raises(ValueError, match="alias_swap_plan_ref"):
        PolicyBlueprintMigrationPlan(
            migration_plan_id="mp:1",
            target_surface="blueprint",
            source_version_ref="bp:v1",
            target_version_ref="bp:v2",
            rollback_plan_ref="rb:1",
            owner="platform-team",
            signer_identity="signer:1",
            UWG_commit_request_ref="cr:1",
            activation_policy="aliased",
            # alias_swap_plan_ref intentionally omitted
        )

    # Missing UWG_commit_request_ref -> rejected
    with pytest.raises(ValueError, match="UWG_commit_request_ref"):
        PolicyBlueprintMigrationPlan(
            migration_plan_id="mp:2",
            target_surface="blueprint",
            source_version_ref="bp:v1",
            target_version_ref="bp:v2",
            rollback_plan_ref="rb:1",
            owner="platform-team",
            signer_identity="signer:1",
            UWG_commit_request_ref="",  # empty string -> rejected
            activation_policy="aliased",
            alias_swap_plan_ref="alias:1",
        )

    # Both present -> accepted
    plan = stamp_digest(
        PolicyBlueprintMigrationPlan(
            migration_plan_id="mp:3",
            target_surface="blueprint",
            source_version_ref="bp:v1",
            target_version_ref="bp:v2",
            rollback_plan_ref="rb:1",
            owner="platform-team",
            signer_identity="signer:1",
            UWG_commit_request_ref="cr:1",
            activation_policy="aliased",
            alias_swap_plan_ref="alias:1",
        )
    )
    assert plan.alias_swap_plan_ref == "alias:1"
    assert plan.UWG_commit_request_ref == "cr:1"
    assert plan.deterministic_digest


# ============================================================================
# 9.T3 — breaking version requires migration plan
# ============================================================================


def test_breaking_version_requires_migration_plan() -> None:
    """00B.9 §RULES line 102: 'Breaking changes require replay pack proof
    and rollback plan before activation.'

    ``VersionCompatibilityRecord(compatibility='breaking')`` with
    ``migration_required=False`` MUST be rejected at construction.
    """
    # Breaking + migration_required=False -> rejected
    with pytest.raises(ValueError, match="migration_required=True"):
        VersionCompatibilityRecord(
            compatibility_record_id="vc:1",
            surface="policy",
            old_version_ref="pm:v1",
            new_version_ref="pm:v2",
            old_hash="h1",
            new_hash="h2",
            compatibility="breaking",
            migration_required=False,
            activation_policy="aliased",
        )

    # Breaking + migration_required=True -> accepted, with replay/rollback impact
    rec = stamp_digest(
        VersionCompatibilityRecord(
            compatibility_record_id="vc:2",
            surface="policy",
            old_version_ref="pm:v1",
            new_version_ref="pm:v2",
            old_hash="h1",
            new_hash="h2",
            compatibility="breaking",
            migration_required=True,
            activation_policy="aliased",
            replay_impact="full_invalidation",
            rollback_impact="full",
            affected_route_classes=("research", "rfp"),
        )
    )
    assert rec.migration_required is True
    assert rec.replay_impact == "full_invalidation"
    assert rec.deterministic_digest

    # Backward-compatible without migration_required -> accepted
    rec2 = VersionCompatibilityRecord(
        compatibility_record_id="vc:3",
        surface="policy",
        old_version_ref="pm:v1",
        new_version_ref="pm:v1.1",
        old_hash="h1",
        new_hash="h1b",
        compatibility="backward_compatible",
        migration_required=False,
        activation_policy="immediate",
    )
    assert rec2.compatibility == "backward_compatible"


# ============================================================================
# 9.T4 — deprecated policy version blocks new run_start after window
# ============================================================================


def test_deprecated_policy_version_blocks_new_run_start_after_window() -> None:
    """00B.9 §DeprecationWindowRecord + §RULES line 104.

    A run starting AFTER ``deprecation_end`` MUST be blocked from any
    route not in ``allowed_legacy_routes``. ``blocked_new_routes`` is
    enforced both inside and outside the window.
    """
    rec = stamp_digest(
        DeprecationWindowRecord(
            deprecation_id="dep:1",
            deprecated_version_ref="pm:v1",
            replacement_version_ref="pm:v2",
            deprecation_start="2026-01-01T00:00:00Z",
            deprecation_end="2026-06-01T00:00:00Z",
            allowed_legacy_routes=("research_legacy",),
            blocked_new_routes=("research_v2",),
        )
    )

    # Inside window -> only blocked_new_routes apply
    assert rec.is_route_blocked_at("research_v2", "2026-03-15T00:00:00Z") is True
    assert rec.is_route_blocked_at("research_legacy", "2026-03-15T00:00:00Z") is False
    assert rec.is_route_blocked_at("rfp", "2026-03-15T00:00:00Z") is False

    # After window -> only allowed_legacy_routes survive; everything else blocked
    assert rec.is_route_blocked_at("research_v2", "2026-07-01T00:00:00Z") is True
    assert rec.is_route_blocked_at("research_legacy", "2026-07-01T00:00:00Z") is False
    assert rec.is_route_blocked_at("rfp", "2026-07-01T00:00:00Z") is True
    assert rec.is_route_blocked_at("anything_new", "2026-07-01T00:00:00Z") is True


# ============================================================================
# 9.T5 — replay-bound runtime detects policy version mismatch
# ============================================================================


def test_replay_bound_runtime_detects_policy_version_mismatch() -> None:
    """00B.9 §RULES line 103: 'Runtime packets already bound to a replay
    snapshot may complete under their bound snapshot unless policy
    requires fail-closed.'

    The detection helper returns 'policy_version_mismatch' when the
    active policy hash differs from the replay snapshot's bound hash.
    """
    replay = stamp_digest(
        ReplaySnapshotRecord(
            replay_snapshot_id="rs:1",
            trace_root="trace:1",
            tenant_id="t:1",
            policy_hash="hash:v1",
            blueprint_hash="bh:1",
            replay_key="rk:1",
            snapshot_id="snap:1",
        )
    )

    # Same hash -> no mismatch
    assert (
        detect_policy_version_mismatch(
            active_policy_hash=replay.policy_hash,
            replay_snapshot_policy_hash=replay.policy_hash,
        )
        is None
    )

    # Different hash -> mismatch detected with deterministic reason code
    reason = detect_policy_version_mismatch(
        active_policy_hash="hash:v2",
        replay_snapshot_policy_hash=replay.policy_hash,
    )
    assert reason == "policy_version_mismatch"


# ============================================================================
# Record-shape / immutability / digest tests
# ============================================================================


class TestVersionMigrationRecordShapes:
    """Shape, immutability, and digest stability for the 3 new records."""

    def test_version_compatibility_record_is_frozen(self) -> None:
        rec = VersionCompatibilityRecord(
            compatibility_record_id="vc:imm",
            surface="policy",
            old_version_ref="a",
            new_version_ref="b",
            old_hash="h1",
            new_hash="h2",
            compatibility="backward_compatible",
            migration_required=False,
            activation_policy="immediate",
        )
        with pytest.raises((AttributeError, TypeError)):
            rec.compatibility = "breaking"  # type: ignore[misc]

    def test_migration_plan_is_frozen(self) -> None:
        plan = PolicyBlueprintMigrationPlan(
            migration_plan_id="mp:imm",
            target_surface="policy",
            source_version_ref="v1",
            target_version_ref="v2",
            rollback_plan_ref="rb:1",
            owner="o",
            signer_identity="s",
            UWG_commit_request_ref="cr:1",
            activation_policy="aliased",
            alias_swap_plan_ref="alias:1",
        )
        with pytest.raises((AttributeError, TypeError)):
            plan.owner = "tampered"  # type: ignore[misc]

    def test_deprecation_window_is_frozen(self) -> None:
        rec = DeprecationWindowRecord(
            deprecation_id="dep:imm",
            deprecated_version_ref="v1",
            replacement_version_ref="v2",
            deprecation_start="2026-01-01T00:00:00Z",
            deprecation_end="2026-02-01T00:00:00Z",
        )
        with pytest.raises((AttributeError, TypeError)):
            rec.deprecation_end = "9999-01-01"  # type: ignore[misc]

    def test_invalid_surface_rejected(self) -> None:
        with pytest.raises(ValueError, match="surface must be one of"):
            VersionCompatibilityRecord(
                compatibility_record_id="vc:bad",
                surface="not_a_surface",
                old_version_ref="a",
                new_version_ref="b",
                old_hash="h1",
                new_hash="h2",
                compatibility="backward_compatible",
                migration_required=False,
                activation_policy="immediate",
            )
        with pytest.raises(ValueError, match="target_surface must be one of"):
            PolicyBlueprintMigrationPlan(
                migration_plan_id="mp:bad",
                target_surface="not_a_surface",
                source_version_ref="v1",
                target_version_ref="v2",
                rollback_plan_ref="rb:1",
                owner="o",
                signer_identity="s",
                UWG_commit_request_ref="cr:1",
                activation_policy="immediate",
            )

    def test_invalid_compatibility_rejected(self) -> None:
        with pytest.raises(ValueError, match="compatibility must be one of"):
            VersionCompatibilityRecord(
                compatibility_record_id="vc:bad2",
                surface="policy",
                old_version_ref="a",
                new_version_ref="b",
                old_hash="h1",
                new_hash="h2",
                compatibility="not_a_mode",
                migration_required=False,
                activation_policy="immediate",
            )

    def test_digests_are_deterministic_and_distinct(self) -> None:
        a = stamp_digest(
            VersionCompatibilityRecord(
                compatibility_record_id="vc:a",
                surface="policy",
                old_version_ref="a",
                new_version_ref="b",
                old_hash="h1",
                new_hash="h2",
                compatibility="backward_compatible",
                migration_required=False,
                activation_policy="immediate",
            )
        )
        # Same construction -> same digest (deterministic)
        a2 = stamp_digest(
            VersionCompatibilityRecord(
                compatibility_record_id="vc:a",
                surface="policy",
                old_version_ref="a",
                new_version_ref="b",
                old_hash="h1",
                new_hash="h2",
                compatibility="backward_compatible",
                migration_required=False,
                activation_policy="immediate",
            )
        )
        assert a.deterministic_digest == a2.deterministic_digest
        assert len(a.deterministic_digest) == 64  # SHA-256 hex

        # Different id -> different digest
        b = stamp_digest(
            VersionCompatibilityRecord(
                compatibility_record_id="vc:b",
                surface="policy",
                old_version_ref="a",
                new_version_ref="b",
                old_hash="h1",
                new_hash="h2",
                compatibility="backward_compatible",
                migration_required=False,
                activation_policy="immediate",
            )
        )
        assert a.deterministic_digest != b.deterministic_digest

    def test_doctrine_vocabulary_constants(self) -> None:
        """Constants match doctrine 00B.9 lines 60 and 65."""
        assert "policy" in VERSION_MIGRATION_SURFACES
        assert "blueprint" in VERSION_MIGRATION_SURFACES
        assert "registry" in VERSION_MIGRATION_SURFACES
        assert "prompt" in VERSION_MIGRATION_SURFACES
        assert "retrieval_profile" in VERSION_MIGRATION_SURFACES
        assert "rubric" in VERSION_MIGRATION_SURFACES
        assert len(VERSION_MIGRATION_SURFACES) == 6

        assert set(COMPATIBILITY_MODES) == {
            "backward_compatible",
            "forward_compatible",
            "breaking",
            "unknown",
        }
