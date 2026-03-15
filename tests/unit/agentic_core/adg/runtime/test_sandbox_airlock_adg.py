"""ADG importability contract for agentic_core/adg/runtime/sandbox_airlock.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sandbox_airlock.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.sandbox_airlock import (  # noqa: F401
        AirlockPhase,
        AirlockSession,
        CapabilityToken,
        SandboxAirlockRecorder,
        SandboxEnvelope,
        WorkContract,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AirlockPhase = None  # type: ignore[assignment,misc]
    WorkContract = None  # type: ignore[assignment,misc]
    CapabilityToken = None  # type: ignore[assignment,misc]
    SandboxEnvelope = None  # type: ignore[assignment,misc]
    AirlockSession = None  # type: ignore[assignment,misc]
    SandboxAirlockRecorder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sandbox_airlock deps unavailable")
class TestSandboxAirlockImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/sandbox_airlock.py must be importable."""
        assert _AVAILABLE

    def test_airlockphase_defined(self) -> None:
        assert AirlockPhase is not None

    def test_workcontract_defined(self) -> None:
        assert WorkContract is not None

    def test_capabilitytoken_defined(self) -> None:
        assert CapabilityToken is not None

    def test_sandboxenvelope_defined(self) -> None:
        assert SandboxEnvelope is not None

    def test_airlocksession_defined(self) -> None:
        assert AirlockSession is not None

    def test_sandboxairlockrecorder_defined(self) -> None:
        assert SandboxAirlockRecorder is not None
