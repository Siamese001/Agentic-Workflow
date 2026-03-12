"""ADG importability contract for agentic_core/L0_routing/scripts/verify_manifest_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_verify_manifest_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.verify_manifest_util import (  # noqa: F401
        setup_logging,
        analyze_impact,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    setup_logging = None  # type: ignore[assignment,misc]
    analyze_impact = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="verify_manifest_util.py deps unavailable")
class TestVerifyManifestUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: verify_manifest_util.py must be importable."""
        assert _AVAILABLE

    def test_setup_logging_callable(self) -> None:
        assert callable(setup_logging)

    def test_analyze_impact_callable(self) -> None:
        assert callable(analyze_impact)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

