"""Tests for L4 State Writer - Phase 7 functionality.

Tests write-once idempotency and version ID stability.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from system_learning.engines.l4_state_writer import (
    DefaultL4StateWriter,
    NoOpL4StateWriter,
    SimpleChangePackage,
)
from system_learning.engines.l4_version_store import L4VersionStore


class FakeL4VersionStore(L4VersionStore):
    """Fake L4 version store for testing."""

    def __init__(self) -> None:
        self._packages: dict[str, SimpleChangePackage] = {}
        self._activation_pointers: dict[str, str] = {}

    def commit_change_package(
        self,
        package: SimpleChangePackage,
        parent_version_id: str | None,
        change_spec_hash: str,
        committed_at_utc: int,
    ) -> str:
        """Commit a change package and return its version ID."""
        # Simulate content-hash based version ID
        import hashlib

        content = f"{package.component}:{package.payload_bytes}:{committed_at_utc}"
        version_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        self._packages[version_id] = package
        return version_id

    def get_change_package(self, version_id: str) -> SimpleChangePackage:
        """Retrieve a change package by version ID."""
        if version_id not in self._packages:
            raise ValueError(f"Version not found: {version_id}")
        return self._packages[version_id]

    def list_versions(self, component: str) -> list[str]:
        """List all versions for a component."""
        return [vid for vid, pkg in self._packages.items() if component in pkg.component]

    def get_active_version(self, component: str) -> str | None:
        """Get the active version for a component."""
        return self._active_pointers.get(component)

    def activate_version(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        if version_id not in self._packages:
            raise ValueError(f"Version not found: {version_id}")
        self._active_pointers[component] = version_id


class TestL4StateWriter:
    """Test suite for L4 State Writer implementations."""

    def test_default_writer_write_once_idempotent_same_payload(self):
        """Test that writing the same payload twice returns the same version ID."""
        fake_store = FakeL4VersionStore()
        writer = DefaultL4StateWriter(fake_store)

        payload_bytes = b"test payload for l4a"
        component_name = "test_component"
        created_utc = 1000

        # Write twice with same payload
        version1 = writer.write_l4a_detection_signal(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        version2 = writer.write_l4a_detection_signal(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        # Should return same version ID for same content
        assert version1 == version2
        assert len(fake_store._packages) == 1

    def test_default_writer_version_id_stable_from_content_hash(self):
        """Test that version ID is deterministic from content hash."""
        fake_store = FakeL4VersionStore()
        writer = DefaultL4StateWriter(fake_store)

        payload_bytes = b"deterministic test payload"
        component_name = "deterministic_component"
        created_utc = 2000

        # Write L4A signal
        l4a_version = writer.write_l4a_detection_signal(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        # Write L4B snapshot
        l4b_version = writer.write_l4b_healing_snapshot(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        # Different components should have different version IDs
        assert l4a_version != l4b_version

        # But same content in same component should be stable
        l4a_version2 = writer.write_l4a_detection_signal(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )
        assert l4a_version == l4a_version2

    def test_default_writer_different_payloads_different_versions(self):
        """Test that different payloads produce different version IDs."""
        fake_store = FakeL4VersionStore()
        writer = DefaultL4StateWriter(fake_store)

        payload1 = b"first payload"
        payload2 = b"second payload"
        component_name = "test_component"
        created_utc = 1000

        version1 = writer.write_l4a_detection_signal(
            payload_bytes=payload1, component_name=component_name, created_utc=created_utc
        )

        version2 = writer.write_l4a_detection_signal(
            payload_bytes=payload2, component_name=component_name, created_utc=created_utc
        )

        # Different payloads should have different version IDs
        assert version1 != version2
        assert len(fake_store._packages) == 2

    def test_noop_writer_returns_placeholder_ids(self):
        """Test that NoOpL4StateWriter returns placeholder version IDs."""
        writer = NoOpL4StateWriter()

        payload_bytes = b"any payload"
        component_name = "any_component"
        created_utc = 1000

        l4a_version = writer.write_l4a_detection_signal(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        l4b_version = writer.write_l4b_healing_snapshot(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        # Should return placeholder IDs
        assert l4a_version == f"noop_l4a_{created_utc}"
        assert l4b_version == f"noop_l4b_{created_utc}"

    def test_default_writer_component_name_in_package(self):
        """Test that component name is correctly stored in the package."""
        fake_store = FakeL4VersionStore()
        writer = DefaultL4StateWriter(fake_store)

        payload_bytes = b"test payload"
        component_name = "specific_component"
        created_utc = 1000

        version_id = writer.write_l4a_detection_signal(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        # Check the stored package
        package = fake_store.get_change_package(version_id)
        assert "l4a_detection_signal_specific_component" in package.component
        assert package.metadata["component_name"] == component_name
        assert package.metadata["created_utc"] == created_utc
        assert package.metadata["type"] == "detection_signal"

    def test_default_writer_l4b_snapshot_metadata(self):
        """Test that L4B snapshots have correct metadata."""
        fake_store = FakeL4VersionStore()
        writer = DefaultL4StateWriter(fake_store)

        payload_bytes = b"healing snapshot data"
        component_name = "meta-learning"
        created_utc = 2000

        version_id = writer.write_l4b_healing_snapshot(
            payload_bytes=payload_bytes, component_name=component_name, created_utc=created_utc
        )

        # Check the stored package
        package = fake_store.get_change_package(version_id)
        assert "l4b_healing_snapshot_meta-learning" in package.component
        assert package.metadata["component_name"] == component_name
        assert package.metadata["created_utc"] == created_utc
        assert package.metadata["type"] == "healing_snapshot"
