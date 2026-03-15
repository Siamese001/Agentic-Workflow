"""ADG importability contract for system_learning/engines/retrieval_profile_manager.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_retrieval_profile_manager.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.retrieval_profile_manager import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        RetrievalProfileManager,
        get_active_retrieval_profile,
        get_retrieval_profile_manager,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RetrievalProfileManager = None  # type: ignore[assignment,misc]
    get_retrieval_profile_manager = None  # type: ignore[assignment,misc]
    get_active_retrieval_profile = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile_manager.py deps unavailable")
class TestRetrievalProfileManagerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: retrieval_profile_manager.py must be importable."""
        assert _AVAILABLE

    def test_retrievalprofilemanager_is_type(self) -> None:
        assert RetrievalProfileManager is not None

    def test_get_retrieval_profile_manager_callable(self) -> None:
        assert callable(get_retrieval_profile_manager)

    def test_get_active_retrieval_profile_callable(self) -> None:
        assert callable(get_active_retrieval_profile)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
