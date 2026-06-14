"""DEPRECATED shim — renamed to decision_ledger_calibrator (Author-Gate decoupling, ADR-093). Remove after 2026-07 sunset."""
import sys as _sys
import warnings as _w
_w.warn("author_gate_calibrator renamed to decision_ledger_calibrator; update imports", DeprecationWarning, stacklevel=2)
from ops_scripts.calibration import decision_ledger_calibrator as _mod
_sys.modules[__name__] = _mod
