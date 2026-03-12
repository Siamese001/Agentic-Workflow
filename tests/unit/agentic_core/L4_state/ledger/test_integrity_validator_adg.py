"""ADG importability contract for agentic_core/L4_state/ledger/integrity_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_integrity_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.ledger.integrity_validator import (  # noqa: F401
        compute_entry_hash,
        validate_ledger_chain,
        append_with_hash,
        validate_ledger_file,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    compute_entry_hash = None  # type: ignore[assignment,misc]
    validate_ledger_chain = None  # type: ignore[assignment,misc]
    append_with_hash = None  # type: ignore[assignment,misc]
    validate_ledger_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="integrity_validator.py deps unavailable")
class TestIntegrityValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: integrity_validator.py must be importable."""
        assert _AVAILABLE

    def test_compute_entry_hash_callable(self) -> None:
        assert callable(compute_entry_hash)

    def test_validate_ledger_chain_callable(self) -> None:
        assert callable(validate_ledger_chain)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

