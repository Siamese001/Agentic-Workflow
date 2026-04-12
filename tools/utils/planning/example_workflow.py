"""Shim: re-exports from canonical location for backward compatibility."""

import importlib as _il
import sys as _sys
import types as _types

_p = _types.ModuleType(__name__)
_sys.modules[__name__] = _p
_c = _il.import_module("tools.utils.planning.workflows.example_workflow")
_sys.modules[__name__] = _c
_p.__dict__.update(_c.__dict__)
