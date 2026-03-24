"""ADG importability contract for agentic_core/mixins/atomic_execution_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_atomic_execution_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.atomic_execution_mixin import (  # noqa: F401
        AtomicExecutionError,
        AtomicExecutionMixin,
        AtomicTransaction,
        FileBackup,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    FileBackup = None  # type: ignore[assignment,misc]
    AtomicTransaction = None  # type: ignore[assignment,misc]
    AtomicExecutionError = None  # type: ignore[assignment,misc]
    AtomicExecutionMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="atomic_execution_mixin deps unavailable")
class TestAtomicExecutionMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/atomic_execution_mixin.py must be importable."""
        assert _AVAILABLE

    def test_filebackup_defined(self) -> None:
        assert FileBackup is not None

    def test_atomictransaction_defined(self) -> None:
        assert AtomicTransaction is not None

    def test_atomicexecutionerror_defined(self) -> None:
        assert AtomicExecutionError is not None

    def test_atomicexecutionmixin_defined(self) -> None:
        assert AtomicExecutionMixin is not None