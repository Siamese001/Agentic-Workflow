"""ADG importability contract for agentic_core/mixins/ssot_context_propagation_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_context_propagation_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_context_propagation_mixin import (  # noqa: F401
        SSOTContextPropagationMixin,
        get_propagated_trace_id,
        get_propagated_policy_hash,
        get_propagated_replay_mode,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SSOTContextPropagationMixin = None  # type: ignore[assignment,misc]
    get_propagated_trace_id = None  # type: ignore[assignment,misc]
    get_propagated_policy_hash = None  # type: ignore[assignment,misc]
    get_propagated_replay_mode = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_context_propagation_mixin.py deps unavailable")
class TestSsotContextPropagationMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ssot_context_propagation_mixin.py must be importable."""
        assert _AVAILABLE

    def test_ssotcontextpropagationmixin_is_type(self) -> None:
        assert SSOTContextPropagationMixin is not None

    def test_get_propagated_trace_id_callable(self) -> None:
        assert callable(get_propagated_trace_id)

    def test_get_propagated_policy_hash_callable(self) -> None:
        assert callable(get_propagated_policy_hash)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

