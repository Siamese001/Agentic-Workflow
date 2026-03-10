"""Unit tests for system_learning.engines.l4_version_store.

Covers:
  Wave 2.1 — Versioned ChangePackage Store:
    - Write-once semantics
    - Same content → same version_id
    - Parent existence enforced
    - No mutation of stored objects
  Wave 2.2 — Activation Pointer + Rollback:
    - Activate version
    - Rollback to parent
    - O(1) pointer reversion
    - Attempt activation of unknown version → fail
"""

import hashlib

import pytest

from system_learning.engines.l4_version_store import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    L4VersionStore,
    ParentVersionNotFound,
    VersionNotFound,
)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake ChangePackage for tests
# =============================================================================


class FakeChangePackage:
    """Minimal ChangePackage implementation for testing."""

    def __init__(self, content: str) -> None:
        self._content = content

    def canonical_bytes(self) -> bytes:
        return self._content.encode("utf-8")


# =============================================================================
# Wave 2.1 — Versioned ChangePackage Store
# =============================================================================


class TestCommitChangePackage:
    def test_commit_returns_sha256_version_id(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(
            package=pkg,
            parent_version_id=None,
            change_spec_hash="abc123",
            committed_at_utc=1700000000,
        )
        expected = hashlib.sha256(b"test-content").hexdigest()
        assert version_id == expected

    def test_same_content_produces_same_version_id(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("identical-content")
        pkg2 = FakeChangePackage("identical-content")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        assert v1 == v2

    def test_different_content_produces_different_version_id(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        assert v1 != v2

    def test_write_once_semantics_idempotent_on_same_content(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")

        v1 = store.commit_change_package(pkg, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg, None, "hash1", 1700000000)

        assert v1 == v2

    def test_parent_version_not_found_raises(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")

        with pytest.raises(ParentVersionNotFound, match="PARENT_VERSION_NOT_FOUND"):
            store.commit_change_package(
                pkg, parent_version_id="nonexistent", change_spec_hash="hash", committed_at_utc=1700000000
            )

    def test_genesis_version_allowed(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("genesis-content")

        version_id = store.commit_change_package(
            pkg, parent_version_id=None, change_spec_hash="hash", committed_at_utc=1700000000
        )

        assert version_id is not None
        retrieved = store.get_change_package(version_id)
        assert retrieved.parent_version_id is None

    def test_child_version_with_valid_parent(self):
        store = L4VersionStore()
        parent_pkg = FakeChangePackage("parent-content")
        child_pkg = FakeChangePackage("child-content")

        parent_id = store.commit_change_package(parent_pkg, None, "hash1", 1700000000)
        child_id = store.commit_change_package(
            child_pkg, parent_version_id=parent_id, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        child = store.get_change_package(child_id)
        assert child.parent_version_id == parent_id


class TestGetChangePackage:
    def test_get_existing_version(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        retrieved = store.get_change_package(version_id)
        assert retrieved.version_id == version_id
        assert retrieved.package_bytes == b"test-content"

    def test_get_nonexistent_version_raises(self):
        store = L4VersionStore()
        with pytest.raises(VersionNotFound, match="VERSION_NOT_FOUND"):
            store.get_change_package("nonexistent-version-id")

    def test_retrieved_package_is_immutable(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        retrieved = store.get_change_package(version_id)
        # VersionedPackage is frozen dataclass
        with pytest.raises((AttributeError, TypeError)):
            retrieved.version_id = "tampered"  # type: ignore[misc]


class TestListVersions:
    def test_list_all_versions(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-1")
        pkg2 = FakeChangePackage("content-2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        versions = store.list_versions()
        assert sorted(versions) == sorted([v1, v2])

    def test_list_versions_empty_store(self):
        store = L4VersionStore()
        assert store.list_versions() == []

    def test_list_versions_deterministic_order(self):
        store = L4VersionStore()
        for i in range(5):
            pkg = FakeChangePackage(f"content-{i}")
            store.commit_change_package(pkg, None, f"hash{i}", 1700000000 + i)

        versions1 = store.list_versions()
        versions2 = store.list_versions()
        assert versions1 == versions2


# =============================================================================
# Wave 2.2 — Activation Pointer + Rollback
# =============================================================================


class TestUpdateActivationPointer:
    def test_activate_version(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        store.update_activation_pointer("routing_config", version_id)
        active = store.get_active_version("routing_config")
        assert active == version_id

    def test_activate_nonexistent_version_raises(self):
        store = L4VersionStore()
        with pytest.raises(VersionNotFound, match="ACTIVATION_TARGET_NOT_FOUND"):
            store.update_activation_pointer("routing_config", "nonexistent-version")

    def test_activation_does_not_mutate_package(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        original = store.get_change_package(version_id)
        store.update_activation_pointer("routing_config", version_id)
        after_activation = store.get_change_package(version_id)

        assert original == after_activation

    def test_atomic_pointer_update(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        store.update_activation_pointer("routing_config", v1)
        assert store.get_active_version("routing_config") == v1

        store.update_activation_pointer("routing_config", v2)
        assert store.get_active_version("routing_config") == v2


class TestGetActiveVersion:
    def test_get_active_version_when_set(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        store.update_activation_pointer("routing_config", version_id)
        assert store.get_active_version("routing_config") == version_id

    def test_get_active_version_when_not_set(self):
        store = L4VersionStore()
        assert store.get_active_version("routing_config") is None

    def test_multiple_components_independent(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-1")
        pkg2 = FakeChangePackage("content-2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        store.update_activation_pointer("routing_config", v1)
        store.update_activation_pointer("policy_config", v2)

        assert store.get_active_version("routing_config") == v1
        assert store.get_active_version("policy_config") == v2


class TestRollback:
    def test_rollback_to_parent(self):
        store = L4VersionStore()
        parent_pkg = FakeChangePackage("parent-content")
        child_pkg = FakeChangePackage("child-content")

        parent_id = store.commit_change_package(parent_pkg, None, "hash1", 1700000000)
        child_id = store.commit_change_package(
            child_pkg, parent_version_id=parent_id, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        store.update_activation_pointer("routing_config", child_id)
        assert store.get_active_version("routing_config") == child_id

        store.rollback("routing_config", parent_id)
        assert store.get_active_version("routing_config") == parent_id

    def test_rollback_is_o1_pointer_reversion(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        store.update_activation_pointer("routing_config", v2)
        store.rollback("routing_config", v1)

        # Rollback does not delete v2
        assert store.get_change_package(v2) is not None
        # Active pointer now points to v1
        assert store.get_active_version("routing_config") == v1

    def test_rollback_to_nonexistent_version_raises(self):
        store = L4VersionStore()
        with pytest.raises(VersionNotFound):
            store.rollback("routing_config", "nonexistent-version")

    def test_no_deletion_of_historical_versions(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")
        pkg3 = FakeChangePackage("content-v3")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )
        v3 = store.commit_change_package(
            pkg3, parent_version_id=v2, change_spec_hash="hash3", committed_at_utc=1700000002
        )

        store.update_activation_pointer("routing_config", v3)
        store.rollback("routing_config", v1)

        # All versions still exist
        assert store.get_change_package(v1) is not None
        assert store.get_change_package(v2) is not None
        assert store.get_change_package(v3) is not None


# =============================================================================
# Version ID Determinism
# =============================================================================


class TestVersionIdDeterminism:
    def test_version_id_determinism_assertion(self):
        """Canonical determinism assertion: same content → same version_id."""
        store1 = L4VersionStore()
        store2 = L4VersionStore()

        pkg1 = FakeChangePackage("deterministic-content")
        pkg2 = FakeChangePackage("deterministic-content")

        v1 = store1.commit_change_package(pkg1, None, "hash", 1700000000)
        v2 = store2.commit_change_package(pkg2, None, "hash", 1700000000)

        assert v1 == v2, f"version_id mismatch: {v1!r} != {v2!r}"
