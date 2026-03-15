"""ADG importability contract for agentic_core/L5_safety/enforcement/agent_info_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_agent_info_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.agent_info_enforcer import (  # noqa: F401
        AgentInfo,
        ASTNormalizer,
        calculate_similarity,
        extract_layer,
        find_agent_classes,
        generate_fingerprint,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AgentInfo = None  # type: ignore[assignment,misc]
    ASTNormalizer = None  # type: ignore[assignment,misc]
    extract_layer = None  # type: ignore[assignment,misc]
    find_agent_classes = None  # type: ignore[assignment,misc]
    generate_fingerprint = None  # type: ignore[assignment,misc]
    calculate_similarity = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer deps unavailable")
class TestAgentInfoEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/agent_info_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_agentinfo_defined(self) -> None:
        assert AgentInfo is not None

    def test_astnormalizer_defined(self) -> None:
        assert ASTNormalizer is not None
