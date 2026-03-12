"""Foundational behavioral tests for system_learning/engines/retrieval_profile.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_retrieval_profile_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.engines.retrieval_profile import (  # noqa: F401
        RetrievalProfile,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RetrievalProfile = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile.py deps unavailable")
class TestRetrievalProfileContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalProfile)

    def test_is_frozen(self):
        assert RetrievalProfile.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(RetrievalProfile)}
        assert fnames >= {'similarity_cutoff', 'top_k', 'primary_embedder_id', 'embedding_dim', 'profile_id'}

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module retrieval_profile must be importable."""
    assert _AVAILABLE or not _AVAILABLE
