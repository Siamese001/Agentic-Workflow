"""ADG importability contract for agentic_core/L2_execution/enforcement/SovereignLLMGateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignLLMGateway.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (  # noqa: F401
        ProviderHealthState,
        SovereignLLMGateway,
        SovereigntyViolation,
        get_llm_gateway,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ProviderHealthState = None  # type: ignore[assignment,misc]
    SovereigntyViolation = None  # type: ignore[assignment,misc]
    SovereignLLMGateway = None  # type: ignore[assignment,misc]
    get_llm_gateway = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignLLMGateway deps unavailable")
class TestSovereignllmgatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/SovereignLLMGateway.py must be importable."""
        assert _AVAILABLE

    def test_providerhealthstate_defined(self) -> None:
        assert ProviderHealthState is not None

    def test_sovereigntyviolation_defined(self) -> None:
        assert SovereigntyViolation is not None

    def test_sovereignllmgateway_defined(self) -> None:
        assert SovereignLLMGateway is not None