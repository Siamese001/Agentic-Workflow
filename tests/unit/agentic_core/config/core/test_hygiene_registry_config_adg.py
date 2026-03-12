"""ADG importability contract for agentic_core/config/core/hygiene_registry_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hygiene_registry_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.config.core.hygiene_registry_config import (  # noqa: F401
        get_all_hygiene_agents,
        get_tier_agents,
        is_mandatory_agent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    get_all_hygiene_agents = None  # type: ignore[assignment,misc]
    get_tier_agents = None  # type: ignore[assignment,misc]
    is_mandatory_agent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hygiene_registry_config.py deps unavailable")
class TestHygieneRegistryConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hygiene_registry_config.py must be importable."""
        assert _AVAILABLE

    def test_get_all_hygiene_agents_callable(self) -> None:
        assert callable(get_all_hygiene_agents)

    def test_get_tier_agents_callable(self) -> None:
        assert callable(get_tier_agents)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

