"""Unit tests for the Tier 3 auto-wrap helper.

Plan: `.windsurf/plans/runtime-adg-tier3-broader-adoption-8f2d1c.md`

Validates `install_seal_step_autowrap` correctly wraps concrete `execute`
methods on subclasses — sync and async — while leaving abstract methods,
missing methods, and already-wrapped methods alone.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

import pytest

from apps_shared.utils.engine_seal_step_mixin import install_seal_step_autowrap
from system_learning.runtime_adg.runtime_span_emitter import (
    SPAN_STEP_SEAL,
    reset_current_adapter,
    set_current_adapter,
)


class _FakeAdapter:
    def __init__(self) -> None:
        self._completed_spans: list[dict[str, Any]] = []


class _BaseWithAutowrap(ABC):
    """Minimal stand-in for BaseExecEngine / BaseResearchEngine / etc."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        install_seal_step_autowrap(cls)

    @abstractmethod
    def execute(self, input_data: Any) -> Any: ...


class _SyncChild(_BaseWithAutowrap):
    def execute(self, input_data: Any) -> str:
        return f"sync:{input_data}"


class _AsyncChild(_BaseWithAutowrap):
    async def execute(self, input_data: Any) -> str:
        await asyncio.sleep(0)
        return f"async:{input_data}"


class _IntermediateAbstract(_BaseWithAutowrap):
    """Does NOT override execute — stays abstract; wrapper must no-op."""


class TestAutowrap:
    def test_sync_subclass_wrapped_emits_seal(self) -> None:
        adapter = _FakeAdapter()
        tok = set_current_adapter(adapter)
        try:
            result = _SyncChild().execute("alpha")
        finally:
            reset_current_adapter(tok)
        assert result == "sync:alpha"
        seals = [s for s in adapter._completed_spans if s["name"] == SPAN_STEP_SEAL]
        assert len(seals) == 1
        assert seals[0]["attributes"]["step_id"].endswith("_SyncChild.execute")

    def test_async_subclass_wrapped_emits_seal(self) -> None:
        adapter = _FakeAdapter()
        tok = set_current_adapter(adapter)
        try:
            result = asyncio.run(_AsyncChild().execute("beta"))
        finally:
            reset_current_adapter(tok)
        assert result == "async:beta"
        seals = [s for s in adapter._completed_spans if s["name"] == SPAN_STEP_SEAL]
        assert len(seals) == 1
        assert seals[0]["attributes"]["step_id"].endswith("_AsyncChild.execute")

    def test_no_adapter_active_runs_untouched(self) -> None:
        # No set_current_adapter — fail-open path.
        assert _SyncChild().execute("gamma") == "sync:gamma"

    def test_intermediate_abstract_is_not_wrapped(self) -> None:
        """Classes that don't override execute MUST not acquire a wrapper."""
        # _IntermediateAbstract doesn't define execute -> install is a no-op.
        assert "execute" not in _IntermediateAbstract.__dict__

    def test_idempotent_double_wrap(self) -> None:
        """Calling install twice on the same class MUST be a no-op."""
        original_wrapper = _SyncChild.__dict__["execute"]
        install_seal_step_autowrap(_SyncChild)
        # Must still be the same function object, not wrapped again.
        assert _SyncChild.__dict__["execute"] is original_wrapper

    def test_output_hash_populated_from_return(self) -> None:
        adapter = _FakeAdapter()
        tok = set_current_adapter(adapter)
        try:
            _SyncChild().execute("delta")
        finally:
            reset_current_adapter(tok)
        seal = [s for s in adapter._completed_spans if s["name"] == SPAN_STEP_SEAL][0]
        assert seal["attributes"]["output_hash"]  # non-empty

    def test_exception_still_seals_with_error_status(self) -> None:
        class _Raiser(_BaseWithAutowrap):
            def execute(self, input_data: Any) -> Any:
                raise ValueError("boom")

        adapter = _FakeAdapter()
        tok = set_current_adapter(adapter)
        try:
            with pytest.raises(ValueError, match="boom"):
                _Raiser().execute(None)
        finally:
            reset_current_adapter(tok)
        seals = [s for s in adapter._completed_spans if s["name"] == SPAN_STEP_SEAL]
        assert len(seals) == 1
        assert seals[0]["status"] == "error"
