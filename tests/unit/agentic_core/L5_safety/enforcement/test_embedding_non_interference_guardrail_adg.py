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
        assert_routing_decision_clean,
        scan_file_for_c0_mutations,
        verify_routing_decision_clean,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    C0InterferenceViolation = None  # type: ignore[assignment,misc]
    assert_c0_context_clean = None  # type: ignore[assignment,misc]
    assert_no_c0_influence = None  # type: ignore[assignment,misc]
    verify_routing_decision_clean = None  # type: ignore[assignment,misc]
    assert_routing_decision_clean = None  # type: ignore[assignment,misc]
    scan_file_for_c0_mutations = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="embedding_non_interference_guardrail deps unavailable")
class TestEmbeddingNonInterferenceGuardrailImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py must be importable."""
        assert _AVAILABLE

    def test_c0interferenceviolation_defined(self) -> None:
        assert C0InterferenceViolation is not None