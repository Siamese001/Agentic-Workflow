"""DEPRECATED shim — renamed to decision_ledger_integrity (Author-Gate decoupling, ADR-093). Remove after 2026-07 sunset."""
import sys as _sys
import warnings as _w
_w.warn("author_gate_ledger_integrity renamed to decision_ledger_integrity; update imports", DeprecationWarning, stacklevel=2)
import decision_ledger_integrity as _mod
_sys.modules[__name__] = _mod
