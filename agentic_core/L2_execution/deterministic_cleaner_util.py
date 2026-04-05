"""Shim: re-exports from canonical location for backward compatibility."""
import sys as _sys, types as _types, importlib as _il
_p = _types.ModuleType(__name__); _sys.modules[__name__] = _p
_c = _il.import_module('agentic_core.L2_execution.utils.deterministic_cleaner_util'); _sys.modules[__name__] = _c; _p.__dict__.update(_c.__dict__)
