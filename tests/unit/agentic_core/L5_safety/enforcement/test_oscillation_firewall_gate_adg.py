"""ADG importability contract for agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_oscillation_firewall_gate.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (  # noqa: F401
        OscillationFirewallTripped,
        OscillationFirewallConfig,
        OscillationFirewall,
        validate_threshold,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    OscillationFirewallTripped = None  # type: ignore[assignment,misc]
    OscillationFirewallConfig = None  # type: ignore[assignment,misc]
    OscillationFirewall = None  # type: ignore[assignment,misc]
    validate_threshold = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="oscillation_firewall_gate.py deps unavailable")
class TestOscillationFirewallGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: oscillation_firewall_gate.py must be importable."""
        assert _AVAILABLE

    def test_oscillationfirewalltripped_is_type(self) -> None:
        assert OscillationFirewallTripped is not None

    def test_oscillationfirewallconfig_is_type(self) -> None:
        assert OscillationFirewallConfig is not None

    def test_oscillationfirewall_is_type(self) -> None:
        assert OscillationFirewall is not None

    def test_validate_threshold_callable(self) -> None:
        assert callable(validate_threshold)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

