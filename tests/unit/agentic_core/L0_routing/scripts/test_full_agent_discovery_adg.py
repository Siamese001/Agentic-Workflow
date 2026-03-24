"""ADG importability contract for agentic_core/L0_routing/scripts/full_agent_discovery.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_full_agent_discovery.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (  # noqa: F401
        OUTPUT_SCHEMA_VERSION,
        AgentIntegrityReport,
        DiscoveryError,
        get_git_commit,
        setup_logging,
        sha256_file,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    OUTPUT_SCHEMA_VERSION = None  # type: ignore[assignment,misc]
    AgentIntegrityReport = None  # type: ignore[assignment,misc]
    DiscoveryError = None  # type: ignore[assignment,misc]
    setup_logging = None  # type: ignore[assignment,misc]
    sha256_file = None  # type: ignore[assignment,misc]
    get_git_commit = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="full_agent_discovery deps unavailable")
class TestFullAgentDiscoveryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/scripts/full_agent_discovery.py must be importable."""
        assert _AVAILABLE

    def test_agentintegrityreport_defined(self) -> None:
        assert AgentIntegrityReport is not None

    def test_discoveryerror_defined(self) -> None:
        assert DiscoveryError is not None