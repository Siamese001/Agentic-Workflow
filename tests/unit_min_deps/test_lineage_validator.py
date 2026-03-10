"""Unit tests for system_learning.validators.lineage_validator.

Covers:
  Wave 2.3 — Lineage Chain Validator:
    - Valid chain passes
    - Missing parent rejected
    - Artificial cycle rejected
    - Genesis version allowed
    - DAG structure enforced
"""

import pytest

from system_learning.engines.l4_version_store import L4VersionStore
from system_learning.validators.lineage_validator import (
    CycleDetected,
    LineageValidator,
    ParentNotFound,
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
# Wave 2.3 — Lineage Chain Validator
# =============================================================================


class TestValidateLineage:
    def test_genesis_version_valid(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("genesis-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        validator = LineageValidator(store)
        # Should not raise
        validator.validate_lineage(version_id)
        assert True  # no-exception contract

    def test_valid_parent_child_chain(self):
        store = L4VersionStore()
        parent_pkg = FakeChangePackage("parent-content")
        child_pkg = FakeChangePackage("child-content")

        parent_id = store.commit_change_package(parent_pkg, None, "hash1", 1700000000)
        child_id = store.commit_change_package(
            child_pkg, parent_version_id=parent_id, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        validator = LineageValidator(store)
        # Should not raise
        validator.validate_lineage(child_id)
        assert True  # no-exception contract

    def test_valid_three_generation_chain(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("gen1")
        pkg2 = FakeChangePackage("gen2")
        pkg3 = FakeChangePackage("gen3")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )
        v3 = store.commit_change_package(
            pkg3, parent_version_id=v2, change_spec_hash="hash3", committed_at_utc=1700000002
        )

        validator = LineageValidator(store)
        # Should not raise
        validator.validate_lineage(v3)
        assert True  # no-exception contract

    def test_missing_parent_raises(self):
        store = L4VersionStore()
        validator = LineageValidator(store)

        # Attempt to validate a version that doesn't exist
        with pytest.raises(ParentNotFound, match="PARENT_NOT_FOUND"):
            validator.validate_lineage("nonexistent-version")

    def test_cycle_detection_raises(self):
        """Artificial cycle test: manually inject a cycle into the store."""
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content1")
        pkg2 = FakeChangePackage("content2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        # Manually create a cycle by tampering with the store (for test purposes only)
        # In production, this is impossible due to write-once semantics
        versioned_v1 = store.get_change_package(v1)
        # Create a modified version with v2 as parent (creating v1 -> v2 -> v1 cycle)
        from system_learning.engines.l4_version_store import VersionedPackage

        tampered_v1 = VersionedPackage(
            version_id=v1,
            parent_version_id=v2,  # Create cycle
            change_spec_hash=versioned_v1.change_spec_hash,
            committed_at_utc=versioned_v1.committed_at_utc,
            package_bytes=versioned_v1.package_bytes,
        )
        store._versions[v1] = tampered_v1

        validator = LineageValidator(store)
        with pytest.raises(CycleDetected, match="CYCLE_DETECTED"):
            validator.validate_lineage(v1)


class TestValidateChain:
    def test_validate_chain_returns_ordered_list(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("gen1")
        pkg2 = FakeChangePackage("gen2")
        pkg3 = FakeChangePackage("gen3")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )
        v3 = store.commit_change_package(
            pkg3, parent_version_id=v2, change_spec_hash="hash3", committed_at_utc=1700000002
        )

        validator = LineageValidator(store)
        chain = validator.validate_chain(v3)

        # Chain should be ordered from genesis to current
        assert chain == [v1, v2, v3]

    def test_validate_chain_genesis_only(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("genesis")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        validator = LineageValidator(store)
        chain = validator.validate_chain(version_id)

        assert chain == [version_id]

    def test_validate_chain_with_invalid_parent_raises(self):
        store = L4VersionStore()
        validator = LineageValidator(store)

        with pytest.raises(ParentNotFound):
            validator.validate_chain("nonexistent-version")

    def test_validate_chain_enforces_dag_structure(self):
        """Verify that validate_chain enforces DAG (no cycles)."""
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content1")
        pkg2 = FakeChangePackage("content2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        # Manually create a cycle (for test purposes only)
        from system_learning.engines.l4_version_store import VersionedPackage

        versioned_v1 = store.get_change_package(v1)
        tampered_v1 = VersionedPackage(
            version_id=v1,
            parent_version_id=v2,  # Create cycle
            change_spec_hash=versioned_v1.change_spec_hash,
            committed_at_utc=versioned_v1.committed_at_utc,
            package_bytes=versioned_v1.package_bytes,
        )
        store._versions[v1] = tampered_v1

        validator = LineageValidator(store)
        with pytest.raises(CycleDetected):
            validator.validate_chain(v1)


class TestLineageIntegration:
    def test_full_lineage_workflow(self):
        """Integration test: commit chain, validate, rollback, validate again."""
        store = L4VersionStore()
        pkg1 = FakeChangePackage("v1")
        pkg2 = FakeChangePackage("v2")
        pkg3 = FakeChangePackage("v3")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )
        v3 = store.commit_change_package(
            pkg3, parent_version_id=v2, change_spec_hash="hash3", committed_at_utc=1700000002
        )

        validator = LineageValidator(store)

        # Validate v3 chain
        chain = validator.validate_chain(v3)
        assert chain == [v1, v2, v3]

        # Activate v3
        store.update_activation_pointer("test_component", v3)
        assert store.get_active_version("test_component") == v3

        # Rollback to v1
        store.rollback("test_component", v1)
        assert store.get_active_version("test_component") == v1

        # Validate v1 chain (should still be valid)
        chain = validator.validate_chain(v1)
        assert chain == [v1]

        # All versions still exist
        assert store.get_change_package(v1) is not None
        assert store.get_change_package(v2) is not None
        assert store.get_change_package(v3) is not None
