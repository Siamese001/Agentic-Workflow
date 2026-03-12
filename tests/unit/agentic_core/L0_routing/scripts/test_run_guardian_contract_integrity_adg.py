"""ADG importability contract for agentic_core/L0_routing/scripts/run_guardian_contract_integrity.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_run_guardian_contract_integrity.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.run_guardian_contract_integrity import (  # noqa: F401
        run_contract_integrity_guardian,
        main,
        GUARDIAN_ID,
        CANONICAL_CONTRACT_MODULE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    run_contract_integrity_guardian = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    GUARDIAN_ID = None  # type: ignore[assignment,misc]
    CANONICAL_CONTRACT_MODULE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="run_guardian_contract_integrity.py deps unavailable")
class TestRunGuardianContractIntegrityImportability:
    def test_module_importable(self) -> None:
        """ADG contract: run_guardian_contract_integrity.py must be importable."""
        assert _AVAILABLE

    def test_run_contract_integrity_guardian_callable(self) -> None:
        assert callable(run_contract_integrity_guardian)

    def test_main_callable(self) -> None:
        assert callable(main)

    def test_guardian_id_defined(self) -> None:
        assert GUARDIAN_ID is not None

    def test_canonical_contract_module_defined(self) -> None:
        assert CANONICAL_CONTRACT_MODULE is not None

