"""DEPRECATED shim — renamed to decision_ledger_w1_bind (Author-Gate decoupling, ADR-093). Remove after 2026-07 sunset."""
import sys as _sys
import warnings as _w
_w.warn("author_gate_w1_bind renamed to decision_ledger_w1_bind; update imports", DeprecationWarning, stacklevel=2)
from tools.refactor_decisions import decision_ledger_w1_bind as _mod
_sys.modules[__name__] = _mod
