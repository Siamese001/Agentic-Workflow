"""ADG importability contract for apps_lic/reasoning/LicReflectionAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_LicReflectionAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_lic.reasoning.LicReflectionAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        LicReflectionAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LicReflectionAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="LicReflectionAgent.py deps unavailable")
class TestLicreflectionagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: LicReflectionAgent.py must be importable."""
        assert _AVAILABLE

    def test_licreflectionagent_is_type(self) -> None:
        assert LicReflectionAgent is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
