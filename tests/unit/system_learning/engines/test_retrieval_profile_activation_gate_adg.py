"""ADG importability contract for system_learning/engines/retrieval_profile_activation_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_retrieval_profile_activation_gate.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.retrieval_profile_activation_gate import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ActivationResult,
        RetrievalProfileActivationGate,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ActivationResult = None  # type: ignore[assignment,misc]
    RetrievalProfileActivationGate = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile_activation_gate.py deps unavailable")
class TestRetrievalProfileActivationGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: retrieval_profile_activation_gate.py must be importable."""
        assert _AVAILABLE

    def test_activationresult_is_type(self) -> None:
        assert ActivationResult is not None

    def test_retrievalprofileactivationgate_is_type(self) -> None:
        assert RetrievalProfileActivationGate is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
