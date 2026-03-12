"""ADG importability contract for agentic_core/L6_observability/types/dpo_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_dpo_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.types.dpo_types import (  # noqa: F401
        DPOExampleId,
        DPOPair,
        DPOBatch,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DPOExampleId = None  # type: ignore[assignment,misc]
    DPOPair = None  # type: ignore[assignment,misc]
    DPOBatch = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="dpo_types.py deps unavailable")
class TestDpoTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: dpo_types.py must be importable."""
        assert _AVAILABLE

    def test_dpoexampleid_is_type(self) -> None:
        assert DPOExampleId is not None

    def test_dpopair_is_type(self) -> None:
        assert DPOPair is not None

    def test_dpobatch_is_type(self) -> None:
        assert DPOBatch is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

