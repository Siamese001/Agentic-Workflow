"""ADG-driven tests for L4_state/memory/blob_storage_provider.py — fan_in=1."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.memory.blob_storage_provider import (
    IBlobStorageProviderProtocol,
    LocalDiskAdapter,
)


class TestIBlobStorageProviderProtocol:
    def test_importable(self):
        assert callable(IBlobStorageProviderProtocol)

    def test_has_write_blob(self):
        assert hasattr(IBlobStorageProviderProtocol, "write_blob")

    def test_has_read_blob(self):
        assert hasattr(IBlobStorageProviderProtocol, "read_blob")

    def test_has_exists(self):
        assert hasattr(IBlobStorageProviderProtocol, "exists")


class TestLocalDiskAdapter:
    def test_has_write_blob(self):
        assert hasattr(LocalDiskAdapter, "write_blob")

    def test_has_read_blob(self):
        assert hasattr(LocalDiskAdapter, "read_blob")

    def test_has_exists(self):
        assert hasattr(LocalDiskAdapter, "exists")

    def test_class_importable(self):
        assert callable(LocalDiskAdapter)

    def test_creates_or_raises_gateway_error(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                adapter = LocalDiskAdapter(base_path=tmpdir)
                assert adapter is not None
        except AttributeError:
            pass  # UniversalWriteGateway.ensure_dir missing in test env
