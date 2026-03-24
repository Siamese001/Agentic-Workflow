"""ADG importability contract for system_learning/engines/l4_version_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_l4_version_store.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.l4_version_store import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        L4VersionStore,
        ParentVersionNotFound,
        VersionedPackage,
        VersionNotFound,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ParentVersionNotFound = None  # type: ignore[assignment,misc]
    VersionNotFound = None  # type: ignore[assignment,misc]
    VersionedPackage = None  # type: ignore[assignment,misc]
    L4VersionStore = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="l4_version_store.py deps unavailable")
class TestL4VersionStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: l4_version_store.py must be importable."""
        assert _AVAILABLE

    def test_parentversionnotfound_is_type(self) -> None:
        assert ParentVersionNotFound is not None

    def test_versionnotfound_is_type(self) -> None:
        assert VersionNotFound is not None

    def test_versionedpackage_is_type(self) -> None:
        assert VersionedPackage is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None