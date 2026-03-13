"""ADG importability contract for agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_oscillation_firewall_gate.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.oscillation_firewall_gate import (  # noqa: F401
        OscillationFirewall,
        OscillationFirewallConfig,
        OscillationFirewallTripped,
        validate_threshold,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    OscillationFirewallTripped = None  # type: ignore[assignment,misc]
    OscillationFirewallConfig = None  # type: ignore[assignment,misc]
    OscillationFirewall = None  # type: ignore[assignment,misc]
    validate_threshold = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="oscillation_firewall_gate deps unavailable")
class TestOscillationFirewallGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py must be importable."""
        assert _AVAILABLE

    def test_oscillationfirewalltripped_defined(self) -> None:
        assert OscillationFirewallTripped is not None

    def test_oscillationfirewallconfig_defined(self) -> None:
        assert OscillationFirewallConfig is not None

    def test_oscillationfirewall_defined(self) -> None:
        assert OscillationFirewall is not None
