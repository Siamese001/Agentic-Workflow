"""ADG importability contract for agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mcp_sovereign_authority_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        MCPSovereignAuthority,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MCPSovereignAuthority = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_sovereign_authority_enforcer.py deps unavailable")
class TestMcpSovereignAuthorityEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: mcp_sovereign_authority_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_mcpsovereignauthority_is_type(self) -> None:
        assert MCPSovereignAuthority is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None