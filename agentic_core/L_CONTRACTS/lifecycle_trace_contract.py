"""Shim: redirects agentic_core.L_CONTRACTS.lifecycle_trace_contract -> agentic_core.runtime.lifecycle_trace_contract."""
import sys as _sys
import importlib as _importlib

_canonical = _importlib.import_module("agentic_core.runtime.lifecycle_trace_contract")
_sys.modules[__name__] = _canonical
