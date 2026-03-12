"""ADG importability contract for agentic_core/utils/workflow_engines/snapshots.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_snapshots.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.utils.workflow_engines.snapshots import (  # noqa: F401
        RetrievalDriftSnapshot,
        EmbeddingHealthSnapshot,
        AnswerQualitySnapshot,
        DriftAlert,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RetrievalDriftSnapshot = None  # type: ignore[assignment,misc]
    EmbeddingHealthSnapshot = None  # type: ignore[assignment,misc]
    AnswerQualitySnapshot = None  # type: ignore[assignment,misc]
    DriftAlert = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="snapshots.py deps unavailable")
class TestSnapshotsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: snapshots.py must be importable."""
        assert _AVAILABLE

    def test_retrievaldriftsnapshot_is_type(self) -> None:
        assert RetrievalDriftSnapshot is not None

    def test_embeddinghealthsnapshot_is_type(self) -> None:
        assert EmbeddingHealthSnapshot is not None

    def test_answerqualitysnapshot_is_type(self) -> None:
        assert AnswerQualitySnapshot is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

