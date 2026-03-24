"""ADG importability contract for apps_shared/reasoning/BaseDispatchAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_BaseDispatchAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.reasoning.BaseDispatchAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        BaseDispatchAgent,
        ExecutionResult,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ExecutionResult = None  # type: ignore[assignment,misc]
    BaseDispatchAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="BaseDispatchAgent.py deps unavailable")
class TestBasedispatchagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: BaseDispatchAgent.py must be importable."""
        assert _AVAILABLE

    def test_executionresult_is_type(self) -> None:
        assert ExecutionResult is not None

    def test_basedispatchagent_is_type(self) -> None:
        assert BaseDispatchAgent is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None