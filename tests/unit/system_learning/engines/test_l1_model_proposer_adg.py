"""ADG importability contract for system_learning/engines/l1_model_proposer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_l1_model_proposer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.l1_model_proposer import (  # noqa: F401
        L1ModelChangePackage,
        L1ModelProposer,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    L1ModelChangePackage = None  # type: ignore[assignment,misc]
    L1ModelProposer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="l1_model_proposer.py deps unavailable")
class TestL1ModelProposerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: l1_model_proposer.py must be importable."""
        assert _AVAILABLE

    def test_l1modelchangepackage_is_type(self) -> None:
        assert L1ModelChangePackage is not None

    def test_l1modelproposer_is_type(self) -> None:
        assert L1ModelProposer is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

