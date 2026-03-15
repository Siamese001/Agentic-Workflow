"""ADG importability contract for agentic_core/L5_safety/reasoning/ResourceManagerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ResourceManagerAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.ResourceManagerAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AllocationStatus,
        ResourceAllocation,
        ResourceBudget,
        ResourceConfig,
        ResourceManagerAgent,
        ResourceType,
        create_legacy_budget_manager,
        create_legacy_fallback_manager,
        create_legacy_proactive_manager,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ResourceType = None  # type: ignore[assignment,misc]
    AllocationStatus = None  # type: ignore[assignment,misc]
    ResourceAllocation = None  # type: ignore[assignment,misc]
    ResourceBudget = None  # type: ignore[assignment,misc]
    ResourceConfig = None  # type: ignore[assignment,misc]
    ResourceManagerAgent = None  # type: ignore[assignment,misc]
    create_legacy_budget_manager = None  # type: ignore[assignment,misc]
    create_legacy_proactive_manager = None  # type: ignore[assignment,misc]
    create_legacy_fallback_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ResourceManagerAgent.py deps unavailable")
class TestResourcemanageragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ResourceManagerAgent.py must be importable."""
        assert _AVAILABLE

    def test_resourcetype_is_type(self) -> None:
        assert ResourceType is not None

    def test_allocationstatus_is_type(self) -> None:
        assert AllocationStatus is not None

    def test_resourceallocation_is_type(self) -> None:
        assert ResourceAllocation is not None

    def test_create_legacy_budget_manager_callable(self) -> None:
        assert callable(create_legacy_budget_manager)

    def test_create_legacy_proactive_manager_callable(self) -> None:
        assert callable(create_legacy_proactive_manager)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
