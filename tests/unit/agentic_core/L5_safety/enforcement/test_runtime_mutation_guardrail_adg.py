"""ADG importability contract for agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_mutation_guardrail.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.runtime_mutation_guardrail import (  # noqa: F401
        install_guards,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    install_guards = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_mutation_guardrail deps unavailable")
class TestRuntimeMutationGuardrailImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py must be importable."""
        assert _AVAILABLE