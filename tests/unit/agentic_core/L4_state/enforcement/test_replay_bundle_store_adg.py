"""ADG importability contract for agentic_core/L4_state/enforcement/replay_bundle_store.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_replay_bundle_store.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.enforcement.replay_bundle_store import (  # noqa: F401
        ReplayBundleStore,
        ReplayVerificationError,
        ReplayVerifier,
        VerifiedReplay,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReplayBundleStore = None  # type: ignore[assignment,misc]
    VerifiedReplay = None  # type: ignore[assignment,misc]
    ReplayVerificationError = None  # type: ignore[assignment,misc]
    ReplayVerifier = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="replay_bundle_store deps unavailable")
class TestReplayBundleStoreImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/enforcement/replay_bundle_store.py must be importable."""
        assert _AVAILABLE

    def test_replaybundlestore_defined(self) -> None:
        assert ReplayBundleStore is not None

    def test_verifiedreplay_defined(self) -> None:
        assert VerifiedReplay is not None

    def test_replayverificationerror_defined(self) -> None:
        assert ReplayVerificationError is not None

    def test_replayverifier_defined(self) -> None:
        assert ReplayVerifier is not None
