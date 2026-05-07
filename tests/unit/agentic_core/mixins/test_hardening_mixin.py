"""Regression tests for ``agentic_core.mixins.hardening_mixin``.

Plan: ``anthropic-rag-gaps-7f3c2a.md``, phase W5.1.

Covers the NameError regression that blocked all real executor calls:
``execute_hardened`` caught ``CircuitBreakerOpenError`` in an except
clause while the class was only lazily imported inside a helper. Any
real call that raised it triggered ``NameError: name
'CircuitBreakerOpenError' is not defined`` instead of the clean
circuit-open path.
"""

from __future__ import annotations

import inspect

from agentic_core.L4_state.utils.circuit_breaker_util import (
    CircuitBreakerOpenError as CanonicalCircuitBreakerOpenError,
)
from agentic_core.mixins import hardening_mixin


def test_circuit_breaker_open_error_is_module_resolvable() -> None:
    """``CircuitBreakerOpenError`` must be bound at module scope.

    Guards against reintroduction of the lazy-import regression: the
    name MUST be resolvable without calling any helper, so ``except
    CircuitBreakerOpenError`` clauses inside ``execute_hardened`` can
    bind the class at function-definition time.
    """
    assert hasattr(hardening_mixin, "CircuitBreakerOpenError")
    assert hardening_mixin.CircuitBreakerOpenError is CanonicalCircuitBreakerOpenError


def test_execute_hardened_except_clause_binds_circuit_breaker_error() -> None:
    """The except CircuitBreakerOpenError clause must reference the
    module-scope name, not an undefined symbol.

    We parse the source of ``execute_hardened`` and confirm the
    CircuitBreakerOpenError token appears in an ``except`` context; the
    module-scope import above guarantees the name resolves cleanly.
    """
    source = inspect.getsource(hardening_mixin.HardeningMixin.execute_hardened)
    # Accept both single-line "except CircuitBreakerOpenError:" and
    # multi-line "except (\n    CircuitBreakerOpenError\n) as e:" syntax
    has_single_line = "except CircuitBreakerOpenError" in source
    has_multi_line = "except (" in source and "CircuitBreakerOpenError" in source
    assert has_single_line or has_multi_line, (
        "execute_hardened must still have the dedicated circuit-open "
        "except branch; if this was removed intentionally, update the "
        "regression test accordingly."
    )
