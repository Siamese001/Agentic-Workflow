"""Unit tests for agentic_core.L4_state.utils.lifecycle.state_lifecycle.

Targets Wave-4 / Phase P11. Source: 585 lines, fan_in=41 (L4, impact 71.8).
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.utils.lifecycle.state_lifecycle import (
    LifecyclePolicy,
    LifecycleStatus,
    RetentionClass,
    StateLifecycleError,
    StateLifecycleRecord,
    StateLifecycleRegistry,
    get_state_lifecycle_registry,
    reset_state_lifecycle_registry,
)


from collections.abc import Iterator


@pytest.fixture(autouse=True)
def _fresh_registry() -> Iterator[None]:
    """Reset the singleton registry between tests."""
    reset_state_lifecycle_registry()
    yield
    reset_state_lifecycle_registry()


class TestEnums:
    def test_lifecycle_status_values(self) -> None:
        assert LifecycleStatus.ACTIVE.value == "ACTIVE"
        assert LifecycleStatus.STALE.value == "STALE"
        assert LifecycleStatus.EXPIRED.value == "EXPIRED"
        assert LifecycleStatus.ARCHIVED.value == "ARCHIVED"
        assert LifecycleStatus.PENDING_DELETION.value == "PENDING_DELETION"
        assert LifecycleStatus.DELETED.value == "DELETED"

    def test_retention_class_values(self) -> None:
        assert RetentionClass.SHORT_TERM.value == "SHORT_TERM"
        assert RetentionClass.MEDIUM_TERM.value == "MEDIUM_TERM"
        assert RetentionClass.LONG_TERM.value == "LONG_TERM"
        assert RetentionClass.PERMANENT.value == "PERMANENT"

    def test_state_lifecycle_error_is_exception(self) -> None:
        assert issubclass(StateLifecycleError, Exception)
        with pytest.raises(StateLifecycleError):
            raise StateLifecycleError("no policy")


class TestStateLifecycleRecord:
    def test_create_factory_sets_all_fields(self) -> None:
        rec = StateLifecycleRecord.create(
            state_namespace="ns/x",
            lifecycle_policy_id="policy-1",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="expire_after=3600s",
            archival_rule="archive_after=7200s",
            deletion_rule="delete_after=86400s",
        )
        assert rec.state_namespace == "ns/x"
        assert rec.lifecycle_policy_id == "policy-1"
        assert rec.retention_class == "SHORT_TERM"
        assert rec.lifecycle_status == "ACTIVE"

    def test_frozen(self) -> None:
        rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
        )
        with pytest.raises(AttributeError):
            rec.state_namespace = "other"  # type: ignore[misc]

    def test_has_lifecycle_policy_true_when_id_nonempty(self) -> None:
        rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
        )
        assert rec.has_lifecycle_policy() is True

    def test_has_lifecycle_policy_false_when_empty(self) -> None:
        rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
        )
        assert rec.has_lifecycle_policy() is False

    def test_is_active_status(self) -> None:
        rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
            lifecycle_status=LifecycleStatus.ACTIVE,
        )
        assert rec.is_active() is True
        assert rec.is_expired() is False

    def test_is_expired_status(self) -> None:
        rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
            lifecycle_status=LifecycleStatus.EXPIRED,
        )
        assert rec.is_expired() is True
        assert rec.is_active() is False

    def test_has_lifecycle_transition(self) -> None:
        active_rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
            lifecycle_status=LifecycleStatus.ACTIVE,
        )
        assert active_rec.has_lifecycle_transition() is False
        stale_rec = StateLifecycleRecord.create(
            state_namespace="ns",
            lifecycle_policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="",
            archival_rule="",
            deletion_rule="",
            lifecycle_status=LifecycleStatus.STALE,
        )
        assert stale_rec.has_lifecycle_transition() is True


class TestLifecyclePolicy:
    def test_create_factory(self) -> None:
        p = LifecyclePolicy.create(
            policy_id="p-1",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_duration_seconds=3600,
            archival_duration_seconds=7200,
            deletion_duration_seconds=86400,
        )
        assert p.policy_id == "p-1"
        assert p.retention_class == RetentionClass.SHORT_TERM
        assert p.requires_approval_for_deletion is True
        assert p.trace_linkage_required is True
        assert p.destructive_action_classification == "DESTRUCTIVE"

    def test_should_expire_true_when_aged(self) -> None:
        p = LifecyclePolicy.create(
            policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_duration_seconds=100,
            archival_duration_seconds=200,
            deletion_duration_seconds=300,
        )
        # Created at 0, current at 200 → should expire (200 > 100)
        assert p.should_expire(created_at_tick=0.0, current_tick=200.0) is True

    def test_should_expire_false_when_young(self) -> None:
        p = LifecyclePolicy.create(
            policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_duration_seconds=100,
            archival_duration_seconds=200,
            deletion_duration_seconds=300,
        )
        assert p.should_expire(created_at_tick=0.0, current_tick=50.0) is False

    def test_should_archive_applies_archival_duration(self) -> None:
        p = LifecyclePolicy.create(
            policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_duration_seconds=100,
            archival_duration_seconds=500,
            deletion_duration_seconds=1000,
        )
        assert p.should_archive(0.0, 400.0) is False
        assert p.should_archive(0.0, 600.0) is True

    def test_should_delete_applies_deletion_duration(self) -> None:
        p = LifecyclePolicy.create(
            policy_id="p",
            retention_class=RetentionClass.SHORT_TERM,
            expiration_duration_seconds=100,
            archival_duration_seconds=500,
            deletion_duration_seconds=1000,
        )
        assert p.should_delete(0.0, 900.0) is False
        assert p.should_delete(0.0, 1100.0) is True


class TestStateLifecycleRegistry:
    def _make_record(self, ns: str = "ns", policy_id: str = "p-1") -> StateLifecycleRecord:
        return StateLifecycleRecord.create(
            state_namespace=ns,
            lifecycle_policy_id=policy_id,
            retention_class=RetentionClass.SHORT_TERM,
            expiration_rule="r",
            archival_rule="a",
            deletion_rule="d",
        )

    def test_singleton_pattern(self) -> None:
        r1 = get_state_lifecycle_registry()
        r2 = get_state_lifecycle_registry()
        assert r1 is r2

    def test_reset_restores_empty(self) -> None:
        reg = get_state_lifecycle_registry()
        reg.persist_record(self._make_record())
        assert reg.get_record_count() == 1
        reset_state_lifecycle_registry()
        reg2 = get_state_lifecycle_registry()
        assert reg2 is not reg
        assert reg2.get_record_count() == 0

    def test_persist_and_query_by_namespace(self) -> None:
        reg = get_state_lifecycle_registry()
        rec = self._make_record(ns="ns/a")
        reg.persist_record(rec)
        got = reg.query_by_namespace("ns/a")
        assert got is not None
        assert got.state_namespace == "ns/a"

    def test_query_by_namespace_missing(self) -> None:
        reg = get_state_lifecycle_registry()
        assert reg.query_by_namespace("nope") is None

    def test_query_by_status(self) -> None:
        reg = get_state_lifecycle_registry()
        reg.persist_record(self._make_record(ns="a"))
        reg.persist_record(self._make_record(ns="b"))
        active = reg.query_by_status(LifecycleStatus.ACTIVE)
        assert len(active) == 2
        expired = reg.query_by_status(LifecycleStatus.EXPIRED)
        assert expired == []

    def test_query_by_policy(self) -> None:
        reg = get_state_lifecycle_registry()
        reg.persist_record(self._make_record(ns="a", policy_id="P1"))
        reg.persist_record(self._make_record(ns="b", policy_id="P1"))
        reg.persist_record(self._make_record(ns="c", policy_id="P2"))
        p1 = reg.query_by_policy("P1")
        assert len(p1) == 2
        assert reg.query_by_policy("NOPE") == []

    def test_register_policy_and_get(self) -> None:
        reg = get_state_lifecycle_registry()
        p = LifecyclePolicy.create(
            policy_id="policy-test",
            retention_class=RetentionClass.MEDIUM_TERM,
            expiration_duration_seconds=60,
            archival_duration_seconds=120,
            deletion_duration_seconds=240,
        )
        reg.register_policy(p)
        got = reg.get_policy("policy-test")
        assert got is p
        assert reg.get_policy("missing") is None

    def test_get_record_count_with_filter(self) -> None:
        reg = get_state_lifecycle_registry()
        reg.persist_record(self._make_record(ns="a"))
        assert reg.get_record_count() == 1
        assert reg.get_record_count(status=LifecycleStatus.ACTIVE) == 1
        assert reg.get_record_count(status=LifecycleStatus.EXPIRED) == 0

    def test_verify_namespace_has_policy(self) -> None:
        reg = get_state_lifecycle_registry()
        reg.persist_record(self._make_record(ns="with-policy", policy_id="p1"))
        reg.persist_record(self._make_record(ns="without", policy_id=""))
        assert reg.verify_namespace_has_policy("with-policy") is True
        assert reg.verify_namespace_has_policy("without") is False
        assert reg.verify_namespace_has_policy("missing") is False

    def test_update_access_time_overwrites_record(self) -> None:
        reg = get_state_lifecycle_registry()
        reg.persist_record(self._make_record(ns="ns1"))
        original = reg.query_by_namespace("ns1")
        assert original is not None
        reg.update_access_time("ns1")
        updated = reg.query_by_namespace("ns1")
        assert updated is not None
        # last_accessed_tick should be >= original (could be same tick)
        assert updated.last_accessed_tick >= original.last_accessed_tick

    def test_update_access_time_no_op_for_missing(self) -> None:
        reg = get_state_lifecycle_registry()
        # Must not raise
        reg.update_access_time("no-such-ns")
        assert reg.query_by_namespace("no-such-ns") is None
