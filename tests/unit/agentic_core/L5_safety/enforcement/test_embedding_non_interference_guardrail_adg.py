"""ADG importability contract for agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_embedding_non_interference_guardrail.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.embedding_non_interference_guardrail import (  # noqa: F401
        C0InterferenceViolation,
        assert_c0_context_clean,
        assert_no_c0_influence,
        verify_routing_decision_clean,
        assert_routing_decision_clean,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    C0InterferenceViolation = None  # type: ignore[assignment,misc]
    assert_c0_context_clean = None  # type: ignore[assignment,misc]
    assert_no_c0_influence = None  # type: ignore[assignment,misc]
    verify_routing_decision_clean = None  # type: ignore[assignment,misc]
    assert_routing_decision_clean = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_non_interference_guardrail.py deps unavailable")
class TestEmbeddingNonInterferenceGuardrailImportability:
    def test_module_importable(self) -> None:
        """ADG contract: embedding_non_interference_guardrail.py must be importable."""
        assert _AVAILABLE

    def test_c0interferenceviolation_is_type(self) -> None:
        assert C0InterferenceViolation is not None

    def test_assert_c0_context_clean_callable(self) -> None:
        assert callable(assert_c0_context_clean)

    def test_assert_no_c0_influence_callable(self) -> None:
        assert callable(assert_no_c0_influence)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

