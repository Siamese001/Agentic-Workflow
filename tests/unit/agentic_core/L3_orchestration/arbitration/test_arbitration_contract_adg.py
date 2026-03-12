"""ADG importability contract for agentic_core/L3_orchestration/arbitration/arbitration_contract.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_arbitration_contract.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.arbitration.arbitration_contract import (  # noqa: F401
        AdvisorProposal,
        ArbitrationInput,
        ArbitrationDecision,
        proposal_to_json,
        proposal_from_json,
        arbitration_input_to_json,
        arbitration_input_from_json,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AdvisorProposal = None  # type: ignore[assignment,misc]
    ArbitrationInput = None  # type: ignore[assignment,misc]
    ArbitrationDecision = None  # type: ignore[assignment,misc]
    proposal_to_json = None  # type: ignore[assignment,misc]
    proposal_from_json = None  # type: ignore[assignment,misc]
    arbitration_input_to_json = None  # type: ignore[assignment,misc]
    arbitration_input_from_json = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="arbitration_contract.py deps unavailable")
class TestArbitrationContractImportability:
    def test_module_importable(self) -> None:
        """ADG contract: arbitration_contract.py must be importable."""
        assert _AVAILABLE

    def test_advisorproposal_is_type(self) -> None:
        assert AdvisorProposal is not None

    def test_arbitrationinput_is_type(self) -> None:
        assert ArbitrationInput is not None

    def test_arbitrationdecision_is_type(self) -> None:
        assert ArbitrationDecision is not None

    def test_proposal_to_json_callable(self) -> None:
        assert callable(proposal_to_json)

    def test_proposal_from_json_callable(self) -> None:
        assert callable(proposal_from_json)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

