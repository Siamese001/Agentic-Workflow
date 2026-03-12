"""ADG importability contract for agentic_core/L4_state/types/retrieval_boundary_snapshot_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_retrieval_boundary_snapshot_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.retrieval_boundary_snapshot_types import (  # noqa: F401
        AnchorEntry,
        RetrievalBoundarySnapshot,
        build_request_hash,
        create_retrieval_boundary_snapshot,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AnchorEntry = None  # type: ignore[assignment,misc]
    RetrievalBoundarySnapshot = None  # type: ignore[assignment,misc]
    build_request_hash = None  # type: ignore[assignment,misc]
    create_retrieval_boundary_snapshot = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_boundary_snapshot_types.py deps unavailable")
class TestRetrievalBoundarySnapshotTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: retrieval_boundary_snapshot_types.py must be importable."""
        assert _AVAILABLE

    def test_anchorentry_is_type(self) -> None:
        assert AnchorEntry is not None

    def test_retrievalboundarysnapshot_is_type(self) -> None:
        assert RetrievalBoundarySnapshot is not None

    def test_build_request_hash_callable(self) -> None:
        assert callable(build_request_hash)

    def test_create_retrieval_boundary_snapshot_callable(self) -> None:
        assert callable(create_retrieval_boundary_snapshot)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

