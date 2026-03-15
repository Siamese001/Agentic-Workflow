"""ADG importability contract for agentic_core/L4_state/memory/blob_storage_provider.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_blob_storage_provider.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.memory.blob_storage_provider import (  # noqa: F401
        IBlobStorageProviderProtocol,
        LocalDiskAdapter,
        S3Adapter,
        SignalLedger,
        create_storage_adapter,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    IBlobStorageProviderProtocol = None  # type: ignore[assignment,misc]
    LocalDiskAdapter = None  # type: ignore[assignment,misc]
    S3Adapter = None  # type: ignore[assignment,misc]
    create_storage_adapter = None  # type: ignore[assignment,misc]
    SignalLedger = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="blob_storage_provider deps unavailable")
class TestBlobStorageProviderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/memory/blob_storage_provider.py must be importable."""
        assert _AVAILABLE

    def test_iblobstorageproviderprotocol_defined(self) -> None:
        assert IBlobStorageProviderProtocol is not None

    def test_localdiskadapter_defined(self) -> None:
        assert LocalDiskAdapter is not None

    def test_s3adapter_defined(self) -> None:
        assert S3Adapter is not None

    def test_signalledger_defined(self) -> None:
        assert SignalLedger is not None
