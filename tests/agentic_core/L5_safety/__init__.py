import sys as _sys
import importlib as _il
from pathlib import Path as _P

_root = str(_P(__file__).parent.parent.parent.parent)
if _root not in _sys.path:
    _sys.path.insert(0, _root)

_me = _sys.modules.get("agentic_core.L5_safety")
if _me is not None and "tests" in str(getattr(_me, "__file__", "")):
    _to_del = [
        k for k in list(_sys.modules)
        if k == "agentic_core.L5_safety" or k.startswith("agentic_core.L5_safety.")
    ]
    for _k in _to_del:
        del _sys.modules[_k]
    _il.import_module("agentic_core.L5_safety")
